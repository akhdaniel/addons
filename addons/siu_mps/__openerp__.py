{
    'name': 'Master Production Schedule',
    'version': '1.0',
    'category': 'Manufacture',
    'description': """
    This module aims to create master scheduling for production.    
       """,
    'author': 'Openerpsoft',
    'depends': ['siu_stock_order', 'mrp', 'sale','wtc_shop','procurement_jit'],
    'data': ['mps_view.xml'],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}