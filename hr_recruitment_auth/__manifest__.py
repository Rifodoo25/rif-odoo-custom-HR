{
    'name': 'Recruitment Authentication',
    'version': '1.0',
    'summary': 'Requires authentication for job applications',
    'description': """
        Redirects non-authenticated users to login/signup when applying for jobs
    """,
    'author': 'SiSi',
    'depends': ['website_hr_recruitment'],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'application': False,
}