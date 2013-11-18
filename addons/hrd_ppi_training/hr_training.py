from openerp.osv import fields, osv
import math
import time
import datetime
from openerp.tools.translate import _
from openerp import tools

TRAINING_STATES =[
    ('draft','Draft'),
    ('verify','Verify'),
    ('approve','Approve'),
    ('approve2','Second Approve'),
    ('reject','Reject'),
    ('evaluation','Evaluation')]
    
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
        'employee_id' : fields.many2one('hr.employee','Nama Karyawan',store=True),
        'job_id' :fields.related('employee_id','job_id',type='many2one',relation='hr.job',string='Jabatan'),
        'department_id' : fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='Departemen',store=True),
        'paket_id': fields.related('analisa_id','bukti',type='char',relation='hr_training.analisa',string='Paket Pelatihan'),
        'analisa_id':fields.many2one('hr_training.analisa','Nama Training'),
        'subject_id':fields.related('analisa_id','subject_id',type='char',relation='hr_training.analisa',string='Nama Training ID'),
        'subject':fields.related('analisa_id','subject',type='char',relation='hr_training.analisa',string='Nama Training',store=True), 
        'evaluasi_id':fields.many2one('hr_training.evaluasi_training','Evaluasi Training'),
        'rekomendasi_id':fields.many2one('hr_training.rekomendasi_training','Rekomendasi'),
        'lama' : fields.related('analisa_id','lama',type='char',relation='hr_training.analisa',string='Lama'),
        'tanggal': fields.related('analisa_id','tanggal',type='date',relation='hr_training.analisa',string='Tanggal'),
        'bukti_ids':fields.one2many('hr_training.bukti','train_id','Bukti File'),
        'penyelenggara':fields.related('analisa_id','penyelenggara',type='char',relation='hr_training.analisa',string='Lembaga'),
        'is_internal':fields.related('analisa_id','is_internal',type='boolean',relation='hr_training.analisa',string='Ceklis Jika Training Internal'),  
        'nonik':fields.char('Kode Training'),
        #'email':fields.char('Email'), TODO if needed for email confirmstion for non-OpenERP-user 
        'state': fields.selection(TRAINING_STATES, 'Status', readonly=True, help="Status Training"),
        }

    _defaults = {
        'state': TRAINING_STATES[0][0],
        }

    def create(self, cr, uid, vals, context=None):    
        emp = self.pool.get('hr.employee')         
        vals['email'] = emp.browse(cr,uid,vals['employee_id']).work_email        
        return super(train, self).create(cr, uid, vals, context) 

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


class analisa(osv.osv):
    _name='hr_training.analisa'
    _rec_name='no'
    
    def action_draft(self,cr,uid,ids,context=None): 
        return self.write(cr,uid,ids,{'state':TRAINING_STATES[0][0]},context=context)

    def action_verify(self,cr,uid,ids,context=None):  
        return self.write(cr,uid,ids,{'state':TRAINING_STATES[1][0]},context=context)
 
    def action_reject(self,cr,uid,ids,context=None): 
        return self.write(cr,uid,ids,{'state':TRAINING_STATES[4][0]},context=context) 
        
    def action_approve(self,cr,uid,ids,context=None):
        obj=self.browse(cr,uid,ids)[0]
        kode=obj.no; state=obj.state      
        train_obj = self.pool.get('hr_training.train')
        sr = train_obj.search(cr,uid,[('analisa_id','=',kode)])
        tr=train_obj.browse(cr,uid,sr)
        #yids=[];
        for xids in tr:
            nikid=xids.employee_id.nik
            kod=str(kode) +'/'+ str(nikid)
            #yids.append({"nonik" : yes})
            train_obj.write(cr, uid, [xids.id], {'nonik':kod})
        #train_obj.write(cr, uid, [xids.id for ux in tr], {'nonik':yids.nonik})     
        return self.write(cr,uid,ids,{'state':TRAINING_STATES[2][0]},context=context)
        
    '''def action_reject_hr_department(self,cr,uid,ids,context=None): 
        return self.write(cr,uid,ids,{'state':TRAINING_STATES[2][0]},context=context)''' 
        
    def action_approve_hr_department(self,cr,uid,ids,context=None): 
        return self.write(cr,uid,ids,{'state':TRAINING_STATES[3][0]},context=context)
        
    def action_evaluation(self,cr,uid,ids,context=None):
        obj=self.browse(cr,uid,ids)[0]
        kode=obj.id; state=obj.state      
        train_obj = self.pool.get('hr_training.train')
        sr = train_obj.search(cr,uid,[('analisa_id','=',kode)])
        tr = train_obj.browse(cr,uid,sr)
        for xids in tr:
            train_obj.write(cr, uid, [xids.id], {'state':state})
        return self.write(cr,uid,ids,{'state':TRAINING_STATES[5][0]},context=context)       
 
    def create(self, cr, uid, vals, context=None):       
        obj = self.pool.get('hr_training.subject')
        sid = vals['subject_id']           
        vals['subject'] = obj.browse(cr,uid,sid).name
        kode=self.pool.get('ir.sequence').get(cr,uid,'hr_training.analisa.nomor')
        kode=str(obj.browse(cr,uid,sid).code)+'/'+str(kode)
        vals['no']=kode               
        return super(analisa, self).create(cr, uid, vals, context) 

    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        #import pdb;pdb.set_trace()
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day              

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            #import pdb;pdb.set_trace()
            date_to_with_delta = datetime.datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
            result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['durasi'] = round(math.floor(diff_day))+1
        else:
            result['value']['durasi'] = 0

        return result

    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['durasi'] = round(math.floor(diff_day))+1
        else:
            result['value']['durasi'] = 0

        return result  

    def _compute_number_of_days(self, cr, uid, ids, name, args, context=None):
        result = {}
        for hol in self.browse(cr, uid, ids, context=context):
            result[hol.id] = -hol.lama
        return result 

    _columns= {
        'employee_id':fields.many2one('hr.employee','Karyawan'),
        'is_internal':fields.boolean('Centang Jika Training Internal'),
        'department_id': fields.many2one('hr.department', 'Department',required=True),
        'bulan':fields.selection([('Januari','Januari'),('Februari','Februari'),('Maret','Maret'),('April','April'),('Mei','Mei'),('Juni','Juni'),('Juli','Juli'),('Agustus','Agustus'),('September','September'),('Oktober','Oktober'),('November','November'),('Desember','Desember')],'Bulan'),
        'presentasi':fields.char('Presentasi Pelatihan',60),
        'no':fields.char('Nomor', 10, readonly=True),
        'paket_id':fields.many2one('hr_training.paket','Paket Training'),
        'subject_id':fields.many2one('hr_training.subject','Nama Training',required=True, store=True),
        'penyelenggara':fields.char('Lembaga Penyelenggara',128),
        'mgt_id':fields.many2one('hr_training.mgt_company','MGT Company'),
        'nama':fields.char('Nama Trainer',50,),
        'tanggal':fields.date('Tanggal Penyelenggaraan'),
        'catatan':fields.char('Catatan Umum',60,),
        'lama':fields.char('Lama',25),
        'durasi':fields.integer('Durasi',store=True),
        'employee_ids':fields.one2many('hr_training.train','analisa_id','Nama Karyawan'),        
        'state': fields.selection(TRAINING_STATES, 'Status', readonly=True, help="Gives the status of the training."),  
        'user_id' : fields.many2one('res.users', 'Creator','Masukan User ID Anda'),
        'description' : fields.text('Deskripsi Training'),
        'subject': fields.char("Nama Training", readonly=True),
        'date_from': fields.datetime('Tanggal Mulai',),
        'date_to': fields.datetime('Tanggal Berakhir',),
        'number_of_days': fields.function(_compute_number_of_days, string='Jumlah Hari', store=True,readonly=True),
            }
            
    _defaults = {
        'state': TRAINING_STATES[0][0],
        'user_id': lambda obj, cr, uid, context: uid,
        #'no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hr_training.analisa.nomor'),
        }  
        
    _sql_constraints = [('no_uniq', 'unique(no)','Kode Training tidak boleh sama')]
        
analisa()    

class paket(osv.osv):
    _name='hr_training.paket'
    
    _columns={
        'name':fields.char('Paket Training',35,required=True),  
        'code':fields.char('Kode',5),
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
