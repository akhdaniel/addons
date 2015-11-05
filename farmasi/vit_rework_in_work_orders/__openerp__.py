# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Rework in Work Orders',
    'description': """
* Proses pengulangan produksi pada work orders dengan mengambil bahan baku baru (internal move)
""",
    'version': '0.1',
    'depends': ['base','mrp','mrp_operations','web_m2x_options','stock'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        
        'view_rework_orders.xml',
        'wizard/view_rework_wizard.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: