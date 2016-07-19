# -*- coding: utf-8 -*-
{
    'name': "HR Transfer Bank",

    'summary': """
        Create list for bank transfer , list of employees, payroll, and bank account""",

    'description': """
        Export employee payroll as Excel for Bank Transfer
    """,

    'author': "aiksuwandra@gmail.com, b4mzbang@gmail.com",
    'website': "http://www.odoo-bandung.com",

    'category': 'Human Resources',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/xport_views.xml',
    ],
    'qweb': [
        'static/src/xml/xport_xcel.xml'
        ],
}
