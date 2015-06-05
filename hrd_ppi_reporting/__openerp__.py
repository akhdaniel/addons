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
        'security/ir.model.access.csv',
        'manpower.xml',
        'turnover.xml',
        'absensi.xml',
        'payroll.xml',
        'pajak.xml',
    ],
    'data' : [],
    'installable':True,
}