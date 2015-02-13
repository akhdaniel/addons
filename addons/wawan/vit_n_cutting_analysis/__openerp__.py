# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Cutting Analysis',
    'description': """

Note
---

""",
    'version': '0.1',
    'depends': ['base','vit_n_cutting_order'],
    'author': 'vitraining.com',
    'category': 'manufacture', # i.e a technical module, not shown in Application install menu
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'cutting_analysis.xml',
        'wizard/report_wizard.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: