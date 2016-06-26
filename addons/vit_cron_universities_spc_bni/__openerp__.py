#
# SI Akademik manifest file
#
{
    'name': 'Cron SPC BNI for Sistem Informasi Akademik Perguruan Tinggi (Support)',
    'depends': ['vit_universities_spc_bni'],
    'author'  :'vitraining.com',
    'version': '0.1',
    "website" : "http://www.vitraining.com",
    'category': 'Tools',
    'description': """
    
Student payment center (SPC) BNI
======================================================
* Cron untuk mengecek data tagihan di SPC BNI
* Pola : cek di sistem invoice yg sudah validate apakah sukses insert ke SPC
* jika gagal, cancel invoice tsb, dan validasi lagi

""",
    'installable':True,
    'data': [
        'cron_spc.xml',
    ],
}