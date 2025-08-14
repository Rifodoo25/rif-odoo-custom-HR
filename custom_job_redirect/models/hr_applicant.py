from odoo import models, fields, api

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    
    # Additional fields for the custom form
    university = fields.Char(string='Université')
    education_level = fields.Selection([
        ('bac', 'Baccalauréat'),
        ('bac+1', 'Bac+1'),
        ('bac+2', 'Bac+2'),
        ('bac+3', 'Bac+3 (Licence)'),
        ('bac+4', 'Bac+4'),
        ('bac+5', 'Bac+5 (Master)'),
        ('bac+6', 'Bac+6'),
        ('bac+7', 'Bac+7'),
        ('bac+8', 'Bac+8 (Doctorat)'),
    ], string='Niveau d\'études')
    
    speciality = fields.Char(string='Spécialité')
    stage_type = fields.Selection([
        ('pfe', 'PFE (Projet de Fin d\'Études)'),
        ('stage_ete', 'Stage d\'été'),
        ('stage_ouvrier', 'Stage ouvrier'),
        ('stage_technicien', 'Stage technicien'),
        ('autre', 'Autre'),
    ], string='Type de stage')
    
    stage_agreement = fields.Boolean(string='Convention de stage', default=False)
    start_date = fields.Date(string='Date de début')
    end_date = fields.Date(string='Date de fin')
    duration = fields.Char(string='Durée')
    linkedin_profile = fields.Char(string='Profil LinkedIn')