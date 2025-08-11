from odoo import models, fields, _
from odoo.exceptions import UserError

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