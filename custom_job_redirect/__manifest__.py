
{
    'name': 'Custom Job Application Redirect',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Redirect users to login page instead of 403 error',
   'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'website',
        'website_hr_recruitment',

    ],
    'data': [
        'views/job_application_form.xml',
    ], 
    # No templates needed for controller solution
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}