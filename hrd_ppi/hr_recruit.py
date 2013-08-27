from openerp.osv import fields, osv
#from openerp.addons.base_status.base_stage import base_stage

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
        'pendidikan_id':fields.many2one('hr_recruit.pendidikan','Pendidikan'),
        'jurusan_ids':fields.one2many('hr_recruit.jurusan','permohonan_recruit_id','jurusan'),
        'pengalaman':fields.integer('Pengalaman (min-th)'),
        'usia':fields.integer('Usia (max)'),
        'sts_prk':fields.selection([('Belum_Menikah','Belum Menikah'),('Menikah','Menikah')],'Status Pernikahan'),
        'kelamin':fields.selection([('Laki-laki','Laki-Laki'),('Perempuan','Perempuan'),('Laki-Laki/Perempuan','Laki-Laki / Perempuan')],'Jenis Kelamin'),
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
    _rec_name = 'partner_name'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    
    _default = {
        'tanggal': lambda *a : time.strftime('%Y'),
             }    
    
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
                pes=self.browse(cr,uid,ids)[0]
                coy=pes.partner_name
                le=self.pool.get('hr_recruit.suskel1')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)
                prod_ids=[]              
                for pr in lele:
                    prod_ids.append((0,0, {'name':pr.name,'jenis_kel':pr.jenis_kel,'tmp_lahir':pr.tmp_lahir,'tgl_lahir':pr.tgl_lahir,'pendidikan':pr.pendidikan,'pekerjaan':pr.pekerjaan}))
                le=self.pool.get('hr_recruit.suskel2')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids1=[]   
                for pr in lele:
                    prod_ids1.append((0,0, {'susunan':pr.susunan,'name':pr.name,'jenis_kel':pr.jenis_kel,'tmp_lahir':pr.tmp_lahir,'tgl_lahir':pr.tgl_lahir,'pendidikan':pr.pendidikan,'pekerjaan':pr.pekerjaan}))          
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
                                                     'address_home_id': address_id,
                                                     'department_id': applicant.department_id.id,
                                                     'tmp_lahir' : applicant.tmp_lahir,
                                                     'tgl_lahir' : applicant.tgl_lahir,
                                                     'agama' : applicant.agama,
                                                     'country_id' : applicant.country_id.id,
                                                     'ktp' : applicant.ktp,
                                                     'dikeluarkan' : applicant.dikeluarkan,
                                                     'tgl_keluar_ktp' : applicant.tgl_keluar_ktp,
                                                     'tgl_berlaku' : applicant.tgl_berlaku,
                                                     'sim' : applicant.sim,
                                                     'tgl_keluar_sim' : applicant.tgl_keluar_sim,
                                                     'alamat1' : applicant.alamat1,
                                                     'alamat2' : applicant.alamat2,
                                                     'telp1' : applicant.telp1,
                                                     'telp2' : applicant.telp2,
                                                     'status': applicant.status,
                                                     'sjk_tanggal' : applicant.sjk_tanggal,
                                                     'kelamin' : applicant.kelamin,
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
    
    #def sorting(self, cr, uid,vals, context=None):  
     #   import pdb;pdb.set_trace()  
      #  sor=vals['tgl_lahir']
       # jbulan= time.strftime('%Y')
       # vals['tanggal']=ya    
       # sort=vals['tanggal']
        #sor=self.browse(cr, uid, vals['usia'], context=context)
        #sor_umur=sor.usia
        #job=self.pool.get('hr.job')
        #per=job.search(cr,uid,[])
        #per=job.browse(cr,uid,['job_id'],context)
        #umur=per.usia
        #pendidikan=per.type_id.id
        #semester=vals['semester']
        #tahun_ajaran=vals['tahun_ajaran']
        #kurikulum=self.pool.get('master.kurikulum')        
        #kur_id=kurikulum.search(cr, uid,[('prodi_id','=',prodi_id),('semester','=',semester),('tahun_ajaran','=',tahun_ajaran)])       
        #kur=kurikulum.browse(cr,uid,kur_id,context)[0]
        #mk_ids=[]
        #for mk in kur.kurikulum_detail_ids:
        #    mk_ids.append((0,0, {'mata_kuliah_id':mk.mata_kuliah_id.id,'sks':mk.sks}))
        #vals['krs_detail_ids']=mk_ids    
        #return vals
    
    #def create(self, cr, uid, vals, context=None):       
     #   vals=self.sorting(cr, uid, vals, context=None)
      #  result= super(krs,self).create (cr, uid, vals, context=None)
       # return result 
    
    def _compute_age(self, cr, uid, ids, field_name, field_value, context=None):
        import pdb;pdb.set_trace()
        records = self.browse(cr, uid, ids, context=context)[0]
        result={}
        for r in records:
            age=0
            if r.usia:
                d = strptime(r.date_birth,"%Y-%m-%d")
                count = date(d[0],d[1],d[2])-date.today()
                age = count.days/365 
            result[r.id] = age
        return result
        
    
    _columns= {
        'usia' : fields.function(_compute_age,'Usia'),
        'kelamin' : fields.selection([('P','Pria'),('W','Wanita')], 'Jenis Kelamin' ),
        'tmp_lahir':fields.char('Tempat Lahir',50),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'agama':fields.selection([('Islam','Islam'),('Kristen','Kristen'),('Budha','Budha'),('Hindu','Hindu'),('Kepercayaan','Kepercayaan')],'Agama'),
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
        'status':fields.selection([('Lajang','Lajang'),('Menikah','Menikah'),('Bercerai','Bercerai')],'Status Pernikahan'),
        'sjk_tanggal':fields.date('Sejak Tanggal'),
        'pengalaman' : fields.integer("pengalaman Kerja"),        
        'susunan_kel1_ids':fields.one2many('hr_recruit.suskel1','applicant_id','Susunan Keluarga'),
        'susunan_kel2_ids':fields.one2many('hr_recruit.suskel2','applicant_id','Susunan Keluarga'),
        'rwt_pend_ids':fields.one2many('hr_recruit.rwt_pend','applicant_id','Riwayat Pendidikan'),
        'bahasa_ids':fields.one2many('hr_recruit.bahasa','applicant_id','Bahasa'),
        'rwt_krj_ids':fields.one2many('hr_recruit.rwt_krj','applicant_id','Rwayat Pekerjaan'),
        'koneksi1_ids':fields.one2many('hr_recruit.kon1','applicant_id','Koneksi Internal'),
        'koneksi2_ids':fields.one2many('hr_recruit.kon2','applicant_id','Koneksi Eksternal'),
        'keahlian_ids' : fields.one2many('hr.keahlian','applicant_id', 'Keahlian'),
        'tanggal':fields.date('Tanggal Sekarang')
        }
      
    
hr_applicant()

class keahlian(osv.osv):
    _name='hr.keahlian'
    
    _columns ={
        'applicant_id' : fields.many2one('hr.applicant'),
        'name' : fields.char('Keahlian')
    }
keahlian()

class susunan_keluarga1(osv.osv):
    _name='hr_recruit.suskel1'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),
        'name':fields.char('Nama',required=True),
        'jenis_kel':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'tmp_lahir':fields.char('Tempat Lahir',50),
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
        'tmp_lahir':fields.char('Tempat Lahir',50),
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
        'tempat':fields.char('Tempat',30),
        'tahun':fields.char('Dari-Sampai tahun',11),
        'ijazah':fields.char('Ijazah yang Diperoleh',100),
            }
rwt_pendidikan()      

class bahasa(osv.osv):
    _name='hr_recruit.bahasa'
    
    _columns= {
        'applicant_id':fields.many2one('hr.applicant'),        
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




