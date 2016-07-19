{
    'name': 'hrd_Schedule_warning',
    'author'  :'macmour house',
    'category': 'Human Resources',
    'description': """
Human Resource Employee
""",    
    'depends': ['hr','hrd_employee'],
    'update_xml':[
            "schedule_view.xml",
            ],
    'data': [],
    'installable':True,
}
