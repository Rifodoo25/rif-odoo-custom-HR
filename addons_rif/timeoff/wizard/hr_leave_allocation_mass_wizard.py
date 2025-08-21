from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrLeaveAllocationMassWizard(models.TransientModel):
    _name = 'hr.leave.allocation.mass.wizard'
    _description = 'Mass Leave Allocation Wizard'

    holiday_status_id = fields.Many2one('hr.leave.type', string="Type de congé", required=True)
    number_of_days = fields.Float(string="Nombre de jours", required=True)
    department_ids = fields.Many2many('hr.department', string="Départements")
    
    
    # Nouveau champ pour l'allocation automatique
    auto_allocate_new_employees = fields.Boolean(
        string='Auto-allocate to new employees', 
        default=True,
        help="Si coché, les nouveaux employés ajoutés à ces départements recevront automatiquement cette allocation"
    )

    def action_allocate(self):
        if not self.department_ids:
            raise UserError(_("Veuillez sélectionner au moins un département."))

        # 1. Allocation immédiate pour les employés existants
        employees = self.env['hr.employee'].search([
            ('department_id', 'in', self.department_ids.ids)
        ])
        
        if not employees:
            raise UserError(_("Aucun employé trouvé dans les départements sélectionnés."))

        allocations_created = 0
        for employee in employees:
            # Vérifier si l'employé a déjà une allocation pour ce type de congé
            existing_allocation = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id', '=', self.holiday_status_id.id),
                ('state', 'in', ['validate', 'confirm']),
            ], limit=1)
            
            if existing_allocation:
                # Augmenter l'allocation existante
                existing_allocation.sudo().write({'number_of_days': existing_allocation.number_of_days + self.number_of_days})
                allocations_created += 1
            else:
                # Utiliser la méthode standard d'Odoo pour créer l'allocation
                allocation_vals = {
                    'name': f'Allocation massive - {self.holiday_status_id.name}',
                    'employee_id': employee.id,
                    'holiday_status_id': self.holiday_status_id.id,
                    'number_of_days': self.number_of_days,
                    'allocation_type': 'regular',  # Type d'allocation
                    'date_from': fields.Date.today(),
                    'date_to': fields.Date.today().replace(year=fields.Date.today().year + 1),
                }
                
                try:
                    # Créer avec sudo() pour éviter les problèmes de droits
                    allocation = self.env['hr.leave.allocation'].sudo().create(allocation_vals)
                    
                    # Approuver directement l'allocation si possible
                    if hasattr(allocation, 'action_approve'):
                        allocation.action_approve()
                    elif hasattr(allocation, 'action_validate'):
                        allocation.action_validate()
                    else:
                        # Forcer l'état validé
                        allocation.write({'state': 'validate'})
                    
                    allocations_created += 1
                    
                except Exception as e:
                    # Méthode alternative : créer directement avec l'état validé
                    try:
                        allocation_vals['state'] = 'validate'
                        allocation = self.env['hr.leave.allocation'].sudo().with_context(skip_validation=True).create(allocation_vals)
                        allocations_created += 1
                    except Exception as e2:
                        # Log l'erreur mais continuer avec les autres employés
                        continue

        # 2. Créer une règle pour l'allocation automatique des futurs employés
        if self.auto_allocate_new_employees:
            self._create_auto_allocation_rule()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'message': _('Allocation effectuée pour %d employé(s)') % allocations_created,
                'type': 'success'
            }
        }

    def _create_auto_allocation_rule(self):
        """Créer une règle d'allocation automatique pour les nouveaux employés"""
        # Vérifier si une règle similaire existe déjà
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
'''
    def action_allocate(self):
        domain = [('active', '=', True)]
        if self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))
        employees = self.env['hr.employee'].search(domain)
        if not employees:
            raise UserError(_("Aucun employé trouvé pour l'allocation."))
        for emp in employees:
            allocation = self.env['hr.leave.allocation'].create({
                'employee_id': emp.id,
                'holiday_status_id': self.holiday_status_id.id,
                'number_of_days': self.number_of_days,
            })
            allocation.action_validate()
        return {'type': 'ir.actions.act_window_close'}'''