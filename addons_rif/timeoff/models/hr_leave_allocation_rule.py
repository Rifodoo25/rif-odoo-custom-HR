from odoo import api, fields, models, _

class HrLeaveAllocationRule(models.Model):
    _name = 'hr.leave.allocation.rule'
    _description = 'Leave Allocation Rule for New Employees'

    name = fields.Char(string='Rule Name', required=True)
    holiday_status_id = fields.Many2one('hr.leave.type', string='Leave Type', required=True)
    department_ids = fields.Many2many('hr.department', string='Departments')
    number_of_days = fields.Float(string='Number of Days', required=True)
    active = fields.Boolean(string='Active', default=True)
    
    def apply_to_employee(self, employee):
        """Appliquer cette règle à un employé spécifique"""
        if not self.active or not employee.department_id or employee.department_id.id not in self.department_ids.ids:
            return False
            
       
        existing_allocation = self.env['hr.leave.allocation'].sudo().search([
            ('employee_id', '=', employee.id),
            ('holiday_status_id', '=', self.holiday_status_id.id),
            ('state', 'in', ['validate', 'confirm', 'draft']),  # Inclure tous les états
            ('date_from', '<=', fields.Date.today()),
            ('date_to', '>=', fields.Date.today()),
        ], limit=1)
        
        if existing_allocation:
            return False
            
        auto_allocation = self.env['hr.leave.allocation'].sudo().search([
            ('employee_id', '=', employee.id),
            ('holiday_status_id', '=', self.holiday_status_id.id),
            ('name', 'ilike', f'Auto-allocation - {self.holiday_status_id.name}'),
        ], limit=1)
        
        if auto_allocation:
            return False
            

        try:
            self.env.cr.execute("""
                INSERT INTO hr_leave_allocation 
                (name, employee_id, holiday_status_id, number_of_days, state, 
                 date_from, date_to, create_date, write_date, create_uid, write_uid, allocation_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, %s)
            """, (
                f'Auto-allocation - {self.holiday_status_id.name}',
                employee.id,
                self.holiday_status_id.id,
                self.number_of_days,
                'validate',
                #fields.Date.today(),
                #fields.Date.today().replace(year=fields.Date.today().year + 1),
                self.env.uid,
                self.env.uid,
                'regular'
            ))
            

            self.env.cr.commit()
            return True
            
        except Exception as e:
            self.env.cr.rollback()
            return False