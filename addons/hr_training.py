from openerp.osv import fields, osv
import time

class bukti(osv.osv):
    _name='hr_training.bukti'
    
    _columns={
        'name':fields.binary('Sertifikat',required=True),  
        'employee_id' : fields.many2one('hr.employee','Nama Karyawan'),
        'train_id':fields.many2one('hr_training.train','Nama Training'),
            }
bukti()   

class train(osv.osv):
    _name = 'hr_training.train'

    _columns = {
        'employee_id' : fields.many2one('hr.employee','Nama Karyawan'),
        'job_id' :fields.related('employee_id','job_id',type='many2one',relation='hr.job',string='Jabatan'),
        'department_id' : fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='Departemen'),
        'paket_id': fields.related('analisa_id','bukti',type='char',relation='hr_training.analisa',string='Paket Pelatihan'),
        'analisa_id':fields.many2one('hr_training.analisa','Nama Training'),
        'subject_id':fields.related('analisa_id','subject_id',type='char',relation='hr_training.analisa',string='Nama Training ID'),
        'subject':fields.related('analisa_id','subject',type='char',relation='hr_training.analisa',string='Nama Training'),
        'evaluasi_id':fields.many2one('hr_training.evaluasi_training','Evaluasi Training'),
        'rekomendasi_id':fields.many2one('hr_training.rekomendasi_training','Rekomendasi'),
        'lama' : fields.related('analisa_id','lama',type='char',relation='hr_training.analisa',string='Lama'),
        'tanggal': fields.related('analisa_id','tanggal',type='date',relation='hr_training.analisa',string='Tanggal'),
        'bukti_ids':fields.one2many('hr_training.bukti','train_id','Bukti File'),
        'penyelenggara':fields.related('analisa_id','penyelenggara',type='char',relation='hr_training.analisa',string='Lembaga'),
        'is_internal':fields.related('analisa_id','is_internal',type='boolean',relation='hr_training.analisa',string='Ceklist Jika Training Internal'),        
        #'state':fields.related('analisa_id','state',type='selection',relation='hr_training.analisa',string='Status'),
        'kode':fields.char('Kode Pelatihan Karyawan',5),
            }   
train()

class employee(osv.osv):
    _name='hr.employee'
    _inherit = 'hr.employee'
    _columns ={
        #'nik': fields.char('NIK',20),
        'train_ids':fields.one2many('hr_training.train','employee_id','Training'),
        'analisa_id':fields.many2one('hr_training.analisa'),           
        }
employee()

TRAINING_STATES =[
	('draft','Draft'),
	('verify','Verify'),
	('reject','Reject'),
	('approve','Approve'),
	('reject2','Second Reject'),
	('approve2','Second Approve'),
	('evaluation','Evaluation')]

class analisa(osv.osv):
    _name='hr_training.analisa'
    _rec_name='subject_id'
    
    def action_draft(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':TRAINING_STATES[0][0]},context=context)

    def action_verify(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':TRAINING_STATES[1][0]},context=context)
 
    def action_reject(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':TRAINING_STATES[2][0]},context=context) 
    	
    def action_approve(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':TRAINING_STATES[3][0]},context=context)
    	
    def action_reject_hr_department(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':TRAINING_STATES[4][0]},context=context) 
    	
    def action_approve_hr_department(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':TRAINING_STATES[5][0]},context=context)
    	
    def action_evaluation(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':TRAINING_STATES[6][0]},context=context)       
 
    def create(self, cr, uid, vals, context=None):
        obj = self.pool.get('hr_training.subject')
        sid=vals['subject_id']
        vals['subject'] = obj.browse(cr,uid,sid).name
        return super(analisa, self).create(cr, uid, vals, context)
  
        
    _columns= {
        'employee_id':fields.many2one('hr.employee','Karyawan'),
        'is_internal':fields.boolean('Ceklist Jika Training Internal'),
        'department_id': fields.many2one('hr.department', 'Department',required=True),
        'bulan':fields.selection([('Januari','Januari'),('Februari','Februari'),('Maret','Maret'),('April','April'),('Mei','Mei'),('Juni','Juni'),('Juli','Juli'),('Agustus','Agustus'),('September','September'),('Oktober','Oktober'),('November','November'),('Desember','Desember')],'Bulan'),
        'presentasi':fields.char('Presentasi Pelatihan',60),
        'no':fields.char('Nomor',10),
        'paket_id':fields.many2one('hr_training.paket','Paket Training'),
        'subject_id':fields.many2one('hr_training.subject','Nama Training',required=True, store=True),
        'penyelenggara':fields.char('Lembaga Penyelenggara',128),
        'mgt_id':fields.many2one('hr_training.mgt_company','MGT Company'),
        'nama':fields.char('Nama Trainer',50),
        'tanggal':fields.date('Tanggal Penyelenggaraan'),
        'catatan':fields.char('Catatan Umum',60),
        'lama':fields.char('Lama',25),
        'realisasi':fields.date('Realisasi Pelaksanaan'),
        'employee_ids':fields.one2many('hr_training.train','analisa_id','Nama Karyawan'),        
        'state': fields.selection(TRAINING_STATES, 'Status', readonly=True, help="Gives the status of the training."),  
        'user_id' : fields.many2one('res.users', 'Creator','Masukan User ID Anda'),
        'description'   : fields.text('Deskripsi Training'),
        'subject': fields.char("Nama Training", readonly=True),
            }
            
    _defaults = {
        'state': TRAINING_STATES[0][0],
        'user_id': lambda obj, cr, uid, context: uid,
        'no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hr_training.analisa.nomor'),
        }  
analisa()    

class paket(osv.osv):
    _name='hr_training.paket'
    
    _columns={
        'name':fields.char('Paket Training',35,required=True),  
            }
paket()   

class subject(osv.osv):
    _name='hr_training.subject'
    
    _columns={
        'name':fields.char('Nama Training',50,required=True),
        'code':fields.char('Kode',5),
            }
subject()  

class evaluasi_training(osv.osv):
    _name='hr_training.evaluasi_training'
    
    _columns={
        'name':fields.char('Evaluasi Training',50,required=True),  
            }
evaluasi_training()       

class rekomendasi_training(osv.osv):
    _name='hr_training.rekomendasi_training'
    
    _columns={
        'name':fields.char('Rekomendasi Training',50,required=True),  
            }
rekomendasi_training()      

class mgt_company(osv.osv):
    _name='hr_training.mgt_company'
    
    _columns={
        'name':fields.char('MGT Company',50,required=True),  
            }
mgt_company() 
