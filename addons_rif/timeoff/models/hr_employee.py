from odoo import api, models
import functools

def avoid_duplicate_calls(func):
    """Décorateur pour éviter les appels multiples de la même fonction"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        cache_key = f"{func.__name__}{self.id}"

        if hasattr(self.env, "_allocation_cache"):
            if cache_key in self.env._allocation_cache:
                return
        else:
            self.env._allocation_cache = set()

        self.env._allocation_cache.add(cache_key)
        result = func(self, *args, **kwargs)
        self.env._allocation_cache.discard(cache_key)
        return result
    return wrapper



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        for employee in employees:
            if employee.department_id:
                employee._apply_allocation_rules()
        return employees

    def write(self, vals):
        old_departments = {emp.id: emp.department_id.id if emp.department_id else False for emp in self}
        result = super().write(vals)

        if 'department_id' in vals:
            for employee in self:
                old_dept = old_departments.get(employee.id, False)
                new_dept = employee.department_id.id
                if old_dept != new_dept and new_dept:
                    employee._apply_allocation_rules()
        return result

    @avoid_duplicate_calls
    def _apply_allocation_rules(self):
        """Appliquer les règles d'allocation automatique à cet employé"""
        if not self.department_id:
            return

        rules = self.env['hr.leave.allocation.rule'].sudo().search([
            ('active', '=', True),
            ('department_ids', 'in', self.department_id.ids)
        ])

        for rule in rules:
            exists = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', self.id),
                ('holiday_status_id', '=', rule.holiday_status_id.id),
            ], limit=1)
            if not exists:
                rule.sudo().apply_to_employee(self)