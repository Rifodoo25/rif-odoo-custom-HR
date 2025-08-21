from odoo import api, models, fields, _
from odoo.exceptions import UserError , ValidationError
from datetime import datetime, date 

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    refuse_reason = fields.Text(string="Raison du refus")
    
    # NOUVELLE FONCTION UTILITAIRE (à ajouter)
    def _convert_to_date(self, date_value):
        """Convertir datetime en date si nécessaire"""
        if isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, date):
            return date_value
        return date_value
    
     # -------- Utilitaire : action du wizard --------
    def _get_refuse_wizard_action(self):
        """Retourne l'action qui ouvre le wizard de refus pour l'enregistrement courant."""
        self.ensure_one()
        action = self.env.ref('timeoff.action_leave_refuse_wizard').read()[0]
        # forcer les active_* pour lier le wizard au leave sélectionné
        action['context'] = {
            **self._context,
            'active_id': self.id,
            'active_ids': [self.id],
            'active_model': 'hr.leave',
        }
        return action

    # -------- Interception du clic "Refuser" depuis la LISTE --------
    def action_refuse(self):
        """
        Si appelé depuis la liste (ou n'importe où) SANS passer par le wizard,
        on ouvre le wizard. Si appelé depuis le wizard (context flag), on refuse vraiment.
        """
        # 1) contrôles d'état (les seuls états refusables)
        refusables = {'confirm', 'validate1', 'validate'}
        if any(r.state not in refusables for r in self):
            # si l'appel vient de la liste, on n'ouvre rien ; si du wizard on lève une erreur explicite
            if not self.env.context.get('from_refuse_wizard'):
                return False
            raise UserError(_("Cette demande n'est pas dans un état refus-able."))

        # 2) Ouverture du wizard si on n'y est pas déjà
        if not self.env.context.get('from_refuse_wizard'):
            # clic direct sur "Refuser" (liste/kanban/form d'origine) -> ouvrir popup
            return self._get_refuse_wizard_action()

        # 3) Exécution du refus réel (appelé par le wizard)
        current_employee = self.env.user.employee_id

        # logique de refus standard + marquage des approbateurs
        self._notify_manager()
        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({
            'state': 'refuse',
            'first_approver_id': current_employee.id
        })
        (self - validated_holidays).write({
            'state': 'refuse',
            'second_approver_id': current_employee.id
        })
        self.mapped('meeting_id').write({'active': False})

        # message au salarié (unique, incluant la raison si présente)
        for holiday in self:
            if holiday.employee_id.user_id:
                body = _('Votre %(leave_type)s prévu le %(date)s a été refusé.') % {
                    'leave_type': holiday.holiday_status_id.display_name,
                    'date': holiday.date_from.strftime('%d/%m/%Y') if holiday.date_from else 'N/A',
                }
                if holiday.refuse_reason:
                    body += ' ' + _('Raison : %s') % holiday.refuse_reason

                holiday.with_context(tracking_disable=True, mail_notrack=True).message_post(
                    body=body,
                    partner_ids=holiday.employee_id.user_id.partner_id.ids,
                )

        self.activity_update()
        return True

    # --- (le reste de tes méthodes inchangé) ---
    @api.onchange('state')
    def _onchange_state(self):
        if self.state != 'refuse':
            self.refuse_reason = False
    
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
            # Vérifier seulement pour les types de congés qui nécessitent une allocation
            if leave.holiday_status_id.requires_allocation == 'yes':
                allocation = self.env['hr.leave.allocation'].search([
                    ('employee_id', '=', leave.employee_id.id),
                    ('holiday_status_id', '=', leave.holiday_status_id.id),
                    ('state', '=', 'validate'),
                ], limit=1)

                if allocation:
                    # Convertir toutes les dates au même format pour éviter l'erreur de comparaison
                    alloc_from = self._convert_to_date(allocation.date_from)
                    alloc_to = self._convert_to_date(allocation.date_to)
                    leave_from = self._convert_to_date(leave.date_from)
                    leave_to = self._convert_to_date(leave.date_to)
                    
                    if not (alloc_from <= leave_from and alloc_to >= leave_to):
                        raise ValidationError(_("Impossible d'envoyer la demande : la période demandée dépasse la période programmée dans l'allocation."))
                else:
                    # Seulement si une allocation est requise
                    raise ValidationError(_("Aucune allocation valide trouvée pour ce type de congé."))
    
    @api.model_create_multi
    def create(self, vals_list):
        holidays = super(HrLeave, self).create(vals_list)
        admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)

        # Liste des XML IDs des types de congés à ignorer
        types_sans_email = [
            'hr_holidays.holiday_status_cl',
            'hr_holidays.holiday_status_sl',
            'hr_holidays.holiday_status_unpaid',
            'hr_holidays.holiday_status_comp',
            'hr_holidays_attendance.holiday_status_extra_hours',
            'hr_holidays.hr_holiday_status_dv',
            'hr_holidays.holiday_status_training',
        ]

        for holiday in holidays:
            # Vérifier si le type de congé est dans la liste à ignorer
            if not holiday.holiday_status_id:
                continue

            # On compare directement avec env.ref pour chaque type
            if any(holiday.holiday_status_id.id == self.env.ref(xml_id).id for xml_id in types_sans_email):
                continue

            employee = holiday.employee_id
            manager_partner = (
                employee.parent_id.user_id.partner_id
                if employee.parent_id and employee.parent_id.user_id
                else None
            )

            partner_ids_to_subscribe = set()
            if admin_user and admin_user.partner_id:
                partner_ids_to_subscribe.add(admin_user.partner_id.id)
            if manager_partner:
                partner_ids_to_subscribe.add(manager_partner.id)

            existing_followers = set(holiday.message_follower_ids.mapped('partner_id').ids)
            new_followers = list(partner_ids_to_subscribe - existing_followers)
            if new_followers:
                holiday.message_subscribe(partner_ids=new_followers)

            holiday.with_context().message_post(
                body=_(
                    "Nouvelle demande de congé :\n"
                    "- Employé : %(employee)s\n"
                    "- Type de congé : %(type)s\n"
                    "- Du : %(date_from)s\n"
                    "- Au : %(date_to)s"
                ) % {
                    'employee': employee.name,
                    'type': holiday.holiday_status_id.name,
                    'date_from': holiday.request_date_from.strftime('%d/%m/%Y') if holiday.request_date_from else 'N/A',
                    'date_to': holiday.request_date_to.strftime('%d/%m/%Y') if holiday.request_date_to else 'N/A',
                },
                subtype_xmlid='mail.mt_comment',
            )

        return holidays