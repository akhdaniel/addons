# -*- coding: utf-8 -*-
{
    'name': "Website MLM",

    'summary': """
        Homepage untuk aplikasi MLM""",

    'description': """
        Add link in homepage for MLM purpose
        also blog and shop.
    """,

    'author': "vitraining.com",
    'website': "http://www.vitraining.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website','vit_mlm','website_blog','website_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pages.xml',

    ],
    'css':['static/src/css/*.css'],
    'js':['static/src/js/*.js'],
    'installable':True,
}