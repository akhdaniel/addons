from openerp.osv import fields, osv
#from openerp.addons.base_status.base_stage import base_stage

PERMOHONAN_STATES =[
	('draft','Draft'),
	('verify','Verify'),
	('in_progress','In Progress')]
class permohonan_recrut(osv.osv):
    _name = 'hr.job'
    _inherit = 'hr.job'
    
    def action_draft(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':PERMOHONAN_STATES[0][0]},context=context)

    def action_verify(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':PERMOHONAN_STATES[1][0]},context=context)
 
    def action_in_progress(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':PERMOHONAN_STATES[2][0]},context=context)
    
    _columns= {
        'jenis_permohonan':fields.selection([('Bulanan','Bulanan'),('Harian','Harian')],'Jenis Permohonan'),
        'no':fields.char('Nomor',20),
        'status_jabatan':fields.selection([('P','Pengganti'),('T','Tambahan'),('JB','Jabatan Baru')],'Status Jabatan'),
        'pendidikan_id':fields.many2one('hr_recrut.pendidikan','Pendidikan'),
        'jurusan_ids':fields.one2many('hr_recrut.jurusan','permohonan_recrut_id','jurusan'),
        'pengalaman':fields.integer('Pengalaman (min-th)'),
        'usia':fields.integer('Usia (max)'),
        'sts_prk':fields.selection([('Belum_Menikah','Belum Menikah'),('Menikah','Menikah')],'Status Pernikahan'),
        'kelamin':fields.selection([('Laki-laki','Laki-Laki'),('Perempuan','Perempuan')],'Jenis Kelamin'),
        'wkt_pemohon':fields.date('Permintaan Pemohon'),
        'wkt_rekruter':fields.date('Kesanggupan Rekruter'),
        'catatan':fields.char('Realisasi Penempatan',128),
        'catatan2':fields.text('Catatan'),
        'state': fields.selection(PERMOHONAN_STATES, 'Status', readonly=True, help="Gives the status of the Recrutment."),  
        'user_id' : fields.many2one('res.users', 'Creator','Masukan User ID Anda'),      
                }
    _defaults = {
        'state': PERMOHONAN_STATES[0][0],
        'user_id': lambda obj, cr, uid, context: uid,
                 }  
            
permohonan_recrut()

class pendidikan(osv.osv):
    _name='hr_recrut.pendidikan'
    
    _columns= {
        'name':fields.char('Pendidikan',25,required=True),
        #'jurusan':fields.one2many('hr_recrut.jurusan','pendidikan_id','Jurusan'),
            }
pendidikan()

class jurusan(osv.osv):
    _name='hr_recrut.jurusan'
    
    _columns= {
        'name':fields.many2one('hr_recrut.jurusan_detail','Jurusan',required=True),
        #'pendidikan_id':fields.many2one('hr_recrut.pendidikan'),
        'permohonan_recrut_id':fields.many2one('hr.job'),
            }
jurusan()

class jurusan_detail(osv.osv):
    _name='hr_recrut.jurusan_detail'
    
    _columns= {
        'name':fields.char('Jurusan',30,required=True),
            }
jurusan_detail()

class hr_applicant(osv.osv):
    _name='hr.applicant'
    _inherit='hr.applicant'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    
    _columns= {
        'tmp_lahir':fields.char('Tempat Lahir',50),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'agama':fields.selection([('Islam','Islam'),('Kristen','Kristen'),('Budha','Budha'),('Hindu','Hindu'),('Kepercayaan','Kepercayaan')],'Agama'),
        'country_id': fields.many2one('res.country', 'Kewarganegaraan'),
        'ktp':fields.char('No KTP',20),
        'dikeluarkan':fields.char('Dikeluarkan di',50),
        'tgl_keluar_ktp':fields.date('Tanggal Dikeluarkan',),
        'tgl_berlaku':fields.date('Tanggal Berlaku'),
        'sim':fields.selection([('A','A'),('B1','B1'),('B2','B2'),('C','C')],'SIM'),
        'tgl_keluar_sim':fields.date('Tanggal Dikeluarkan'),
        'alamat1':fields.text('Alamat 1'),
        'alamat2':fields.text('Alamat 2'),
        'telp1':fields.char('Telepon',50),
        'telp2':fields.char('Telepon',50),
        'status':fields.selection([('Lajang','Lajang'),('Menikah','Menikah'),('Bercerai','Bercerai')],'Status Pernikahan'),
        'sjk_tanggal':fields.date('Sejak Tanggal'),        
        'susunan_kel1_ids':fields.one2many('hr_recrut.suskel1','applicant_id'),
        'susunan_kel2_ids':fields.one2many('hr_recrut.suskel2','applicant_id'),
        'rwt_pend_ids':fields.one2many('hr_recrut.rwt_pend','applicant_id'),
        'bahasa_ids':fields.one2many('hr_recrut.bahasa','applicant_id'),
        'rwt_krj_ids':fields.one2many('hr_recrut.rwt_krj','applicant_id'),
        'koneksi1_ids':fields.one2many('hr_recrut.kon1','applicant_id'),
        'koneksi2_ids':fields.one2many('hr_recrut.kon2','applicant_id'),

        }
hr_applicant()

class susunan_keluarga1(osv.osv):
    _name='hr_recrut.suskel1'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),
        'name':fields.char('Nama',required=True),
        'jenis_kel':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'tmp_lahir':fields.char('Tempat Lahir',50),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'pendidikan':fields.char('Pendidikan',50),
        'pekerjaan':fields.char('Pekerjaan',60),
            }
susunan_keluarga1()

class susunan_keluarga2(osv.osv):
    _name='hr_recrut.suskel2'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),
        'susunan':fields.selection([('Ayah','Ayah'),('Ibu','Ibu'),('anak1','Anak ke-1'),('anak2','Anak ke-2'),('anak3','Anak ke-3'),('anak4','Anak ke-4'),('anak5','Anak ke-5'),('anak6','Anak ke-6')],'Nama Susunan Keluarga'),
        'name':fields.char('Nama',required=True),
        'jenis_kel':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'tmp_lahir':fields.char('Tempat Lahir',50),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'pendidikan':fields.char('Pendidikan',50),
        'pekerjaan':fields.char('Pekerjaan',60),
            }
susunan_keluarga2()   

class rwt_pendidikan(osv.osv):
    _name='hr_recrut.rwt_pend'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),
        'name':fields.char('Nama Sekolah',128,required=True),
        'jurusan':fields.char('Jurusan',50),
        'tempat':fields.char('Tempat',30),
        'tahun':fields.char('Dari-Sampai tahun',11),
        'ijazah':fields.char('Ijazah yang Diperoleh',100),
            }
rwt_pendidikan()      

class bahasa(osv.osv):
    _name='hr_recrut.bahasa'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),        
        'name':fields.char('Nama',30,required=True),
        'tulis':fields.selection([('Sedang','Sedang'),('Cukup_Baik','Cukup Baik'),('Baik','Baik'),('Sangat_Baik','Sangat Baik')],'Tertulis'),
        'lisan':fields.selection([('Sedang','Sedang'),('Cukup_Baik','Cukup Baik'),('Baik','Baik'),('Sangat_Baik','Sangat Baik')],'Lisan'),
            }
bahasa()    

class rwt_pekerjaan(osv.osv):
    _name='hr_recrut.rwt_krj'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'), 
        'no':fields.integer('No'),
        'name':fields.char('Nama Perusahaan & Tempat',128),
        'tahun':fields.char('Dari-Sampai Tahun',11),
        'jabatan':fields.char('Jabatan',30),
        'gaji':fields.float('Gaji'),
        'alasan':fields.char('Alasan Pindah',30),
            }
rwt_pekerjaan()

class koneksi1(osv.osv):
    _name='hr_recrut.kon1'
    
    _columns={        
        'applicant_id':fields.many2one('hr.applicant',),
        'employee_id':fields.many2one('hr.employee','Nama'),
        'alamat':fields.text('Alamat/Telepon'),
        'jabatan':fields.char('Jabatan',30),
            }
koneksi1()

class koneksi2(osv.osv):
    _name='hr_recrut.kon2'
    
    _columns={        
        'applicant_id':fields.many2one('hr.applicant'),
        'name':fields.char('Nama',60),
        'alamat':fields.text('Alamat/Telepon'),
        'jabatan':fields.char('Jabatan',30),
            }
koneksi2()




