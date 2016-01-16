# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Show Customer, Supplier, Makloon, and Product Ranking',
    'description': """
*Reporting untuk mengetahui Ranking Customer, Supplier, Makloon, dan Product terbaik/terlaris
""",
    'version': '0.2',
    'depends': ['base','stock','account'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'view_ranking.xml',
        'groups/groups.xml',
        'security/ir.model.access.csv',
        'wizard/view_report_wizard.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: