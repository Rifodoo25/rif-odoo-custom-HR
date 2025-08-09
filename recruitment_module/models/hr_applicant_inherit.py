from odoo import models, fields


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    
    x_custom_note = fields.Char(string="Custom Note")
