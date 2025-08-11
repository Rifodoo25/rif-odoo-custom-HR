{
    "name": "TimeOff",
    "summary": "Gestion des congés des employés",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources",
    "author": "Ton Nom ou Groupe",
    "website": "https://tonsite.com",
    "depends": ["base","hr","hr_holidays","mail","portal","calendar"],
    "data": [
        'security/ir.model.access.csv',
        'views/leave_refuse_wizard_views.xml',
        'views/hr_leave_views.xml',
        
        ],
    'installable': True,
    'auto_install': False,
    'application': True,
}