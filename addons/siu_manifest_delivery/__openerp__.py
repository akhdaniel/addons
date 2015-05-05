# -*- encoding: utf-8 -*-


{
    "name": "Manifest Delivery Orders",
    "author": "Openerpsoft",
    "Description": """
    This module adds a facility to merge several Delivery Orders
    """,
    "version": "0.1",
    "depends": ["stock", "sale", "base", "siu_stock_order","siu_report","siu_sale_order","wtc_shop"],
    "category" : "Tools",
    "init_xml": [],
    "data": [
        'manifest_view.xml',
    ],
    "demo_xml": [],
    "test": [],
    "installable": True,
    "active": False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
