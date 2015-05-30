# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Work Orders',
    'description': """

""",
    'version': '0.1',
    'depends': ['base','sale','mrp','mrp_operations','vit_product'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        
        'vit_view_work_order.xml',
        'vit_view_mrp.xml',
        
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: