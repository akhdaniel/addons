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

    def on_change_koperasi(self, cr, uid, ids, hutang_koperasi, context=None):
        values = {}
        values = {
            'sisa_tunggakan': hutang_koperasi
        }
        return {'value' : values}

    def on_change_perusahaan(self, cr, uid, ids, hutang_perusahaan, context=None):
        values = {}
        values = {
            'sisa_tunggakan2': hutang_perusahaan
        }
        return {'value' : values}

    def on_change_denda(self, cr, uid, ids, denda_kelalaian, context=None):
        values = {}
        values = {
            'sisa_denda': denda_kelalaian
        }
        return {'value' : values}

    _columns = {
    	'work_location2'		: fields.selection([('lucas','Lucas'),('marin','Marin')],'Lokasi Kerja'), 
    	'kelas'					: fields.many2one('hr.kelas.jabatan','Kelas Jabatan'),   
    	'hutang_koperasi'		: fields.float('Hutang Ke Koperasi'),
    	'pembayaran'			: fields.integer('Lama Cicilan'),
 		'sisa_tunggakan'		: fields.float('Sisa Hutang'),
    	'hutang_perusahaan'		: fields.float('Hutang Ke Perusahaan'),
    	'pembayaran2'			: fields.integer('Lama Cicilan'),
    	'sisa_tunggakan2'		: fields.float('Sisa Hutang'),
        'denda_kelalaian'       : fields.float('Denda Kelalaian'),
        'cicilan'               : fields.integer('Lama Cicilan'),
        'sisa_denda'            : fields.float('Sisa Denda'),
        'date_to_koperasi'      : fields.date('hahah'),#jagan di hapus, nanti eror
        
    }
employee()

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
                if field == 'work_location2' or field == 'gol_id' or field == 'active' or field == 'job_id' or field == 'department_id' or field == 'employee_id' or field == 'type_id' :
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
                    sts_kerja = key in new_values and new_values[key]['value'].get('type_id')
                    if sts_kerja != False :
                        sts_kerja = sts_kerja[1]
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