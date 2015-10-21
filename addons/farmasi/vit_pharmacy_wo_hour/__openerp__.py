{
    'name': 'Pharmacy Manufacture Work Order Machine Hour',
    'version': '1.0',
    'category': 'Manufacture',
    'description': """
        1. Menunculkan Tab Bom Man Hour Di WO
        2. Menambahkan Tab Mechine Hour (wo_machine_hour)
       """,
    'author': 'Wawan|Fb/email:rahasia2alpha@gmail.com',
    'depends': ['mrp','mrp_operations'],
    'data': [
        'mrp_operations_view.xml',
        'security/ir.model.access.csv'
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}