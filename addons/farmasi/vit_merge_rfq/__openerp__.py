# -*- coding: utf-8 -*-
{
    'name': "Merge RfQ",

    'summary': """
        Merge RfQ""",

    'description': """
        Merge multiple RfQ for same Supplier
    """,

    'author': "aiksuwandra@gmail.com",
    'website': "http://www.vitraining.com",

    'category': 'purchase',
    'version': '0.1',

    'depends': ['purchase'],

    'data': [
        'purchase.xml',
        'rfq_sequence.xml',
    ],
}