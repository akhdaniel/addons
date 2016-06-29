# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Product Parent',
    'description': """
""",
    'version': '0.1',
    'depends': ['base','product'],
    'author': 'vitraining.com',
    'category': 'product',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'parent_view.xml',
        "update.sql"
    ],

    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
