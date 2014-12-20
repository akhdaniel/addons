# -*- coding: utf-8 -*-
######################################################################
#
#  Note: Program metadata is available in /__init__.py
#
######################################################################

{
    'name' : 'Partner Aging on Screen',
    'version' : '1.0',
    'author' : 'vitraining.com',
    'summary': 'Aging as a view on Screen',
    'description': """
*This module creates new AR and AP views.
""",
    'maintainer': 'vitraining.com',
    'website': 'http://www.vitraining.com',
    'category': 'Accounting & Finance',
    'images' : [],
    'depends' : ['base','account_accountant'],
    'data' : [
              'partner_aging_supplier.xml',
              'partner_aging_customer.xml',
            ],
    'test' : [],
    'auto_install': False,

    'active': False,
    'installable': True,
    'application': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: