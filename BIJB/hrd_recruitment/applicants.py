from datetime import datetime
from datetime import date
from openerp import tools
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from time import strptime
from time import strftime
from openerp.tools.translate import _


class hr_applicant(osv.osv):
    _name='hr.applicant'
    _inherit='hr.applicant'
    _rec_name='partner_name'

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

    def create_employee_from_applicant(self, cr, uid, ids, context=None):
        """ Create an hr.employee from the hr.applicants """
        if context is None:
            context = {}
        hr_employee = self.pool.get('hr.employee')
        model_data = self.pool.get('ir.model.data')
        act_window = self.pool.get('ir.actions.act_window')
        emp_id = False
        for applicant in self.browse(cr, uid, ids, context=context):
            address_id = contact_name = False
            if applicant.partner_id:
                address_id = self.pool.get('res.partner').address_get(cr, uid, [applicant.partner_id.id], ['contact'])['contact']
                contact_name = self.pool.get('res.partner').name_get(cr, uid, [applicant.partner_id.id])[0][1]
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                create_ctx = dict(context, mail_broadcast=True)

                pes=self.browse(cr,uid,ids)[0]
                coy=pes.partner_name

                ##### Susunan Keluarga ayah/ibu #####
                le=self.pool.get('hr_recruit.suskel1')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)
                prod_ids=[]           
                for pr in lele:
                    prod_ids.append((0,0, {'name':pr.name,'kelamin':pr.kelamin,'kota_id':pr.kota_id.id,'tgl_lahir':pr.tgl_lahir,'type_id':pr.type_id.id,'pekerjaan':pr.pekerjaan,'susunan':pr.susunan}))
                
                ###### Susunan Keluarga Suami/istri #####
                le=self.pool.get('hr_recruit.suskel2')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids1=[]   
                for pr in lele:
                    prod_ids1.append((0,0, {'susunan':pr.susunan,'name':pr.name,'kelamin':pr.kelamin,'kota_id':pr.kota_id.id,'tgl_lahir':pr.tgl_lahir,'type_id':pr.type_id.id,'pekerjaan':pr.pekerjaan}))          
                
                ###### riwayat Pendidikan #######
                le=self.pool.get('hr_recruit.rwt_pend')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids2=[]   
                for pr in lele:
                    prod_ids2.append((0,0, {'name':pr.name,'jurusan':pr.jurusan.id,'tempat':pr.tempat,'tahun_msk':pr.tahun_msk,'tahun_klr':pr.tahun_klr,'ijazah':pr.ijazah.id})) 
                
                ###### bahasa ######
                le=self.pool.get('hr_recruit.bahasa')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids3=[]   
                for pr in lele:
                    prod_ids3.append((0,0, {'name':pr.name.id,'tulis':pr.tulis.id,'lisan':pr.lisan.id})) 
                
                ##### Riwayat Pekerjaan ####
                le=self.pool.get('hr_recruit.rwt_krj')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids4=[]   
                for pr in lele:
                    prod_ids4.append((0,0, {'no':pr.no,'name':pr.name,'tempat':pr.tempat,'tahun_msk':pr.tahun_msk,'tahun_klr':pr.tahun_klr,'jabatan':pr.jabatan,'gaji':pr.gaji,'alasan':pr.alasan})) 
                
                ###### Koneksi Internal #####
                le=self.pool.get('hr_recruit.kon1')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids5=[]   
                for pr in lele:
                    prod_ids5.append((0,0, {'employee_id':pr.employee_id.name,'alamat':pr.alamat,'job_id':pr.job_id.id,'telepon':pr.telepon})) 
                
                ###### Koneksi Eksternal ####
                le=self.pool.get('hr_recruit.kon2')
                lel=le.search(cr,uid,[('applicant_id','=',coy)])
                lele=le.browse(cr,uid,lel,context=context)   
                prod_ids6=[]
                for pr in lele:   
                    prod_ids6.append((0,0, {'name':pr.name,'alamat':pr.alamat,'jabatan':pr.jabatan,'telepon':pr.telepon}))  

                ####### create Employee ########  
                emp_id = hr_employee.create(cr, uid, {'name': applicant.partner_name or applicant.name,
                                                     'job_id': applicant.job_id.id,
                                                     'department_id' : applicant.department_id.id,
                                                     'address_id2' : applicant.job_id.address_id.id,
                                                     #### informasi Probadi ####
                                                     'kelamin':applicant.jen_kel,
                                                     'blood' : applicant.blood,
                                                     'agama' : applicant.agama_id.id,
                                                     'birthday' : applicant.tgl_lahir,
                                                     'place_of_birth' : applicant.kota_id.name,
                                                     'marital':applicant.status,
                                                     'sjk_tanggal' : applicant.sjk_tanggal,
                                                     'mobile_phone':applicant.partner_phone,
                                                     'country_id' : applicant.country_id.id,

                                                     #### Pendidikan ####
                                                     'type_id':applicant.type_id.id,
                                                     'bid_id':applicant.bidang_id.id,
                                                     'jurusan_id':applicant.jurusan_id.id,
                                                     'pt_id':applicant.pt_id.id,
                                                     'gelar_id':applicant.gelar_id.id,

                                                     #### alamat DOmisili ####
                                                     'country_id1':applicant.country_id1.id,
                                                     'prov_id':applicant.prov_id.id,
                                                     'kab_id' : applicant.kab_id.id,
                                                     'kec_id':applicant.kec_id.id,
                                                     'alamat1' : applicant.alamat1,
                                                     'kodepos' :applicant.kode1,
                                                     'telp1' : applicant.telp1,

                                                     #### kartu identitas ####
                                                     'jenis_id': applicant.jenis_id,
                                                     'ktp' : applicant.no_id,
                                                     'tgl_berlaku' : applicant.tgl_berlaku,
                                                     # 'issued_id' : applicant.dikeluarkan.id,
                                                     
                                                     #### Alamat Sesuai KTP #### 
                                                     'country_id2':applicant.country_id2.id,
                                                     'prov_id2':applicant.prov_id2.id,
                                                     'kab_id2':applicant.kab_id2.id,
                                                     'kec_id2':applicant.kec_id2.id,
                                                     'alamat2' : applicant.alamat2,
                                                     'kodepos1':applicant.kode2,
                                                     'telp2' : applicant.telp2,
                                                     
                                                     # 'status': applicant.status,
                                                     #### IDS ####
                                                     'susunan_kel1_ids' : prod_ids,
                                                     'susunan_kel2_ids':prod_ids1,
                                                     'rwt_pend_ids':prod_ids2,
                                                     'bahasa_ids':prod_ids3,
                                                     'rwt_krj_ids':prod_ids4,
                                                     'koneksi1_ids':prod_ids5,
                                                     'koneksi2_ids':prod_ids6,                                                     
                                                     })
                self.write(cr, uid, [applicant.id], {'emp_id': emp_id}, context=context)
                self.pool['hr.job'].message_post(
                    cr, uid, [applicant.job_id.id],
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired", context=context)
            else:
                raise osv.except_osv(_('Warning!'), _('You must define an Applied Job and a Contact Name for this applicant.'))

        action_model, action_id = model_data.get_object_reference(cr, uid, 'hr', 'open_view_employee_list')
        dict_act_window = act_window.read(cr, uid, [action_id], [])[0]
        if emp_id:
            dict_act_window['res_id'] = emp_id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window

    _columns= {
    	################## infomrasi Pribadi ###################
        'jen_kel':fields.selection([('L','Pria'),('W','Wanita')],'Jenis Kelamin',required=False),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir',required=False),
        'age': fields.function(_compute_age, type='integer', obj='hr.applicant', method=True, store=False, string='Usia (Thn)', readonly=True),
   		'agama_id':fields.many2one('hr_recruit.agama','Agama'),
        'country_id': fields.many2one('res.country', 'Kewarganegaraan'),
        'status':fields.selection([('single','Single'),('married','Menikah'),('divorced','Cerai')],'Status Pernikahan'),
        'sjk_tanggal':fields.date('Sejak Tanggal'), 
        'email_from': fields.char('Email', size=128, help="These people will receive email.", select=True),
        'partner_phone': fields.char('Phone', size=32),
    	"blood":fields.selection([('A','A'),('B','B'),('AB','AB'),('O','O')],'Gol Darah'),
    	'pengalaman':fields.integer('Pengalaman Kerja (min-th)'),
    	#######################################################

    	################# Pendidikan ################
    	'type_id': fields.many2one('hr.recruitment.degree', 'Pendidikan',required=False),
		'bidang_id':fields.many2one('hr_recruit.bidang','Fakultas'),
		'jurusan_id':fields.many2one('hr_recruit.jurusan_detail','Jurusan', domain="[('bidang_id','=',bidang_id)]"), 
		'pt_id':fields.many2one('hr_recruit.pt','Perguruan Tinggi'), 
		'gelar_id':fields.many2one('hr_recruit.gelar','Gelar'),
		#############################################

		################ Alamat Domisili ################
		'country_id1':fields.many2one('res.country','Negara'),
		'prov_id':fields.many2one('hr_recruit.prov','Provinsi',domain="[('country_id','=',country_id1)]"),
		'kab_id':fields.many2one('hr_recruit.kota','Kab./kota',domain="[('provinsi_id','=',prov_id)]"),
		'kec_id':fields.many2one('hr_recruit.issued','Kecamatan',domain="[('kota_id','=',kab_id)]"),
		'alamat1':fields.char('Alamat Domisili',100),  
		'kode1' :fields.char('Kode Pos'),      
		'telp1':fields.char('Telepon',50),
		#################################################
    	
    	############## Alamat Sesuai KTP ##############
    	'country_id2':fields.many2one('res.country','Negara'),
    	'prov_id2':fields.many2one('hr_recruit.prov','Provinsi', domain="[('country_id','=',country_id2)]"),
    	'kab_id2':fields.many2one('hr_recruit.kota','Kab./Kota', domain="[('provinsi_id','=',prov_id2)]"),
        'kec_id2':fields.many2one('hr_recruit.issued','Kecamatan', domain="[('kota_id','=',kab_id2)]"),
        'alamat2':fields.char('Alamat sesuai KTP',100),
        'kode2' :fields.char('Kode Pos'),
        'telp2':fields.char('Telepon',50),
		###############################################

		############## Kartu Identitas #################
		'jenis_id':fields.selection([('KTP','Kartu Tanda Penduduk'),('Passport','Passport')],'Jenis ID'),
		'no_id':fields.char('No.ID',20),
		'tgl_berlaku' :fields.date("Tanggal Berlaku"),
		'dikeluarkan' : fields.many2one('hr_recruit.kota', 'Dikeluarkan Di'),
        ################################################

        ##################### IDS One2many #################
        'susunan_kel1_ids':fields.one2many('hr_recruit.suskel1','applicant_id','Susunan Keluarga'),
        'susunan_kel2_ids':fields.one2many('hr_recruit.suskel2','applicant_id','Susunan Keluarga'),
        'rwt_pend_ids':fields.one2many('hr_recruit.rwt_pend','applicant_id','Riwayat Pendidikan'),
        'bahasa_ids':fields.one2many('hr_recruit.bahasa','applicant_id','Bahasa'),
        'rwt_krj_ids':fields.one2many('hr_recruit.rwt_krj','applicant_id','Riwayat Pekerjaan'),
        'koneksi1_ids':fields.one2many('hr_recruit.kon1','applicant_id','Referensi Internal'),
        'koneksi2_ids':fields.one2many('hr_recruit.kon2','applicant_id','Referensi Eksternal'),
        ####################################################

        'app_id' : fields.many2one('hr.job','Job'),
        
        #################### one2many calendar #############
        #'applicant_id':fields.many2one('calendar.event'),
        ####################################################
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
            
rwt_pekerjaan()

class koneksi1(osv.osv):
    _name='hr_recruit.kon1'
    
    _columns={        
        'applicant_id':fields.many2one('hr.applicant',),
        'employee_id':fields.many2one('hr.employee','Nama',required=True),
        'job_id':fields.related('employee_id','job_id',type='many2one',relation='hr.job',string='Jabatan',readonly=True),
        'alamat':fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='departmen',readonly=True), 
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

