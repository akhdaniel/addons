{
    'version': '0.5',
    'name': 'shop import data, slave side',
    'depends': ['base','account','sale','purchase', 'stock'],
    'author'  :'vitraining.com',
    'category': 'Tools',
    'description': """

Di shop install vit_sync_slave
di pusat install vit_sync_master

ada function cron_process_export() yang dipanggil periodic dari jobs

1. cari account_move dan account_move_line yang exported = false
2. tulis ke file account_move.csv
3. cari stock_move dan stock_move_line yang exported = false
4. tulis ke file stock_move.csv
5. zip file csv
6. upload ke server via FTP/HTTP

7. cek apakah ada update produk dari master

""",
    'installable':True,
    'data': [
        'account_move.xml',
        'stock_picking_out.xml',
        'scheduler.xml',
        'menu.xml'
    ],
}
