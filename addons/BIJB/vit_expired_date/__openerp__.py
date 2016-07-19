{
    'name': 'Warning Expired Date',
    'version': '1.0',
    'category': 'Warehouse',
    'description': """
Fitur Modul
==================================

* Warning Expred Date

       """,
    'author': 'vitraining.com',
    'depends': ['stock'],
    'data': [
        'stock_views.xml',
        'data/ir_cron_expired_date.xml',
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}
