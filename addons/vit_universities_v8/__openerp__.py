#
# SI Akademik manifest file
#
{
    'name': 'Sistem Informasi Akademik Perguruan Tinggi',
    'depends': ['base','hr','account','account_voucher'],
    'author'  :'vitraining.com',
    'version': '0.2',
    "website" : "http://www.vitraining.com",
    'category': 'Tools',
    'description': """
Sistem Informasi Akademik Perguruan Tinggi yang sudah di sesuaikan dengan standar perguruan tinggi yang ada di Indonesia (Odoo v8)
""",
    'installable':True,
    'data': ['akademik.xml',
    		'partner.xml',
            'wisuda.xml',
    		'spmb.xml',	
    		'operasional.xml',
    		'kelas.xml',
    		'employee.xml',
            'jadwal.xml',
            'kurikulum.xml',
            'cuti_kuliah.xml',
            'invoice.xml',
            'pembayaran.xml',
            'product.xml',
            'partner_calon_mhs.xml',
            'konversi.xml',
            'jadwal_usm.xml',
            'jenis_pendaftaran.xml',
            'reports/report.xml',
            'data/data_view.xml',
            'company.xml',
            'imports.xml',
            'beasiswa_prodi.xml',
            'security/groups.xml',
            'security/ir.model.access.csv'
    ],
}
