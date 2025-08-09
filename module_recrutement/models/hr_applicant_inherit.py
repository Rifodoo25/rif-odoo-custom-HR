from odoo import models, fields

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    x_custom_note = fields.Text(string="Custom Note")
