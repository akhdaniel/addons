# -*- coding: utf-8 -*-
{
    'name': "MRP Makloon",
    'description': """
Add is makloon field in MO.
The field is used to determine whether MO is a makloon process or internal.
Overide generate Batch Number for makloon.
    """,
    'author': "akhmad.daniel@gmail.com",
    'website': "http://www.vitraining.com",
    'category': 'Manufacturing',
    'version': '0.1',
    'depends': [
        'base',
        'product',
        'mrp',
        'vit_batch_number_in_mo'
    ],
    'data': [
        "mrp.xml",
        "product.xml",
    ],
    'demo': [
    ],
}