# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Stock Move Analysis',
    'description': """
Report Harian Barang masuk dan barang keluar Gudang Barang Jadi per hari

""",
    'version': '0.3',
    'depends': ['stock','product','vit_n_cutting_order'],
    'author': 'vitraining.com',
    'category': 'Warehouse', # i.e a technical module, not shown in Application install menu
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'view_vit_move_analysis.xml',
        'groups/groups.xml',
        'security/ir.model.access.csv',
        'wizard/vit_move_analysis_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: