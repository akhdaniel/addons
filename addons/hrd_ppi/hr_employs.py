from openerp.osv import fields, osv

class employee(osv.osv):
    _name = "hr.employee"
    _inherit = 'hr.employee'
    
    _columns = {
        'kelamin':fields.selection([('Male','Male'),('Female','Female')],'Jenis Kelamin'),
        'tmp_lahir':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'agama':fields.many2one('hr_recruit.agama','Agama'),
        'birthday':fields.date('Tanggal Lahirku'),
        'country_id': fields.many2one('res.country', 'Kewarganegaraan'),
        'ktp':fields.char('No KTP',20),
        'no_pass':fields.char('No Passport',30),
        'no_rek':fields.char('No. Rekening',20),
        'no_sim':fields.char('No. SIM',30),
        'dikeluarkan':fields.char('Dikeluarkan di',50),
        'tgl_keluar_ktp':fields.date('Tanggal Dikeluarkan',),
        'tgl_berlaku':fields.date('Tanggal Berlaku'),
        'sim':fields.selection([('A','A'),('B1','B1'),('B2','B2'),('C','C')],'SIM'),
        'tgl_keluar_sim':fields.date('Tanggal Dikeluarkan'),
        'alamat1':fields.text('Alamat 1'),
        'alamat2':fields.text('Alamat 2'),
        'telp1':fields.char('Telepon',50),
        'telp2':fields.char('Telepon',50),
        'status':fields.selection([('Single','Menikah'),('Menikah','Menikah'),('Cerai','Cerai')],'Status Pernikahan'),
        'sjk_tanggal':fields.date('Sejak Tanggal'),        
        'employee_id' :fields.many2one('hr.employee'),
        'susunan_kel1_ids':fields.one2many('hr_employee.suskel1','employee_id','Susunan Keluarga'),
        'susunan_kel2_ids':fields.one2many('hr_employee.suskel2','employee_id','Susunan Keluarga'),
        'rwt_pend_ids':fields.one2many('hr_employee.rwt_pend','employee_id','Riwayat Pendidikan'),
        'bahasa_ids':fields.one2many('hr_employee.bahasa','employee_id','Bahasa'),
        'rwt_krj_ids':fields.one2many('hr_employee.rwt_krj','employee_id','Rwayat Pekerjaan'),
        'koneksi1_ids':fields.one2many('hr_employee.kon1','employee_id','Koneksi Internal'),
        'koneksi2_ids':fields.one2many('hr_employee.kon2','employee_id','Koneksi Eksternal'),
        
        'blood':fields.selection([('A','A'),('B','B'),('AB','AB'),('O','O')],'Gol Darah'),
        'bahasa_id':fields.many2one('hr_recruit.bahasa','Bahasa'),
        'kota_id':fields.many2one('hr_recruit.kota','Kota'),
        'country_id2': fields.many2one('res.country', 'Negara'),
        'kodepos':fields.char('Kode Pos',8),
        'jenis_id':fields.selection([('Rek.Bank','Rekening Bank'),('KTP','Kartu Tanda Penduduk'),('Passport','Passport'),('SIM','SURAT IZIN MENGEMUDI'),('SIM_A','Surat Izin Mengemudi A'),('SIM_C','Surat Izin Mengemudi C')],'Jenis ID'),
        }
        
    _defaults = {
        'sjk_tanggal': ('invisible','=',True),
    }    
    
employee()

class susunan_keluarga1(osv.osv):
    _name='hr_employee.suskel1'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama',required=True),
        'jenis_kel':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'tmp_lahir':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'pendidikan':fields.char('Pendidikan',50),
        'pekerjaan':fields.char('Pekerjaan',60),
            }
susunan_keluarga1()

class susunan_keluarga2(osv.osv):
    _name='hr_employee.suskel2'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'susunan':fields.selection([('Ayah','Ayah'),('Ibu','Ibu'),('anak1','Anak ke-1'),('anak2','Anak ke-2'),('anak3','Anak ke-3'),('anak4','Anak ke-4'),('anak5','Anak ke-5'),('anak6','Anak ke-6')],'Nama Susunan Keluarga'),
        'name':fields.char('Nama',required=True),
        'jenis_kel':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'tmp_lahir':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'pendidikan':fields.char('Pendidikan',50),
        'pekerjaan':fields.char('Pekerjaan',60),
            }
susunan_keluarga2()   

class rwt_pendidikan(osv.osv):
    _name='hr_employee.rwt_pend'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama Sekolah',128,required=True),
        'jurusan':fields.char('Jurusan',50),
        'tempat':fields.char('Tempat',30),
        'tahun':fields.char('Dari-Sampai tahun',11),
        'ijazah':fields.char('Ijazah yang Diperoleh',100),
            }
rwt_pendidikan()      

class bahasa(osv.osv):
    _name='hr_employee.bahasa'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),        
        'name':fields.char('Nama',30,required=True),
        'tulis':fields.selection([('Sedang','Sedang'),('Cukup_Baik','Cukup Baik'),('Baik','Baik'),('Sangat_Baik','Sangat Baik')],'Tertulis'),
        'lisan':fields.selection([('Sedang','Sedang'),('Cukup_Baik','Cukup Baik'),('Baik','Baik'),('Sangat_Baik','Sangat Baik')],'Lisan'),
            }
bahasa()    

class rwt_pekerjaan(osv.osv):
    _name='hr_employee.rwt_krj'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'), 
        'no':fields.integer('No'),
        'name':fields.char('Nama Perusahaan & Tempat',128),
        'tahun':fields.char('Dari-Sampai Tahun',11),
        'jabatan':fields.char('Jabatan',30),
        'gaji':fields.float('Gaji'),
        'alasan':fields.char('Alasan Pindah',30),
            }
rwt_pekerjaan()

class koneksi1(osv.osv):
    _name='hr_employee.kon1'
    
    _columns={        
        'employee_id':fields.many2one('hr.employee',),
        'employee_id':fields.many2one('hr.employee','Nama'),
        'alamat':fields.text('Alamat/Telepon'),
        'jabatan':fields.char('Jabatan',30),
            }
koneksi1()

class koneksi2(osv.osv):
    _name='hr_employee.kon2'
    
    _columns={        
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama',60),
        'alamat':fields.text('Alamat/Telepon'),
        'jabatan':fields.char('Jabatan',30),
            }
koneksi2()




