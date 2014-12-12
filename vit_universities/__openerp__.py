#
# SI Akademik manifest file
#
{
    'name': 'Sistem Informasi Akademik Perguruan Tinggi',
    'depends': ['base','hr','account'],
    'author'  :'vitraining.com',
    "website" : "http://www.vitraining.com",
    'category': 'Tools',
    'description': """
Sistem Informasi Akademik Perguruan Tinggi yang sudah di sesuaikan dengan standar perguruan tinggi yang ada di Indonesia
""",
    'installable':True,
    'data': ['akademik.xml',
    		'partner.xml',
    		'spmb.xml',
    		'wisuda.xml',
    		'operasional.xml',
    		'kelas.xml',
    		'employee.xml',
            'jadwal.xml',
            'kurikulum.xml',
            'invoice.xml',],
}
