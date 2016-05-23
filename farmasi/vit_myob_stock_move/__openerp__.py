{
    'name': 'Stock Move export to MYOB',
    'version': '1.0',
    'category': 'Warehouse',
    'description': """
Stock Move export to MYOB       """,
    'author': 'akhmad.daniel@gmail.com',
    'depends': ['stock'],
    'data': [
        'stock.xml',
        'cron.xml',
        'security/ir.model.access.csv',
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}