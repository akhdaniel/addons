# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Import master data Lucas Marin',
    'description': """

Install module:
-----------------------------------
* Purchasing
* Accounting dengan template US - Product Based
* MRP

Configuration > Warehouse:
-----------------------------------
* Traceability
    Track lots or serial numbers
    Expiry date on serial numbers

* Accounting
    Generate accounting entries per stock movement

* Logistic
    Generate procurement in real time
    Manage multiple locations and warehouses
    Manage advanced routes for your warehouse

* Products
    Manage different units of measure for products

Warehouse Gudang Bahan Awal setting:
-----------------------------------
* Incoming Shipments: Unload in input location then go to stock (2 steps)

Configuration > Manufacturing Order
-----------------------------------
Planning
* Manage routings and work orders
* Allow detailed planning of work order

data berikut ini akan otomatis diimport:
-----------------------------------
* account.account         : untuk menambah account COGS
* product.uom.csv         : Product Unit Of Meassure and Ratio Unit Of Meassure, 
* product.category.csv    : Category Bahan, 
* res.partner.csv         : Supplier and Manufacture Supplier, 
* product.product.csv     : Produk Bahan Baku, Barang jadi, 
* mrp.bom                 : BOM

""",
    'version': '0.1',
    'depends': [
        'base',
        'mrp',
        'mrp_operations',
        'stock',
        'vit_sediaan',
        'vit_ppn',
        'vit_approval_routings',
        # 'vit_batch_number_in_mo',
        # 'vit_man_hour_and_yield',
        'vit_rework_in_work_orders',
        'vit_pharmacy_manufacture',
        'vit_pharmacy_machine_hour',
        'vit_bom_component_type',
		# 'vit_automatically_retest_date',
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
        'vit.sediaan.csv',
        'product.category.csv',
        'res.partner.category.csv',
        'stock.warehouse.csv',
        'stock.location.csv',
        'res.partner.csv',
        'product.product.csv',
        'mrp.bom.csv',
        'vit_pharmacy_machine_hour.machine_master.csv',
        'vit_pharmacy_machine_hour.bom_machine_hour.csv',
        'vit_pharmacy_machine_hour.bom_man_hour.csv',
        'vit_pharmacy_manufacture.forecast_product.csv',
        'batch.year.csv',
        'batch.number.csv',
    ],
    'installable': True,
    'auto_install': False,
    'active': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
