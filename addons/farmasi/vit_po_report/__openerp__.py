# -*- coding: utf-8 -*-
{
    'name': "Print for PO",

    'summary': """
        Print PO""",

    'description': """
        Print PO in A5 Paper size
    """,

    'author': "aiksuwandra@gmail.com",
    'website': "http://www.vitraining.com",

    'category': 'purchase',
    'version': '0.1',

    'depends': ['purchase','web','base'],

    'data': [
        'purchase.xml',
        'reports/templates.xml',
        'view/web_print_button_assets.xml',
    ],

    'qweb': [
        'static/src/xml/web_print_button.xml',
    ],
}