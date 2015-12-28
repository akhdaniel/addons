{
    'name': 'lucas',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource PT.PPI
""",    
    'depends': ['hrd_ppi','hrd_overtime','hrd_ppi_attendance','hr_payroll','hrd_ppi_payroll'],
    'update_xml':[
         'recruitment.xml',
         'payroll.xml',
         'contract_view.xml',
         'employee_view.xml',
         'salary_structure.xml',
         'working_schedule.xml',
         'salary_structur_hl.xml',
             ],
    'data': [],
    'installable':True,
}
