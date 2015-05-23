# -*- coding: utf-8 -*-

{
    'name': 'Custom Module',
    'category': 'Hidden',
    'summary': 'Module customisation',
    'version': '1.0',
    'description': """Customisation in Existing Module.....""",
    'author': 'Logicious',
    'website': 'http://logicious.net',
    'depends': ['base','product','stock','mrp','vit_product'],
    'data': [
        'wizard/mrp_product_produce_view.xml',
        # 'product_view.xml',
        'mrp_view.xml',
#        'stock_view.xml',
        'product_data.xml',
        ###########patches by harsh jain #################
        'ir.model.access.csv',
        # 'product_package_view.xml',
        # 'product_collection_view.xml',
        #################################################


    ],
    'installable': True,
}
