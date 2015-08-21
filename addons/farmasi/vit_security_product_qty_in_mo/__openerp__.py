# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Security Product Qty in Manufacturing Orders',
    'description': """
*On change Product qty pada MO di buat readonly dan berubah sesuai peroduct qty di BoM
*Tambah group baru untuk user yang bisa edit product qty di form MO

""",
    'version': '0.1',
    'depends': ['base','mrp','mrp_operations'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'security/group.xml',
        'view_mrp.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
