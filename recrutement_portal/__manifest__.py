{
    'name': 'Authentication for Jobs',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Redirect users to login page instead of 403 error and track candidate applications',
    'depends': [
        'website', 
        'hr_recruitment',
        'website_hr_recruitment',
        'portal'  # Added portal dependency for better integration
    ],
    'data': [
        'views/templates.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}


