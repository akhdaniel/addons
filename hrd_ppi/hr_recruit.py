from openerp.osv import fields, osv
#from openerp.addons.base_status.base_stage import base_stage
from datetime import date
from time import strptime

PERMOHONAN_STATES =[
	('draft','Draft'),
	('verify','Verify'),
	('in_progress','In Progress')]
class permohonan_recruit(osv.osv):
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
        'pendidikan_id': fields.many2one('hr.recruitment.degree', 'Pendidikan'),
        'jurusan_ids':fields.one2many('hr_recruit.jurusan','permohonan_recruit_id','jurusan'),
        'pengalaman':fields.integer('Pengalaman (min-th)'),
        'usia':fields.integer('Usia (max)'),
        'sts_prk':fields.selection([('Belum_Menikah','Belum Menikah'),('Menikah','Menikah')],'Status Pernikahan'),
        'kelamin':fields.selection([('male','Male'),('female','female'),('male/female','Male / Female')],'Jenis Kelamin'),
        'wkt_pemohon':fields.date('Permintaan Pemohon'),
        'wkt_rekruter':fields.date('Kesanggupan Rekruter'),
        'catatan':fields.char('Realisasi Penempatan',128),
        'catatan2':fields.text('Catatan'),
        'state': fields.selection(PERMOHONAN_STATES, 'Status', readonly=True, help="Gives the status of the recruitment."),  
        'user_id' : fields.many2one('res.users', 'Creator','Masukan User ID Anda'),      
                }
    _defaults = {
        'state': PERMOHONAN_STATES[0][0],
        'user_id': lambda obj, cr, uid, context: uid,
                 }  
            
permohonan_recruit()

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
        'permohonan_recruit_id':fields.many2one('hr.job'),
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
                    prod_ids.append((0,0, {'name':pr.name,'jenis_kel':pr.jenis_kel,'kota_id':pr.kota_id.id,'tgl_lahir':pr.tgl_lahir,'pendidikan':pr.pendidikan,'pekerjaan':pr.pekerjaan}))
                le=self.pool.get('hr_recruit.suskel2')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids1=[]   
                for pr in lele:
                    prod_ids1.append((0,0, {'susunan':pr.susunan,'name':pr.name,'jenis_kel':pr.jenis_kel,'kota_id':pr.kota_id.id,'tgl_lahir':pr.tgl_lahir,'pendidikan':pr.pendidikan,'pekerjaan':pr.pekerjaan}))          
                le=self.pool.get('hr_recruit.rwt_pend')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids2=[]   
                for pr in lele:
                    prod_ids2.append((0,0, {'name':pr.name,'jurusan':pr.jurusan,'tempat':pr.tempat,'tahun':pr.tahun,'ijazah':pr.ijazah})) 
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
                    prod_ids4.append((0,0, {'no':pr.no,'name':pr.name,'tahun':pr.tahun,'jabatan':pr.jabatan,'gaji':pr.gaji,'alasan':pr.alasan})) 
                le=self.pool.get('hr_recruit.kon1')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids5=[]   
                for pr in lele:
                    prod_ids5.append((0,0, {'employee_id':pr.employee_id.id,'alamat':pr.alamat,'jabatan':pr.jabatan})) 
                le=self.pool.get('hr_recruit.kon2')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids6=[]   
                for pr in lele:
                    prod_ids6.append((0,0, {'name':pr.name,'alamat':pr.alamat,'jabatan':pr.jabatan}))  
                emp_id = hr_employee.create(cr,uid,{'name': applicant.partner_name or applicant.name,
                                                     'job_id': applicant.job_id.id,
                                                     'department_id': applicant.department_id.id,
                                                     'gender':applicant.kelamin,
                                                     'kota_id' : applicant.kota_id.id,
                                                     'birthday' : applicant.tgl_lahir,
                                                     'agama_id' : applicant.agama_id.id,
                                                     'country_id' : applicant.country_id.id,
                                                     'ktp' : applicant.ktp,
                                                     'dikeluarkan' : applicant.dikeluarkan,
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
                                                     'koneksi2_ids':prod_ids6
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
        #job
        partner=self.pool.get('hr.job')  
        pero=partner.search(cr,uid,[('name','=',ap_jb)])     
        per=partner.browse(cr,uid,pero,context)[0] 
        job_name=per.name     
        job_umr=per.usia
        job_pend=per.pendidikan_id.id
        job_kelamin =per.kelamin
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
            stage=line.name
            if stage == 'Refused' :
                stgs=line.id
                if ap_umr > job_umr or ap_pend != job_pend or job_kelamin != ap_kelamin :                                                 
                    return self.write(cr,uid,ids,{'stage_id': stgs},context=context) 
            if stage == 'Wawancara Pertama' :
                stg=line.id
                if ap_umr <= job_umr and ap_pend == job_pend :
                    if job_kelamin == 'male/female' or job_kelamin == ap_kelamin :
                        for jjr in jur:
                            perok=jjr.name.id
                            if perok == ap_jurusan :                                
                                return self.write(cr,uid,ids,{'stage_id': stg},context=context)                         
        return self.write(cr,uid,ids,{'stage_id': stgs},context=context)

    def interview(self,cr, uid,ids, context):
        import pdb;pdb.set_trace()
        #applicant=vals(cr,uid,['partner_name'],context)
        appl=self.browse(cr,uid,ids)[0]
        applicant=appl.partner_name
        interv=self.pool.get('hr_recruit.interview')
        inter=interv.search(cr,uid,[('applicant_id','=',applicant)])
        inte=interv.browse(cr,uid,inter,context)[0]
        for app in inte.interview_ids:
            kesimpulan = app.kesimpulan     
        return 
        
    #def write(self,cr, uid, ids, vals, context):
        #vals=self.interview(cr, uid, vals, context)
        #result= super(applicant,self).write (cr, uid,ids, vals, context)
        #return result 
                    
    
    _columns= {
        'kelamin':fields.selection([('male','Male'),('female','Female')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'age': fields.function(_compute_age, type='integer', obj='hr.applicant', method=True, store=False, string='Usia (Thn)', readonly=True),
        'agama_id':fields.many2one('hr_recruit.agama','Agama'),
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
        'status':fields.selection([('single','Single'),('menikah','Menikah'),('duda','Duda'),('janda','Janda')],'Status Pernikahan'),
        'sjk_tanggal':fields.date('Sejak Tanggal'),  
        'survey_id': fields.many2one('survey', 'Interview Form', help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job"),      
        'susunan_kel1_ids':fields.one2many('hr_recruit.suskel1','applicant_id','Susunan Keluarga'),
        'susunan_kel2_ids':fields.one2many('hr_recruit.suskel2','applicant_id','Susunan Keluarga'),
        'rwt_pend_ids':fields.one2many('hr_recruit.rwt_pend','applicant_id','Riwayat Pendidikan'),
        'bahasa_ids':fields.one2many('hr_recruit.bahasa','applicant_id','Bahasa'),
        'rwt_krj_ids':fields.one2many('hr_recruit.rwt_krj','applicant_id','Rwayat Pekerjaan'),
        'koneksi1_ids':fields.one2many('hr_recruit.kon1','applicant_id','Koneksi Internal'),
        'koneksi2_ids':fields.one2many('hr_recruit.kon2','applicant_id','Koneksi Eksternal'),
        'interview_ids':fields.one2many('hr_recruit.interview','applicant_id','Mulai Interview'),
        'jurusan_id':fields.many2one('hr_recruit.jurusan_detail','Jurusan'),
        'result_id':fields.many2one('hr_recruit.result','Result'),
        }
hr_applicant()

class susunan_keluarga1(osv.osv):
    _name='hr_recruit.suskel1'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),
        'name':fields.char('Nama',required=True),
        'jenis_kel':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'pendidikan':fields.char('Pendidikan',50),
        'pekerjaan':fields.char('Pekerjaan',60),
            }
susunan_keluarga1()

class susunan_keluarga2(osv.osv):
    _name='hr_recruit.suskel2'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),
        'susunan':fields.selection([('Ayah','Ayah'),('Ibu','Ibu'),('anak1','Anak ke-1'),('anak2','Anak ke-2'),('anak3','Anak ke-3'),('anak4','Anak ke-4'),('anak5','Anak ke-5'),('anak6','Anak ke-6')],'Nama Susunan Keluarga'),
        'name':fields.char('Nama',required=True),
        'jenis_kel':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'pendidikan':fields.char('Pendidikan',50),
        'pekerjaan':fields.char('Pekerjaan',60),
            }
susunan_keluarga2()   

class rwt_pendidikan(osv.osv):
    _name='hr_recruit.rwt_pend'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),
        'name':fields.char('Nama Sekolah',128,required=True),
        'jurusan':fields.char('Jurusan',50),
        'tempat':fields.char('Tempat',60),
        'tahun':fields.char('Dari-Sampai tahun',11),
        'ijazah':fields.char('Ijazah yang Diperoleh',100),
            }
rwt_pendidikan()      

class bahasa(osv.osv):
    _name='hr_recruit.bahasa'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant','Applicant'),        
        'name':fields.char('Nama',30,required=True),
        'tulis':fields.selection([('Sedang','Sedang'),('Cukup_Baik','Cukup Baik'),('Baik','Baik'),('Sangat_Baik','Sangat Baik')],'Tertulis'),
        'lisan':fields.selection([('Sedang','Sedang'),('Cukup_Baik','Cukup Baik'),('Baik','Baik'),('Sangat_Baik','Sangat Baik')],'Lisan'),
            }
bahasa()    

class rwt_pekerjaan(osv.osv):
    _name='hr_recruit.rwt_krj'
    
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
    _name='hr_recruit.kon1'
    
    _columns={        
        'applicant_id':fields.many2one('hr.applicant',),
        'employee_id':fields.many2one('hr.employee','Nama'),
        'alamat':fields.text('Alamat/Telepon'),
        'jabatan':fields.char('Jabatan',30),
            }
koneksi1()

class koneksi2(osv.osv):
    _name='hr_recruit.kon2'
    
    _columns={        
        'applicant_id':fields.many2one('hr.applicant'),
        'name':fields.char('Nama',60),
        'alamat':fields.text('Alamat/Telepon'),
        'jabatan':fields.char('Jabatan',30),
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


