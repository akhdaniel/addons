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
    ('approval', 'Proses Approval'),
    ('in_progress', 'Sedang Dalam Proses'),
]

class permohonan_recruit(osv.osv):
    _name 		= 'hr.job'
    _inherit 	= 'hr.job'

    def cancel(self,cr,uid,ids,context=None):
        obj 		= self.browse(cr,uid,ids)[0]
        objk 		= self.pool.get('hr.job.approval')
        objk_src 	= objk.search(cr,uid,[('state','=','submit')])
        objk_brw	= objk.browse(cr,uid,objk_src)[0]
        self.write(cr,uid,ids,{'state':objk_brw.id, 'states_id' : 'submit','status_rec':'new'},context=context)
        return True

    def selesai(self,cr,uid,ids,context=None):
        obj = self.browse(cr,uid,ids)[0]
        names = obj.name
        no = obj.no_permohonan
        lap_obj = self.pool.get('hr.lap_permintaan_karyawan')
        lap_src = lap_obj.search(cr,uid,[('no','=',obj.no_permohonan)])
        for lap in lap_obj.browse(cr,uid,lap_src) :
            lap_obj.write(cr,uid,[lap.id],{'stat' : 'selesai'},context=context)
        objk 		= self.pool.get('hr.job.approval')
        objk_src 	= objk.search(cr,uid,[('state','=','submit')])
        objk_brw	= objk.browse(cr,uid,objk_src)[0]    
        self.write(cr,uid,ids,{'state':objk_brw.id, 'states_id' : 'submit','status_rec':'new'},context=context)
        hr_pemi =self.pool.get('hr_pemenuhan')
        hr_pem_src = hr_pemi.search(cr,uid,[('jabatan','=',names),('no_pmintaan','=', no)])
        hr_pem_brw = hr_pemi.browse(cr,uid,hr_pem_src,context)
        for hr_pem in hr_pem_brw :
            hr_pemi.write(cr, uid, [hr_pem.id], {'status' : 'Done'}, context=context)
        return True

    def action_apporve(self, cr, uid,ids,vals,context=None):   
        hasil=self.browse(cr,uid,ids)[0]
        job = hasil.job_name.id
        partner=self.pool.get('hr.job.approval')  
        pero=partner.search(cr,uid,['|',('job_id','=',False),('job_id','=',job)])     
        pers=partner.browse(cr,uid,pero,context)
        stg3=hasil.state.sequence
        st = 1000
        for line in pers: 
            stage 			= line.sequence
            if stg3 < stage and st > stage :
                stg 		=line.id        
                states_id 	=line.state             
                self.write(cr,uid,ids,{'state': stg,'states_id' : line.state},context=context)  
                if line.state == 'in_progress' :
                	self.write(cr,uid,ids,{'status_rec':'filter'},context=context)
                st 		= stage
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
   
        filt=[('stage_id','=','Seleksi Administrasi')]
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
                partner.write(cr,uid,pero,{'app_id':per.id,'dep_app':per.department_id.id},context=context)
        elif job_b_name:
            ada = partner.browse(cr,uid,pero)
            for rr in ada:
                if rr.job_id.name==job_name :
                    partner.write(cr,uid,[rr.id],{'app_id': rr.job_id.id,'dep_app':rr.department_id.id},context=context)                              
        self.write(cr,uid,ids,{'status_rec':'execute'},context=context)                                                                                                                                        
        return True   

    _columns 	= {
        'name'              : fields.char('Job name', size=128, required=True, select=True,states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
    	'job_name'			: fields.many2one('hr.job.position','Job Position', size=128, required=True, select=True,states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
    	'jenis_permohonan'	: fields.many2one('hr.jenis_permohonan','Jenis Permohonan',required=True,states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
    	'state'				: fields.many2one ('hr.job.approval','Stage',domain="['&', ('fold', '=', False), '|', ('job_id', '=', job_name), ('job_id', '=', False)]"),   
    }

permohonan_recruit()

class job_position(osv.osv):
	_name			= 'hr.job.position'

	_columns		={
		'name'				:fields.char('Job Position'),
	}

class jenis_permohonan(osv.osv):
	_name			= 'hr.jenis_permohonan'
	_description 	= 'master jenis permohonan recruitment'

	_columns 		= {
		'name'				: fields.char('Nama Permohonan'),
	}
jenis_permohonan()

class hr_recruitment_stage(osv.osv):
	_name 			= 'hr.recruitment.stage'
	_inherit 		= 'hr.recruitment.stage'

	_columns		={
		'job_id' 			: fields.one2many('hr.job.stage','stage_id','Job Name'),
	}

class hr_job_stage(osv.osv):
	_name			= 'hr.job.stage'
	_description	= 'filter by job'

	_columns		= {
		'stage_id'			: fields.many2one('hr.recruitment.stage','stage'),
		'name'				: fields.many2one('hr.job','Job Name'),
	}

class hr_applicant(osv.osv):
    _name='hr.applicant'
    _inherit='hr.applicant'

    def simpul(self, cr, uid,ids,vals,context=None):   
        hasil=self.browse(cr,uid,ids)[0]
        dept = hasil.dep_app.id
        partner=self.pool.get('hr.recruitment.stage')  
        pero=partner.search(cr,uid,['|',('job_id','=',False),('job_id','=',dept)])     
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
hr_applicant()

class hr_recruitment_stage(osv.osv):
    """ Aproval of Permohonan Recrutiment """
    _name = "hr.job.approval"
    _inherit = "hr.job.approval"
    
    _columns = {
    	'state'				: fields.selection(AVAILABLE_STATES, 'Status', required=True, help="The related status for the stage. The status of your document will automatically change according to the selected stage. Example, a stage is related to the status 'Close', when your document reach this stage, it will be automatically closed."),
        'job_id'			:fields.many2one('hr.job.position', 'Specific to a Job', help="Jika ada proses aproval tambahan pada salah satu bidang pekerjaan."),

    }

class hr_applicant(osv.osv):
    _name='hr.applicant'
    _inherit='hr.applicant'
    _rec_name='partner_name'

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
                                                     'job_des':applicant.app_id.job_name.id,
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
                import pdb;pdb.set_trace()
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

hr_applicant()