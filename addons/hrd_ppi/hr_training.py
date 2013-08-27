from openerp.osv import fields, osv
import time
class training(osv.osv):
    _name = 'hr_training.training'
    _rec_name = 'nama'
    
    _columns = {
        'nama' :fields.char('Judul Pelatihan', 128,required = True,ondelete="cascade"),
        'lama' :fields.char('Lama',25,ondelete='cascade'),
        'instansi' : fields.char('Instansi Penyelenggara',128,ondelete='cascade'),
        'tanggal': fields.date('Tanggal',),
        'bukti': fields.binary('Bukti Keikutsertaan',required=True), 
        'employee_ids':fields.one2many('hr.employee','training_id','Nama Karyawan'),     
        'employee_id' : fields.many2one('hr.employee','Nama Karyawan'),   
    }
    _defaults = {
        #'tahun' : lambda*a : time.strftime('%Y'),
        }
   
training()

class train(osv.osv):
    _name = 'hr_training.train'

    _columns = {
        'training_id' :fields.many2one('hr_training.training', 'Nama Training',128),
        'instansi' :fields.related('training_id','instansi',type='char',relation='hr_training.training',string='Instansi Penyelenggara'),
        'employee_id' : fields.many2one('hr.employee','Nama Karyawan'),
        'job_id' :fields.related('employee_id','job_id',type='many2one',relation='hr.job',string='Jabatan'),
        'department_id' : fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='Departemen'),
        'lama' : fields.related('training_id','lama',type='char',relation='hr_training.training',string='Lama'),
        'tanggal': fields.related('training_id','tanggal',type='date',relation='hr_training.training',string='Tanggal'),
        'bukti': fields.related('training_id','bukti',type='binary',relation='hr_training.training',string='Bukti Keikutsertaan'),
        'analisa_id':fields.many2one('hr_training.analisa'),
            }
    
train()

class employee(osv.osv):
    _name='hr.employee'
    _inherit = 'hr.employee'
    _columns ={
        'nik': fields.char('NIK',20),
        'training_ids':fields.one2many('hr_training.training','employee_id',),
        'training_id': fields.many2one('hr_training.training','Training'),

        }
employee()

class kualifikasi(osv.osv):
    _name='hr_training.kualifikasi'
    #_inherit='hr.job'
    
    _columns= {
        'name':fields.many2one('hr.job','Job Name',),
        'kualifikasi_ids':fields.one2many('hr_training.kualifikasi_detail','kualifikasi_id',string='Kualifikasi'),
            }
kualifikasi()

class analisa(osv.osv):
    _name='hr_training.analisa'
    
    _columns= {
        'is_internal':fields.boolean('Ceklist Jika Training Internal'),
        'department_id': fields.many2one('hr.department', 'Department',required=True),
        'bulan':fields.selection([('Januari','Januari'),('Februari','Februari'),('Maret','Maret'),('April','April'),('Mei','Mei'),('Juni','Juni'),('Juli','Juli'),('Agustus','Agustus'),('September','September'),('Oktober','Oktober'),('November','November'),('Desember','Desember')],'Bulan'),
        'presentasi':fields.char('Presentasi Pelatihan',60),
        'no':fields.char('Nomor',10),
        'name':fields.char('Nama Pelatihan',128,required=True),
        'penyelenggara':fields.char('Lembaga Penyelenggara',128),
        'nama':fields.char('Nama Trainer',50),
        'tanggal':fields.date('Tanggal Penyelenggaraan'),
        'catatan':fields.char('Catatan Umum',60),
        'lama':fields.char('Lama',25),
        'realisasi':fields.date('Realisasi Pelaksanaan'),
        'employee_ids':fields.one2many('hr_training.train','analisa_id','Nama Karyawan'),
            }
analisa()           
