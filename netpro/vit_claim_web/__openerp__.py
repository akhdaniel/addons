# -*- coding: utf-8 -*-
{
    'name': "Claim Website",

    'summary': """
        Homepage untuk aplikasi insurance""",

    'description': """
Homepage untuk aplikasi insurance
    """,

    'author': "vitraining.com",
    'website': "http://www.vitraining.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website','website_blog','website_instantclick',
         'vit_actuary', 'vit_policy', 'vit_member', 'vit_claim', 'vit_syntech'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/claim_web_asset.xml',
        'views/pages.xml',
        'views/search.xml',
        'views/registration.xml',
        'views/discharge.xml',
        'views/claim_list.xml',

    ],
    'css':['static/src/css/*.css'],
    'js':['static/src/js/*.js','static/src/js/jquery-ui/jquery.ui.autocomplete.html.js'],
    'installable':True,
}