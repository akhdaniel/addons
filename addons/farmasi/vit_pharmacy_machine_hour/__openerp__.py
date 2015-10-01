{
    'name': 'Pharmacy Manufacture Machine Hour',
    'version': '1.0',
    'category': 'Manufacture',
    'description': """
        1. Menambahkan Master Mesin 
        2. Menambahkan Bom Man Hour
        3. Menambahkan Bom Mechine Hour
       """,
    'author': 'Wawan|Fb/email:rahasia2alpha@gmail.com',
    'depends': ['mrp'],
    'data': [
        'bom_man_hour.xml',
        'bom_machine_hour.xml',
        'machine_master.xml',
        'security/ir.model.access.csv',
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}