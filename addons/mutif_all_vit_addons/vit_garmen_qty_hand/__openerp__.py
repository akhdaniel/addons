# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Vit Garment Quantity On Hand Add On sales order + Discount',
    'description': """
         Custom Sales Order Line Add Quantity On Hand, Forecasted, Discount 
""",
    'version': '0.1',
    'depends': ['base','sale','vit_partner_addmutif'],
    'author': 'vitraining.com',
    'category': 'Tools', # i.e a technical module, not shown in Application install menu
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'sale.xml',
        # 'data/data.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: