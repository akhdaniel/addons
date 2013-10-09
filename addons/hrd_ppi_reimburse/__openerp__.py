{
    'name': 'ppi_reimburse',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource - Reimburse PT.PPI
""",    
    'depends': ['hr','hrd_ppi','hrd_ppi_payroll'],
    'update_xml':[
            'reimburse_view.xml',
            'reimburse_workflow.xml',
            ],
    'data': [],
    'installable':True,
}
