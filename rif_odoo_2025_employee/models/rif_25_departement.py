from odoo import models, fields,_

class HrRif25Department(models.Model):
    _inherit = 'hr.department'

    description = fields.Text(string=_("Description"),store=True)