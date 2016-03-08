{
    'name': 'hrd_Recruitment',
    'author'  :'www.vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource Recruitment Proses
""",    
    'depends': ['hr','hrd_employee','hr_recruitment','survey'],
    'update_xml':[
        'applicant_view.xml',
        'recruitment_view.xml',
            ],
    'data': [],
    'installable':True,
}
