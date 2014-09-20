{
    'name': 'Distrbution Payment',
    'version': '0.3',
    'author'  :'vitraining.com',
    'category': 'Accounting',
    'description': """
Manage :
========

* Create LPH documnent
* Tarik invoice ke LPH
* Print out LPH
* Penyetoran ke Kasir
* Pelunasan Invoice yang ada di LPH 

""",    
    'depends': ['base','sale', 
        'sale_stock', 'product', 'account', 
        'vit_custom_djislu'],
    'data': [
        'lph.xml',
    ],
    'active': False,
    'installable': True,
    'application': True,
}
