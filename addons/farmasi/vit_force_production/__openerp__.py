# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Filter Force Production in Manufacturing Orders',
    'description': """

*Ketika Force Production Pada MO, eksekusi barang yang berkategori (pada objek kategory barang) kemas sekunder

""",
    'version': '0.1',
    'depends': ['base','mrp','mrp_operations'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'view_product_categ.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
