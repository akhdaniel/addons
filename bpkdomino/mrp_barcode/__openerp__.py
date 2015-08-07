# -*- coding: utf-8 -*-
{
    'name': "MRP Add Barcode",

    'summary': """
        Barcode for manufacturing
        """,

    'description': """
        Barcode for MRP
    """,

    'author': "aiksuwandra@gmail.com",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacture',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp','siu_mrp','siu_mps','web_print_barcode'],

    # always loaded
    'data': [
        'setting.xml','serial_number.xml','mrp_view.xml','wizard/product_produce.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}