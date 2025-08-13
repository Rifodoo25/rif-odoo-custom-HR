from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrLeaveAllocationMassWizard(models.TransientModel):
    _name = 'hr.leave.allocation.mass.wizard'
    _description = 'Mass Leave Allocation Wizard'

    holiday_status_id = fields.Many2one('hr.leave.type', string="Type de congé", required=True)
    number_of_days = fields.Float(string="Nombre de jours", required=True)
    department_ids = fields.Many2many('hr.department', string="Départements")

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
        return {'type': 'ir.actions.act_window_close'}