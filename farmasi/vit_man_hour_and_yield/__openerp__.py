# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Man Hour & Yield in Work Center',
    'description': """
*Tambah perhitungan man hour di Work center dan Work order
*Tambah informasi yield di work center
""",
    'version': '0.1',
    'depends': ['base','mrp','mrp','mrp_operations','vit_pharmacy_machine_hour'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        
        'vit_view_mrp.xml',
        
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: