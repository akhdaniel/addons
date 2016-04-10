# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Install depends module',
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
  #       # 'base',
  #       'mrp',
  #       'mrp_operations',
  #       'stock',
  #       'vit_sediaan',
  #       'vit_ppn',
  #       'vit_approval_routings',
  #       # 'vit_batch_number_in_mo',
  #       'vit_man_hour_and_yield',
  #       'vit_rework_in_work_orders',
  #       # 'vit_pharmacy_manufacture',
  #       'vit_pharmacy_machine_hour',
  #       'vit_bom_component_type',
		# # 'vit_automatically_retest_date',
  #       'vit_lucas_groups',
  #       'vit_ph_checklist_bahan_lucas',
  #       'vit_expired_date',
  #       'vit_force_production',
  #       # 'vit_mrp_stock_move_editable',
  #       'vit_ph_rack_move_warning',
  #       'vit_ph_release_qc_qa',
  #       'vit_multiple_start_finish_wo',
  #       'vit_ph_reschedule_approval_picking',
  #       'vit_ph_add_fields',
  #       'vit_ph_starting_material',
  #       'vit_pharmacy_wo_hour',
  #       'vit_product_request',
  #       'vit_purchase_revision',
  #       'vit_purchase_triple_validation',
  #       'vit_recalculate_so_qty_line_modify',
  #       'vit_security_product_qty_in_mo',
  #       # 'vit_split_work_orders',
  #       'product_get_cost_field',
  #       'product_cost_incl_bom',
    ],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        
    ],
    'installable': True,
    'auto_install': False,
    'active': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
