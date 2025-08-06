{
    'name': 'Recruitment',
    'version': '1.0',
    'summary': 'Manage recruitment process and candidates',
    'category': 'Human Resources',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/candidate_form.xml',
    ],
    'installable': True,
}
