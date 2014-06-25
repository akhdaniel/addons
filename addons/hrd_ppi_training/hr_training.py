from openerp.osv import fields, osv
import math
import time
import datetime
from openerp.tools.translate import _
from openerp import tools
from datetime import date
from time import strptime
from time import strftime
from datetime import datetime
import base64

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
        'name':fields.binary('Sertifikat'),  
        'employee_id' : fields.many2one('hr.employee','Nama Karyawan'),
        'train_id':fields.many2one('hr_training.train','Nama Training'),
            }
bukti()   


class train(osv.osv):
    _name = 'hr_training.train'

    def _employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False   

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

    def _persentase(self, cr, uid, ids, arg,field, context=None):
        #import pdb.set_trace()
        result = {}
        obj = self.browse(cr,uid,ids)[0]
        ID = obj.id
        obj_simpul = self.pool.get('hr_training.evaluasi_training')
        src_simpul = obj_simpul.search(cr,uid,[('eval_id','=',ID)])
        brw_simpul = obj_simpul.browse(cr,uid,src_simpul)
        nilai = 0
        x = 0
        date = datetime.now()
        for sim in  brw_simpul :
            nilai += float(sim.skor)
            x += 1
        if brw_simpul == [] :
            total = 0
        else :
            total =(nilai*100)/(x * 10)
        if total >= 90 :
            self.write(cr,uid,ids,{'kesimpulan':'sangat_efektif'})
        elif total >= 70 :
            self.write(cr,uid,ids,{'kesimpulan':'efektif'})
        elif total >= 50 :
            self.write(cr,uid,ids,{'kesimpulan':'cukup_efektif'})
        elif total >= 30 :
            self.write(cr,uid,ids,{'kesimpulan':'kurang_efektif'})
        else :
            self.write(cr,uid,ids,{'kesimpulan':'tidak_efektif'})
        self.write(cr,uid,ids,{'tanggal1': date})
        result[ID]= total
        return result

    _columns = {
        'employee_id' : fields.many2one('hr.employee','Nama Peserta',store=True),
        'job_id' :fields.related('employee_id','job_id',type='many2one',relation='hr.job',string='Jabatan'),
        'department_id' : fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='Departemen',store=True),
        'paket_id': fields.related('analisa_id','paket_id',type='char',relation='hr_training.analisa',string='Paket Pelatihan'),
        'analisa_id':fields.many2one('hr_training.analisa','Nama Training'),
        'subject_id':fields.related('analisa_id','subject_id',type='many2one',relation='hr_training.subject',string='Nama Training',store=True),
        'subject':fields.related('analisa_id','subject',type='char',relation='hr_training.analisa',string='Nama Training',store=True), 
        'evaluasi_id':fields.one2many('hr_training.evaluasi_training','eval_id','Topik Pelatihan'),
        'rekomendasi_id':fields.many2one('hr_training.rekomendasi_training','Rekomendasi Atasan'),
        'lama' : fields.related('analisa_id','lama',type='char',relation='hr_training.analisa',string='Lama'),
        'date_from' : fields.related('analisa_id','date_from',type='datetime',relation='hr_training.analisa',string='Tanggal Mulai'),
        'date_to' : fields.related('analisa_id','date_to',type='datetime',relation='hr_training.analisa',string='Tanggal Berakhir'),
        'durasi' : fields.related('analisa_id','durasi',type='integer',relation='hr_training.analisa',string='Durasi (Hari)'),
        'tanggal': fields.related('analisa_id','tanggal',type='date',relation='hr_training.analisa',string='Tanggal'),
        #'bukti_ids':fields.one2many('hr_training.bukti','train_id','Bukti File'),
        'bukti_id':fields.binary('Bukti File'),
        'penyelenggara':fields.related('analisa_id','penyelenggara',type='char',relation='hr_training.analisa',string='Lembaga'), 
        'nonik':fields.char('Kode Training'),
        #'email':fields.char('Email'), TODO if needed for email confirmstion for non-OpenERP-user 
        'state': fields.selection(TRAINING_STATES, 'Statuses', readonly=True, help="Status Training"),
        'number_of_days': fields.function(_compute_number_of_days, string='Jumlah Hari', store=True,readonly=True),
        'berlaku' : fields.date('Sertifikat Berlaku Sampai'),
        'ket' : fields.selection([('Aktif','Aktif'),('Pending','Pending')],'status',readonly=True),
        'persentase_penguasaan': fields.function(_persentase,type='float',obj='hr_training.train',method=True,string='Persentase Penguasaan topik Pelatihan (%)',readonly=True),
        #'kesimpulan' : fields.many2one('hr_training.kesimpulan','Kesimpulan Penilaian'),
        'kesimpulan' : fields.selection([('sangat_efektif','Sangat Efektif'),('efektif','efektif'),('cukup_efektif','Cukup Efektif'),('kurang_efektif','Kurang Efektif'),('tidak_efektif','Tidak Efektif')],'Kesimpulan'),
        'tanggal1' : fields.date('tanggal', readonly=True),
        'nama_penilai':fields.many2one('hr.employee','Nama Penilai',readonly=True),
        'jabatan_penilai':fields.related('nama_penilai','job_id',type='many2one',relation='hr.job',string='Jabatan',readonly=True),
        }

    _defaults = {
        'state': TRAINING_STATES[0][0],
        'ket' : 'Pending',
        #'tanggal1': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
        'nama_penilai': _employee_get,
        }

    def create(self, cr, uid, vals, context=None):    
        emp = self.pool.get('hr.employee')         
        vals['email'] = emp.browse(cr,uid,vals['employee_id']).work_email        
        return super(train, self).create(cr, uid, vals, context) 

train()

class one2many_mod2(fields.one2many):
    
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if context is None:
            context = {}
        if not values:
            values = {}
        res = {}
        for id in ids:
            res[id] = []    
        ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',ids),('state', '=', 'evaluation')], limit=self._limit)
        for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
            res[r[self._fields_id]].append( r['id'] )
        return res

class employee(osv.osv):
    _name='hr.employee'
    _inherit = 'hr.employee'

    _columns ={
        'train_ids':one2many_mod2('hr_training.train','employee_id', readonly=True), 
        'non_train' : fields.one2many('hr_non.emp','employee_id','Non Training'),
        'training_lainya' : fields.one2many('hr.training_lainya','employee_id','Training Lainya'),
        'sio_ids' : one2many_mod2('hr.training_sio','employee_id','Sertifikat SIO', readonly = True),
        'sio_id' : fields.one2many('hr.train_keahlian','employee_id','Keahlian Yang Harus Dimiliki'),
        }
employee()

class Keahlian(osv.osv):
    _name = 'hr.train_keahlian'

    _columns ={
        'name' : fields.many2one('iso','Nama SIO'),
        'employee_id' : fields.many2one('hr.employee'),
    } 

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
        kode=obj.id; state=TRAINING_STATES[5][0] 
        # for Training internal and external     
        train_obj = self.pool.get('hr_training.train')
        sr = train_obj.search(cr,uid,[('analisa_id','=',kode)])
        tr = train_obj.browse(cr,uid,sr)
        for xids in tr:
            train_obj.write(cr, uid, [xids.id], {'state':state, 'ket':'Aktif'})
        # for Training SIO
        sio_obj = self.pool.get('hr.training_sio')
        sio_src = sio_obj.search(cr,uid,[('analisa_id','=',kode)])
        for sio in sio_obj.browse(cr,uid,sio_src):
            sio_obj.write(cr,uid,[sio.id],{'state':state,'status': True})
        import pdb;pdb.set_trace()
        tes = obj.tes
        if tes == 'SIO' :
            for employee in obj.sio_ids :
                iso = employee.iso.id
                name = employee.employee_id.id
                analisa = employee.analisa_id.id
                obj = self.pool.get('hr.training_sio')
                src = obj.search(cr,uid,[('employee_id','=',name),('iso','=',iso),
                    ('state','=','evaluation'),('analisa_id','!=',analisa),('status','=',True)]) 
                for sio in obj.browse(cr,uid,src) :
                    obj.write(cr,uid,[sio.id],{'status':False, 'link_warning': False})
    	return self.write(cr,uid,ids,{'state':state},context=context)       
 
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

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state == 'evaluation':
                raise osv.except_osv(_('Peringatan!'),_('anda tidak bisa menghapus Training karna Status Training Evaluasi.'))
            no = rec.id
            obj = self.pool.get('hr_training.train')
            src = obj.search(cr,uid,[('analisa_id','=',no)])
            for ana in obj.browse(cr,uid,src) :
                obj.unlink(cr, uid, ana.id, context=context)
        return super(analisa, self).unlink(cr, uid, ids, context)

    _columns= {
        'employee_id':fields.many2one('hr.employee','Nama Peserta'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'bulan':fields.selection([('Januari','Januari'),('Februari','Februari'),('Maret','Maret'),('April','April'),('Mei','Mei'),('Juni','Juni'),('Juli','Juli'),('Agustus','Agustus'),('September','September'),('Oktober','Oktober'),('November','November'),('Desember','Desember')],'Bulan'),
        'tes': fields.selection([('Internal','Internal'),('Eksternal','Eksternal'),('SIO','SIO'),('non_training','Non Training')],'Jenis Training',readonly=True),
        'presentasi':fields.char('Presentasi Pelatihan',60),
        'no':fields.char('Nomor', 10, readonly=True),
        'paket_id':fields.many2one('hr_training.paket','Paket Pelatihan'),
        'subject_id':fields.many2one('hr_training.subject','Nama Pelatihan',required=True, store=True),
        'penyelenggara':fields.char('Lembaga Penyelenggara',128),
        'mgt_id':fields.many2one('hr_training.mgt_company','MGT Company'),
        'nama':fields.char('Nama Trainer',50,),
        'tanggal':fields.date('Tanggal Penyelenggaraan'),
        'catatan':fields.char('Catatan Umum',60,),
        'lama':fields.char('Lama',25),
        'durasi':fields.integer('Durasi',store=True),
        'employee_ids':fields.one2many('hr_training.train','analisa_id','Nama Karyawan'),    
        'sio_ids':fields.one2many('hr.training_sio','analisa_id','Nama Karyawan'),    
        'state': fields.selection(TRAINING_STATES, 'Status', readonly=True, help="Gives the status of the training."),  
        'user_id' : fields.many2one('res.users', 'Creator','Masukan User ID Anda'),
        'description' : fields.text('Deskripsi Pelatihan'),
        'subject': fields.char("Nama Pelatihan", readonly=True),
        'date_from': fields.datetime('Tanggal Mulai',),
        'date_to': fields.datetime('Tanggal Berakhir',),
        'number_of_days': fields.function(_compute_number_of_days, string='Jumlah Hari', store=True,readonly=True),
        'pp' :fields.many2one('peraturan.perundangan','Peraturan Perundangan'),
        'pt' :fields.many2one('peraturan.tentanng','Peraturan Tentang'), 
        'nama_sertifikat' :fields.many2one('sertifikat','Nama Sertifikat',),
        'iso' : fields.many2one('iso','Nama SIO'),
        'tempat_pelatihan': fields.char('Templat Pelatihan'),   
            }
            
    _defaults = {
        'state': TRAINING_STATES[0][0],
        'user_id': lambda obj, cr, uid, context: uid,
        'tes':'SIO',
        'subject_id': 1,
        #'no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hr_training.analisa.nomor'),
        }  
        
    _sql_constraints = [('no_uniq', 'unique(no)','Kode Training tidak boleh sama')]
        
analisa()    

class pp(osv.osv):
    _name="peraturan.perundangan"

    _columns = {
        'name' : fields.char('Peraturan Perundangan')
    }

class sertifikat(osv.osv):
    _name='sertifikat'

    _columns = {
        'name' : fields.char('Nama Sertifikat')
    }

class iso(osv.osv):
    _name='iso'

    _columns = {
        'name' : fields.char('Nama ISO')
    }

class pt(osv.osv):
    _name='peraturan.tentanng'

    _columns = {
        'name' : fields.char('Peraturan Perundangan Tentang')
    }

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

class evaluasi_training(osv.osv):
    _name='hr_training.evaluasi_training'
    
    _columns={        
        'name' : fields.char('Topik-topik Pelatihan'),
        'skor' : fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')],'Score Penguasaan Topik Pelatihan'),
        'eval_id':fields.many2one('hr_training.train'),  
            }
evaluasi_training()       
 
 ##################################
 ##### Clas Untuk Non Training ####
 ##################################

class non_training(osv.osv):
    _name = "hr.non_training"

    _rec_name = 'id'

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            no = rec.id
            obj = self.pool.get('hr_non.emp')
            src = obj.search(cr,uid,[('non_train','=',no)])
            for ana in obj.browse(cr,uid,src) :
                obj.unlink(cr, uid, ana.id, context=context)
        return super(non_training, self).unlink(cr, uid, ids, context)

    _columns = {
        'id':fields.integer('No Training'),
        'subject_id' : fields.many2one('hr_training.subject','Judul Seminar'),
        'penyelenggara' : fields.char('Penyelanggara'),
        'tanggal' : fields.datetime('Tanggal Mulai'),
        'employee_ids':fields.one2many('hr_non.emp','non_train','Nama Karyawan'),
    }
non_training()

class peserta_non(osv.osv):
    _name = 'hr_non.emp'

    _columns = {
        'employee_id' :fields.many2one('hr.employee','Nama Peserta'),
        'nik' :fields.related('employee_id','nik',type='char',relation='hr.employee',string='NIK'),
        'tgl_msk' : fields.related('employee_id','tgl_msk',type='date',relation='hr.employee',string='Tanggal Masuk Kerja'),
        'clas_id' :fields.related('employee_id','clas_id', type='many2one', relation='hr_employs.clas', string='Level'),
        'department_id' : fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='Departemen',store=True),    
        'work_location2' : fields.related('employee_id','work_location2', type='selection', relation='hr.employee', string='Loker'),
        'bukti' :fields.binary('Bukti Keikutsertaan',required=True),  
        'ket':fields.char('Keterangan'),
        'non_train':fields.many2one('hr.non_training','Judul Seminar'),
        'subject_id' : fields.related('non_train','subject_id',type='many2one',relation='hr_training.subject',string='Judul Seminar'),
        'penyelenggara' : fields.related('non_train','penyelenggara',type='char',relation='hr.non_training',string='Penyelenggara'),
        'tanggal' : fields.related('non_train','tanggal',type='datetime',relation='hr.non_training',string='Tanggal Mulai'),
    }

class training_lainya(osv.osv):
    _name = 'hr.training_lainya'

    _columns ={
        'employee_id' : fields.many2one('hr.employee','Karyawan'),
        'train' : fields.char('Nama Training'),
        'penyelenggara' : fields.char('Penyelenggara'),
        'tgl_mulai' : fields.date("Tanggal Mulai"),
        'tgl_berakhir' : fields.date('Tanggal Berakhir'),
        'lembaga':fields.char('Lembaga Penyelenggara'),
        'bukti' : fields.binary('Bukti File'),
        }

class sio(osv.osv):
    _name = 'hr.training_sio'

    def schedule_iso(self, cr, uid, ids=None, context=None):
        if context is None :
            context = {}
        context = dict(context, mail_create_nolog=True)
        obj_warning = self.pool.get('warning.schedule')
        src_warning = obj_warning.search(cr,uid,[('name','=','sio')])
        brw_warning = obj_warning.browse(cr,uid,src_warning)
        lama = brw_warning[0]
        durasi = lama.date_warning
        obj = self.pool.get('hr.training_sio')
        src = obj.search(cr,uid,[('status','=',True),('state','=','evaluation')])
        import pdb;pdb.set_trace()
        for warning in obj.browse(cr, uid, src) :
            tgl = warning.berlaku
            day_now = datetime.now()
            tgl_akhir = datetime.strptime(tgl,"%Y-%m-%d")
            nb_of_days = (tgl_akhir - day_now).days + 1
            if nb_of_days <= durasi :
                obj.write(cr, uid, [warning.id],{'warning_hari':nb_of_days,'link_warning':lama.id})
            else :
                obj.write(cr, uid, [warning.id],{'warning_hari':nb_of_days,'link_warning': False})
        return {'type': 'ir.actions.act_window_close'}

    _columns = {
        'employee_id' :fields.many2one('hr.employee','Nama Peserta'),
        'nik' :fields.related('employee_id','nik',type='char',relation='hr.employee',string='NIK',readonly=True),
        'department_id' : fields.related('employee_id','department_id',type='many2one',readonly=True, relation='hr.department',string='Departemen',store=True),    
        'bukti' :  fields.binary('Bukti'),  
        'berlaku' :fields.date('Masa Berlaku',required=True),
        'nama_sertifikat' : fields.related('analisa_id','nama_sertifikat', type='many2one', readonly=True, relation='sertifikat', string='Sertifikat'),
        'iso' : fields.related('analisa_id','iso', type='many2one', readonly=True, relation='iso', string='Nama SIO'),
        'analisa_id':fields.many2one('hr_training.analisa','Nama Training'),
        'link_warning':fields.many2one('warning.schedule'),
        'warning_hari' : fields.integer('Kadaluarsa'),
        'status':fields.boolean('status'),
        'state': fields.selection(TRAINING_STATES, 'Statuses', readonly=True, help="Status Training"),

        }
    _defaults = {
        'status' : True,
        'warning_hari' : 100000, 
    }


class warning_schedule(osv.osv):
    _name = 'warning.schedule'
    _inherit = 'warning.schedule'#

    _columns = {
        'warning_sio' :fields.one2many('hr.training_sio','link_warning','SIO Yang Akan Berakhir', readonly=True),
    }