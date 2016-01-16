{
    'version': '0.1',
    'name': 'Fix tanggal jurnal stock opname',
    'depends': ['base','account','stock','product'],
    'author'  :'vitraining.com',
    'category': 'Tools',
    'description': """
Waktu stock opname, tanggal jurnal stock yang dihasilkan = tanggal system ketika proses validate opname.
Diinginkan agar tanggal jurnal adalah tanggal create date opname ybs.

Modul ini memodifikasi function _create_account_move_line() di stock.move 
agar tanggal jurnal = tanggal stock inventory 

""",
    'installable':True,
    'data': [
    ],
}
