# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'SAGE-PetroPlus Integration',
    'description': """
This module adds a new feature to sync data between OpenERP and PetroPlus 

The module allows:
------------------
* sync res.partner to PetroPlus client
* sync res.partner to PetroPlus client account
* sync payment transaction 
* sync bonus transaction
* generate payment journals
* generate bonus journals
* create invoice for post payment transactions

The module will create:
-----------------------
* scheduled action to run read_trans() on res.partner model to prosess transactions 
* scheduled action to run read_bonus() on res.partner model to prosess bonuses

Requirements and Installation:
------------------------------
* manually create PetroPlus temporary DB tables to be accessed by their interface software
  SQL script is located at sql folder
* 

""",
    'version': '0.9',
    'depends': ['base'],
    'author': 'vitraining.com',
    'category': 'Tools', # i.e a technical module, not shown in Application install menu
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'partner.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: