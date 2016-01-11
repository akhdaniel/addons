# -*- coding: utf-8 -*-
{
    'name': "vit_mrp_access",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "aiksuwandra@gmail.com",
    'website': "http://www.vitraining.com",

    'category': 'manufacturing',
    'version': '0.1',

    'depends': ['product','vit_lucas_groups'],

    'data': [
        # 'security/ir.model.access.csv',
        'security/warehouse_rules.xml',
    ],
}