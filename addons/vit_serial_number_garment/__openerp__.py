# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Serial Number Garment',
    'description': """
*Metoda pemberian serial number untuk pabrik garment
""",
    'version': '0.1',
    'depends': ['base','stock','vit_n_cutting_order'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        
        'vit_view_production_lot_form.xml',
        'vit_view_hand_tag_form.xml',
        'vit_view_stock_move_sn.xml',
        'vit_cutting_order.xml',
        'wizard/vit_stock_move_sn_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: