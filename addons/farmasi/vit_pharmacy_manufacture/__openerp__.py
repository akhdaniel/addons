{
    'name': 'Pharmacy Manufacture',
    'version': '1.0',
    'category': 'Manufacture',
    'description': """
        1. Modul Forecast Product Di input secara manual oleh user  
        2. Modul Master Production Schedule
        
       """,
    'author': 'Wawan|Fb/email:rahasia2alpha@gmail.com',
    'depends': ['mrp','vit_batch_number_in_mo'],
    'data': [
        'forecast_product.xml',
        'mps.xml',
        'wps.xml',
        'mrp_view.xml',
        'security/ir.model.access.csv'
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}