{
    'version': '0.5',
    'name': 'Tiket.com import data',
    'depends': ['base','account','sale','purchase'],
    'author'  :'vitraining.com',
    'category': 'Tools',
    'description': """
Import data tiket.com, to generate customer invoice, payment, supplier invoice, 
""",
    'installable':True,
    'data': [
    	'menu.xml',
        'security/ir.model.access.csv',
        'invoice.xml',
    	'voucher.xml',
        'scheduler.xml',
        'bank_mapping.xml'
    ],
}
