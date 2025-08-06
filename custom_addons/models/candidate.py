from odoo import models, fields

class RecruitmentCandidate(models.Model):
    _name = 'recruitment.candidate'
    _description = 'Recruitment Candidate'
    _order = 'create_date desc'

    name = fields.Char(string="Full Name", required=True)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    experience_years = fields.Integer(string="Years of Experience")
    
    cv = fields.Binary(string="CV")
    cv_filename = fields.Char(string="CV Filename")

    motivation_letter = fields.Binary(string="Motivation Letter")
    motivation_letter_filename = fields.Char(string="Motivation Letter Filename")

    status = fields.Selection([
        ('new', 'New'),
        ('reviewed', 'Reviewed'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ], default='new', string="Status")
