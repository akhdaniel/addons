# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Approval Routings',
    'description': """
* Approval alur work order pada routing sesuai dengan kebutuhan
* Work order dapat di start jika work order atau gabungan dari work order tertentu sebelumnya sudah finish
""",
    'version': '0.1',
    'depends': ['base','mrp','mrp','mrp_operations'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        
        'view_routings.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: