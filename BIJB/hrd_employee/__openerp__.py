{
    'name': 'hrd_employee',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource Employee
""",    
    'depends': ['hr','hr_recruitment'],
    'update_xml':[
            'employee_view.xml',
            'action.xml',
            'working_Schedule.xml',
            ],
    'data': [],
    'installable':True,
}
