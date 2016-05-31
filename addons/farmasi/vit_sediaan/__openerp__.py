{
    'name': 'Product Category SEdiaan',
    'version': '1.0',
    'category': 'Manufacture',
    'description': """
Fitur Modul
==================================

* tambah sediaan_id di master produk category


       """,
    'author': 'vitraining.com',
    'depends': ['stock'],
    'data': [
        'product_category_views.xml',
        'security/ir.model.access.csv',
        'data/vit.sediaan.csv',
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}