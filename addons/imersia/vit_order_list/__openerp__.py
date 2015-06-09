# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Order List',
    'description': """

""",
    'version': '0.1',
    'depends': ['base','sale','mrp','vit_product'],
    'author': 'vitraining.com',
    'category': 'Sale',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'security/ir.model.access.csv',
        'view_order_list.xml',
        'order_list_report.xml',
        'reports/sale_order_list_report.xml',
        'edi/sale_order_list_action_data.xml',
        'inherit_sale_order_line.xml'
        
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: