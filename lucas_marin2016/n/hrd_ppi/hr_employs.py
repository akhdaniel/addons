from openerp.osv import fields, osv
import datetime
import time
from datetime import date
from time import strptime
from time import strftime
from datetime import datetime
from openerp.osv.osv import object_proxy
from openerp.tools.translate import _
from openerp import pooler
from openerp import tools
from openerp import SUPERUSER_ID

class employee(osv.osv):
    _name = "hr.employee"
    _inherit = 'hr.employee'

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
       
    def _compute_age(self, cr, uid, ids, usia, birthday, arg, context=None):
        #import pdb;pdb.set_trace()
        # Fetch data structure and store it in object form
        records = self.browse(cr, uid, ids, context=context)
        result = {}
        # For all records in 'ids'
        for r in records:
            # In case 'birthdate' field is null
            usia = 0
            # If 'birthdate' field not null
            if r.birthday:
                # Encode string from 'birthdate' attribute
                d = strptime(r.birthday,"%Y-%m-%d")
                # Compute age as a time interval
                #delta = date(d[0], d[1], d[2]) - date.today()
                delta = date.today() - date(d[0], d[1], d[2])
                # Convert time interval to string value
                usia = delta.days / 365
            result[r.id] = usia
        return result    
           
    
    _columns = {
        'nik': fields.char('NIK',20),
        'kelamin':fields.selection([('male','Male'),('female','Female')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'agama':fields.many2one('hr_recruit.agama','Agama'),
        'birthday':fields.date('Tanggal Lahir'),
        'country_id': fields.many2one('res.country', 'Kewarganegaraan'),
        'ktp':fields.char('No ID',20),
        'no_pass':fields.char('No Passport',30),
        'no_rek':fields.char('No. Rekening',20),
        'no_sim':fields.char('No. SIM',30),
        'no_sima':fields.char('No. SIM A',30),
        'no_simc':fields.char('No. SIM C',30),
        'issued_id2':fields.many2one('res.country','Dikeluarkan di Negara'),
        'issued_id':fields.many2one('hr_recruit.issued','Dikeluarkan di'),
        'tgl_keluar_ktp':fields.date('Tanggal Dikeluarkan',),
        'tgl_berlaku':fields.date('Tanggal Berlaku'),
        'sim':fields.selection([('A','A'),('B1','B1'),('B2','B2'),('C','C')],'SIM'),
        'tgl_keluar_sim':fields.date('Tanggal Dikeluarkan SIM'),
        'tgl_keluar_sima':fields.date('Tanggal Dikeluarkan SIM A'),
        'tgl_keluar_simc':fields.date('Tanggal Dikeluarkan SIM C'),
        'type_id': fields.many2one('hr.recruitment.degree', 'Degree'),
        'jurusan_id':fields.many2one('hr_recruit.jurusan_detail','Jurusan'),
        'result_id':fields.many2one('hr_recruit.result','Result'),
        'gelar_id':fields.many2one('hr_recruit.gelar','Pendidikan'),
        'alamat1':fields.char('Alamat',100),
        'prov_id':fields.many2one('hr_recruit.prov','Provinsi', domain="[('country_id','=',country_id1)]"),
        'kab_id':fields.many2one('hr_recruit.kota','Kab./kota', domain="[('provinsi_id','=',prov_id)]"),
        'kec_id':fields.many2one('hr_recruit.issued','Kecamatan', domain="[('kota_id','=',kab_id)]"),
        'alamat2':fields.char('Alamat',100),
        'prov_id2':fields.many2one('hr_recruit.prov','Provinsi', domain="[('country_id','=',country_id2)]"),
        'kec_id2':fields.many2one('hr_recruit.issued','Kecamatan', domain="[('kota_id','=',kab_id2)]"),
        'telp1':fields.char('Telepon',50),
        'telp2':fields.char('Telepon',50),
        'status':fields.selection([('single','Single'),('married','Menikah'),('duda','Duda'),('janda','Janda')],'Status Pernikahan'),
        'jml_anak':fields.integer('Jumlah Tanggungan'),
        'sjk_tanggal':fields.date('Sejak Tanggal'),        
        'employee_id' :fields.many2one('hr.employee'),
        'clas_id':fields.many2one('hr_employs.clas','Level'),
        'title_id':fields.many2one('hr.title','Title/Jabatan'),
        'extitle_id':fields.many2one('hr.extitle','Ex Title'),
        'gol_id':fields.many2one('hr_employs.gol','Golongan'),
        'wfield_id':fields.many2one('hr_employs.wfield','Bidang Pekerjaan'),
        'pansion_id':fields.many2one('hr_employs.pansion','Masa Pensiun'),
        'susunan_kel1_ids':fields.one2many('hr_employee.suskel1','employee_id','Susunan Keluarga'),
        'susunan_kel2_ids':fields.one2many('hr_employee.suskel2','employee_id','Susunan Keluarga'),
        'rwt_pend_ids':fields.one2many('hr_employee.rwt_pend','employee_id','Riwayat Pendidikan'),
        'bahasa_ids':fields.one2many('hr_employee.bahasa','employee_id','Bahasa'),
        'rwt_krj_ids':fields.one2many('hr_employee.rwt_krj','employee_id','Riwayat Pekerjaan'),
        'koneksi1_ids':fields.one2many('hr_employee.kon1','employee_id','Koneksi Internal'),
        'koneksi2_ids':fields.one2many('hr_employee.kon2','employee_id','Koneksi Eksternal'),
        'blood':fields.selection([('A','A'),('B','B'),('AB','AB'),('O','O')],'Gol Darah'),
        'bahasa2_id':fields.many2one('hr_recruit.bahasa2','Bahasa'),
        'kab_id2':fields.many2one('hr_recruit.kota','Kota', domain="[('provinsi_id','=',prov_id2)]"),
        'country_id2': fields.many2one('res.country', 'Negara'),
        'kodepos':fields.char('Kode Pos',8),
	    'kodepos1':fields.char('Kode Pos',8),
        'jenis_id':fields.selection([('Rek.Bank','Rekening Bank'),('KTP','Kartu Tanda Penduduk'),('Passport','Passport'),('SIM','SURAT IZIN MENGEMUDI'),('SIM_A','Surat Izin Mengemudi A'),('SIM_C','Surat Izin Mengemudi C')],'Jenis ID'),
        'pt_id':fields.many2one('hr_recruit.pt','Perguruan Tinggi'),
        'bidang_id':fields.related('jurusan_id','bidang_id',type='char',relation='hr_recruit.jurusan_detail',string='Bidang',readonly=True,store=True),  
	    'country_id1':fields.many2one('res.country','Negara'),
        'country_id2':fields.many2one('res.country','Negara'),
        'address_id2': fields.many2one('res.partner', 'Nama Kantor'),
        'work_location2': fields.selection([('karawang','Karawang'),('tanggerang','Jakarta')],'Lokasi Kerja',required=True), 
        'usia':fields.function(_compute_age, type='integer', obj='hr.employee', method=True, store=False, string='Usia (Thn)', readonly=True),        
        'ptkp_id': fields.many2one('hr.ptkp','Status Pajak', required=True),
        'npwp':fields.char('NPWP',size=20),
        'bid_id':fields.many2one('hr_recruit.bidang','Bidang'), 
        'wage':fields.float('Proposed Salary'), 
        'npp' :fields.integer('NPP', help="Nomor Pokok Perusahaan"),
        'npkj' :fields.integer('NPKJ', help='Nomor Kepesertaan Jamsostek'), 
        'remaining_leaves' :fields.float('Remaining Legal Leavs',readonly=True),  
        'tgl_masuk' :fields.date('Tanggal Masuk'),
        'hierarcy_history' : fields.one2many('hr.hierarcy_history','employee_id','Hieracy History', readonly=True),
        'work_email' : fields.char('Email Kantor'),
        'work_phone' : fields.char('Telepon Kantor'),
        'coach_id' : fields.many2one('hr.employee', '',readonly=True),
        #'status_contract' : fields.selection(([('aktif','Aktif'),('hampir_habis','Hampir Habis'),('nonaktif','Tidak Aktif')],'Jenis Kelamin'),
        }

    _defaults = {    
        'nik': lambda self, cr, uid, context={}: self.pool.get('ir.sequence').get(cr, uid, 'hr.employee'),
        'jenis_id': 'KTP',
        'tgl_masuk' : lambda *a: time.strftime('%Y-%m-%d'),
                }
        
    def onchange_alamat(self, cr, uid, ids, address_id2, context=None):
        result = {}
        result2 = {}
        result3 = {}

        if address_id2:
            #import pdb;pdb.set_trace()
            address_id2_obj = self.pool.get('res.partner')
            result['street'] = address_id2_obj.browse(cr, uid, address_id2, context=context).street
            result2['phone'] = address_id2_obj.browse(cr, uid, address_id2, context=context).phone
            result3['email'] = address_id2_obj.browse(cr, uid, address_id2, context=context).email
            return {'value':{'work_location2': result['street'],'work_phone': result2['phone'],'work_email': result3['email']}}
        return {'value': {'work_location2': False,'work_phone': False,'work_email': False}}                 
employee()

class hierarcy_history(osv.osv):
    _name = 'hr.hierarcy_history'

    _columns= {
        'employee_id' : fields.many2one('hr.employee'),
        'status_karyawan' : fields.selection([('aktif','Aktif'),('tidak_aktif','Tidak Aktif')],'Status Aktif'),
        'tgl' : fields.date('Tanggal Perubahan'),
        'status_kerja' : fields.char('Status Pegawai'),
        'golongan' :fields.many2one('hr_employs.gol','Golongan'),
        'jabatan' : fields.many2one('hr.job','Jabatan'),
        'dept_track' :fields.many2one('hr.department','Department'),
        'lokasi' : fields.char('Lokasi'),
    }

class susunan_keluarga1(osv.osv):
    _name='hr_employee.suskel1'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
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
    _name='hr_employee.suskel2'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'susunan':fields.selection([('Ayah','Ayah'),('Ibu','Ibu'),('anak1','Anak ke-1'),('anak2','Anak ke-2'),('anak3','Anak ke-3'),('anak4','Anak ke-4'),('anak5','Anak ke-5'),('anak6','Anak ke-6')],'Status Dalam Keluarga'),
        'name':fields.char('Nama'),
        'kelamin':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'type_id':fields.many2one('hr.recruitment.degree', 'Pendidikan',50),
        'pekerjaan':fields.char('Pekerjaan',60),
            }
susunan_keluarga2()   

class rwt_pendidikan(osv.osv):
    _name='hr_employee.rwt_pend'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama Sekolah',128,required=True),
        'jurusan':fields.many2one('hr_recruit.jurusan_detail','Jurusan'),
        'tempat':fields.text('Alamat'),
        'tahun_msk':fields.date('Tahun Masuk'),
        'tahun_klr':fields.date('Tahun Keluar'),
        'ijazah':fields.many2one('hr.recruitment.degree','Ijazah yang Diperoleh'),
            }
rwt_pendidikan()      

class bahasa(osv.osv):
    _name='hr_employee.bahasa'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee','Applicant'),        
        'name':fields.many2one('res.country', 'Bahasa',required=True),
        'tulis':fields.many2one('hr_recruit.b_tulisan','Tertulis'),
        'lisan':fields.many2one('hr_recruit.b_lisan','Lisan'),
            }
bahasa()    

class rwt_pekerjaan(osv.osv):
    _name='hr_employee.rwt_krj'
    
    _columns= {
        'no':fields.integer('Nomor'),
        'employee_id':fields.many2one('hr.employee'), 
        'name':fields.char('Nama Perusahaan',60,required=True),
        'tempat':fields.text('Alamat'),
        'tahun_msk':fields.date('Tahun Masuk'),
        'tahun_klr':fields.date('Tahun Keluar'),
        'jabatan':fields.char('Jabatan',30),
        'gaji':fields.float('Gaji'),
        'alasan':fields.char('Alasan Pindah',30),
            }
rwt_pekerjaan()

class koneksi1(osv.osv):
    _name='hr_employee.kon1'
    
    _columns={        
        'employee_idd':fields.char('Nama',),
        'employee_id':fields.many2one('hr.employee','Nama',required=True),
        'job_id':fields.related('employee_id','job_id',type='many2one',relation='hr.job',string='Jabatan',readonly=True),
        'alamat':fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='departmen',readonly=True), 
        'telepon':fields.char('Telepon',25),
            }
koneksi1()

class koneksi2(osv.osv):
    _name='hr_employee.kon2'
    
    _columns={        
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama',60),
        'alamat':fields.text('Alamat/Telepon'),
        'jabatan':fields.char('Jabatan',30),
        'telepon':fields.char('Telepon',25),
            }
koneksi2()

class bahasa2(osv.osv):
    _name='hr_recruit.bahasa2'
    
    _columns= {       
        'name':fields.char('Nama Bahasa',30,required=True),
            }
bahasa2()

class clas(osv.osv):
    _name='hr_employs.clas'
    
    _columns= {       
        'name':fields.char('Class',50,required=True),
            }
clas()

class title(osv.osv):
    _name='hr_employs.title'
    
    _columns= {       
        'name':fields.char('Title',50,required=True),
            }
title()

class extitle(osv.osv):
    _name='hr_employs.extitle'
    
    _columns= {       
        'name':fields.char('Ex Title',50,required=True),
            }
extitle()

class golongan(osv.osv):
    _name='hr_employs.gol'
    
    _columns= {       
        'name':fields.char('Golongan',20,required=True),
        'rec':fields.char('record'),
        'no' : fields.char('Urutan')
            }
golongan()

class wfield(osv.osv):
    _name='hr_employs.wfield'
    
    _columns= {       
        'name':fields.char('Bidang Pekerjaan',50,required=True),
            }
wfield()

class pansion(osv.osv):
    _name='hr_employs.pansion'
    
    _columns= {       
        'name':fields.char('Masa Pensiun',50,required=True),
            }
pansion()

class employee_objects_proxy(object_proxy):

    def get_value_text(self, cr, uid, pool, resource_pool, method, field, value):
        field_obj = (resource_pool._all_columns.get(field)).column
        if field_obj._type in ('one2many','many2many'):
            data = pool.get(field_obj._obj).name_get(cr, uid, value)
            #return the modifications on x2many fields as a list of names
            res = map(lambda x:x[1], data)
        elif field_obj._type == 'many2one':
            #return the modifications on a many2one field as its value returned by name_get()
            res = value #and value[1] or value
        else:
            res = value
        return res

    def log_fct(self, cr, uid_orig, model, method, fct_src, *args, **kw):
        """
        Logging function: This function is performing the logging operation
        @param model: Object whose values are being changed
        @param method: method to log: create, read, write, unlink, action or workflow action
        @param fct_src: execute method of Object proxy

        @return: Returns result as per method of Object proxy
        """
        #import pdb;pdb.set_trace()
        pool = pooler.get_pool(cr.dbname)
        resource_pool = pool.get(model)
        model_pool = pool.get('ir.model')
        model_ids = model_pool.search(cr, SUPERUSER_ID, [('model', '=', model)])
        model_id = model_ids and model_ids[0] or False
        assert model_id, _("'%s' Model does not exist..." %(model))
        model = model_pool.browse(cr, SUPERUSER_ID, model_id)

        # fields to log. currently only used by log on read()
        field_list = []
        old_values = new_values = {}
        #else: # method is write, action or workflow actions
        if method == 'create':
            res = fct_src(cr, uid_orig, model.model, method, *args, **kw)
            if res:
                res_ids = [res]
                new_values = self.get_data(cr, uid_orig, pool, res_ids, model, method)
        else :
            res_ids = []
            if args:
                res_ids = args[0]
                if isinstance(res_ids, (long, int)):
                    res_ids = [res_ids]
            if res_ids:
                # store the old values into a dictionary
                old_values = self.get_data(cr, uid_orig, pool, res_ids, model, method)
            # process the original function, workflow trigger...
            res = fct_src(cr, uid_orig, model.model, method, *args, **kw)
            if method == 'copy':
                res_ids = [res]
            if res_ids:
                # check the new values and store them into a dictionary
                new_values = self.get_data(cr, uid_orig, pool, res_ids, model, method)
        #import pdb;pdb.set_trace()
        # compare the old and new values and create audittrail log if need
        self.process_data(cr, uid_orig, pool, res_ids, model, method, old_values, new_values, field_list)
        return res

    def get_data(self, cr, uid, pool, res_ids, model, method):
        #import pdb;pdb.set_trace()
        data = {}
        resource_pool = pool.get(model.model)
        # read all the fields of the given resources in super admin mode
        for resource in resource_pool.read(cr, SUPERUSER_ID, res_ids, resource_pool._all_columns):
            values = {}
            values_text = {}
            resource_id = resource['id']
            # loop on each field on the res_ids we just have read
            for field in resource:
                if field == 'work_location2' or field == 'gol_id' or field == 'active' or field == 'job_id' or field == 'department_id' :
                    #import pdb;pdb.set_trace()
                    if field in ('__last_update', 'id'):
                        continue
                    values[field] = resource[field]
                    # get the textual value of that field for this record
                    values_text[field] = self.get_value_text(cr, SUPERUSER_ID, pool, resource_pool, method, field, resource[field])

                    field_obj = resource_pool._all_columns.get(field).column
                    if field_obj._type in ('one2many','many2many'):
                        #import pdb;pdb.set_trace()
                        # check if an audittrail rule apply in super admin mode
                        #if self.check_rules(cr, SUPERUSER_ID, field_obj._obj, method):
                            # check if the model associated to a *2m field exists, in super admin mode
                        x2m_model_ids = pool.get('ir.model').search(cr, SUPERUSER_ID, [('model', '=', field_obj._obj)])
                        x2m_model_id = x2m_model_ids and x2m_model_ids[0] or False
                        assert x2m_model_id, _("'%s' Model does not exist..." %(field_obj._obj))
                        x2m_model = pool.get('ir.model').browse(cr, SUPERUSER_ID, x2m_model_id)
                        field_resource_ids = list(set(resource[field]))
                        if model.model == x2m_model.model:
                            #import pdb;pdb.set_trace()
                            if model.model != 'res.partner' and model.model != 'res.company' :
                            # we need to remove current resource_id from the many2many to prevent an infinit loop
                                if resource_id in field_resource_ids:
                                    field_resource_ids.remove(resource_id)
                        if model.model != 'res.partner' and model.model != 'res.company' :
                            data.update(self.get_data(cr, SUPERUSER_ID, pool, field_resource_ids, x2m_model, method))
            data[(model.id, resource_id)] = {'text':values_text, 'value': values}
        return data 

    def prepare_audittrail_log_line(self, cr, uid, pool, model, resource_id, method, old_values, new_values, field_list=None):
        if field_list is None:
            field_list = []
        key = (model.id, resource_id)
        lines = {
            key: []
        }
        #search id
        dates =datetime.now()
        # loop on all the fields
        #import pdb;pdb.set_trace()
        for field_name, field_definition in pool.get(model.model)._all_columns.items():
            if field_name in ('__last_update', 'id'):
                continue
            #if the field_list param is given, skip all the fields not in that list
            if field_list and field_name not in field_list:
                continue
            field_obj = field_definition.column
            if model.model == 'hr.contract' :
                if field_name == 'type_id' :
                    employee = key in new_values and new_values[key]['value'].get('employee_id')[1]
                    objk = pool.get('hr.employee')
                    src = objk.search(cr,uid,[('name','=',employee)])
                    brw = objk.browse(cr,uid,src)[0]
                    emp = brw.id
                    sts_kerja = key in new_values and new_values[key]['value'].get('type_id')[1]
                    gol = brw.gol_id.id
                    jab = brw.job_id.id
                    dep = brw.department_id.id
                    lokasi = brw.work_location2
            if model.model == 'hr.employee' :
                    if field_name == 'work_location2' or field_name == 'gol_id' or method == 'create' or field_name == 'active' or field_name == 'job_id' or field_name == 'department_id' :
                        employee = key in new_values and new_values[key]['value'].get('name')
                        objs = pool.get('hr.hierarcy_history')
                        srcs = objs.search(cr,uid,[('employee_id','=',employee)])
                        brws = objs.browse(cr,uid,srcs)
                        obj = pool.get('hr.contract')
                        src = obj.search(cr,uid,[('employee_id','=',employee)])
                        brw = obj.browse(cr,uid,src)
                        if brw == [] :
                            sts_kerja = ''
                        else :
                            brw = obj.browse(cr,uid,src)[0]
                            sts_kerja = brw.type_id.name   
                        if key in new_values and new_values[key]['value'].get('gol_id') == False :
                            gol = False
                        else :
                            gol = key in new_values and new_values[key]['value'].get('gol_id')[0]
                        if key in new_values and new_values[key]['value'].get('job_id') == False :
                            jab = False
                        else :
                            jab = key in new_values and new_values[key]['value'].get('job_id')[0]
                        if key in new_values and new_values[key]['value'].get('department_id') == False :
                            dep = False
                        else :
                            dep = key in new_values and new_values[key]['value'].get('department_id')[0]
                        # for new hierarcy history
                        if key in new_values and new_values[key]['value'].get('work_location2') == False :
                            lokasi = ""
                        else :
                            lokasi = key in new_values and new_values[key]['value'].get('work_location2')
                        if brws == [] :
                            if key in old_values and old_values[key]['value'].get('gol_id') == False :
                                gol1 = False
                            else :
                                gol1 = old_values and old_values[key]['value'].get('gol_id')[0]
                            if key in old_values and old_values[key]['value'].get('job_id') == False :
                                jab1 = False
                            else :
                                jab1 = old_values and old_values[key]['value'].get('job_id')[0]
                            if key in old_values and old_values[key]['value'].get('department_id') == False :
                                dep1 = False
                            else :
                                dep1 = old_values and old_values[key]['value'].get('department_id')[0]
                            if key in new_values and new_values[key]['value'].get('work_location2') == False :
                                lokasi = ""
                            else :
                                lokasi = key in new_values and new_values[key]['value'].get('work_location2')
            if field_obj._type in ('one2many','many2many'):
                # checking if an audittrail rule apply in super admin mode
                #if self.check_rules(cr, SUPERUSER_ID, field_obj._obj, method):
                    # checking if the model associated to a *2m field exists, in super admin mode
                x2m_model_ids = pool.get('ir.model').search(cr, SUPERUSER_ID, [('model', '=', field_obj._obj)])
                x2m_model_id = x2m_model_ids and x2m_model_ids[0] or False
                assert x2m_model_id, _("'%s' Model does not exist..." %(field_obj._obj))
                x2m_model = pool.get('ir.model').browse(cr, SUPERUSER_ID, x2m_model_id)
                # the resource_ids that need to be checked are the sum of both old and previous values (because we
                # need to log also creation or deletion in those lists).
                x2m_old_values_ids = old_values.get(key, {'value': {}})['value'].get(field_name, [])
                x2m_new_values_ids = new_values.get(key, {'value': {}})['value'].get(field_name, [])
                # We use list(set(...)) to remove duplicates.
                res_ids = list(set(x2m_old_values_ids + x2m_new_values_ids))
                if model.model == x2m_model.model:
                    # we need to remove current resource_id from the many2many to prevent an infinit loop
                    if resource_id in res_ids:
                        res_ids.remove(resource_id)
                for res_id in res_ids:
                    lines.update(self.prepare_audittrail_log_line(cr, SUPERUSER_ID, pool, x2m_model, res_id, method, old_values, new_values, field_list))
            # if the value value is different than the old value: record the change
            #import pdb;pdb.set_trace()
            if key not in old_values or key not in new_values or old_values != new_values:
                if model.model == 'hr.employee' :
                    if field_name == 'work_location2' or field_name == 'gol_id' or method == 'create' or field_name == 'active' or field_name == 'job_id' or field_name == 'department_id' :
                        act = key in new_values and new_values[key]['value'].get('active')
                        if act == True :
                            status = 'aktif'
                        else :
                            status = 'tidak_aktif'
                        data = {
                              'employee_id': resource_id,
                              'tgl' : dates,
                              'status_karyawan': status,
                              'status_kerja' : sts_kerja,
                              'golongan': gol,
                              'jabatan': jab,
                              'dept_track': dep,
                              'lokasi' : lokasi,
                        }
                        if brws == [] :
                            data1 = {
                                  'employee_id': resource_id,
                                  'tgl' : dates,
                                  'status_karyawan': status,
                                  'status_kerja' : sts_kerja,
                                  'golongan': gol1,
                                  'jabatan': jab1,
                                  'dept_track': dep1,
                                  'lokasi' : lokasi,
                            }
                            pool.get('hr.hierarcy_history').create(cr, SUPERUSER_ID, data1)
                        return pool.get('hr.hierarcy_history').create(cr, SUPERUSER_ID, data)
                if model.model == 'hr.contract' :
                    if field_name == 'type_id' :
                        data = {
                            'employee_id': emp,
                            'tgl' : dates,
                            'status_karyawan': 'aktif',
                            'status_kerja' : sts_kerja,
                            'golongan': gol,
                            'jabatan': jab,
                            'dept_track': dep,
                            'lokasi' : lokasi,
                        }
                        return pool.get('hr.hierarcy_history').create(cr, SUPERUSER_ID, data)
        return lines
    def process_data(self, cr, uid, pool, res_ids, model, method, old_values=None, new_values=None, field_list=None):
        #import pdb;pdb.set_trace()
        if field_list is None:
            field_list = []
        # loop on all the given ids
        for res_id in res_ids:
            # compare old and new values and get audittrail log lines accordingly
            lines = self.prepare_audittrail_log_line(cr, uid, pool, model, res_id, method, old_values, new_values, field_list)
        return True

    def execute_cr(self, cr, uid, model, method, *args, **kw):
        fct_src = super(employee_objects_proxy, self).execute_cr
        if model == 'hr.employee' and method == 'write' :
            return self.log_fct(cr, uid, model, method, fct_src, *args, **kw)
        if model == 'hr.contract':
            if method == 'write' or method == 'create' :
                return self.log_fct(cr, uid, model, method, fct_src, *args, **kw)
        return fct_src(cr, uid, model, method, *args, **kw)

employee_objects_proxy()
