# -*- coding: utf-8 -*-
{
    'name': "Product Customisation",

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
    'depends': ['product','stock','mrp','sale','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/mrp_product_produce_view.xml',
        'mrp_view.xml',
        # 'stock_view.xml',
        'product_views.xml',
        # 'product_data.xml',
        'sales_views.xml',
        'sales_lines_views.xml',
        'reports/proforma.xml',
        'purchase_line.xml'
    ],

    # only loaded in demonstration mode
    'demo': [],

    # Static files
    # 'css':[
    #     'static/src/css/xxcss.css',
    # ],
}