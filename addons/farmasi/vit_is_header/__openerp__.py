# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Tambah Field is Header pada Product',
    'description': """

*Tambah field pada objek product 'is_header'(boolean) 

BOM
* product_id domain ===> is_header = TRUE

MO : 
* Product to Consume, masih editable setelah confirm MO.
* product_id domain  ===> is_header = FALSE
""",
    'version': '0.1',
    'depends': ['base','mrp','mrp_operations', 'purchase_requisition'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'view_product_and_mo.xml',
        'pr.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
