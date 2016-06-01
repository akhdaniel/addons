from openerp.osv import fields, osv
from osv import osv, fields
from datetime import date
from datetime import datetime
from time import strptime
from time import strftime
from openerp.osv.osv import object_proxy
from openerp.tools.translate import _


class permohonan_recruit(osv.osv):
    _name 		= 'hr.job'
    _inherit 	= 'hr.job'

    _columns 	= {
        'jenis_permohonan'	: fields.many2one('hr.jenis_permohonan','Jenis Permohonan',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
        'kelas'             : fields.many2one('hr.kelas.jabatan','Kelas Jabatan'),   
    }

    def action_submit(self,cr,uid,ids,context=None): 
        #function for number automatic
        objk = self.browse(cr,uid,ids)[0]
        day_now = datetime.now()
        name = objk.jenis_permohonan.id
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
        name = hasil.jenis_permohonan.id
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
        name = obj.jenis_permohonan.id
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
permohonan_recruit()

class jenis_permohonan(osv.osv):
 	_name			= 'hr.jenis_permohonan'
 	_description 	= 'master jenis permohonan recruitment'
 	_columns 		= {
 		'name'				: fields.char('Nama Permohonan'),
 	}
jenis_permohonan()

class job_approval(osv.osv):
    _name           = 'hr.job.approval'
    _inherit        = 'hr.job.approval'

    _columns        ={
        'jenis_permohonan'  : fields.many2one('hr.jenis_permohonan','Jenis Permohonan'),
    }

class hr_kelas_jabatan(osv.osv):
    _name           = 'hr.kelas.jabatan'
    _description    = 'master kelas jabatan'

    _columns        ={
        'name'              : fields.integer('Kelas jabatan')
    }

class hr_applicant(osv.osv):
    _name='hr.applicant'
    _inherit='hr.applicant'
    _rec_name='partner_name'

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
        # hr_status = self.pool.get('hr.seleksi_pelamar')
        # hr_search = hr_status.search(cr,uid,[('nama','=',names),('stat','=',stat)])
        # hr_brws = hr_status.browse(cr,uid,hr_search)[0]
        values=False
        meet = False
        st = 1000
        # for men in hasil.meeting_ids :
        #     date = men.date
        #     if meet == False :
        #         meet = men.date
        #     if men.stat == 'interview1' :
        #         hr_status.write(cr, uid, [hr_brws.id], {'tgl_seleksi':date}, context=context)
        #     elif men.stat == "interview2" :
        #         hr_status.write(cr, uid, [hr_brws.id], {'tgl_seleksi1':date}, context=context)
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
                                                     'job_id': applicant.job_id.id,
                                                     'department_id' : applicant.department_id.id,
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
        jbtn = objk.job_id.name
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
        bul_har = objk.job_id.jenis_permohonan
        dep = objk.job_id.department_id.name
        date = objk.job_id.wkt_pemohon
        year = datetime.strptime(date,"%Y-%m-%d").year
        sum_keb = self.pool.get('hr.sumary_kebutuhan')
        obj_src_sum_keb = sum_keb.search(cr,uid,[('tahun','=',year),('dep','=',dep),('bul_har','=',bul_har)])
        obj_brw_sum_keb = sum_keb.browse(cr,uid,obj_src_sum_keb)
        for sumary in obj_brw_sum_keb :
            jum = sumary.jum_terpenuhi + 1
            sum_keb.write(cr,uid,[sumary.id],{'jum_terpenuhi':jum},context=context)
        return True

    _columns = {
        'lokasi_id'  : fields.selection([('lucas','Lucas'),('marin','Marin')],'Lokasi Kerja'), 
        #'kantor'     : fields.many2one('res.partner','Nama Kantor')
    }

    _defaults = {
        'lokasi_id' : False
    }
