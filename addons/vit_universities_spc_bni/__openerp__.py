#
# SI Akademik manifest file
#
{
    'name': 'SPC BNI for Sistem Informasi Akademik Perguruan Tinggi',
    'depends': ['base','hr','account','account_voucher'],
    'author'  :'vitraining.com',
    'version': '0.3',
    "website" : "http://www.vitraining.com",
    'category': 'Tools',
    'description': """
    
Student payment center (SPC) BNI
======================================================
* koneksi ke Mysql databse SPC BNI: setting host, database, user, pwd di System Parameters
* waktu validate invoice, create satu record di biller_tagihan dan biller_tagihan_detil
* waktu cancel invoice, delete record tsb
* cron job ngecek dari tabel ca_pembayaran dan ca_pembayaran_detil
* jika ada record ca_pembayaran, insert payment voucher untuk invoice yang bersangkutan

""",
    'installable':True,
    'data': [
        'parameters.xml',
        'cron.xml',
    ],
}
