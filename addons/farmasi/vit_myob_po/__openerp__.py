{
    'name': 'PO export to MYOB',
    'version': '1.0',
    'category': 'Purchase',
    'description': """
PO export to MYOB       """,
    'author': 'akhmad.daniel@gmail.com',
    'depends': ['purchase'],
    'data': [
        'po.xml',
        'cron.xml',
        'security/ir.model.access.csv',
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}