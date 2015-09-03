# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Split Work Orders and Batch Number ',
    'description': """

*Tambah Tombol Split di form Work Order
Setiap WO bisa split
ketika di spiit di tengan jalan, maka hasil akhir menjadi 2 serial number,
misal awalnya 15XA002, ketika split serial number produk jadi terbagi 2:
15XA002A
15XA002B

""",
    'version': '0.1',
    'depends': ['base','mrp','mrp_operations','vit_batch_number_in_mo'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'mrp_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
