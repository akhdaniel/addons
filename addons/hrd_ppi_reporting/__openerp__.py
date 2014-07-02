{
    'name': 'HRD PPI Reporting',
    'author'  :'vitraining.com',
    'depends': ['hrd_ppi'],
    'category': 'Reporting',
    'description': """
Human Resource PT.PPI Reporting
- add report for CV, Manpower, Employee Turnover
""",    
    'update_xml': [
        'manpower.xml',
        'turnover.xml',
    ],
    'data' : [],
    'installable':True,
}