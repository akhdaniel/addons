{
    'name': 'HRD PPI Access Rights',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Manage access rights based on employee access level - Human Resource PT.PPI
""",    
    'depends': ["hrd_ppi"],
    'data':[
            'security/hr_security.xml',
            'security/ir.model.access.csv',
            'res_user.xml',
            'hr_employee.xml',
            ],
    'installable':True,
}
