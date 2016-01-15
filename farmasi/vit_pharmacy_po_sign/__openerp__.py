# -*- coding: utf-8 -*-
{
    'name': "Print PO Sign",
    'summary': """
                PO Print Sign""",
    'description': """
        PO Print Sign
    """,
    'author': "wawan",
    'website': "http://www.vitraining.com",
    'category': 'purchase',
    'version': '0.1',
    'depends': ['base','purchase'],
    'data': [
        'purchase_report2.xml',
        'views/report_purchaseorder.xml',
        'views/report_purchasequotation.xml',

    ],
    'demo': [
    ],
}