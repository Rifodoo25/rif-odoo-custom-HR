from odoo import api, models, fields, _
from odoo.exceptions import UserError , ValidationError

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    refuse_reason = fields.Text(string="Raison du refus")

    def action_refuse(self):
        """Surcharge pour inclure la raison du refus dans les notifications"""
        current_employee = self.env.user.employee_id
        if any(holiday.state not in ['confirm', 'validate', 'validate1'] for holiday in self):
            raise UserError(_('Time off request must be confirmed or validated in order to refuse it.'))

        self._notify_manager()
        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        (self - validated_holidays).write({'state': 'refuse', 'second_approver_id': current_employee.id})
        self.mapped('meeting_id').write({'active': False})

        # Message simple avec la raison - UN SEUL EMAIL
        for holiday in self:
            if holiday.employee_id.user_id:
                body = _('Votre %(leave_type)s prévu le %(date)s a été refusé.') % {
                    'leave_type': holiday.holiday_status_id.display_name,
                    'date': holiday.date_from.strftime('%d/%m/%Y') if holiday.date_from else 'N/A'
                }
                
                # Ajouter la raison si elle existe
                if holiday.refuse_reason:
                    body += _('Raison : %s') % holiday.refuse_reason
                
                holiday.message_post(
                    body=body,
                    partner_ids=holiday.employee_id.user_id.partner_id.ids
                )

        self.activity_update()
        return True
    
    def _validate_leave_request(self):
        """Surcharge pour désactiver l'email automatique d'approbation"""
        import pytz
        from pytz import timezone
        
        holidays = self.filtered("employee_id")
        holidays._create_resource_leave()
        meeting_holidays = holidays.filtered(lambda l: l.holiday_status_id.create_calendar_meeting)
        meetings = self.env['calendar.event']
        
        if meeting_holidays:
            meeting_values_for_user_id = meeting_holidays._prepare_holidays_meeting_values()
            Meeting = self.env['calendar.event']
            for user_id, meeting_values in meeting_values_for_user_id.items():
                meetings += Meeting.with_user(user_id or self.env.uid).with_context(
                                allowed_company_ids=[],
                                no_mail_to_attendees=True,
                                calendar_no_videocall=True,
                                active_model=self._name
                            ).create(meeting_values)
        
        Holiday = self.env['hr.leave']
        for meeting in meetings:
            Holiday.browse(meeting.res_id).meeting_id = meeting

        # Email personnalisé avec désactivation du tracking
        for holiday in holidays:
            if holiday.employee_id.user_id:
                user_tz = timezone(holiday.tz)
                utc_tz = pytz.utc.localize(holiday.date_from).astimezone(user_tz)
                
                body = _('Votre %(leave_type)s prévu le %(date)s a été accepté.') % {
                    'leave_type': holiday.holiday_status_id.display_name,
                    'date': utc_tz.strftime('%d/%m/%Y')
                }
                
                # DÉSACTIVER LE TRACKING pour éviter le 2ème email
                holiday.with_context(tracking_disable=True, mail_notrack=True).message_post(
                    body=body,
                    partner_ids=holiday.employee_id.user_id.partner_id.ids
                )

    def write(self, values):
        """Surcharger write pour désactiver le tracking sur le champ state"""
        # Si on modifie le state, désactiver le tracking
        if 'state' in values and values.get('state') in ['validate', 'validate1']:
            # Désactiver le tracking pour éviter l'email automatique
            return super(HrLeave, self.with_context(
                tracking_disable=True,
                mail_notrack=True
            )).write(values)
        return super().write(values)
    

    def action_validate(self, check_state=True):
        # Récupérer l'objet correspondant au congé maladie (par ID XML)
        sick_leave_type = self.env.ref('hr_holidays.holiday_status_sl', raise_if_not_found=False)

        # Limitation des congés maladie à 5 jours par année
        for leave in self:
            if sick_leave_type and leave.holiday_status_id.id == sick_leave_type.id:
                year = leave.date_from.year
                domain = [
                    ('employee_id', '=', leave.employee_id.id),
                    ('holiday_status_id', '=', sick_leave_type.id),
                    ('state', 'in', ['validate', 'validate1']),
                    ('date_from', '>=', f'{year}-01-01'),
                    ('date_to', '<=', f'{year}-12-31'),
                ]
                sick_leaves = self.search(domain)

                # Calcul des jours déjà pris (hors celui en cours si pas encore validé)
                total_sick_days = sum(l.number_of_days for l in sick_leaves if l.id != leave.id)
                if leave.state not in ['validate', 'validate1']:
                    total_sick_days += leave.number_of_days

                if total_sick_days > 5:
                    raise ValidationError(_("Le congé maladie est limité à 5 jours par année."))

        current_employee = self.env.user.employee_id
        leaves = self._get_leaves_on_public_holiday()
        if leaves:
            raise ValidationError(_('The following employees are not supposed to work during that period:\n %s')
                                % ','.join(leaves.mapped('employee_id.name')))
        if check_state and any(
            holiday.state not in ['confirm', 'validate1']
            and holiday.validation_type != 'no_validation' for holiday in self
        ):
            raise UserError(_('Time off request must be confirmed in order to approve it.'))

        self.write({'state': 'validate'})

        leaves_second_approver = self.env['hr.leave']
        leaves_first_approver = self.env['hr.leave']

        for leave in self:
            if leave.validation_type == 'both':
                leaves_second_approver += leave
            else:
                leaves_first_approver += leave

        leaves_second_approver.write({'second_approver_id': current_employee.id})
        leaves_first_approver.write({'first_approver_id': current_employee.id})

        self._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            self.filtered(lambda holiday: holiday.validation_type != 'no_validation').activity_update()
        return True
    
    @api.constrains('holiday_status_id', 'employee_id', 'date_from', 'date_to', 'number_of_days')
    def _check_sick_leave_limit(self):
        sick_leave_type = self.env.ref('hr_holidays.holiday_status_sl', raise_if_not_found=False)
        paid_leave_type = self.env.ref('hr_holidays.holiday_status_cl', raise_if_not_found=False)  # <-- Utilisation de l'ID XML

        for leave in self:
            # --- Limite congé maladie ---
            if sick_leave_type and leave.holiday_status_id.id == sick_leave_type.id:
                year = leave.date_from.year
                domain = [
                    ('employee_id', '=', leave.employee_id.id),
                    ('holiday_status_id', '=', sick_leave_type.id),
                    ('state', 'in', ['validate', 'validate1']),
                    ('date_from', '>=', f'{year}-01-01'),
                    ('date_to', '<=', f'{year}-12-31'),
                    ('id', '!=', leave.id),
                ]
                sick_leaves = self.search(domain)
                total_sick_days = sum(l.number_of_days for l in sick_leaves) + leave.number_of_days
                if total_sick_days > 5:
                    raise ValidationError(_("Impossible d'envoyer la demande : le congé maladie est limité à 5 jours par année."))

            # --- Limite congé payé ---
            if paid_leave_type and leave.holiday_status_id.id == paid_leave_type.id:
                year = leave.date_from.year
                domain = [
                    ('employee_id', '=', leave.employee_id.id),
                    ('holiday_status_id', '=', paid_leave_type.id),
                    ('state', 'in', ['validate', 'validate1']),
                    ('date_from', '>=', f'{year}-01-01'),
                    ('date_to', '<=', f'{year}-12-31'),
                    ('id', '!=', leave.id),
                ]
                paid_leaves = self.search(domain)
                total_paid_days = sum(l.number_of_days for l in paid_leaves) + leave.number_of_days
                if total_paid_days > 20:
                    raise ValidationError(_("Impossible d'envoyer la demande : le congé payé est limité à 20 jours par année."))
                
    @api.constrains('employee_id', 'holiday_status_id', 'date_from', 'date_to')
    def _check_allocation_period(self):
        for leave in self:
            allocation = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', leave.employee_id.id),
                ('holiday_status_id', '=', leave.holiday_status_id.id),
                ('state', '=', 'validate'),
                ('date_from', '<=', leave.date_from),
                ('date_to', '>=', leave.date_to),
            ], limit=1)
            if not allocation:
                raise ValidationError(_(
                    "Impossible d'envoyer la demande : la période demandée dépasse la période programmée dans l'allocation."
                ))