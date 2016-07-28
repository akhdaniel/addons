# -*- coding: utf-8 -*-
{
    'name': "Release Module QA/QC",
    'summary': """
        Release Module QA/QC""",
    'description': """
Release Module QA/QC
========================================================
* menu QA QC 
* tambah menu QC PR/PA (produk ruah dan produk antara) dibahwa menu Release: 
isinya adalah data Work Order khusus untuk proses QC: workcenter_id = QC
* menu product 

    """,
    'author': "rahasia2alha@gmail.com",
    'website': "http://www.one2pret.com",
    'category': 'warehouse',
    'version': '0.1',
    'depends': ['base','stock', 'mrp' , 'mrp_operations'],
    'data': [
        # 'security/ir.model.access.csv',
        'release.xml',
        # "data/stock.warehouse.csv"
    ],
    'demo': [
    ],
}