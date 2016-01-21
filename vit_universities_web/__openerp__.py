#-*- coding: utf-8 -*-
{
    'name': "Akademik Website",

    'summary': """
        Homepage untuk aplikasi akademik""",

    'description': """
Homepage untuk aplikasi akademik:
* pendaftaran
* alumni portal
* dosen portal
* mahasiswa portal

    """,

    'author': "vitraining.com",
    'website': "http://www.vitraining.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'website',
        'website_blog',
        'website_instantclick',
        'vit_universities_v8'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/web_asset.xml',
        # 'views/pages.xml', # homepage
        # 'views/search.xml',
        'views/registration.xml',
        # 'views/discharge.xml',
        'views/menu.xml',
    ],
    'css':['static/src/css/*.css'],
    'js':['static/src/js/*.js','static/src/js/jquery-ui/jquery.ui.autocomplete.html.js'],
    'installable':True,
}