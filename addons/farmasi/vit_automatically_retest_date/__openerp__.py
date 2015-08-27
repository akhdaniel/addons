# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Cron Job Retest Date',
    'description': """
*Ed dan Retest pada penentuan tanggal kadaluarsa barang pada saat receiving

*Cron Job:
utk setiap Bahan Baku , cek tgl hari ini = retest_date pada stock.production.lot?
ya: create internal move utk produk-produk tsb dari Stock Bahan Baku > ke Location Karantina Bahan Baku.

*tambah flag di location (Stock gudang bahan baku atau stok gudang karantina bahan baku)

""",
    'version': '0.1',
    'depends': ['base','stock','vit_batch_number_in_mo'],
    'author': 'vitraining.com',
    'category': 'Warehouse',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        'view_stock.xml',
        'data/ir_cron_retest_date.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: