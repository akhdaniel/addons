# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Multiple Post & Cancel Journal Entries',
    'description': """

*Tambah Fitur Wizard untuk multiple post dan cancel journal entries

""",
    'version': '0.1',
    'depends' : ['account_accountant'],
    'author': 'vitraining.com',
    'category': 'Accounting & Finance',
    'website': 'http://www.vitraining.com',
    'data': [ 
        #'wizard/account_move_wizard_view.xml',
        'journal_entries_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: