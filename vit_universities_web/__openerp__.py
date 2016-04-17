#-*- coding: utf-8 -*-
{
    'name': "Akademik Website",

    'summary': """
        Homepage untuk aplikasi akademik""",

    'description': """

Homepage untuk aplikasi akademik:
=================================================================
* pendaftaran mahasiswa baru
* test potensi akademik 
* dosen portal: isi absen dan nilai 
* alumni portal: daftar alumni/ search 
* mahasiswa portal: cek nilai , jadwal kuliah dan ujian, info news 

Persiapan:
=================================================================
* Buat Jadwal USM: Gelombang 1
* Buat "Portal User" sebagai template utk user yang sign up via website
* Kasi Akses right "Portal User" = Portal 
* General Settings : allow user sign up via website 

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
        'vit_universities_v8',
        'survey',
       # 'evaluation'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/web_asset.xml',
        # 'views/pages.xml', # homepage
        # 'views/search.xml',
        'views/registration.xml',
        'views/mahasiswa.xml',
        
    ],
    'css':['static/src/css/*.css'],
    'js':['static/src/js/*.js','static/src/js/jquery-ui/jquery.ui.autocomplete.html.js'],
    'installable':True,
}