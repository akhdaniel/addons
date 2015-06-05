import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import netsvc
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval
import math,pprint

class bln_libur(osv.osv):
    _name="hr.bln_libur"

    
    _columns = {
        'hol_ids':fields.one2many('hr.holidays','bln_libur_id','Tanggal Libur'),
        'name': fields.selection([('Libur','Libur Nasional')]),
    }
    _defaults={
        'name':'Libur',
    }
bln_libur()

class hr_holidays_status(osv.osv):
    _name = "hr.holidays.status"
    _inherit="hr.holidays.status"

    _columns={
        'libur_bersih':fields.boolean('Hitung Tanggal Merah'), 
        'is_5_years' :  fields.boolean('Cuti per 5 tahun masa kerja',readonly=True),
        'is_1_year' :  fields.boolean('Cuti per tahun',readonly=True),  
        'limit_cuti': fields.boolean('Limit Cuti',help="Ceklist jika cuti tidak bisa minus"),  
            }
            
    _defaults={
        'libur_bersih':False,
            }               
    
hr_holidays_status()
#referensi leave
D = datetime.strftime(datetime.now(), "%Y-%m-%d") #type:int
D_y = datetime.strptime(D,"%Y-%m-%d").year
D_m = datetime.strptime(D,"%Y-%m-%d").month
D_d = datetime.strptime(D,"%Y-%m-%d").day

class hr_holidays(osv.osv):
    _name = "hr.holidays"
    _description = "Leave"
    _inherit = "hr.holidays"

    def check_holidays(self, cr, uid, ids, context=None):
        holi_status_obj = self.pool.get('hr.holidays.status')
        for record in self.browse(cr, uid, ids):
            if record.holiday_type == 'employee' and record.type == 'remove':
                if record.employee_id and record.holiday_status_id.limit_cuti == True:
                    leaves_rest = holi_status_obj.get_days( cr, uid, [record.holiday_status_id.id], record.employee_id.id, False)[record.holiday_status_id.id]['remaining_leaves']
                    if leaves_rest < record.number_of_days_temp:
                        raise osv.except_osv(_('Warning!'), _('There are not enough %s allocated for employee %s; please create an allocation request for this leave type.') % (record.holiday_status_id.name, record.employee_id.name))
        return True

    def action_draft(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids)
        return self.write(cr,uid,ids,{'state':'confirm'},context=context)

    def create(self, cr, uid, values, context=None):
        """ Override to avoid automatic logging of creation """
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True)
        tipe = values['type']
        if tipe == 'remove' :
            date_from = values['date_from']
            date_to = values['date_to']
            month_from=datetime.strptime(date_from,'%Y-%m-%d %H:%M:%S').month
            month_to=datetime.strptime(date_to,'%Y-%m-%d %H:%M:%S').month
            if month_from != month_to :
                raise osv.except_osv(_('Warning!'),_('Bulan Harus Sama'))
        return super(hr_holidays, self).create(cr, uid, values, context=context)

    def holidays_first_validate(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        brw =obj_emp.browse(cr,uid,ids2)[0]
        manager = ids2 and ids2[0] or False
        self.holidays_first_validate_notificate(cr, uid, ids, context=context)
        objk = self.browse(cr,uid,ids)[0] 
        if objk.department_id.manager_id == False :
                raise osv.except_osv(_('Warning!'),_('Manager Tidak Boleh Kosong')) 
        emp = objk.employee_id.id
        dep = objk.department_id.manager_id
        if dep :
            dep = objk.department_id.manager_id.id
        state =objk.state
        if objk.type != "add" and objk.holiday_type != 'lokasi':
            if objk.employee_id.department_id.name != "HRD" :
                if ids2[0] == emp and emp == dep :
                    raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Aproval'))  
                if brw.user_id.approve_presdir == True :
                    raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Aproval'))
                if brw.department_id.name == "HRD" and objk.department_id.name != "HRD" and objk.employee_id.id != dep :
                    raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Aproval'))
                self.write(cr, uid, ids, {'state':'validate1', 'manager_id': manager})
            else :
                if brw.user_id.approve_presdir == False :
                    raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Aproval')) 
                else :
                    self.write(cr, uid, ids, {'state':'validate1', 'manager_id': manager})   
        else :
                self.write(cr, uid, [objk.id], {'state': 'validate1', 'manager_id': manager})
        return True

    def holidays_validate(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        brw =obj_emp.browse(cr,uid,ids2)[0]
        manager = ids2 and ids2[0] or False
        data_holiday = self.browse(cr, uid, ids)
        #if data_holiday[0].employee_id.user_id.id != uid :         
        for record in data_holiday:
            if record.department_id.manager_id == False :
                raise osv.except_osv(_('Warning!'),_('Manager Tidak Boleh Kosong')) 
            employ = record.employee_id.id
            dep = record.department_id.manager_id
            if dep :
                dep = record.department_id.manager_id.id
            if record.double_validation:
                self.write(cr, uid, [record.id], {'manager_id2': manager})
            else:
                self.write(cr, uid, [record.id], {'manager_id': manager})
            if record.holiday_type == 'lokasi':
                emp_ids = obj_emp.search(cr, uid, [('work_location2','=' ,record.lokasi_id)])
                leave_ids = []
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=None))
                wf_service = netsvc.LocalService("workflow")
                for leave_id in leave_ids:
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
            if record.type != "add" and record.holiday_type != 'lokasi':
                if record.employee_id.department_id.name != "HRD" and record.employee_id.id != dep :
                    if ids2[0] == employ and employ == dep :
                        raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Aproval'))
                    if brw.user_id.approve_presdir == True :
                        raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Aproval'))
                else :
                    if brw.user_id.approve_presdir == False and employ == ids2[0] :
                        raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Aproval')) 
                self.write(cr, uid, ids, {'state':'validate'})
            else :
                self.write(cr, uid, [record.id], {'state': 'validate', 'manager_id': manager})
        return True

    def holidays_refuse(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        brw =obj_emp.browse(cr,uid,ids2)[0]
        manager = ids2 and ids2[0] or False
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.department_id.manager_id == False :
                raise osv.except_osv(_('Warning!'),_('Manager Tidak Boleh Kosong')) 
            emp = holiday.employee_id.id
            dep = holiday.department_id.manager_id
            if dep != "" :
                dep = holiday.department_id.manager_id.id
            if holiday.type != "add" and holiday.holiday_type != 'lokasi':
                if holiday.employee_id.department_id.name != "HRD"  :
                    if ids2[0] == emp and emp == dep :
                        raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Aproval')) 
                    if brw.user_id.approve_presdir == True :
                        raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Aproval'))
                else :
                    if brw.user_id.approve_presdir == False :
                        raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Aproval')) 
                if holiday.state == 'validate1':
                    self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id': manager})
                else:
                    self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id': manager})
            else :
                self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id': manager})
        #self.holidays_cancel(cr, uid, ids, context=context)
        return True

    def holiday(self, cr,uid,ids=None,context=None):
        val='validate'
        obj = self.pool.get('hr.holidays')        
        src = obj.search(cr,uid,[('state','=',val)])
        brw = obj.browse(cr,uid,src)
        tahun = datetime.now().year
        date = datetime.now()
        obj_emp = self.pool.get('hr.employee')
        obj_src = obj_emp.search(cr,uid,[('tgl_masuk','=',date)])
        obj_brw = obj_emp.browse(cr,uid,obj_src)
        leave_ids=[]
        for holiday in brw :
            dates = holiday.date_from
            year = datetime.strptime(dates,'%Y-%m-%d %H:%M:%S').year
            for data in obj_brw :
                if tahun == year and holiday.lokasi_id == data.work_location2 and holiday.type == 'remove' :
                    vali = {
                            'name': holiday.name,
                            'type': holiday.type,
                            'holiday_type': 'employee',
                            'holiday_status_id': holiday.holiday_status_id.id,
                            'date_from': holiday.date_from,
                            'date_to': holiday.date_to,
                            'notes': holiday.notes,
                            'number_of_days_temp': holiday.number_of_days_temp,
                            'parent_id': holiday.id,
                            'employee_id': data.id,
                        }
                    leave_ids.append(self.create(cr, uid, vali, context=None))
                    wf_service = netsvc.LocalService("workflow")
                    for leave_id in leave_ids:
                        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        return True   

    _columns = {
        'bln_libur_id':fields.many2one('hr.bln_libur',''),
        'libur_bersih':fields.boolean('Hitung Tanggal Merah'),
        'is_libur':fields.boolean('Libur'),
        'libur_bersih2':fields.related('holiday_status_id','libur_bersih',type='boolean',relation='hr.holidays.status',string='Hitung Tanggal Merah',readonly=True),
        'limit_cuti':fields.related('holiday_status_id','limit_cuti',type='boolean',relation='hr.holidays.status',string='Limit Cuti',readonly=True),
        'is_edit':fields.boolean('Kunci ?',required=True),
        'holiday_type': fields.selection([('employee','By Employee'),('lokasi','Lokasi')], 'Allocation Mode', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category', required=True),
        'lokasi_id': fields.selection([('karawang','Karawang'),('tanggerang','Tanggerang')],'Alamat Kantor', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'category_id': fields.many2one('hr.employee.category', "Employee Tag"),
        'agama':fields.many2one('hr_recruit.agama','Agama'),
    }
    
    _sql_constraints = [
        ('type_value', "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or (holiday_type='category' AND category_id IS NOT NULL)) or (holiday_type='lokasi' AND category_id IS NOT NULL)", 
         "The employee or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
    ]   

    def onchange_dep1(self,cr,uid,ids,employee_id,department_id,context=None):
        obj = self.pool.get('hr.employee')
        src = obj.search(cr,uid,[('id','=',employee_id)])
        brw = obj.browse(cr,uid,src)
        dep = False
        for department in brw :
            dep = department.department_id.id
        return {'value': {
            'department_id' : dep,
        }}

    def hapus_cuti(self,cr,uid,ids=None,context=None):
        obj = self.pool.get('hr.employee')
        src = obj.search(cr,uid,[])
        for employe in obj.browse(cr,uid,src) :
            alok = employe.alokasi1
            cuti = employe.cuti_tahunan1
            if cuti > alok :
                sisa = cuti - alok
                sisa_cuti = employe.sisa - sisa
                obj.write(cr,uid,[employe.id],{'sisa': sisa_cuti})
        return True
    
    def onchange_hol_status(self, cr, uid, ids, holiday_status_id, context=None):
        result = {}
        if holiday_status_id:
            hol_obj = self.pool.get('hr.holidays.status')
            result['libur_bersih2'] = hol_obj.browse(cr, uid, holiday_status_id, context=context).libur_bersih
            return {'value':{'libur_bersih2': result['libur_bersih2']}}
        return {'value':{'libur_bersih2': False}} 
 
    def _get_holi_status(self, cr, uid, context=None):
        obj_model = self.pool.get('ir.model.data')
        res = False
        data_id = obj_model.search(cr, uid, [('model', '=', 'hr.holidays.status'), ('name', '=','holiday_status_cl')])
        if data_id:
            res = obj_model.browse(cr, uid, data_id[0], context=context).res_id
        return res 
        
    _defaults={
        'holiday_status_id': _get_holi_status,
        'date_from':lambda *a : time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_to':lambda *a : time.strftime('%Y-%m-%d %H:%M:%S'),
        'is_edit': True,
    }

    '''def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        import pdb;pdb.set_trace()
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
       return diff_day
    '''      
    def _get_number_of_days2(self,date_from, date_to):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        day_from = datetime.strptime(date_from,DATETIME_FORMAT)
        day_to = datetime.strptime(date_to,DATETIME_FORMAT)
        nb_of_days = (day_to - day_from).days + 1        
        bob=0
        for day in range(0, nb_of_days):  
            date = (day_from + timedelta(days=day)) 
            isNonWorkingDay = date.isoweekday()==6 or date.isoweekday()==7      
            if isNonWorkingDay :
                non=bob
                bob=non+1
        diff_day = (nb_of_days - 1) - bob
        return diff_day
            
    def onchange_date_from2(self, cr, uid,args,libur_bersih2,date_to, date_from):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """   
        # date_to has to be greater than date_from

        #import pdb;pdb.set_trace()
        
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}
        month_from=datetime.strptime(date_from,'%Y-%m-%d %H:%M:%S').month
        month_to=datetime.strptime(date_to,'%Y-%m-%d %H:%M:%S').month
        if month_from != month_to :
            raise osv.except_osv(_('Warning!'),_('Bulan Harus Sama'))
        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to) and libur_bersih2 == False:
            diff_day = self._get_number_of_days2(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
                    
        elif (date_to and date_from) and (date_from <= date_to) and libur_bersih2 == True:
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
                        
        else:
            diff_day = self._get_number_of_days2(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1         
            #result['value']= 0
        return result

    def onchange_date_to2(self, cr, uid,args,libur_bersih2,date_to, date_from):

        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}
        month_from=datetime.strptime(date_from,'%Y-%m-%d %H:%M:%S').month
        month_to=datetime.strptime(date_to,'%Y-%m-%d %H:%M:%S').month
        if month_from != month_to :
            raise osv.except_osv(_('Warning!'),_('Bulan Harus Sama'))
        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to) and libur_bersih2 == False:
            diff_day = self._get_number_of_days2(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1 
        
        elif (date_to and date_from) and (date_from <= date_to) and libur_bersih2 == True:
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
           
        else:
            diff_day = self._get_number_of_days2(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1         
            #result['value']['number_of_days_temp'] = 0

        return result

    def leave_allocation_annual(self, cr, uid, ids=None, context=None):
        """ Override to avoid automatic logging of creation """
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True) 
        employee_ids = self.pool.get('hr.employee')
        src = employee_ids.search(cr, uid, [])
        employs = employee_ids.browse(cr, uid, src)
        years = datetime.now().year
        values = {}
        date = -1
        hol_id = 1
        leave_ids = []
        hol_brw = self.pool.get('hr.holidays.status')
        hol_src = hol_brw.search(cr,uid,[('name','=','Cuti Tahunan')])
        for holid in hol_brw.browse(cr,uid,hol_src) :
            hol_id = holid.id
        for emp in employs:
            no_contract = emp.no_contract
            tgl = emp.tanggal
            date = False
            alok = emp.cuti_tahunan1
            if  tgl != False :
                date = datetime.strptime(tgl,"%Y-%m-%d").year
            if no_contract != False :
                if date == years :
                    if alok > 0 :
                        employee_ids.write(cr,uid,[emp.id],{'sisa':alok})
                    end_date = datetime.strptime(tgl,"%Y-%m-%d").month
                    values = {
                        'name': _("Alokasi Cuti %s") % _(D_y),
                        'employee_id':emp.id,
                        'type':'add',       #Allocation-> 'add'
                        'holiday_status_id':hol_id,
                        'number_of_days_temp':end_date,
                        #'holiday_type':'employee',
                        'notes':"",
                        }
                    leave_ids.append(self.create(cr, uid, values, context=None))
                else :
                    if alok > 0 :
                        employee_ids.write(cr,uid,[emp.id],{'sisa':alok})
                    values = {
                        'name': _("Alokasi Cuti %s") % _(D_y),
                        'employee_id':emp.id,
                        'type':'add',       #Allocation-> 'add'
                        'holiday_status_id':hol_id,
                        'number_of_days_temp':12,
                        #'holiday_type':'employee',
                        'notes':"",
                        }
                    if alok > 0 :
                        employee_ids.write(cr,uid,['emp.id'],{'sisa':alok})
                    leave_ids.append(self.create(cr, uid, values, context=None))
                    employee_ids.write(cr,uid,[emp.id],{'sisa':alok})
        wf_service = netsvc.LocalService("workflow")
        for leave_id in leave_ids:
            wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
            wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
            wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        return True    

    def leave_allocation_5(self, cr, uid, ids=None, context=None):       
        """ Override to avoid automatic logging of creation """
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True) 

        obj_contract = self.pool.get('hr.contract')
        c_src = obj_contract.search(cr, uid, [],)
        contracts  = obj_contract.browse(cr, uid, c_src,)
        leave_ids = []
        for contract in contracts:
            if contract.status == True :
                values = {}
                date_from = contract.date_start
                if contract.is_have_allocation: 
                    E_y = datetime.strptime(date_from,"%Y-%m-%d").year
                    E_m = datetime.strptime(date_from,"%Y-%m-%d").month
                    E_d = datetime.strptime(date_from,"%Y-%m-%d").day 
                    #set cuti 22 hari saat masa kerja n*5 tahun, 
                    #n=1,2,... ;masa kerja dihitung dari awal kontrak
                    dy = (D_y - E_y)
                    ddy = dy % 5
                    if dy >= 5: 
                        if ddy == 0 and (D_m >= E_m) and (D_d >= E_d):
                            values = {
                                'name': _("Alokasi Cuti 5 Tahunan tahun %s") % _(D_y),
                                'employee_id':contract.employee_id.id,
                                'type':'add',
                                'holiday_status_id':3,
                                'number_of_days_temp':22,
                                'notes':""
                                }
                            leave_ids.append(self.create(cr, uid, values, context=None))
        wf_service = netsvc.LocalService("workflow")
        for leave_id in leave_ids:
            wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
            wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
            wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        return True 

    def hapus_cuti_5(self,cr,uid,ids=None,context=None):
        import pdb;pdb.set_trace()
        dates=time.strftime('%Y-%m-%d')
        year1=int(datetime.strptime(dates,"%Y-%m-%d").year)
        month1=datetime.strptime(dates,"%Y-%m-%d").month
        day1=datetime.strptime(dates,"%Y-%m-%d").day
        nilai = 'draft'
        tipe='add'
        palidate='validate'
        self_obj=self.pool.get('hr.holidays')
        src_obj=self_obj.search(cr,uid,[('type','=',tipe),('holiday_status_id','=','Compensatory Days'),('state','=',palidate)])
        obj = self_obj.browse(cr,uid,src_obj)     
        for hapus in obj :
            date_from = hapus.date_from
            year=int(datetime.strptime(date_from,"%Y-%m-%d %H:%M:%S").year) + 2
            month=datetime.strptime(date_from,"%Y-%m-%d %H:%M:%S").month
            day=datetime.strptime(date_from,"%Y-%m-%d %H:%M:%S").day     
            yrs = year % year1       
            if yrs == 0 : 
                self_obj.write(cr, uid,[hapus.id], {'state':'confirm'}, context=context)
                #wf_service = netsvc.LocalService("workflow")
                #wf_service.trg_validate(uid, 'hr.holidays', hapus.id, 'refuse', cr)
                self.unlink(cr,uid,[hapus.id],context=None)
        return True

hr_holidays()

class hr_contract_type(osv.osv):
    _name = 'hr.contract.type'
    _description = 'Contract Type'
    _inherit = 'hr.contract.type'

    _columns = {
        'is_have_allocation': fields.boolean('Leave Allocation', help="Ceklist untuk membuat alokasi cuti otomatis"),
    }

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    _columns = {
        'is_have_allocation' :  fields.related('type_id', 'is_have_allocation', type='boolean', relation='hr.contract.type', string='Ceklist untuk membuat alokasi cuti otomatis',),
    }
