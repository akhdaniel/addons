# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Sale Order Analysis',
    'description': """
Fitur
=====
Laporan Analysis untuk membandingkan Real (Initial) Order, Order, Delivered, dan Back Order 
per Produk

Cara Kerja
=====
pada saat recalculate analysis, jalankan Query ini dan simpan hasilnya ke tabel order_analysis

select
    p.id as product_id,
    p.name_template as name_template,
    sum(so_l.real_order_qty) as total_real_order,
    sum(so_l.product_uom_qty) as total_order, 
    (select sum(product_qty) 
        from stock_move 
        where product_id = p.id 
        and state='done' 
        and stock_move.location_dest_id = (select id from stock_location where name = 'Customers' )
        and stock_move.location_id=(select id from stock_location where name = 'Lokasi Barang Jadi' )
        -- and origin <> ''
    ) as delivered,
    (select sum(product_qty) 
        from stock_move 
        where product_id = p.id 
        and state<>'done' and state <> 'draft'
        and stock_move.location_dest_id = 9
        and stock_move.location_id=14
        -- and origin <> ''
    ) as back_order

INTO sale_order_analysis 
from
    product_product p inner join
    sale_order_line so_l on so_l.product_id = p.id inner join
    sale_order so on so_l.order_id = so.id
where
    so.state <> 'draft'

group by
    p.id,
    p.name_template


Note
---
field origin di SQL harusnya ada isinya yaitu nomor SO.
tapi keliatannya ada DO yang dibuat manual tanpa SO sehingga sementara harus diperhitungkan juga
  

Tampilkan data order_analysis ke list view

""",
    'version': '0.2',
    'depends': ['base','sale'],
    'author': 'vitraining.com',
    'category': 'Sale', # i.e a technical module, not shown in Application install menu
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'sale_order_analysis.xml',
        'wizard/report_wizard.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: