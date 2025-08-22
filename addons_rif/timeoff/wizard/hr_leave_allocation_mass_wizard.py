from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrLeaveAllocationMassWizard(models.TransientModel):
    _name = 'hr.leave.allocation.mass.wizard'
    _description = 'Mass Leave Allocation Wizard'

    holiday_status_id = fields.Many2one('hr.leave.type', string="Type de congé", required=True)
    number_of_days = fields.Float(string="Nombre de jours", required=True)
    department_ids = fields.Many2many('hr.department', string="Départements")
    
    
    
    auto_allocate_new_employees = fields.Boolean(
        string='Auto-allocate to new employees', 
        default=True,
        help="Si coché, les nouveaux employés ajoutés à ces départements recevront automatiquement cette allocation"
    )

    def action_allocate(self):

        if self.number_of_days <= 0:
            raise UserError(_("Le champ 'Nombre de jours' est obligatoire et doit être supérieur à 0."))
        
        if not self.department_ids:
            raise UserError(_("Veuillez sélectionner au moins un département."))


        employees = self.env['hr.employee'].search([
            ('department_id', 'in', self.department_ids.ids)
        ])
        
        if not employees:
            raise UserError(_("Aucun employé trouvé dans les départements sélectionnés."))

        allocations_created = 0
        for employee in employees:
            
            existing_allocation = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id', '=', self.holiday_status_id.id),
                ('state', 'in', ['validate', 'confirm']),
            ], limit=1)
            
            if existing_allocation:
                
                existing_allocation.sudo().write({'number_of_days': existing_allocation.number_of_days + self.number_of_days})
                allocations_created += 1
            else:
                
                allocation_vals = {
                    'name': f'Allocation massive - {self.holiday_status_id.name}',
                    'employee_id': employee.id,
                    'holiday_status_id': self.holiday_status_id.id,
                    'number_of_days': self.number_of_days,
                    'allocation_type': 'regular',  # Type d'allocation
                }
                
                try:
                    
                    allocation = self.env['hr.leave.allocation'].sudo().create(allocation_vals)
                    
                    
                    if hasattr(allocation, 'action_approve'):
                        allocation.action_approve()
                    elif hasattr(allocation, 'action_validate'):
                        allocation.action_validate()
                    else:
                        
                        allocation.write({'state': 'validate'})
                    
                    allocations_created += 1
                    
                except Exception as e:
                    
                    try:
                        allocation_vals['state'] = 'validate'
                        allocation = self.env['hr.leave.allocation'].sudo().with_context(skip_validation=True).create(allocation_vals)
                        allocations_created += 1
                    except Exception as e2:
                        continue

        
        if self.auto_allocate_new_employees:
            self._create_auto_allocation_rule()

        return {
            # 'type': 'ir.actions.client',
            'type': 'ir.actions.act_window_close',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'message': _('Allocation effectuée pour %d employé(s)') % allocations_created,
                'type': 'success'
            }
        }

    def _create_auto_allocation_rule(self):
        """Créer une règle d'allocation automatique pour les nouveaux employés"""
        
        existing_rule = self.env['hr.leave.allocation.rule'].sudo().search([
            ('holiday_status_id', '=', self.holiday_status_id.id),
            ('department_ids', 'in', self.department_ids.ids),
            ('active', '=', True)
        ], limit=1)
        
        if not existing_rule:
            self.env['hr.leave.allocation.rule'].sudo().create({
                'name': f'Auto-allocation - {self.holiday_status_id.name} - {", ".join(self.department_ids.mapped("name"))}',
                'holiday_status_id': self.holiday_status_id.id,
                'department_ids': [(6, 0, self.department_ids.ids)],
                'number_of_days': self.number_of_days,
                'active': True,
            })
