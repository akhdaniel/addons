from openerp.osv import fields, osv
#from openerp.addons.base_status.base_stage import base_stage
from datetime import date
from time import strptime
from time import strftime

PERMOHONAN_STATES =[
	('draft','Draft'),
	('submit','Submit'),
	('verify','Verify'),
	('in_progress','In Progress')]
class permohonan_recruit(osv.osv):
    _name = 'hr.job'
    _inherit = 'hr.job'
    
    def action_draft(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':PERMOHONAN_STATES[0][0]},context=context)
    	
    def action_submit(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':PERMOHONAN_STATES[1][0]},context=context) 	

    def action_verify(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':PERMOHONAN_STATES[2][0]},context=context)
 
    def action_in_progress(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':PERMOHONAN_STATES[3][0]},context=context)
    	
    def scroll_no(self, cr, uid, ids, no, args, context=None):
        res = []
        for x in range(15,51):
            res.append(x)
        return res

    
    _columns= {
        'jenis_permohonan':fields.selection([('Bulanan','Bulanan'),('Harian','Harian')],'Jenis Permohonan',required=True),
        'no':fields.char('Nomor',20),
        'status_jabatan':fields.selection([('P','Pengganti'),('T','Tambahan'),('JB','Jabatan Baru')],'Status'),
        'type_id': fields.many2one('hr.recruitment.degree', 'Pendidikan',required=True),
        'jurusan_ids':fields.one2many('hr_recruit.jurusan','permohonan_recruit_id','jurusan'),
        'pengalaman':fields.integer('Pengalaman (min-th)'),
        'usia':fields.selection([('18','18'),('19','19'),('20','20'),('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31'),('32','32'),('33','33'),('34','34'),('35','35'),('36','36'),('37','37'),('38','38'),('39','39'),('40','40'),('41','41'),('42','42'),('43','43'),('44','44'),('45','45'),('46','46'),('47','47'),('48','48'),('49','49'),('50','50')],'Usia (max)'),
        'sts_prk':fields.selection([('single','Single'),('menikah','Menikah')],'Status Pernikahan'),
        'kelamin':fields.selection([('male','Male'),('female','Female'),('male/Female','Male / Female')],'Jenis Kelamin'),
        'wkt_pemohon':fields.date('Permintaan Pemohon'),
        'wkt_rekruter':fields.date('Kesanggupan Rekruter'),
        'catatan':fields.char('Realisasi Penempatan',128),
        'catatan2':fields.text('Catatan'),
        'state': fields.selection(PERMOHONAN_STATES, 'Status', readonly=True, help="Gives the status of the recruitment."),  
        'user_id' : fields.many2one('res.users', 'Creator','Masukan User ID Anda'),    
        'survey_ids':fields.one2many('survey','job_id','Interview Form'),
        'survey_id': fields.many2one('survey', '', readonly=True, help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job"),     
                }
    _defaults = {
        'state': PERMOHONAN_STATES[0][0],
        'user_id': lambda obj, cr, uid, context: uid,
                 }  
            
permohonan_recruit()

class hr_survey(osv.osv):
    _name='hr.survey'
    
    _columns= {
        'surveys_id' :fields.many2one('survey', 'Interview Form'),  
        'jobs_id' : fields.many2one('hr.job'),  
        'applicant_id':fields.many2one('hr.applicant'),
        }
hr_survey()

class pendidikan(osv.osv):
    _name='hr_recruit.pendidikan'
    
    _columns= {
        'name':fields.char('Pendidikan',25,required=True),
        #'jurusan':fields.one2many('hr_recruit.jurusan','pendidikan_id','Jurusan'),
            }
pendidikan()

class jurusan(osv.osv):
    _name='hr_recruit.jurusan'
    
    _columns= {
        'name':fields.many2one('hr_recruit.jurusan_detail','Jurusan',required=True),
        #'pendidikan_id':fields.many2one('hr_recruit.pendidikan'),
        'permohonan_recruit_id':fields.many2one('hr.job','Pekerjaan'),
            }
jurusan()

class jurusan_detail(osv.osv):
    _name='hr_recruit.jurusan_detail'
    
    _columns= {
        'name':fields.char('Jurusan',30,required=True),
            }
jurusan_detail()

class hr_applicant(osv.osv):
    _name='hr.applicant'
    _inherit='hr.applicant'
    _rec_name='partner_name'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def create(self, cr, uid, vals, context=None):
        vals['name'] = vals['name'].title()
        return super(hr_applicant, self).create(cr, uid, vals, context)
 
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('name', False):
            vals['name'] = vals['name'].title()
        return super(hr_applicant, self).write(cr, uid, ids, vals, context)
    
    def case_close_with_emp(self, cr, uid, ids,vals, context=None):
        if context is None:
            context = {}
        hr_employee = self.pool.get('hr.employee')
        model_data = self.pool.get('ir.model.data')
        act_window = self.pool.get('ir.actions.act_window')
        emp_id = False
        for applicant in self.browse(cr, uid, ids, context=context):
            address_id = False
            if applicant.partner_id:
                address_id = self.pool.get('res.partner').address_get(cr,uid,[applicant.partner_id.id],['contact'])['contact']
            if applicant.job_id:
                applicant.job_id.write({'no_of_recruitment': applicant.job_id.no_of_recruitment - 1})
                #import pdb;pdb.set_trace()
                pes=self.browse(cr,uid,ids)[0]
                coy=pes.partner_name
                le=self.pool.get('hr_recruit.suskel1')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)
                prod_ids=[]              
                for pr in lele:
                    prod_ids.append((0,0, {'name':pr.name,'kelamin':pr.kelamin,'kota_id':pr.kota_id.id,'tgl_lahir':pr.tgl_lahir,'type_id':pr.type_id.id,'pekerjaan':pr.pekerjaan,'susunan':pr.susunan}))
                le=self.pool.get('hr_recruit.suskel2')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids1=[]   
                for pr in lele:
                    prod_ids1.append((0,0, {'susunan':pr.susunan,'name':pr.name,'kelamin':pr.kelamin,'kota_id':pr.kota_id.id,'tgl_lahir':pr.tgl_lahir,'type_id':pr.type_id.id,'pekerjaan':pr.pekerjaan}))          
                le=self.pool.get('hr_recruit.rwt_pend')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids2=[]   
                for pr in lele:
                    prod_ids2.append((0,0, {'name':pr.name,'jurusan':pr.jurusan.id,'tempat':pr.tempat,'tahun_msk':pr.tahun_msk,'tahun_klr':pr.tahun_klr,'ijazah':pr.ijazah.id})) 
                le=self.pool.get('hr_recruit.bahasa')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids3=[]   
                for pr in lele:
                    prod_ids3.append((0,0, {'name':pr.name,'tulis':pr.tulis,'lisan':pr.lisan})) 
                le=self.pool.get('hr_recruit.rwt_krj')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids4=[]   
                for pr in lele:
                    prod_ids4.append((0,0, {'no':pr.no,'name':pr.name,'tempat':pr.tempat,'tahun_msk':pr.tahun_msk,'tahun_klr':pr.tahun_klr,'jabatan':pr.jabatan,'gaji':pr.gaji,'alasan':pr.alasan})) 
                le=self.pool.get('hr_recruit.kon1')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids5=[]   
                for pr in lele:
                    prod_ids5.append((0,0, {'employee_id':pr.employee_id.name,'alamat':pr.alamat,'job_id':pr.job_id.id,'telepon':pr.telepon})) 
                le=self.pool.get('hr_recruit.kon2')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids6=[]   
                for pr in lele:
                    prod_ids6.append((0,0, {'name':pr.name,'alamat':pr.alamat,'jabatan':pr.jabatan,'telepon':pr.telepon}))  
                emp_id = hr_employee.create(cr,uid,{'name': applicant.partner_name or applicant.name,
                                                     'job_id': applicant.job_id.id,
                                                     'department_id': applicant.department_id.id,
                                                     'gender':applicant.kelamin,
                                                     'kota_id' : applicant.kota_id.id,
                                                     'birthday' : applicant.tgl_lahir,
                                                     'agama_id' : applicant.agama_id.id,
                                                     'country_id' : applicant.country_id.id,
                                                     'ktp' : applicant.ktp,
                                                     'issued_id' : applicant.issued_id,
                                                     'tgl_keluar_ktp' : applicant.tgl_keluar_ktp,
                                                     'tgl_berlaku' : applicant.tgl_berlaku,
                                                     'sim' : applicant.sim,
                                                     'tgl_keluar_sim' : applicant.tgl_keluar_sim,
                                                     'type_id':applicant.type_id.id,
                                                     'jurusan_id':applicant.jurusan_id.id,
                                                     'result_id':applicant.result_id.id,
                                                     'alamat1' : applicant.alamat1,
                                                     'alamat2' : applicant.alamat2,
                                                     'telp1' : applicant.telp1,
                                                     'telp2' : applicant.telp2,
                                                     'status': applicant.status,
                                                     'sjk_tanggal' : applicant.sjk_tanggal,
                                                     'susunan_kel1_ids' : prod_ids,
                                                     'susunan_kel2_ids':prod_ids1,
                                                     'rwt_pend_ids':prod_ids2,
                                                     'bahasa_ids':prod_ids3,
                                                     'rwt_krj_ids':prod_ids4,
                                                     'koneksi1_ids':prod_ids5,
                                                     'koneksi2_ids':prod_ids6,
                                                    })
                
                
                self.write(cr, uid, [applicant.id], {'emp_id': emp_id}, context=context)
                self.case_close(cr, uid, [applicant.id], context)
            else:
                raise osv.except_osv(_('Warning!'), _('You must define Applied Job for this applicant.'))

        action_model, action_id = model_data.get_object_reference(cr, uid, 'hr', 'open_view_employee_list')
        dict_act_window = act_window.read(cr, uid, action_id, [])
        if emp_id:
            dict_act_window['res_id'] = emp_id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window

    def case_cancel(self, cr, uid, ids, context=None):
        """Overrides cancel for crm_case for setting probability
        """
        res = super(hr_applicant, self).case_cancel(cr, uid, ids, context)
        self.write(cr, uid, ids, {'probability': 0.0})
        return res 
        
    def _compute_age(self, cr, uid, ids, age, tgl_lahir, arg, context=None):
        # Fetch data structure and store it in object form
        records = self.browse(cr, uid, ids, context=context)
        result = {}
        # For all records in 'ids'
        for r in records:
            # In case 'birthdate' field is null
            age = 0
            # If 'birthdate' field not null
            if r.tgl_lahir:
                # Encode string from 'birthdate' attribute
                d = strptime(r.tgl_lahir,"%Y-%m-%d")
                # Compute age as a time interval
                #delta = date(d[0], d[1], d[2]) - date.today()
                delta = date.today() - date(d[0], d[1], d[2])
                # Convert time interval to string value
                age = delta.days / 365
            result[r.id] = age
        return result
        
    def coco(self,cr, uid,ids, context=None): 
		#import pdb;pdb.set_trace()
        par=self.browse(cr,uid,ids)[0]
        #aplican
        ap_jb=par.job_id.name
        ap_umr=par.age
        ap_stage=par.stage_id.id
        ap_pend=par.type_id.id  
        ap_kelamin=par.kelamin 
        ap_jurusan=par.jurusan_id.id
        ap_pengalaman=par.pengalaman
        ap_status=par.status
        #job
        partner=self.pool.get('hr.job')  
        pero=partner.search(cr,uid,[('name','=',ap_jb)])     
        per=partner.browse(cr,uid,pero,context)[0] 
        job_name=per.name     
        job_umr=per.usia
        job_pend=per.type_id.id
        job_kelamin =per.kelamin
        job_pengalaman=per.pengalaman
        job_status=per.sts_prk
		job_state=per.state
        #refused
        partner=self.pool.get('hr.recruitment.stage')  
        pero=partner.search(cr,uid,[])     
        pers=partner.browse(cr,uid,pero,context)
        #jurusan
        jurusan=self.pool.get('hr_recruit.jurusan')        
        jur_id=jurusan.search(cr, uid,[('permohonan_recruit_id','=',job_name)])       
        jur=jurusan.browse(cr,uid,jur_id,context)
        stg_id=[]
        for line in pers :
            stage=line.sequence          
            if stage == 100 :
                stgs=line.id
            if job_state == 'in_progress':    
                if stage == 2 :
                    stg=line.id
                    if ap_umr <= job_umr or job_umr == 0 :
                        if ap_pend == job_pend :
                            if job_kelamin == 'male/female' or job_kelamin == ap_kelamin :
                                if ap_status == job_status or job_status == False :
                                    if ap_pengalaman >= job_pengalaman or job_pengalaman  == 0 :
                                        for jjr in jur:
                                            perok=jjr.name.id
                                            if perok == ap_jurusan or perok == False:                                
                                                return self.write(cr,uid,ids,{'stage_id': stg},context=context)                         
        return self.write(cr,uid,ids,{'stage_id': stgs},context=context)
ju
    

    def interview(self, cr, uid,vals, context=None):
        #import pdb;pdb.set_trace()
        #appl=self.browse(cr,uid,ids)[0]
        app=vals["job_id"]
        apps=self.pool.get('survey')
        appss=apps.search(cr,uid,[('job_id','=',app)])
        ap=apps.browse(cr,uid,appss,context)
        res=[]
        for pr in ap:
            if pr.state == "open":
                prs=pr.id
                res.append((0,0, {'name':prs})) 
        vals['surv_ids']=res
        return vals
        
    def create(self, cr, uid, vals, context=None):       
        vals=self.interview(cr, uid, vals, context=None)
        result= super(hr_applicant,self).create (cr, uid, vals, context=None)
        return result 
        
    def simpul(self, cr, uid,ids,vals,context=None):     
        #import pdb;pdb.set_trace() 
        hasil=self.browse(cr,uid,ids)[0]
        #hasil2=hasil.kesimpulan
        partner=self.pool.get('hr.recruitment.stage')  
        pero=partner.search(cr,uid,[])     
        pers=partner.browse(cr,uid,pero,context)
        stg2=float(hasil.stage_id.sequence)+1
        for line in pers: 
            stage=line.sequence
            #if stage == 100 :
               # stgs=line.id
                #if hasil2 == 'Ditolak':         
                    #vals=stg                       
                    #return self.write(cr,uid,ids,{'stage_id': stgs},context=context)   
            if stage == stg2 :
                stg=line.id
                #if hasil2 == 'Dapat_Diterima':   
                    #vals=stg                             
                return self.write(cr,uid,ids,{'stage_id': stg},context=context)                         
        #return self.write(cr,uid,ids,{'stage_id': stgs},context=context)    
    
    #def write(self, cr, uid, ids, vals, context=None):      
        #vals=self.simpul(cr, uid, ids, vals, context=None)
        #result= super(hr_applicant,self).write (cr, uid, ids,vals, context)
        #return result 
                        
    _columns= {
        'kelamin':fields.selection([('male','Male'),('female','Female')],'Jenis Kelamin',required=True),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir',required=True),
        'age': fields.function(_compute_age, type='integer', obj='hr.applicant', method=True, store=False, string='Usia (Thn)', readonly=True),
        'agama_id':fields.many2one('hr_recruit.agama','Agama'),
        'country_id': fields.many2one('res.country', 'Kewarganegaraan'),
        'ktp':fields.char('No KTP',20),
        'issued_id':fields.many2one('hr_recruit.issued','Dikeluarkan Oleh',50),
        'tgl_keluar_ktp':fields.date('Tanggal Dikeluarkan',),
        'tgl_berlaku':fields.date('Tanggal Berlaku'),
        'tgl_berlaku2':fields.date('Tanggal Berlaku'),
        'sim':fields.selection([('A','A'),('B1','B1'),('B2','B2'),('C','C')],'SIM'),
        'tgl_keluar_sim':fields.date('Tanggal Dikeluarkan'),
        'alamat1':fields.text('Alamat 1'),
        'alamat2':fields.text('Alamat 2'),
        'telp1':fields.char('Telepon',50),
        'telp2':fields.char('Telepon',50),
        'status':fields.selection([('single','Single'),('menikah','Menikah')],'Status Pernikahan',required=True),
        'sjk_tanggal':fields.date('Sejak Tanggal'),  
        'survey_id': fields.many2one('survey', 'Interview Form', help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job"),      
        'susunan_kel1_ids':fields.one2many('hr_recruit.suskel1','applicant_id','Susunan Keluarga'),
        'susunan_kel2_ids':fields.one2many('hr_recruit.suskel2','applicant_id','Susunan Keluarga'),
        'rwt_pend_ids':fields.one2many('hr_recruit.rwt_pend','applicant_id','Riwayat Pendidikan'),
        'bahasa_ids':fields.one2many('hr_recruit.bahasa','applicant_id','Bahasa'),
        'rwt_krj_ids':fields.one2many('hr_recruit.rwt_krj','applicant_id','Riwayat Pekerjaan'),
        'koneksi1_ids':fields.one2many('hr_recruit.kon1','applicant_id','Referensi Internal'),
        'koneksi2_ids':fields.one2many('hr_recruit.kon2','applicant_id','Referensi Eksternal'),
        'interview_ids':fields.one2many('hr_recruit.interview','applicant_id','Mulai Interview'),
        'jurusan_id':fields.many2one('hr_recruit.jurusan_detail','Jurusan',required=True),
        'job_id': fields.many2one('hr.job', 'Applied Job',required=True),
        'type_id': fields.many2one('hr.recruitment.degree', 'Pendidikan',required=True),
        'result_id':fields.many2one('hr_recruit.result','Result'),
        'surv_ids':fields.one2many('hr.survey','applicant_id','Interview Form'),
        'pengalaman':fields.integer('Pengalaman (min-th)'),
        'stage_id': fields.many2one ('hr.recruitment.stage', 'Stage',
                        domain="['&', ('fold', '=', False), '|', ('department_id', '=', department_id), ('department_id', '=', False)]",readonly=True),
        #'kesimpulan':fields.selection([('Dapat_Diterima','Dapat Diterima'),('Untuk_Dicadangkan','Untuk Dicadangkan'),('Ditolak','Ditolak')],'Kesimpulan'), 
        }
hr_applicant()

class susunan_keluarga1(osv.osv):
    _name='hr_recruit.suskel1'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),
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
    _name='hr_recruit.suskel2'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),
        'susunan':fields.selection([('Ayah','Ayah'),('Ibu','Ibu'),('anak1','Anak ke-1'),('anak2','Anak ke-2'),('anak3','Anak ke-3'),('anak4','Anak ke-4'),('anak5','Anak ke-5'),('anak6','Anak ke-6')],'Status Dalam Keluarga'),
        'name':fields.char('Nama',required=True),
        'kelamin':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'type_id':fields.many2one('hr.recruitment.degree', 'Pendidikan'),
        'pekerjaan':fields.char('Pekerjaan',60),
            }
susunan_keluarga2()   

class rwt_pendidikan(osv.osv):
    _name='hr_recruit.rwt_pend'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),
        'name':fields.char('Nama Sekolah',128,required=True),
        'jurusan':fields.many2one('hr_recruit.jurusan_detail','Jurusan',50),
        'tempat':fields.text('Alamat'),
        'tahun_msk':fields.date('Tahun Masuk'),
        'tahun_klr':fields.date('Tahun Keluar'),
        'ijazah':fields.many2one('hr.recruitment.degree','Ijazah yang Diperoleh'),
            }
rwt_pendidikan()      

class bahasa(osv.osv):
    _name='hr_recruit.bahasa'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant','Applicant'),        
        'name':fields.many2one('res.country', 'Bahasa',required=True),
        'tulis':fields.many2one('hr_recruit.b_tulisan','Tertulis'),
        'lisan':fields.many2one('hr_recruit.b_lisan','Lisan'),
            }
bahasa()    

class rwt_pekerjaan(osv.osv):
    _name='hr_recruit.rwt_krj'
    
    _columns= {
        'no':fields.integer('Nomor',readonly=True),
        'applicant_id':fields.many2one('hr.applicant'), 
        'name':fields.char('Nama Perusahaan',60),
        'tempat':fields.text('Alamat'),
        'tahun_msk':fields.date('Tahun Masuk'),
        'tahun_klr':fields.date('Tahun Keluar'),
        'jabatan':fields.char('Jabatan',30),
        'gaji':fields.float('Gaji'),
        'alasan':fields.char('Alasan Pindah',30),
            }
            
    #_defaults = {               
        #'no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hr_recruit.rwt_krj'),
               # }
            
rwt_pekerjaan()

class koneksi1(osv.osv):
    _name='hr_recruit.kon1'
    
    _columns={        
        'applicant_id':fields.many2one('hr.applicant',),
        'employee_id':fields.many2one('hr.employee','Nama'),
        'job_id':fields.related('employee_id','job_id',type='many2one',relation='hr.job',string='Jabatan',readonly=True),
        'alamat':fields.text('Alamat'),
        'telepon':fields.char('Telepon',25),
            }
koneksi1()

class koneksi2(osv.osv):
    _name='hr_recruit.kon2'
    
    _columns={        
        'applicant_id':fields.many2one('hr.applicant'),
        'name':fields.char('Nama',60),
        'alamat':fields.text('Alamat'),
        'jabatan':fields.char('Jabatan',30),
        'telepon':fields.char('Telepon',25),
            }
koneksi2()


class interview(osv.osv):
    _name='hr_recruit.interview'

    _columns={
        'applicant_id':fields.many2one('hr.applicant'),
        #'hr_applicant_id':fields.many2one('hr.applicant'),
        'stage_id':fields.related('applicant_id','stage_id',type='many2one',relation='hr.recruitment.stage',string='Stage'),
        'kesimpulan':fields.selection([('Dapat_Diterima','Dapat Diterima'),('Untuk_Dicadangkan','Untuk Dicadangkan'),('Ditolak','Ditolak')],'Kesimpulan'),        
        'note':fields.text('Komentar/Catatan'),
        'tgl_int':fields.date('Tanggal Interview'), 
        'nilai_interview_ids':fields.one2many('hr_recruit.nilai_interview','interview_id','Penilaian'),              

            }
interview()

class nilai_interview(osv.osv):
    _name='hr_recruit.nilai_interview'
    
    _columns={
            'interview_id':fields.many2one('hr_recruit.interview','Interview'),
            'name':fields.many2one('hr_recruit.aspek','Aspek yang Dinilai'),
            'hasil':fields.selection([('Kurang_Sekali','Kurang Sekali'),('Kurang','Kurang'),('Sedang','Sedang'),('Baik','Baik'),('Baik_Sekali','Baik Sekali')],'Hasil Penilaian'),
            'note2':fields.text('Keterangan'),
            }
nilai_interview() 
  
class aspek(osv.osv):
    _name='hr_recruit.aspek'
    
    _columns={
        'name':fields.char('Aspek Yang Dinilai',50,required=True),
        }
aspek()           

class kota(osv.osv):
    _name='hr_recruit.kota'
    
    _columns={
        'name':fields.char('Nama Kota',50),
        }
kota()

class agama(osv.osv):
    _name='hr_recruit.agama'
        
    _columns={
        'name':fields.char('Agama',12),
        }
agama()                    

class issued(osv.osv):
    _name='hr_recruit.issued'
        
    _columns={
        'name':fields.char('Dikeluarkan Oleh',50),
        }
issued()

class result(osv.osv):
    _name='hr_recruit.result'
        
    _columns={
        'name':fields.char('Result',50),
        }
result()  

class gelar(osv.osv):
    _name='hr_recruit.gelar'
        
    _columns={
        'name':fields.char('Gelar',50),
        }
gelar()

class b_lisan(osv.osv):
    _name='hr_recruit.b_lisan'
        
    _columns={
        'name':fields.char('Lisan',20),
        }
b_lisan()

class b_tulisan(osv.osv):
    _name='hr_recruit.b_tulisan'
        
    _columns={
        'name':fields.char('Tulisan',20),
        }
b_tulisan()

class hr_survey(osv.osv):
    _name='hr.survey'
    
    _columns={
        'name':fields.many2one('survey','Title'),
        'applicant_id':fields.many2one('hr.applicant'),
        } 

class survey(osv.osv):
    _name="survey"
    _inherit="survey"
    
    def survey_close(self, cr, uid, ids, arg):
        self.write(cr, uid, ids, {'state': 'close', 'date_close': strftime("%Y-%m-%d %H:%M:%S"),'job_id' : False })
        return True
    
    _columns = {
        'name': fields.related('job_id',type="many2one", 
            relation="hr.job", string="Job Name", readonly=True),
        'job_id' : fields.many2one('hr.job', 'Job Name',required=True),
        'applicant_id':fields.many2one('hr.applicant'),
        'tgl_int':fields.date('Tanggal Interview')
        
    }
survey()
