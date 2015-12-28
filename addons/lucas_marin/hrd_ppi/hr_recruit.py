from openerp.osv import fields, osv
from osv import osv, fields
from datetime import date
from datetime import datetime
from time import strptime
from time import strftime
from openerp.osv.osv import object_proxy
from openerp.tools.translate import _

AVAILABLE_STATES = [
    ('submit', 'Baru'),
    ('approval', 'Proses Department'),
    ('approval1', 'Aproval HR'),
    ('approval2', 'Approval Presdir'),
    ('in_progress', 'Sedang Dalam Proses'),
]

#PERMOHONAN_STATES =[
#	('draft','Draft'),
#	('submit','Submit'),
#	('verify','Verify'),
#	('in_progress','In Progress')]

class hr_recruitment_stage(osv.osv):
    """ Aproval of Permohonan Recrutiment """
    _name = "hr.job.approval"
    _description = "Approval"
    _order = 'sequence'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of stages."),
        'job_id':fields.many2one('hr.job', 'Specific to a Job', help="Jika ada proses aproval tambahan pada salah satu bidang pekerjaan."),
        'jenis_permohonan':fields.selection([('Bulanan','Bulanan'),('Harian','Harian'),('Manager_dep','manager_dep'),('manager_hr','manager HR')],string='Jenis Permohonan'),
        'state': fields.selection(AVAILABLE_STATES, 'Status', required=True, help="The related status for the stage. The status of your document will automatically change according to the selected stage. Example, a stage is related to the status 'Close', when your document reach this stage, it will be automatically closed."),
        'fold': fields.boolean('Sembunyikan Jika Sudah Tidak Terpakai', help="Jika Aproval Sudah Tidak Terpakai Maka Centang View Ini."),
        'requirements': fields.text('Requirements'),
    }
    _defaults = {
        'sequence': 1,
        'state': 'submit',
        'fold': False,
    }
    _sql_constraints = [('sequence_uniq', 'unique(sequence)','Sequence Tidak Boleh Sama')]

class permohonan_recruit(osv.osv):
    _name = 'hr.job'
    _inherit = 'hr.job'
    
    #def action_draft(self,cr,uid,ids,context=None): 
    #    self.write(cr,uid,ids,{'status_rec':'new'},context=context)
   # 	return self.write(cr,uid,ids,{'state':PERMOHONAN_STATES[0][0]},context=context)

    def action_submit(self,cr,uid,ids,context=None): 
        #function for number automatic
        objk = self.browse(cr,uid,ids)[0]
        day_now = datetime.now()
        name = objk.jenis_permohonan
        stg3=objk.state.sequence
        partner=self.pool.get('hr.job.approval')  
        pero=partner.search(cr,uid,['|',('jenis_permohonan','=',False),('jenis_permohonan','=',name)])     
        pers=partner.browse(cr,uid,pero,context)
        st= 1000
        # emp_obj = self.pool.get('hr.employee')
        # emp_src = emp_obj.search(cr,uid,[('user_id','=',uid)])
        # emp_brw = emp_obj.browse(cr,uid,emp_src)
        # dep_obj = self.pool.get('hr.departmen')
        # employees = []
        # for emps in emp_brw :
        #     import pdb;pdb.set_trace()
        #     cek = True
        #     dep = emps.department_id.id
        #     while cek == True :
        #         employees = dep
        #         dep = dept_obj.browse(cr,uid,dep).parent_id
        #         if dep == False :
        #             cek = False
        #     if objk.department_id.id not in employees :
        #         raise osv.except_osv(_('Peringatan!'), _('Anda Tidak Bisa Approval'))
        for line in pers: 
            stage=line.sequence
            if stg3 < stage and st > stage :
                stg=line.id   
                statuse=line.name                    
                self.write(cr,uid,ids,{'state': stg, 'states_id' : line.state},context=context)  
                st = stage
        obj = self.pool.get('hr.job')
        obj_src = obj.search(cr,uid,[])
        obj_brw = obj.browse(cr,uid,obj_src)
        no1 = 0
        for job in obj_brw :
            no = job.no_permohonan
            if no >= no1 :
                no1 = job.no_permohonan
        no_sum = no1 + 1
        self.write(cr,uid,ids,{'no_permohonan' : no_sum, 'wkt_pemohon' : day_now},context=context)
        #function for create laporan permintaan Recruitment
        #import pdb;pdb.set_trace()
        year =datetime.now().year
        obj_lap = self.pool.get('hr.lap_permintaan_karyawan')
        obj_lap.create(cr,uid,{
                    'dep' : objk.department_id.name,
                    'posisi': objk.name,
                    'jumlah' : objk.no_of_recruitment,
                    'wkt_penempatan' : objk.wkt_pemohon, 
                    'pengalaman' :objk.pengalaman,
                    'usia' : objk.usia,
                    'jenis_kelamin' : objk.kelamin,
                    'status' : objk.sts_prk,
                    'domisili' : objk.domisili_id.name,
                    'tahun' : year,
                    'no': no_sum,
                    'stat' : statuse
                    })
    	return True  	

    def action_verify(self,cr,uid,ids,context=None): 
        hasil=self.browse(cr,uid,ids)[0]
        name = hasil.jenis_permohonan
        stg3=hasil.state.sequence
        partner=self.pool.get('hr.job.approval')  
        pero=partner.search(cr,uid,['|',('jenis_permohonan','=',False),('jenis_permohonan','=',name)])     
        pers=partner.browse(cr,uid,pero,context)
        st= 1000
        for line in pers: 
            stage=line.sequence
            if stg3 < stage and st > stage :
                stg=line.id  
                stats = line.name                     
                self.write(cr,uid,ids,{'state': stg, 'states_id' : line.state},context=context)  
                st = stage
        lap_obj = self.pool.get('hr.lap_permintaan_karyawan')
        lap_src = lap_obj.search(cr,uid,[('no','=',hasil.no_permohonan)])
        for lap in lap_obj.browse(cr,uid,lap_src) :
            lap_obj.write(cr,uid,[lap.id],{'stat' : stats},context=context)
    	return True
 
    def action_in_progress(self,cr,uid,ids,context=None): 
        self.write(cr,uid,ids,{'status_rec':'filter'},context=context)
        obj = self.browse(cr,uid,ids)[0]
        department = obj.department_id.name
        date =obj.wkt_pemohon
        dates = datetime.strptime(date,"%Y-%m-%d").year
        jenis_per = obj.jenis_permohonan
        name = obj.jenis_permohonan
        stg3=obj.state.sequence
        partner=self.pool.get('hr.job.approval')  
        pero=partner.search(cr,uid,['|',('jenis_permohonan','=',False),('jenis_permohonan','=',name)])     
        pers=partner.browse(cr,uid,pero,context)
        st= 1000
        obj_brw = []
        for line in pers: 
            stage=line.sequence
            if stg3 < stage and st > stage :
                stg=line.id    
                stat = line.name                   
                self.write(cr,uid,ids,{'state': stg, 'states_id' : line.state},context=context)  
                st = stage
        #import pdb;pdb.set_trace()
        # if jenis_per == 'Bulanan' :
        #     objk = self.pool.get('hr.sumary_kebutuhan')
        #     obj_src = objk.search(cr,uid,[('tahun','=',dates),('dep','=',department),('bul_har','=',jenis_per)])
        #     obj_brw = objk.browse(cr,uid,obj_src)
        # elif jenis_per == 'Harian' :
        #     objk = self.pool.get('hr.sumary_kebutuhan_harian')
        #     obj_src = objk.search(cr,uid,[('tahun','=',dates),('dep','=',department),('bul_har','=',jenis_per)])
        #     obj_brw = objk.browse(cr,uid,obj_src)
        # if obj_brw ==[] :
        #     objk.create(cr,uid,{
        #             'tahun' : dates,
        #             'bul_har': jenis_per,
        #             'dep' : department,
        #             'jum_kebutuhan' : obj.no_of_recruitment, 
        #             })
        # else :
        #     for sumary in obj_brw :
        #         jum_sumary = sumary.jum_kebutuhan + obj.no_of_recruitment
        #         objk.write(cr,uid,[sumary.id],{'jum_kebutuhan': jum_sumary},context=context)
        # lap_obj = self.pool.get('hr.lap_permintaan_karyawan')
        # lap_src = lap_obj.search(cr,uid,[('no','=',obj.no_permohonan)])
        # for lap in lap_obj.browse(cr,uid,lap_src) :
        #     lap_obj.write(cr,uid,[lap.id],{'stat' : stat},context=context)
    	return True
    	
    def scroll_no(self, cr, uid, ids, no, args, context=None):
        res = []
        for x in range(15,51):
            res.append(x)
        return res

    def selesai(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids)[0]
        names = obj.name
        no = obj.no_permohonan
        lap_obj = self.pool.get('hr.lap_permintaan_karyawan')
        lap_src = lap_obj.search(cr,uid,[('no','=',obj.no_permohonan)])
        for lap in lap_obj.browse(cr,uid,lap_src) :
            lap_obj.write(cr,uid,[lap.id],{'stat' : 'selesai'},context=context)
        self.write(cr,uid,ids,{'state':1, 'states_id' : 'submit'},context=context)
        hr_pemi =self.pool.get('hr_pemenuhan')
        hr_pem_src = hr_pemi.search(cr,uid,[('jabatan','=',names),('no_pmintaan','=', no)])
        hr_pem_brw = hr_pemi.browse(cr,uid,hr_pem_src,context)
        for hr_pem in hr_pem_brw :
            hr_pemi.write(cr, uid, [hr_pem.id], {'status' : 'Done'}, context=context)
        return True

    def cancel(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids)[0]
        self.write(cr,uid,ids,{'state':1, 'states_id' : 'submit'},context=context)
        return True
    
    _columns= {
        'name': fields.char('Job Name', size=128, required=True, select=True,states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'kunci': fields.boolean(''),
        'jenis_permohonan':fields.selection([('Bulanan','Bulanan'),('Harian','Harian'),('Manager_dep','manager Dep'),('manager_hr','manager HR')],string='Jenis Permohonan',required=True,states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'no':fields.char('Nomor',20),
        'status_jabatan':fields.selection([('P','Pengganti'),('T','Tambahan'),('JB','Jabatan Baru')],string='Status',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'type_id': fields.many2one('hr.recruitment.degree', 'Pendidikan',required=True,states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'jurusan_ids':fields.one2many('hr_recruit.jurusan','permohonan_recruit_id','Jurusan',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'pengalaman':fields.integer('Pengalaman (min-th)',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'usia':fields.selection([('18','18'),('19','19'),('20','20'),('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31'),('32','32'),('33','33'),('34','34'),('35','35'),('36','36'),('37','37'),('38','38'),('39','39'),('40','40'),('41','41'),('42','42'),('43','43'),('44','44'),('45','45'),('46','46'),('47','47'),('48','48'),('49','49'),('50','50')],string='Usia (max)',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'sts_prk':fields.selection([('single','Single'),('menikah','Menikah')],string='Status Pernikahan',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'kelamin':fields.selection([('male','Male'),('female','Female'),('male/Female','Male / Female')],string='Jenis Kelamin',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'wkt_pemohon':fields.date('Permintaan Pemohon',required=True),
        'wkt_rekruter':fields.date('Kesanggupan Rekruter'),
        'catatan':fields.char('Realisasi Penempatan',128,states={'draft':[('readonly',True)], 'submit':[('readonly',True)]}),
        'catatan2':fields.text('Catatan'),
        #'state': fields.selection(AVAILABLE_STATES, 'Status', readonly=True, help="Gives the status of the recruitment."),  
        'user_id' : fields.many2one('res.users', 'Creator','Masukan User ID Anda'),    
        'survey_ids':fields.one2many('hr.survey1','job_id','Interview Form'),
        'survey_id': fields.many2one('survey', '', readonly=True, help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job"),     
        'domisili_id':fields.many2one('hr_recruit.kota','Domisili',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),    
        'tempat_lahir_id':fields.many2one('hr_recruit.kota','Tempat Lahir',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}), 
        'bol_name':fields.boolean('Nama Tugas',help="Hilangkan ceklist jika ingin filter tidak sesuai dengan aplikasi yang dilamar"),
        'bol_type_id':fields.boolean('Pendidikan'),
        'bol_jurusan_ids':fields.boolean('Jurusan'),
        'bol_pengalaman':fields.boolean('Pengalaman'),
        'bol_usia':fields.boolean('Usia'),
        'bol_sts_prk':fields.boolean('Status Pernikahan'),
        'bol_kelamin':fields.boolean('Jenis Kelamin'),
        'bol_domisili':fields.boolean('Domisili'),
        'bol_tempat_lahir_id':fields.boolean('Tempat Lahir'),
        'applicant_ids':fields.one2many('hr.applicant','app_id','Daftar Pelamar'), 
        'salary_proposed_botom_margin': fields.float('Standar Gaji Perusahaan', help="Batas range terendah"), 
        'salary_proposed_top_margin': fields.float('Standar Gaji Perusahaan', help="Batas range tertinggi"),   
        'no_of_recruitment': fields.float('Expected in Recruitment', help='Number of new employees you expect to recruit.',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'department_id': fields.many2one('hr.department', 'Department',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'no_permohonan' : fields.integer('No Permohonan',readonly=True),   
        'category_ids' : fields.char('aa'), 
        'divisi_id' : fields.many2one('hr.department','Divisi',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}), 
        'bagian_id' : fields.many2one('hr.department','Bagian',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'level_id' :fields.many2one('hr.level','Level',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),   
        'status_rec' : fields.selection([('new','new'),('filter','filter'),('execute','execute'),('in_progres','in progres'),('pending','pending')],readonly=True, string='Status Record'),  
        'state':fields.many2one ('hr.job.approval','Stage',domain="['&', ('fold', '=', False), '|', ('jenis_permohonan', '=', jenis_permohonan), ('jenis_permohonan', '=', False)]"),   
        'states_id':fields.char('Status'),  
            }

    _defaults = {
        #'state': PERMOHONAN_STATES[0][0],
        'user_id': lambda obj, cr, uid, context: uid,
        'bol_name':True,
        'bol_type_id':True,
        'bol_jurusan_ids':True,
        'bol_pengalaman':True,
        'bol_usia':True,
        'bol_sts_prk':True,
        'bol_kelamin':True, 
        'bol_domisili':True,  
        'bol_tempat_lahir_id':True,  
        'status_rec' : "new",
        'state' : 1,
        'states_id' : 'submit',
        #'no_permohonan' : lambda obj , cr , uid , context: obj.pool.get('ir.sequence').get(cr, uid, 'hr.job'),   
                 }  

    def onchange_department_id(self, cr, uid, ids, department_id):
        result={};result['divisi_id'] =False ;result['bagian_id']=False
        dept_obj = self.pool.get('hr.department')
        parentID = dept_obj.browse(cr,uid,department_id).parent_id
        if parentID : 
            result['divisi_id'] = parentID.id
        parent2ID = dept_obj.browse(cr,uid,parentID.id)
        if parentID.id : 
            result['bagian_id']=parent2ID.parent_id.id
        return {'value':result}
        
    def new_recruitment(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'status_rec':'filter'},context=context)
        hasil = self.browse(cr,uid,ids)[0]
        jbtn = hasil.name
        hr_pemi =self.pool.get('hr_pemenuhan')
        hr_pem_src = hr_pemi.search(cr,uid,[('jabatan','=',jbtn)])
        hr_pem_brw = hr_pemi.browse(cr,uid,hr_pem_src,context)
        for hr_pem in hr_pem_brw :
            if hr_pem.status == "pending" or hr_pem.status == "In Progres":
                hr_pemi.write(cr,uid,[hr_pem.id],{'status':"Done"},context=context) 
        hr_list_pem_bul = self.pool.get('hr.pemenuhan_kebutuhan')
        hr_list_pem_src = hr_list_pem_bul.search(cr,uid,[('jabatan','=',jbtn)])
        hr_list_pem_brw = hr_list_pem_bul.browse(cr,uid,hr_list_pem_src,context=context)
        for hr_list in hr_list_pem_brw :
            if hr_list.status_pemenuhan == "pending" or hr_list.status_pemenuhan == "In Process":
                hr_list_pem_bul.write(cr,uid,[hr_list.id],{'status_pemenuhan':'Done'},context=context)    
        return True

    def pending(self,cr,uid,ids,context=None):
        #import pdb;pdb.set_trace()
        hasil=self.browse(cr,uid,ids)[0]
        jbtn = hasil.name
        hr_pemi =self.pool.get('hr_pemenuhan')
        hr_pem_src = hr_pemi.search(cr,uid,[('jabatan','=',jbtn)])
        hr_pem_brw = hr_pemi.browse(cr,uid,hr_pem_src,context)
        for hr_pem in hr_pem_brw :
            if hr_pem.status == "In Progres" :
                hr_pemi.write(ce,uid,[hr_pem.id,{'status':'pending'}])
            if hr_pem.status == "pending" :
                self.write(cr,uid,ids,{'status_rec':'filter'},context=context)
            else :
                raise osv.except_osv(_('Warning!'),_('Status Calon Pelamar Masih In Progres'))
        return True

    def cancel_recruitment(self,cr,uid,ids,context=None):
        hasil=self.browse(cr,uid,ids)[0]
        jbtn = hasil.name
        hr_pemi =self.pool.get('hr_pemenuhan')
        hr_pem_src = hr_pemi.search(cr,uid,[('jabatan','=',jbtn)])
        hr_pem_brw = hr_pemi.browse(cr,uid,hr_pem_src,context)
        x = False
        for hr_pem in hr_pem_brw :
            if hr_pem.status == "pending" :
                hire = hr_pem.id
                x = True
            if hr_pem.status == "In Progres" :
                hr_pemi.write(cr,uid,[hr_pem.id],{'status':"Cancel Recruitment"},context=context)
        if x == True:
            hr_pemi.write(cr,uid,[hire],{'status':"Cancel Recruitment"},context=context)
        #function for list pemenuhan kebutuhan recruitment bulanan
        hr_list_pem_bul = self.pool.get('hr.pemenuhan_kebutuhan')
        hr_list_pem_src = hr_list_pem_bul.search(cr,uid,[('jabatan','=',jbtn)])
        hr_list_pem_brw = hr_list_pem_bul.browse(cr,uid,hr_list_pem_src,context=context)
        for hr_list in hr_list_pem_brw :
            if hr_list.status_penempatan == "Next Process" :
                hr_list_pem_bul.write(cr,uid,[hr_list.id],{'status_penempatan':'cancel Recruitment','status_pemenuhan':'Cancel Recruitment'},context=context)
        self.write(cr,uid,ids,{'status_rec':'filter'},context=context)
        partner=self.pool.get('hr.recruitment.stage')  
        pero=partner.search(cr,uid,[])     
        pers=partner.browse(cr,uid,pero,context)  
        obj_app=self.pool.get('hr.applicant')
        for exe in hasil.applicant_ids:
            #x = x + 1
            sta_id = exe.stat - 1
            obj_app.write(cr,uid,[exe.id],{'stat':sta_id})
            for ini in pers :
                asu = ini.sequence
                if asu == 0 :
                    asu = ini.id                  
                    obj_app.write(cr,uid,[exe.id for exe in hasil.applicant_ids],{'stage_id':asu})
        return True

    def cici(self,cr, uid,ids, context=None): 
        per=self.browse(cr,uid,ids,context)[0] 
        job_name=per.name     
        job_umr=per.usia
        job_pend=per.type_id.id
        job_kelamin =per.kelamin
        job_pengalaman=per.pengalaman
        job_status=per.sts_prk  
        job_state=per.state
        job_domisili_id=per.domisili_id.id
        job_tempat_lahir_id=per.tempat_lahir_id.id
        job_jurusan_ids=per.jurusan_ids
        job_b_name=per.bol_name
        job_b_pend=per.bol_type_id
        job_b_umr=per.bol_usia
        job_b_kelamin=per.bol_kelamin
        job_b_pengalaman=per.bol_pengalaman
        job_b_status=per.bol_sts_prk
        job_b_jurusan_ids=per.bol_jurusan_ids
        job_b_domisili=per.bol_domisili
        job_b_tempat_lahir_id=per.bol_tempat_lahir_id
        #import pdb;pdb.set_trace()

        partner=self.pool.get('hr.recruitment.stage')  
        pero=partner.search(cr,uid,[])     
        pers=partner.browse(cr,uid,pero,context)[0]
        
        #jurusan
        jurusan=self.pool.get('hr_recruit.jurusan')        
        jur_id=jurusan.search(cr, uid,[('permohonan_recruit_id','=',job_name)])       
        jur=jurusan.browse(cr,uid,jur_id,context)
   
        filt=[('stage_id','=','Initial Qualification')]
        partner=self.pool.get('hr.applicant') 

        perok=partner.search(cr,uid,[('app_id','=',job_name),(pers.id,'=',1)])
        for tt in partner.browse(cr,uid,perok):
            partner.write(cr,uid,perok,{'app_id': False},context=context)
        
        if job_b_pend :
            filt.append(('type_id','=',job_pend))
        if job_b_umr:
            filt.append(('age','<=',job_umr))
        if job_b_kelamin:
            filt.append(('kelamin','=',job_kelamin))
        if job_b_pengalaman:
            filt.append(('pengalaman','>=',job_pengalaman))
        if job_b_status:
            filt.append(('status','=',job_status)) 
        if job_b_domisili:
            filt.append(('kab_id','=',job_domisili_id))  
        if job_b_tempat_lahir_id:
            filt.append(('kota_id','=',job_tempat_lahir_id))  
           
        if job_b_jurusan_ids:
            if len(job_jurusan_ids) == 1:
                filt.append(('jurusan_id','=',job_jurusan_ids[0].name.id))
            elif len(job_jurusan_ids) > 1: 
                A = []
                for xx in job_jurusan_ids:
                    A.append(xx.name.id)
                filt.append(('jurusan_id','in',A))
        pero=partner.search(cr,uid,filt)
        if job_b_name == False:
            for xux in partner.browse(cr,uid,pero): 
                umr = int(job_umr)
                if xux.age <= umr :
                    partner.write(cr,uid,[xux.id],{'app_id':per.id,'dep_app':per.department_id.id},context=context)
        elif job_b_name:
            ada = partner.browse(cr,uid,pero)
            for rr in ada:
                if rr.job_id.name==job_name :
                    partner.write(cr,uid,[rr.id],{'app_id': rr.job_id.id,'dep_app':rr.department_id.id},context=context)                              
        self.write(cr,uid,ids,{'status_rec':'execute'},context=context)                                                                                                                                        
        return True  

    def execute(self,cr, uid,ids, context=None):
        hasil=self.browse(cr,uid,ids,context)[0] 
        execute = hasil.applicant_ids
        if execute == [] :
            raise osv.except_osv(_('Peringatan!'),_('Pelamar Tidak Boleh Kosong.'))
        job_applicant_ids=hasil.applicant_ids[0]    
        obj_app=self.pool.get('hr.applicant')
        hasil_app=obj_app.browse(cr,uid,ids,context)[0]
        no_per = hasil.no_permohonan
        partner=self.pool.get('hr.recruitment.stage')  
        pero=partner.search(cr,uid,[])     
        pers=partner.browse(cr,uid,pero,context)
        year =str(datetime.now().year)
        hr_status = self.pool.get('hr.seleksi_pelamar')
        values=False
        x = 0
        n = 1000
        for ini in pers :
                asu = ini.sequence
                if asu > 0 and asu < n :
                    n = ini.sequence  
                    nn = ini.id
        for exe in hasil.applicant_ids:
            x += 1
            stat_ids = exe.stat + 1
            obj_app.write(cr,uid,[exe.id],{'stat':stat_ids})                  
            obj_app.write(cr,uid,[exe.id],{'stage_id':nn})
        for exe in hasil.applicant_ids:
            values = hr_status.create(cr,uid,{
                    'applicant_id' :exe.id,
                    'nama': exe.partner_name,
                    'pendidikan': exe.type_id.name,
                    'jurusan' : exe.jurusan_id.name,
                    'tgl_lahir' : exe.tgl_lahir,
                    'usia': exe.age,
                    'sumber': exe.source_id.name,
                    'ref' : exe.ref,
                    'department' : exe.department_id.name,
                    'jabatan' :exe.job_id.name,
                    'ref_jab':exe.app_id.name,
                    'tahun' : year,
                    'stat' : exe.stat,
                    })
        obj1 = self.browse(cr,uid,ids)[0]
        year = str(datetime.now().year)
        mont = str(datetime.now().month)
        day = str(datetime.now().day)
        date = mont + '/' + day + '/' + year 
        hr_status = self.pool.get('hr_pemenuhan')
        #for exe in hasil.applicant_ids:
        values = hr_status.create(cr,uid,{
                'no_pmintaan' : obj1.no_permohonan,
                'tgl_permintaan' : obj1.wkt_pemohon,
                'department' : obj1.department_id.name,
                'jabatan' : obj1.name,
                'jml_prmintaan' : obj1.no_of_recruitment,
                'jml_kandidat' : x,
                'status' : 'In Progres',
                })
        #function for list pemenuhan recruitment
        hr_status = self.pool.get('hr.pemenuhan_kebutuhan')
        values = hr_status.create(cr,uid,{
                'bul_har' : obj1.jenis_permohonan,
                'div' : obj1.divisi_id.name,
                'dept' : obj1.department_id.name,
                'bagian' : obj1.bagian_id.name,
                'jabatan' : obj1.name,
                'level' : obj1.level_id.name,
                'tgl_permohonan' : obj1.wkt_pemohon,
                'jumlah_kebutuhan' : obj1.no_of_recruitment,
                'status_pemenuhan' : "In Process",
                'kekurangan_pmenuhan' : obj1.no_of_recruitment,
                })
        self.write(cr,uid,ids,{'status_rec':'in_progres'},context=context)
        hr_monitor = self.pool.get('hr.monitoring_recruitment')
        for exe in hasil.applicant_ids:
            value = hr_monitor.create(cr,uid,{
                'name' : exe.partner_name,
                'dep'  : obj1.department_id.name,
                'test1_hrd' : 'Not Yet',
                'test2_hrd' : 'Not Yet',
                'test1_usr' : 'Not Yet',
                'test2_usr' : 'Not Yet',
                'approval' : 'Not Yet',
                'tes_kesehatan' : 'Not Yet',
                'status' : 'open'
                })
        years = str(datetime.now().year)
        hr_sumary = self.pool.get('hr.sumary_monitoring')
        hr_sumary_src = hr_sumary.search(cr,uid,[('tahun','=',years),('dep','=',obj1.department_id.name,)])
        hr_sumary_brw = hr_sumary.browse(cr,uid,hr_sumary_src)
        x = 0
        if hr_sumary_brw == [] :
            for exe in hasil.applicant_ids:
                x = x + 1
            value = hr_sumary.create(cr,uid,{
                'dep'  : obj1.department_id.name,
                'qty' : x,
                'test1' : x,
                'tahun' : years,
                    })
        else :
            for exe in hasil.applicant_ids:
                x = x + 1
            for xxx in hr_sumary_brw :
                qty = xxx.qty + x
                test = xxx.test1 + x
                hr_sumary.write(cr,uid,[xxx.id],{'qty':qty,'test1':test},context=context)
        return True  

    def _check_sal(self, cr, uid, ids):
        for sal in self.browse(cr, uid, ids):
            sal_src = self.search(cr, uid, [('salary_proposed_botom_margin', '>', sal.salary_proposed_top_margin), ('salary_proposed_top_margin', '<', sal.salary_proposed_botom_margin)])
            if sal_src:
                return False
        return True      
            
    _constraints = [(_check_sal, 'Standar gaji max tidak boleh lebih kecil dari standar gaji min!', ['salary_proposed_botom_margin','salary_proposed_top_margin']),]

permohonan_recruit()

class divisi(osv.osv):
    _name ='hr.divisi'

    _columns = {
        'name' : fields.char('Divisi'), 
    }
divisi()

class bagian(osv.osv):
    _name ='hr.bagian'

    _columns = {
        'name' : fields.char('Bagian'), 
    }
divisi()

class level(osv.osv):
    _name = 'hr.level'

    _columns = {
        'name' : fields.char('Level')
    }

class hr_survey(osv.osv):
    _name='hr.survey'
    
    _columns= {
        'surveys_id' :fields.many2one('survey', 'Interview Form'),  
        'jobs_id' : fields.many2one('hr.job','job'),  
        'applicant_id':fields.many2one('hr.applicant'),
        }
hr_survey()

class hr_survey1(osv.osv):
    _name='hr.survey1'
    
    _columns= {
        'surveys_id' :fields.many2one('survey', 'Interview Form'),  
        'job_id' : fields.many2one('hr.job'),  

        }
hr_survey1()

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
        'bidang_id':fields.many2one('hr_recruit.bidang','Bidang'),
        'name':fields.char("Jurusan",required=True),       
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
                    prod_ids3.append((0,0, {'name':pr.name.id,'tulis':pr.tulis.id,'lisan':pr.lisan.id})) 
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
                    prod_ids5.append((0,0, {'employee_id':pr.employee_id.name,'alamat':pr.Departmen_id.name,'job_id':pr.job_id.id,'telepon':pr.telepon})) 
                le=self.pool.get('hr_recruit.kon2')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids6=[]
                for pr in lele:   
                    prod_ids6.append((0,0, {'name':pr.name,'alamat':pr.alamat,'jabatan':pr.jabatan,'telepon':pr.telepon}))  
                emp_id = hr_employee.create(cr,uid,{'name': applicant.partner_name or applicant.name,
                                                     'job_id': applicant.app_id.id,
                                                     'department_id' : applicant.dep_app.id,
                                                     'gender':applicant.kelamin,
                                                     'place_of_birth' : applicant.kota_id.name,
                                                     'birthday' : applicant.tgl_lahir,
                                                     'agama' : applicant.agama_id.id,
                                                     'country_id' : applicant.country_id.id,
                                                     'jenis_id': applicant.jenis_id,
                                                     'ktp' : applicant.ktp,
                                                     'kab_id' : applicant.kab_id.id,
                                                     'kab_id2' : applicant.kab_id2.id,
                                                     'tgl_keluar_ktp' : applicant.tgl_keluar_ktp,
                                                     'tgl_berlaku' : applicant.tgl_berlaku,
                                                     'sim' : applicant.sim,
                                                     'tgl_keluar_sim' : applicant.tgl_keluar_sim,
                                                     'type_id':applicant.type_id.id,
                                                     'jurusan_id':applicant.jurusan_id.id,
                                                     'pt_id':applicant.pt_id.id,
                                                     'result_id':applicant.result_id.id,
                                                     'alamat1' : applicant.alamat1,
                                                     'prov_id':applicant.prov_id.id,
                                                     'kab_id':applicant.kab_id.id,
                                                     'kec_id':applicant.kec_id.id,
                                                     'prov_id2':applicant.prov_id2.id,
                                                     'kab_id2':applicant.kab_id2.id,
                                                     'kec_id2':applicant.kec_id2.id,
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
                                                     'blood' : applicant.blood,
                                                     'kodepos' :applicant.kode1,
                                                     'kodepos1':applicant.kode2,
                                                     'country_id1':applicant.country_id1.id,
                                                     'country_id2':applicant.country_id2.id,
													 'bid_id':applicant.bidang_id.id,
                                                     'wage':applicant.salary_proposed,
                                                     'kelamin':applicant.kelamin,
                                                     'marital':applicant.status,
                                                     'mobile_phone':applicant.partner_phone,
                                                     'gol_id':applicant.empgol_id.id,
                                                     'work_location2':applicant.lokasi_id,
                                                     'ptkp_id':applicant.ptkp.id,
                                                     'fingerprint_code': applicant.fingerprint_code2,
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
        #function for record status pemenuhan recruitment
        objk = self.browse(cr,uid,ids)[0]
        jbtn = objk.app_id.name
        hr_pemi =self.pool.get('hr_pemenuhan')
        hr_pem_src = hr_pemi.search(cr,uid,[('jabatan','=',jbtn)])
        hr_pem_brw = hr_pemi.browse(cr,uid,hr_pem_src,context)
        year = str(datetime.now().year)
        mont = str(datetime.now().month)
        day = str(datetime.now().day)
        date = mont + '/' + day + '/' + year 
        for hr_pem in hr_pem_brw :
            jml = hr_pem.jml_diterima + 1
            if hr_pem.status == "In Progres" : 
                hr_pemi.write(cr, uid, [hr_pem.id], {'per_masuk':date,'jml_diterima': jml }, context=context)  
        hr_pem_keb = self.pool.get('hr.pemenuhan_kebutuhan')
        hr_pem_keb_src = hr_pem_keb.search(cr,uid,[('status_penempatan','=','Next Process'),('jabatan','=',jbtn)])
        hr_pem_keb_brw = hr_pem_keb.browse(cr,uid,hr_pem_keb_src,context=context)
        for hhh in hr_pem_keb_brw :
            hr_pem_keb.write(cr,uid,[hhh.id],{'status_penempatan':'Done'})
        bul_har = objk.app_id.jenis_permohonan
        dep = objk.app_id.department_id.name
        date = objk.app_id.wkt_pemohon
        year = datetime.strptime(date,"%Y-%m-%d").year
        sum_keb = self.pool.get('hr.sumary_kebutuhan')
        obj_src_sum_keb = sum_keb.search(cr,uid,[('tahun','=',year),('dep','=',dep),('bul_har','=',bul_har)])
        obj_brw_sum_keb = sum_keb.browse(cr,uid,obj_src_sum_keb)
        for sumary in obj_brw_sum_keb :
            jum = sumary.jum_terpenuhi + 1
            sum_keb.write(cr,uid,[sumary.id],{'jum_terpenuhi':jum},context=context)
        return True

    def holiday(self, cr,uid,ids,vals,context=None):
        val='validate'
        obj = self.pool.get('hr.holidays')        
        src = obj.search(cr,uid,[('state','=',val)])
        brw = obj.browse(cr,uid,src)
        tahun = datetime.now().year
        obj_now = self.browse(cr,uid,ids)[0]
        lokasi = obj_now.lokasi_id
        obj_emp = self.pool.get('hr.employee')
        obj_src = obj_emp.search(cr,uid,[('name','=',obj_now.partner_name)])
        obj_brw = obj_emp.browse(cr,uid,obj_src)[0]
        partner = obj_brw.name
        leave_ids=[]
        for holiday in brw :
            dates = holiday.date_from
            year = datetime.strptime(dates,'%Y-%m-%d %H:%M:%S').year
            if tahun == year and holiday.lokasi_id == lokasi and holiday.type == 'remove' :
                vali = {
                        'name': holiday.name,
                        'type': holiday.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': holiday.holiday_status_id.name,
                        'date_from': holiday.date_from,
                        'date_to': holiday.date_to,
                        'notes': holiday.notes,
                        'number_of_days_temp': holiday.number_of_days_temp,
                        'parent_id': holiday.id,
                        'employee_id': partner
                    }
                leave_ids.append(self.create(cr, uid, vali, context=None))
                wf_service = netsvc.LocalService("workflow")
                for leave_id in leave_ids:
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        return True
    '''
    def close(self, cr, uid, ids, vals, context=None):
        """for cancel recruitment
        """
        hasil=self.browse(cr,uid,ids)[0]
        jbtn = hasil.app_id.name
        hr_pemi =self.pool.get('hr_pemenuhan')
        hr_pem_src = hr_pemi.search(cr,uid,[('jabatan','=',jbtn)])
        hr_pem_brw = hr_pemi.browse(cr,uid,hr_pem_src,context)
        for hr_pem in hr_pem_brw :
            if hr_pem.status == "In Proggres" :
                hr_pemi.write(cr,uid,[hr_pem.id],{'status':"Close"})
        #function for list pemenuhan kebutuhan recruitment bulanan
        hr_list_pem_bul = self.pool.get('hr.pemenuhan_kebutuhan')
        hr_list_pem_src = hr_list_pem_bul.search(cr,uid,[('jabatan','=',jbtn)])
        hr_list_pem_brw = hr_list_pem_bul.browse(cr,uid,hr_list_pem_src,context=context)
        for hr_list in hr_list_pem_bul :
            if hr_list.status_pemenuhan == "In Process" :
                hr_list_pem_bul.write(cr,uid,[hr_list.id],{'status_pemenuhan','=','Cancel Recruitment'})
        res = super(hr_applicant, self).case_cancel(cr, uid, ids, context)
        self.write(cr, uid, ids, {'probability': 0.0})
        return res 
    '''
    def case_cancel(self, cr, uid, ids,vals, context=None):
        """Overrides cancel for crm_case for setting probability
        """
        hasil=self.browse(cr,uid,ids)[0]
        names = hasil.partner_name
        stat = hasil.stat - 1
        hr_status = self.pool.get('hr.seleksi_pelamar')
        hr_search = hr_status.search(cr,uid,[('nama','=',names),('stat','=',stat)])
        hr_brws = hr_status.browse(cr,uid,hr_search)[0]
        values=False
        for men in hasil.meeting_ids :
            date = men.date
            if men.stat == 'interview1' :
                hr_status.write(cr, uid, [hr_brws.id], {'tgl_seleksi':date}, context=context)
            elif men.stat == "interview2" :
                hr_status.write(cr, uid, [hr_brws.id], {'tgl_seleksi1':date}, context=context)
        if hasil.stage_id.sequence == 2 :
            hr_status.write(cr, uid, [hr_brws.id], {'status': 'Ditolak','kehadiran':'Hadir','keputusan':'NOK'}, context=context)                
        elif hasil.stage_id.sequence == 90 :
            hr_status.write(cr, uid, [hr_brws.id], {'status1': 'Ditolak','kehadiran':'Hadir','keputusan':'NOK'}, context=context)
        res = super(hr_applicant, self).case_cancel(cr, uid, ids, context)
        self.write(cr, uid, ids, {'probability': 0.0})
        hr_monitor = self.pool.get('hr.monitoring_recruitment')
        hr_monitor_src = hr_monitor.search(cr,uid,[('name','=',hasil.partner_name)])
        hr_monitor_brw = hr_monitor.browse(cr,uid, hr_monitor_src)
        for monit in hr_monitor_brw :
            if monit.status == 'open' :
                if hasil.stage_id.sequence == 10 :
                    hr_monitor.write(cr,uid,[monit.id],{'test1_hrd':'failed','test2_hrd':'','test1_usr':'','test2_usr':'','approval':'','tes_kesehatan':'','status':'closed'})
                elif hasil.stage_id.sequence == 20 :
                    hr_monitor.write(cr,uid,[monit.id],{'test2_hrd':'failed','test1_usr':'','test2_usr':'','approval':'','tes_kesehatan':'','status':'closed'})
                elif hasil.stage_id.sequence == 80 :
                    hr_monitor.write(cr,uid,[monit.id],{'test1_usr':'failed','test2_usr':'','approval':'','tes_kesehatan':'','status':'closed'})
                elif hasil.stage_id.sequence == 90 :
                    hr_monitor.write(cr,uid,[monit.id],{'test2_usr':'failed','approval':'','tes_kesehatan':'','status':'closed'})
                elif hasil.stage_id.sequence == 100 :
                    hr_monitor.write(cr,uid,[monit.id],{'approval':'failed','tes_kesehatan':'','status':'closed'})
        year =str(datetime.now().year)
        hr_sumary = self.pool.get('hr.sumary_monitoring')
        hr_sumary_src = hr_sumary.search(cr,uid,[('dep','=',hasil.dep_app.name),('tahun','=',year)])
        hr_sumary_brw = hr_sumary.browse(cr,uid,hr_sumary_src)
        for mon in hr_sumary_brw :
            if hasil.stage_id.sequence == 95 :
                inter = mon.approval + 1
                qty = mon.qty + 1
                hr_sumary.write(cr,uid,[moni.id],{'tes_kesehatan':inter,'qty':qty})    
        return res 

    def tidak_hadir(self, cr, uid, ids,vals, context=None):
        """Overrides cancel for crm_case for setting probability
        """
        hasil=self.browse(cr,uid,ids)[0]
        names = hasil.partner_name
        stat = hasil.stat - 1
        hr_status = self.pool.get('hr.seleksi_pelamar')
        hr_search = hr_status.search(cr,uid,[('nama','=',names),('stat','=',stat)])
        hr_brws = hr_status.browse(cr,uid,hr_search)[0]
        values=False
        for men in hasil.meeting_ids :
            date = men.date
            if men.stat == 'interview1' :
                hr_status.write(cr, uid, [hr_brws.id], {'tgl_seleksi':date}, context=context)
            elif men.stat == "interview2" :
                hr_status.write(cr, uid, [hr_brws.id], {'tgl_seleksi1':date}, context=context)
        if hasil.stage_id.name == "First Interview" :
            hr_status.write(cr, uid, [hr_brws.id], {'status': 'Ditolak','kehadiran':'Tidak Hadir','keputusan':'NOK'}, context=context)                
        elif hasil.stage_id.name == "Second Interview" :
            hr_status.write(cr, uid, [hr_brws.id], {'status1': 'Ditolak','kehadiran':'Tidak Hadir','keputusan':'NOK'}, context=context)
        res = super(hr_applicant, self).case_cancel(cr, uid, ids, context)
        self.write(cr, uid, ids, {'probability': 0.0})
        hr_monitor = self.pool.get('hr.monitoring_recruitment')
        hr_monitor_src = hr_monitor.search(cr,uid,[('name','=',hasil.partner_name)])
        hr_monitor_brw = hr_monitor.browse(cr,uid, hr_monitor_src)
        for monit in hr_monitor_brw :
            if monit.status == 'open' :
                if hasil.stage_id.sequence == 10 :
                    hr_monitor.write(cr,uid,[monit.id],{'test1_hrd':'failed','test2_hrd':'','test1_usr':'','test2_usr':'','approval':'','tes_kesehatan':'','status':'closed'})
                elif hasil.stage_id.sequence == 20 :
                    hr_monitor.write(cr,uid,[monit.id],{'test2_hrd':'failed','test1_usr':'','test2_usr':'','approval':'','tes_kesehatan':'','status':'closed'})
                elif hasil.stage_id.sequence == 80 :
                    hr_monitor.write(cr,uid,[monit.id],{'test1_usr':'failed','test2_usr':'','approval':'','tes_kesehatan':'','status':'closed'})
                elif hasil.stage_id.sequence == 90 :
                    hr_monitor.write(cr,uid,[monit.id],{'test2_usr':'failed','approval':'','tes_kesehatan':'','status':'closed'})
        year =str(datetime.now().year)
        hr_sumary = self.pool.get('hr.sumary_monitoring')
        hr_sumary_src = hr_sumary.search(cr,uid,[('dep','=',hasil.dep_app.name),('tahun','=',year)])
        hr_sumary_brw = hr_sumary.browse(cr,uid,hr_sumary_src)
        for mon in hr_sumary_brw :
            if hasil.stage_id.sequence == 95 :
                inter = mon.approval + 1
                qty = mon.qty + 1
                hr_sumary.write(cr,uid,[moni.id],{'tes_kesehatan':inter,'qty':qty})    
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
            #self.write(cr,uid,ids,{'age2' : age})
        return result
        
    '''Filter Applicant
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
                if stage == 1 :
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
    '''
    # def interview(self, cr, uid,vals, context=None):
    #     import pdb;pdb.set_trace()
    #     #appl=self.browse(cr,uid,ids)[0]
    #     app=vals["job_id"]
    #     apps=self.pool.get('hr.survey1')
    #     appss=apps.search(cr,uid,[('job_id.id','=',app)])
    #     ap=apps.browse(cr,uid,appss,context)
    #     res=[]
    #     for pr in ap:
    #         if pr.surveys_id.state == "open":
    #             #prs=pr.survey_id.id
    #             prs=pr.surveys_id.id
    #             res.append((0,0, {'name':prs})) 
    #     vals['surv_ids']=res
    #     return vals
           
    def create(self, cr, uid, vals, context=None):       
        #vals=self.interview(cr, uid, vals, context=None)
        result= super(hr_applicant,self).create (cr, uid, vals, context=None)
        return result
        
    def onchange_country(self, cr, uid, ids, country_id, context=None):
       result = {}
       country_id1_obj = self.pool.get('res.country')
       brew = country_id1_obj.browse(cr, uid, country_id, context=context).code_telp
       return {'value':{'partner_phone': brew}}
   
    def onchange_country1(self, cr, uid, ids, country_id1, context=None):
       result = {}
       country_id1_obj = self.pool.get('res.country')
       brew = country_id1_obj.browse(cr, uid, country_id1, context=context).code_telp
       return {'value':{'telp1': brew}}
       
    def onchange_country2(self, cr, uid, ids, country_id2, context=None):
       result = {}
       country_id1_obj = self.pool.get('res.country')
       brow = country_id1_obj.browse(cr, uid, country_id2, context=context).code_telp
       return {'value':{'telp2': brow}}
    
    #fungsi untuk menentukan kesimpulan diterima atau di tolak
    def simpul(self, cr, uid,ids,vals,context=None):   
        hasil=self.browse(cr,uid,ids)[0]
        dept = hasil.dep_app.id
        partner=self.pool.get('hr.recruitment.stage')  
        pero=partner.search(cr,uid,['|',('department_id','=',False),('department_id','=',dept)])     
        pers=partner.browse(cr,uid,pero,context)
        #stg2=float(hasil.stage_id.sequence)+1
        stg3=hasil.stage_id.sequence
        names = hasil.partner_name
        stat = hasil.stat - 1
        hr_status = self.pool.get('hr.seleksi_pelamar')
        hr_search = hr_status.search(cr,uid,[('nama','=',names),('stat','=',stat)])
        hr_brws = hr_status.browse(cr,uid,hr_search)[0]
        values=False
        meet = False
        st = 1000
        for men in hasil.meeting_ids :
            date = men.date
            if meet == False :
                meet = men.date
            if men.stat == 'interview1' :
                hr_status.write(cr, uid, [hr_brws.id], {'tgl_seleksi':date}, context=context)
            elif men.stat == "interview2" :
                hr_status.write(cr, uid, [hr_brws.id], {'tgl_seleksi1':date}, context=context)
        if hasil.stage_id.sequence == 20 :
            hr_status.write(cr, uid, [hr_brws.id], {'status': 'Diterima','kehadiran':'Hadir'}, context=context)                
        elif hasil.stage_id.sequence == 90 :
            hr_status.write(cr, uid, [hr_brws.id], {'status1': 'Diterima','kehadiran':'Hadir','keputusan':'OK'}, context=context)
        for line in pers: 
            stage=line.sequence
            if stg3 < stage and st > stage :
                stg=line.id                       
                self.write(cr,uid,ids,{'stage_id': stg},context=context)  
                st = stage
        obj_perm = self.pool.get('hr.job')
        obj_prsrc = obj_perm.search(cr,uid,[('state','=','in_progress')])
        obj_prbrws = obj_perm.browse(cr,uid,obj_prsrc)
        jbtn = hasil.app_id.name
        hr_pemi =self.pool.get('hr_pemenuhan')
        hr_pem_src = hr_pemi.search(cr,uid,[('jabatan','=',jbtn)])
        hr_pem_brw = hr_pemi.browse(cr,uid,hr_pem_src,context)
        y = 0
        for hr_pem in hr_pem_brw :
            no = hr_pem.no_pmintaan
            for hr_job in obj_prbrws :
                no_id = hr_job.no_permohonan
                if no == no_id :
                    y = y + 1
            if hr_pem.aktifitas == False :              
                aktf = 'Proses Recruitment' + str(y)
                hr_pemi.write(cr, uid, [hr_pem.id], {'aktifitas':aktf}, context=context)
            if hr_pem.tgl_seleksi == False :
                hr_pemi.write(cr, uid, [hr_pem.id], {'tgl_seleksi':meet}, context=context)
            if hr_pem.status != "Done" and hasil.stage_id.sequence == 90 :        
                jum_diterima = hr_pem.jml_diterima + 1
                hr_pemi.write(cr,uid, [hr_pem.id],{'jml_diterima':jum_diterima,'status':'pending'},context=context) 
        #function for list pemenuhan kebutuhan recruitment bulanan
        stages = hasil.stage_id.sequence
        if stages == 90 :
            obj_job = self.pool.get('hr.job')
            obj_jobs = obj_perm.search(cr,uid,[('state','=','in_progress'),('name','=',jbtn)])
            obj_jobb = obj_perm.browse(cr,uid,obj_prsrc)
            for hr_job in obj_jobb :
                obj_job.write(cr,uid,[hr_job.id],{'status_rec':'pending'})
        hr_pem_keb = self.pool.get('hr.pemenuhan_kebutuhan')
        hr_pem_keb_src = hr_pem_keb.search(cr,uid,[('status_pemenuhan','=','In Process'),('jabatan','=',jbtn)])
        hr_pem_keb_brw = hr_pem_keb.browse(cr,uid,hr_pem_keb_src,context=context)
        for hhh in hr_pem_keb_brw :
            jum_terpenuhi = hhh.jumlah_terpenuhi
            jum_kekurangan = hhh.jumlah_kebutuhan
            if hhh.status_pemenuhan != "Done" and hasil.stage_id.sequence == 90 :        
                jum_terpenuhi = hhh.jumlah_terpenuhi + 1
                jum_kekurangan = hhh.kekurangan_pmenuhan - 1
            hr_pem_keb.write(cr,uid,[hhh.id],{'status_wawancara':'OK','jumlah_terpenuhi':jum_terpenuhi,'kekurangan_pmenuhan':jum_kekurangan,'status_penempatan':'Next Process','status_pemenuhan':'Done'})
        #fungsi for monitoring progres recruitment
        hr_monitor = self.pool.get('hr.monitoring_recruitment')
        hr_monitor_src = hr_monitor.search(cr,uid,[('name','=',hasil.partner_name)])
        hr_monitor_brw = hr_monitor.browse(cr,uid, hr_monitor_src)
        for monit in hr_monitor_brw :
            if monit.status == 'open' :
                if hasil.stage_id.sequence == 10 :
                    hr_monitor.write(cr,uid,[monit.id],{'test1_hrd':'done'})
                elif hasil.stage_id.sequence == 20 :
                    hr_monitor.write(cr,uid,[monit.id],{'test2_hrd':'done'})
                elif hasil.stage_id.sequence == 80 :
                    hr_monitor.write(cr,uid,[monit.id],{'test1_usr':'done'})
                elif hasil.stage_id.sequence == 90 :
                    hr_monitor.write(cr,uid,[monit.id],{'test2_usr':'done'})
                elif hasil.stage_id.sequence == 93 :
                    hr_monitor.write(cr,uid,[monit.id],{'approval':'done'})
                elif hasil.stage_id.sequence == 95 :
                    hr_monitor.write(cr,uid,[monit.id],{'tes_kesehatan':'done'})
        year =str(datetime.now().year)
        hr_sumary = self.pool.get('hr.sumary_monitoring')
        hr_sumary_src = hr_sumary.search(cr,uid,[('dep','=',hasil.dep_app.name),('tahun','=',year)])
        hr_sumary_brw = hr_sumary.browse(cr,uid,hr_sumary_src)
        #import pdb;pdb.set_trace()
        for mon in hr_sumary_brw :
            if hasil.stage_id.sequence == 10 :
                inter = mon.wawancara_hrd + 1
                qty = mon.qty + 1
                hr_sumary.write(cr,uid,[mon.id],{'wawancara_hrd':inter,'qty':qty})
            elif hasil.stage_id.sequence == 20 :
                inter = mon.wawancara1_usr + 1
                qty = mon.qty + 1
                hr_sumary.write(cr,uid,[mon.id],{'wawancara1_usr':inter,'qty':qty})
            elif hasil.stage_id.sequence == 80 :
                inter = mon.wawancara2_usr + 1
                qty = mon.qty + 1
                hr_sumary.write(cr,uid,[mon.id],{'wawancara2_usr':inter,'qty':qty})
            elif hasil.stage_id.sequence == 90 :
                inter = mon.approval + 1
                qty = mon.qty + 1
                hr_sumary.write(cr,uid,[mon.id],{'approval':inter,'qty':qty})
            elif hasil.stage_id.sequence == 95 :
                inter = mon.approval + 1
                qty = mon.qty + 1
                hr_sumary.write(cr,uid,[mon.id],{'tes_kesehatan':inter,'qty':qty})    
        return True
    
    def onchange_job(self, cr, uid, ids, job, context=None):
        if job:
            job_record = self.pool.get('hr.job').browse(cr, uid, job, context=context)
            if job_record and job_record.department_id:
                return {'value': {
                    'department_id': job_record.department_id.id,
                    'salary_proposed_botom_margin':job_record.salary_proposed_botom_margin,
                    'salary_proposed_top_margin':job_record.salary_proposed_top_margin}}
        return {}

    _columns= {
        'name': fields.char('Subject', size=128, required=True, select=True),
        'partner_name': fields.char("Applicant's Name", size=64, select=True),
        'email_from': fields.char('Email', size=128, help="These people will receive email.", select=True),
        'partner_phone': fields.char('Phone', size=32, select=True,states={'open':[('readonly',True)], 'cancel':[('readonly',True)], 'pending':[('readonly',True)], 'done':[('readonly',True)]}),
        'kelamin':fields.selection([('male','Male'),('female','Female')],'Jenis Kelamin',required=False),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir',required=False),
        'age': fields.function(_compute_age, type='integer', obj='hr.applicant', method=True, store=False, string='Usia (Thn)', readonly=True),
        'agama_id':fields.many2one('hr_recruit.agama','Agama'),
        'country_id': fields.many2one('res.country', 'Kewarganegaraan'),
        'ktp':fields.char('No.ID',20),
        'jenis_id':fields.selection([('KTP','Kartu Tanda Penduduk'),('Passport','Passport')],'Jenis ID'),
        'issued_id':fields.many2one('hr_recruit.kota','Dikeluarkan di'),
        'issued_id2':fields.many2one('res.country','Dikeluarkan di'),
        'tgl_keluar_ktp':fields.date('Tanggal Dikeluarkan',),
        'tgl_berlaku':fields.date('Tanggal Berlaku'),
        'tgl_berlaku2':fields.date('Tanggal Berlaku'),
        'sim':fields.selection([('A','A'),('B1','B1'),('B2','B2'),('C','C')],'SIM'),
        'tgl_keluar_sim':fields.date('Tanggal Dikeluarkan'),              
        'prov_id':fields.many2one('hr_recruit.prov','Provinsi',domain="[('country_id','=',country_id1)]"),
        'kab_id':fields.many2one('hr_recruit.kota','Kab./kota',domain="[('provinsi_id','=',prov_id)]"),
        'kec_id':fields.many2one('hr_recruit.issued','Kecamatan',domain="[('kota_id','=',kab_id)]"),
        'alamat1':fields.char('Alamat Domisili',100),        
        'prov_id2':fields.many2one('hr_recruit.prov','Provinsi', domain="[('country_id','=',country_id2)]"),
        'kab_id2':fields.many2one('hr_recruit.kota','Kab./Kota', domain="[('provinsi_id','=',prov_id2)]"),
        'kec_id2':fields.many2one('hr_recruit.issued','Kecamatan', domain="[('kota_id','=',kab_id2)]"),
        'alamat2':fields.char('Alamat sesuai KTP',100),
        'telp1':fields.char('Telepon',50),
        'telp2':fields.char('Telepon',50),
        'status':fields.selection([('single','Single'),('married','Menikah'),('divorced','Cerai')],'Status Pernikahan'),
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
        'jurusan_id':fields.many2one('hr_recruit.jurusan_detail','Jurusan', domain="[('bidang_id','=',bidang_id)]"),  
        'job_id': fields.many2one('hr.job', 'Applied Job',required=False),
        'type_id': fields.many2one('hr.recruitment.degree', 'Pendidikan',required=False),
        'result_id':fields.many2one('hr_recruit.result','Result'),
        'surv_ids':fields.one2many('hr.survey','applicant_id','Interview Form'),
        'pengalaman':fields.integer('Pengalaman (min-th)'),
        'stage_id': fields.many2one ('hr.recruitment.stage', 'Stage',
                        domain="['&', ('fold', '=', False), '|', ('department_id', '=', department_id), ('department_id', '=', False)]",readonly=True),
        'pt_id':fields.many2one('hr_recruit.pt','Perguruan Tinggi'),  
        'bidang_id':fields.many2one('hr_recruit.bidang','Bidang'),          
        "fasilitas1_ids":fields.one2many("hr.fasilitas","applican_id","Fasilitas"),  
        "fasilitas2_ids":fields.one2many("hr.fasilitas2","applican_id","Fasilitas"),  
        "salary_proposed_extra": fields.char('Proposed Salary Extra', size=100, help="Salary Proposed by the Organisation, extra advantages",readonly=True),
        "blood":fields.selection([('A','A'),('B','B'),('AB','AB'),('O','O')],'Gol Darah'),
        "respon_div":fields.many2one('hr.department','Responsible Division'), 
        'country_id1':fields.many2one('res.country','Negara'),
        'country_id2':fields.many2one('res.country','Negara'),
        'kode1' :fields.char('Kode Pos'),
        'kode2' :fields.char('Kode Pos'),
		'app_id' : fields.many2one('hr.job','Job'),
        'dep_app' : fields.many2one('hr.department', 'Department'),
        'salary_proposed': fields.float('Proposed Salary'),
        'salary_proposed_botom_margin': fields.float('Standar Gaji', help="Batas range terendah"), 
        'salary_proposed_top_margin': fields.float('Standar Gaji', help="Batas range tertinggi"), 
        'empgol_id': fields.many2one('hr_employs.gol','Golongan'),
        'survey_result_ids': fields.one2many('hr_applicant.hasil_wawancara','app_id', "Hasil Wawancara"),
        "meeting_ids" : fields.many2many("crm.meeting","meeting_rel","meeting_id","applicant_id",string="Jadwal Interview",readonly=True, domain="[('status','=',True)]"),
        'daf_pelamar_ids' : fields.one2many('hr.daf_pelamar','applicant_id','Daftar Pelamar'),
        'ref' :fields.char('Ref'),
        'lokasi_id'  : fields.selection([('karawang','Karawang'),('tanggerang','Tanggerang')],'Alamat Kantor'), 
        'ptkp' : fields.many2one('hr.ptkp','Status Pajak'),
        'stat': fields.float('stat'),
        'st_pelamar' :fields.many2one('hr.seleksi_pelamar','status'),
        'fingerprint_code2' : fields.integer('Fingeprint code'),
        }

    _sql_constraints = [
        ('ktp_uniq', 'unique(ktp)','No KTP / Passport sudah ada !')
    ]
    _defaults = {
        'lokasi_id' : 'karawang'
    }
    # fungsi untuk mengisi status ids
    '''def status_pelamar(self, cr, uid, ids, context=None):
        import pdb;pdb.set_trace()
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True) 
        hr_status = self.pool.get('hr.status_pelamar')
        model_data = self.pool.get('ir.model.data')
        act_window = self.pool.get('ir.actions.act_window')
        values = False
        for obj in self.browse(cr,uid,ids, context=context):
            #values = {}
            values = hr_status.create(cr,uid,{
                'applicant_id': obj.id,
                'status': obj.stage_id.name,
                'kondisi' : 'Diterima',
                })
            self.write(cr, uid, [obj.id], {'st_pelamar': values}, context=context)
            self.case_close(cr, uid, [obj.id], context)
        return True  
    '''
    def daf_pelamar(self, cr,uid,ids, context=None):
        #import pdb;pdb.set_trace()
        if context is None:
                context= {}
        context = dict(context, mail_create_nolog=True)
        hr_status = self.pool.get('hr.daf_pelamar')
        model_data = self.pool.get('ir.model.data')
        act_window = self.pool.get('ir.actions.act_window')
        values = False
        year =datetime.now().year
        for obj in self.browse(cr,uid,ids, context=context):
            #values = {}
            stat_id = obj.stat
            name = obj.partner_name
            hr_search = hr_status.search(cr,uid,[('stat','=',stat_id),('name','=',name)])
            hr_brw = hr_status.browse(cr,uid,hr_search)
            if hr_brw == True :
                values = hr_status.create(cr,uid,{
                    'applicant_id' :obj.id,
                    'name': obj.name,
                    'pendidikan': obj.type_id.id,
                    'jurusan' : obj.jurusan_id.id,
                    'tanggal_lahir' : obj.tgl_lahir,
                    'usia': obj.age,
                    'sumber': obj.source_id.id,
                    'ref' : obj.ref,
                    'department' : obj.department_id.id,
                    'jabatan' :obj.job_id.id,
                    'tahun' : year,
                    #'stat' : 
                    })
                self.write(cr, uid, [obj.id], {'st_pelamar': values}, context=context)
                self.case_close(cr, uid, [obj.id], context)
        return True  
hr_applicant()

'''class status_pelamar(osv.osv):
    _name = "hr.status_pelamar"

    _columns = {
        'applicant_id' :fields.many2one('hr.applicant'),
        'status' : fields.char('status Pelamar'),
        'kondisi' : fields.char('Kondisi'),
    }
status_pelamar()
'''
class daftar_pelamar(osv.osv):
    _name = 'hr.daf_pelamar'

    _columns = {
        'applicant_id':fields.many2one('hr.applicant'),
        'nama':fields.char('Nama'),
        'tgl_eksekusi1' : fields.date('Tanggal Eksekusi'),
        'tgl_eksekusi2' : fields.date('Tanggal Eksekusi'),
        'tgl_seleksi' : fields.date('Tanggal Seleksi'),
        'pendidikan' : fields.char('Pendidikan'),
        'jurusan' : fields.char('Jurusan'),
        'tanggal_lahir' : fields.date('Tgl Lahir'),
        'usia' : fields.integer('Usia'),
        'sumber' :fields.char('Sumber'),
        'ref' : fields.char('Ref'),
        'kehadiran' : fields.char('Kehadiran'),
        'department' : fields.char('Department'),
        'bagian' : fields.char('Bagian'),
        'jabatan' :fields.char('Jabatan'),
        'status_hrd' : fields.char('Status Hrd'),
        'status_user' : fields.char('status User'),
        'keputusan' : fields.char('Keputusan'),
        'tanggal_kputusan' : fields.char('Tanggal Keputusan'),
        'stat' : fields.float('stat'),
        'tahun' : fields.integer('tahun'),
    }

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
        'Departmen_id':fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='departmen',readonly=True),            
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
        'name':fields.char('Nama Kab./Kota',50),
        'provinsi_id' : fields.many2one('hr_recruit.prov','Provinsi'),
        }
kota()

class agama(osv.osv):
    _name='hr_recruit.agama'
        
    _columns={
        'name':fields.char('Agama',30),
        }
agama()                    

class issued(osv.osv):
    _name='hr_recruit.issued'
        
    _columns={
        'name':fields.char('Kecamatan',50),
        'kota_id':fields.many2one('hr_recruit.kota','Kota'),
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

class pt(osv.osv):
    _name='hr_recruit.pt'
        
    _columns={
        'name':fields.char('Nama Perguruan Tinggi',50),
        }
pt()

class bidang(osv.osv):
    _name='hr_recruit.bidang'
        
    _columns={
        'name':fields.char('Bidang',50),
        }
bidang()

class provinsi(osv.osv):
    _name='hr_recruit.prov'
        
    _columns={
        'name':fields.char('Provinsi',50),
        'country_id':fields.many2one('res.country','Negara'),
        }
provinsi()

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
        'name': fields.related('job_id',type="many2one",relation="hr.job", string="Job Name", readonly=True),
        'job_id' : fields.many2one('hr.job', 'Job Name',required=True),
        'applicant_id':fields.many2one('hr.applicant'),
        'tgl_int':fields.date('Tanggal Interview')
        
    }
survey()

class fasilitas(osv.osv):
	_name = "hr.fasilitas"
	_rec_name="fasilitas"
	
	_columns = {
		"fasilitas" : fields.many2one("hr.fasilitas3","Fasilitas",required=True),
		"applican_id" : fields.many2one("hr.applicant","Fasilitas"),
		}
fasilitas()

class fasilitas2(osv.osv):
	_name = "hr.fasilitas2"
	_rec_name="fasilitas"
	
	_columns = {
		"fasilitas" : fields.many2one("hr.fasilitas3","Fasilitas",required=True),
		"applican_id" : fields.many2one("hr.applicant","Fasilitas"),
		}
fasilitas()

class fasilitas3(osv.osv):
	_name = "hr.fasilitas3"
	
	_columns = {
		"name" : fields.char("Fasilitas",required=True),
		}
fasilitas3()

class country(osv.osv):
    _name = "res.country"
    _inherit = "res.country"
    
    _columns = {
        "code_telp" : fields.char("Kode Telp"),
    }
country()

class hasil_wawancara(osv.osv):
    _name = "hr_applicant.hasil_wawancara"

    def create(self, cr, uid, vals, context=None):  
        vals['stage'] = self.pool.get("hr.applicant").browse(cr,uid,vals['app_id'],context).stage_id.name
        return super(hasil_wawancara, self).create(cr, uid, vals, context)    

    _columns = {
        'app_id':fields.many2one("hr.applicant","Applicant"),
        'result':fields.selection([('Dapat_Diterima','Dapat Diterima'),('Untuk_Dicadangkan','Untuk Dicadangkan'),('Ditolak','Ditolak')],'Kesimpulan'), 
        'reason': fields.text("Alasan"),
        'user_id': fields.many2one('res.users', 'Responsible', readonly=True),
        'stage':fields.char('Stage', readonly=True),
    }

    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
    }
    
hasil_wawancara()

class meeting(osv.osv):
    _name = "crm.meeting"
    _inherit = "crm.meeting"
    
    _columns = {
        "applicant_ids" : fields.many2many("hr.applicant","meeting_rel","applicant_id","meeting_id","Nama Pelamar"),
        'status' :fields.boolean ('Aktif'),
        'stat' : fields.selection([('interview1','Interview HRD'),('interview2','Interview User'),('not','Bukan Interview')],'status Meeting',required=True)
    }

    _defaults = {
        'status' : True,
    }

    def status(self, cr, uid, ids, context=None):
        date_now =datetime.now().month#.strftime("%Y-%m-%d").month
        year =datetime.now().year#strftime("%Y-%m-%d").year
        day =datetime.now().day#strftime("%Y-%m-%d").day
        obj=self.pool.get('crm.meeting')
        datas=obj.search(cr,uid,[('status','=',True)])
        dates=obj.browse(cr,uid,datas,context)
        for det in dates :
            tanggal=det.date
            mon=datetime.strptime(tanggal,"%Y-%m-%d %H:%M:%S").month
            yr=datetime.strptime(tanggal,"%Y-%m-%d %H:%M:%S").year
            da=datetime.strptime(tanggal,"%Y-%m-%d %H:%M:%S").day
            if date_now == mon and year == yr and day == da :
                self.write(cr,uid,ids,{'status':False},context=context)   
        return True


meeting()  

class daftar_seleksi(osv.osv):
    _name = 'hr.seleksi_pelamar'

    _columns = {
    'applicant_id':fields.many2one('hr.applicant'),
    'nama' :fields.char('Name'),
    'tgl_seleksi' : fields.date('Tgl Selek Hrd'),
    'tgl_seleksi1' : fields.date('Tgl Selek Usr'),
    'pendidikan' : fields.char('Pendidikan'),
    'jurusan' : fields.char('Jurusan'),
    'tgl_lahir' :fields.date('Tgl Lahir'),
    'usia' : fields.integer('Usia'),
    'sumber' : fields.char('Sumber'),
    'ref' : fields.char('Ref'),
    'kehadiran' : fields.char('Kehadiran'),
    'department' : fields.char('Department'),
    'bagian' : fields.char('Bagian'),
    'jabatan': fields.char('Jabatan'),
    'ref_jab' : fields.char('ref Jabatan'),
    'status' : fields.char('Status Hrd'),
    'status1' : fields.char('Status User'),
    'keputusan':fields.char('Keputusan'),
    'tgl_keputusan':fields.date('Tgl Keputusan'),
    'tahun' : fields.char('Tahun'),
    'stat' : fields.float('stat'),
    }
daftar_seleksi()

class pemenuhan_rcruit(osv.osv):
    _name = 'hr_pemenuhan'

    _columns = {
        'no_pmintaan' : fields.integer('No Permintaan'),
        'tgl_permintaan' : fields.date('Tanggal Permintaan'),
        'department' : fields.char('Department'),
        'jabatan' : fields.char('Jabatan'),
        'jml_prmintaan' : fields.integer('Jumlah Permintaan'),
        'aktifitas' : fields.char('Aktifitas'),
        'tgl_seleksi' : fields.date('Tanggal Seleksi'),
        'jml_kandidat' : fields.integer("jumlah Kandidat"),
        'jml_diterima' : fields.integer('Jumlah Ditrima'),
        'per_masuk' : fields.char('Permohonan Masuk'),
        'status' : fields.char('Status'),
        'ket' : fields.char('Keterangan'),
            }

pemenuhan_rcruit() 

class pemenuhan_kebutuhan(osv.osv):
    _name = 'hr.pemenuhan_kebutuhan'
            
    _columns = {
        'bul_har':fields.char('Jenis Kebutuhan'),
        'div' :fields.char('Divison'),
        'dept' : fields.char('Department'),
        'bagian' : fields.char('Bagian'),
        'jabatan' : fields.char('Jabatan'),
        'level' : fields.char("Level"),
        'tgl_permohonan' : fields.date("Tgl Prmohonan"),
        'status_wawancara' : fields.char('Status Wawancara'),
        'status_pemenuhan' :fields.char('Status Pemenuhan'),
        'jumlah_kebutuhan' :fields.integer('Jumlah Kebutuhan'),
        'jumlah_terpenuhi' :fields.integer("Jumlah Terpenuhi"),
        'kekurangan_pmenuhan':fields.integer('Kekurangan Kebutuhan', readonly=True),
        'status_penempatan' :fields.char('status Penempatan'),
        'ket' :fields.char('Keterangan'),
        'review' : fields.char('Review'),
        }  

pemenuhan_kebutuhan()  

class sumary_kebutuhan(osv.osv):
    _name = 'hr.sumary_kebutuhan'

    def _varian(self, cr, uid, ids, args, vals, context=None):
        varian={}
        for var in self.browse(cr,uid,ids, context=context):
            varian[var.id] = var.jum_terpenuhi - var.jum_kebutuhan
        return varian

    def _percentage(self, cr, uid, ids, args, vals, context=None) :
        percentage={}
        for per in self.browse(cr,uid,ids, context=context):
            if per.jum_terpenuhi * 100 == 0 :
                percentage[per.id] = 0
            else :
                percentage[per.id] = (per.jum_terpenuhi * 100) / per.jum_kebutuhan
        return percentage 

    _columns = {
        'tahun' : fields.char('Tahun'),
        'bul_har':fields.char('Jenis Permohonan'),
        'dep' :fields.char('Department'),
        'jum_kebutuhan' : fields.float('Jumlah Kebutuhan'), 
        'jum_terpenuhi' : fields.float('Jumlah Terpenuhi'),
        'varian':fields.function(_varian, type='float',method=True, store=False,string='Variance'),
        'percentage' : fields.function(_percentage, type='float',method=True,store=False,string='Persentase'),
        'ket' : fields.char('Ket'),
    }
sumary_kebutuhan()

class sumary_kebutuhan(osv.osv):
    _name = 'hr.sumary_kebutuhan_harian'

    def _varian(self, cr, uid, ids, args, vals, context=None):
        varian={}
        for var in self.browse(cr,uid,ids, context=context):
            varian[var.id] = var.jum_terpenuhi - var.jum_kebutuhan
        return varian

    def _percentage(self, cr, uid, ids, args, vals, context=None) :
        percentage={}
        for per in self.browse(cr,uid,ids, context=context):
            if per.jum_terpenuhi * 100 == 0 :
                percentage[per.id] = 0
            else :
                percentage[per.id] = (per.jum_terpenuhi * 100) / per.jum_kebutuhan
        return percentage  

    _columns = {
        'tahun' : fields.char('Tahun'),
        'bul_har':fields.char('Jenis Permohonan'),
        'dep' :fields.char('Department'),
        'jum_kebutuhan' : fields.float('Jumlah Kebutuhan'), 
        'jum_terpenuhi' : fields.float('Jumlah Terpenuhi'),
        'varian':fields.function(_varian, type='float',method=True, store=False,string='Variance'),
        'percentage' : fields.function(_percentage, type='float',method=True,store=False,string='Persentase'),
        'ket' : fields.char('Ket'),
    }
sumary_kebutuhan()       

class lap_permintaan_karyawan(osv.osv):
    _name = 'hr.lap_permintaan_karyawan'

    _columns = {
        'dep' : fields.char('Departmen'),
        'posisi' : fields.char('Posisi'),
        'jumlah' : fields.integer('Jumlah'),
        'wkt_penempatan' : fields.date('wkt Penempatan'),
        'pengalaman' : fields.integer('Pengalaman'),
        'usia' :fields.integer("Usia"),
        'jenis_kelamin' : fields.char('Jenis Kelamin'),
        'status' :fields.char('Status Pernikahan'),
        'domisili' : fields.char('Domisili'),
        'tahun' :fields.integer('Tahun'),
        'no' : fields.integer('No Permohonan'),
        'stat' : fields.char('Status'),
    }     
lap_permintaan_karyawan()

class monitoring_recruitment(osv.osv):
    _name = 'hr.monitoring_recruitment'

    _columns = {
        'name' : fields.char('Nama'),
        'dep' : fields.char('Department'),
        'test1_hrd' : fields.char('Test Tertlis HRD'),
        'test2_hrd' : fields.char('Test Wawancara HRD'),
        'test1_usr' : fields.char('Test Wawancara USR 1'),
        'test2_usr' : fields.char('Test Wawancara USR 2'),
        'approval' : fields.char('Management Approval'),
        'tes_kesehatan' : fields.char('Test Kesehatan'),
        'ket' :fields.char('Keterangan'),
        'status': fields.char('status'),
        'tahun' :fields.char('Tahun'),
    }
monitoring_recruitment()

class sumary_monitoring(osv.osv):
    _name = 'hr.sumary_monitoring'

    _columns = {
        'dep' : fields.char('Department'),
        'qty' : fields.integer ('Qty Total'),
        'test1' : fields.integer('Test Tertulis'),
        'wawancara_hrd' :fields.integer('Wawancara HRD'),
        'wawancara1_usr' :fields.integer('Wawancara1 User'),
        'wawancara2_usr' :fields.integer('Wawancara 2 User'),
        'approval' :fields.integer('Mgnt Approval'),
        'tes_kesehatan' : fields.integer('Tes Kesehatan'),
        'pending' :fields.integer ('Pending'),
        'tahun' :fields.char('Tahun'),
    }
sumary_monitoring()

class sarmut(osv.osv):
        _name = 'hr.sarmut'

        _columns = {
            'divisi':fields.char('Divisi', readonly=True),
            'department' : fields.char('Department', readonly=True),
            'bagian' : fields.char('bagian', readonly=True),
            'jabatan' : fields.char('Jabatan', readonly=True),
            'jum_ygdibutuhkan' : fields.integer('Jumlah Yang Dibutuhkan', readonly=True),
            'level' : fields.char('Level', readonly=True),
            'tgl_per_user' :fields.date('Tanggal', readonly=True),
            'per_atasan_usr' : fields.char('Persetujuan Atasan User', readonly=True),
            'waktu1' : fields.integer('Waktu Proses1', readonly=True),
            'per_dir' :fields.date('Persetujuan Direktur', readonly=True),
            'waktu2' : fields.integer('Waktu Proses2', readonly=True),
            'per_dir_fin' : fields.date('Persetujuan Direktur Fin & ADM', readonly=True),
            'waktu3' : fields.integer('Waktu Proses3', readonly=True),
            'diterima_recruitment' : fields.date('Diterima Recruitment', readonly=True),
            'waktu4' : fields.integer('Waktu Proses4', readonly=True),
            'wawancara1' : fields.date('Wawancara1', readonly=True),
            'jum_nwd' : fields.integer('Jumlah NWD', readonly=True),
            'waktu_tot' : fields.integer('Waktu Total', readonly=True),
            'status' : fields.char('Status', readonly=True),
            'ket' : fields.char('Keterangan', readonly=True),
            'tahun' : fields.char('Tahun'),

        }
sarmut()

class sumary_sarmut(osv.osv):
    _name= 'hr.sumary_sarmut'

    _columns = {
        'jabatan' : fields.char('Jabatan'),
        'jumlah_permohonan' : fields.integer('Jumlah Permohonan', readonly=True),
        'jum_ygdibutuhkan' : fields.integer('Jumlah Yang Dibutuhkan', readonly=True),
        'jum_waktu_pros' : fields.integer('jumlah Waktu Proses Persetujuan', readonly=True),
        'rata_waktu_pros' :fields.integer('Rata-Rata Waktu Proses Persetujuan', readonly=True),
        'jum_waktu_wawancara' :fields.integer('Jumlah Proses Waktu Tunggu Wawancara Pertama', readonly=True),
        'rata_waktu_wawancara' : fields.integer('Rata-Rata Proses Waktu Tunggu Wawancara Pertama', readonly=True),
        'jum_nwd' : fields.integer('Jumlah NWD', readonly=True),
        'tot_waktu_proses' : fields.integer('Total Waktu Proses', readonly=True),
        'rata_waktu_pemenuhan' : fields.integer('Rata-Rata Waktu Pemenuhan', readonly=True),
        'target' : fields.integer('Target(Hari)', readonly=True),
        'status' : fields.char('Status', readonly=True),
        'ket' : fields.char('Keterangan'),
        'tahun' : fields.char('tahun')
    }