from openerp.osv import fields, osv

class employee(osv.osv):
    _name = "hr.employee"
    _inherit = 'hr.employee'
    
    _columns = {
        'nik': fields.char('NIK',20,readonly=True),
        'kelamin':fields.selection([('male','Male'),('female','Female')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'agama':fields.many2one('hr_recruit.agama','Agama'),
        'birthday':fields.date('Tanggal Lahirku'),
        'country_id': fields.many2one('res.country', 'Kewarganegaraan'),
        'ktp':fields.char('No ID',20),
        'no_pass':fields.char('No Passport',30),
        'no_rek':fields.char('No. Rekening',20),
        'no_sim':fields.char('No. SIM',30),
        'no_sima':fields.char('No. SIM A',30),
        'no_simc':fields.char('No. SIM C',30),
        'issued_id2':fields.many2one('res.country','Dikeluarkan di'),
        'issued_id':fields.many2one('hr_recruit.issued','Dikeluarkan di'),
        'tgl_keluar_ktp':fields.date('Tanggal Dikeluarkan',),
        'tgl_berlaku':fields.date('Tanggal Berlaku'),
        'sim':fields.selection([('A','A'),('B1','B1'),('B2','B2'),('C','C')],'SIM'),
        'tgl_keluar_sim':fields.date('Tanggal Dikeluarkan SIM'),
        'tgl_keluar_sima':fields.date('Tanggal Dikeluarkan SIM A'),
        'tgl_keluar_simc':fields.date('Tanggal Dikeluarkan SIM C'),
        'type_id': fields.many2one('hr.recruitment.degree', 'Degree'),
        'jurusan_id':fields.many2one('hr_recruit.jurusan_detail','Jurusan'),
        'result_id':fields.many2one('hr_recruit.result','Result'),
        'gelar_id':fields.many2one('hr_recruit.gelar','Gelar'),
        'alamat1':fields.text('Alamat 1'),
        'alamat2':fields.text('Alamat 2'),
        'telp1':fields.char('Telepon',50),
        'telp2':fields.char('Telepon',50),
        'status':fields.selection([('single','Single'),('menikah','Menikah'),('duda','Duda'),('janda','Janda')],'Status Pernikahan'),
        'jml_anak':fields.integer('Jumlah Anak'),
        'sjk_tanggal':fields.date('Sejak Tanggal'),        
        'employee_id' :fields.many2one('hr.employee'),
        'clas_id':fields.many2one('hr_employs.clas','Class'),
        'title_id':fields.many2one('hr.title','Title'),
        'extitle_id':fields.many2one('hr.extitle','Ex Title'),
        'gol_id':fields.many2one('hr_employs.gol','Golongan'),
        'wfield_id':fields.many2one('hr_employs.wfield','Bidang Pekerjaan'),
        'pansion_id':fields.many2one('hr_employs.pansion','Masa Pensiun'),
        'susunan_kel1_ids':fields.one2many('hr_employee.suskel1','employee_id','Susunan Keluarga'),
        'susunan_kel2_ids':fields.one2many('hr_employee.suskel2','employee_id','Susunan Keluarga'),
        'rwt_pend_ids':fields.one2many('hr_employee.rwt_pend','employee_id','Riwayat Pendidikan'),
        'bahasa_ids':fields.one2many('hr_employee.bahasa','employee_id','Bahasa'),
        'rwt_krj_ids':fields.one2many('hr_employee.rwt_krj','employee_id','Rwayat Pekerjaan'),
        'koneksi1_ids':fields.one2many('hr_employee.kon1','employee_id','Koneksi Internal'),
        'koneksi2_ids':fields.one2many('hr_employee.kon2','employee_id','Koneksi Eksternal'),
        'blood':fields.selection([('A','A'),('B','B'),('AB','AB'),('O','O')],'Gol Darah'),
        'bahasa2_id':fields.many2one('hr_recruit.bahasa2','Bahasa'),
        'kota_id':fields.many2one('hr_recruit.kota','Kota'),
        'country_id2': fields.many2one('res.country', 'Negara'),
        'kodepos':fields.char('Kode Pos',8),
        'jenis_id':fields.selection([('Rek.Bank','Rekening Bank'),('KTP','Kartu Tanda Penduduk'),('Passport','Passport'),('SIM','SURAT IZIN MENGEMUDI'),('SIM_A','Surat Izin Mengemudi A'),('SIM_C','Surat Izin Mengemudi C')],'Jenis ID'),
        'pt_id':fields.many2one('hr_recruit.pt','Perguruan Tinggi'),
        'bidang_id':fields.many2one('hr_recruit.bidang','Bidang'),
        }
        
    _defaults = {
        'nik': lambda self, cr, uid, context={}: self.pool.get('ir.sequence').get(cr, uid, 'hr.employee'),
                }
        

employee()

class susunan_keluarga1(osv.osv):
    _name='hr_employee.suskel1'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama',required=True),
        'kelamin':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'type_id': fields.many2one('hr.recruitment.degree', 'Pendidikan'),
        'pekerjaan':fields.char('Pekerjaan',60),
        'susunan':fields.selection([('Suami','Suami'),('Istri','Istri'),('anak1','Anak ke-1'),('anak2','Anak ke-2'),('anak3','Anak ke-3'),('anak4','Anak ke-4'),('anak5','Anak ke-5'),('anak6','Anak ke-6')],'Status Dalam Keluarga'),
            }
susunan_keluarga1()

class susunan_keluarga2(osv.osv):
    _name='hr_employee.suskel2'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
       'susunan':fields.selection([('Ayah','Ayah'),('Ibu','Ibu'),('anak1','Anak ke-1'),('anak2','Anak ke-2'),('anak3','Anak ke-3'),('anak4','Anak ke-4'),('anak5','Anak ke-5'),('anak6','Anak ke-6')],'Status Dalam Keluarga'),
        'name':fields.char('Nama'),
        'kelamin':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'type_id':fields.char('Pendidikan',50),
        'pekerjaan':fields.char('Pekerjaan',60),
            }
susunan_keluarga2()   

class rwt_pendidikan(osv.osv):
    _name='hr_employee.rwt_pend'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama Sekolah',128,required=True),
        'jurusan':fields.many2one('hr_recruit.jurusan_detail','Jurusan'),
        'tempat':fields.text('Alamat'),
        'tahun_msk':fields.date('Tahun Masuk'),
        'tahun_klr':fields.date('Tahun Keluar'),
        'ijazah':fields.many2one('hr.recruitment.degree','Ijazah yang Diperoleh'),
            }
rwt_pendidikan()      

class bahasa(osv.osv):
    _name='hr_employee.bahasa'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee','Applicant'),        
        'name':fields.many2one('res.country', 'Bahasa',required=True),
        'tulis':fields.many2one('hr_recruit.b_tulisan','Tertulis'),
        'lisan':fields.many2one('hr_recruit.b_lisan','Lisan'),
            }
bahasa()    

class rwt_pekerjaan(osv.osv):
    _name='hr_employee.rwt_krj'
    
    _columns= {
        'no':fields.integer('Nomor'),
        'employee_id':fields.many2one('hr.employee'), 
        'name':fields.char('Nama Perusahaan',60,required=True),
        'tempat':fields.text('Alamat'),
        'tahun_msk':fields.date('Tahun Masuk'),
        'tahun_klr':fields.date('Tahun Keluar'),
        'jabatan':fields.char('Jabatan',30),
        'gaji':fields.float('Gaji'),
        'alasan':fields.char('Alasan Pindah',30),
            }
rwt_pekerjaan()

class koneksi1(osv.osv):
    _name='hr_employee.kon1'
    
    _columns={        
        'employee_idd':fields.char('Nama',),
        'employee_id':fields.many2one('hr.employee','Nama',required=True),
        'job_id':fields.related('employee_id','job_id',type='many2one',relation='hr.job',string='Jabatan',readonly=True),
        'alamat':fields.text('Alamat'),
        'telepon':fields.char('Telepon',25),
            }
koneksi1()

class koneksi2(osv.osv):
    _name='hr_employee.kon2'
    
    _columns={        
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama',60),
        'alamat':fields.text('Alamat/Telepon'),
        'jabatan':fields.char('Jabatan',30),
        'telepon':fields.char('Telepon',25),
            }
koneksi2()

class bahasa2(osv.osv):
    _name='hr_recruit.bahasa2'
    
    _columns= {       
        'name':fields.char('Nama Bahasa',30,required=True),
            }
bahasa2()

class clas(osv.osv):
    _name='hr_employs.clas'
    
    _columns= {       
        'name':fields.char('Class',50,required=True),
            }
clas()

class title(osv.osv):
    _name='hr_employs.title'
    
    _columns= {       
        'name':fields.char('Title',50,required=True),
            }
title()

class extitle(osv.osv):
    _name='hr_employs.extitle'
    
    _columns= {       
        'name':fields.char('Ex Title',50,required=True),
            }
extitle()

class golongan(osv.osv):
    _name='hr_employs.gol'
    
    _columns= {       
        'name':fields.char('Golongan',20,required=True),
        'rec':fields.char('record'),
        'no' : fields.char('Urutan')
            }
golongan()

class wfield(osv.osv):
    _name='hr_employs.wfield'
    
    _columns= {       
        'name':fields.char('Bidang Pekerjaan',50,required=True),
            }
wfield()

class pansion(osv.osv):
    _name='hr_employs.pansion'
    
    _columns= {       
        'name':fields.char('Masa Pensiun',50,required=True),
            }
pansion()


employee()