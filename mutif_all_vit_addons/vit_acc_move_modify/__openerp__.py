# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Account Move Modify',
    'description': """

        - Menampilkan Quantity Kg Di Jurnal Entry 

""",
    'version': '0.1',
    'depends': ['base','account'],
    'author': 'rahasia2alpha@gmail.com',
    'category': 'accounting', # i.e a technical module, not shown in Application install menu
    'url': 'rahasia2alpha@gmail.com',
    'data': [ 
        'account_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: