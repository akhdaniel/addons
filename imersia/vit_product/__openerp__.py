# -*- coding: utf-8 -*-
{
    'name': "vit_product",

    'summary': """
        Product furniture  adjustment""",

    'description': """
        Additional information for product in purpose of furniture sales and manufacture.
    """,

    'author': "Vitraining",
    'website': "http://www.vitraining.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product','mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'product_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}