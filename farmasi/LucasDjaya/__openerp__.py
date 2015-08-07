# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Import master data Lucas Marin',
    'description': """

Install module Accounting dengan template US - 

data ini akan otomatis diimport:
* account.account         : untuk menambah account COGS
* product.uom.csv         : Product Unit Of Meassure and Ratio Unit Of Meassure, 
* product.category.csv    : Category Bahan, 
* res.partner.csv         : Supplier and Manufacture Supplier, 

Lalu import manual file ini:
* product.product.csv     : Produk Bahan Baku, Barang jadi, 
* mrp.bom                 : BOM

""",
    'version': '0.1',
    'depends': [
        'base',
        'mrp',
        'mrp_operations',
        'stock',
        'vit_ppn',
        'vit_approval_routings',
        'vit_batch_number_in_mo',
        'vit_man_hour_and_yield',
        'vit_rework_in_work_orders',
        'vit_pharmacy_manufacture',
        'vit_pharmacy_machine_hour',
    ],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'account.account.csv',
        'mrp.workcenter.csv',
        'mrp.routing.csv',
        'mrp.routing.workcenter.csv',
        'product.uom.csv',
        'product.category.csv',
        'res.partner.category.csv',
        'res.partner.csv',
        'product.product.csv',
        # 'mrp.bom.csv',
        # 'bom.machine.hour.csv',
        # 'bom.man.hour.csv',
    ],
    'installable': True,
    'auto_install': False,
    'active': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: