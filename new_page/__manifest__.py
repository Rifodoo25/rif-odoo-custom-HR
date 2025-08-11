{
    'name': 'Authentication for Jobs',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Redirect users to login page instead of 403 error',
    'depends': ['website', 'hr_recruitment','website_hr_recruitment'],
    'data': [
        'views/templates.xml',
    ],  # No templates needed for controller solution
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',}