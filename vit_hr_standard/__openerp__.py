{
    'name': 'HR Standard',
     'version': '0.4',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource Standard for Indonesia
""",    
    'depends': ['hr','hr_recruitment','hr_payroll','hr_attendance'],
    'update_xml':['menu.xml','hr_employs_tab.xml','salary_structure.xml','security/groups.xml','security/ir.model.access.csv',],
    'data': [],
    'active': False,
    'installable': True,
    'application': True,
}
