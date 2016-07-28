# -*- coding: utf-8 -*-
{
    'name': "Print direct Dot Matrix",

    'summary': """
    Print PO, Invoice, SO directly to a dotmatrix printer
    """,

    'description': """
        Direct Dot Matrix Print using printer proxy.
    """,

    'author': "akhmad.daniel@gmail.com",
    'website': "http://www.vitraining.com",

    'category': 'purchase',
    'version': '0.1',

    'depends': ['purchase','sale','account', 'web'],

    'data': [
        'purchase.xml',
        'view/web_print_button_assets.xml',
    ],

    'qweb': [
        'static/src/xml/web_print_button.xml',
    ],
}