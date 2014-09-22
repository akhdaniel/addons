{
    'name': 'Distrbution Payment',
    'version': '0.3',
    'author'  :'vitraining.com',
    'category': 'Accounting',
    'description': """
Manage :
========

* Create LPH documnent
* Tarik invoice ke LPH sesuai route LPH 
* Print out LPH, group by customer 
* Penyetoran ke Kasir via Cash / Bank Receipt Voucher 
* Pelunasan Invoice yang ada di LPH
   - input voucher no 
   - process, pay invoices 

""",    
    'depends': ['base','sale', 
        'sale_stock', 'product', 'account', 
        'vit_custom_djislu'],
    'data': [
        'lph.xml',
        'invoice.xml',
    ],
    'active': False,
    'installable': True,
    'application': True,
}
