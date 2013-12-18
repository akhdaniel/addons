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
    
    _columns = {
        'bln_libur_id':fields.many2one('hr.bln_libur',''),
        'libur_bersih':fields.boolean('Hitung Tanggal Merah'),
        'is_libur':fields.boolean('Libur'),
        'libur_bersih2':fields.related('holiday_status_id','libur_bersih',type='boolean',relation='hr.holidays.status',string='Hitung Tanggal Merah',readonly=True),
        'limit_cuti':fields.related('holiday_status_id','limit_cuti',type='boolean',relation='hr.holidays.status',string='Limit Cuti',readonly=True),
        'is_edit':fields.boolean('Kunci ?',required=True),
        #'name': fields.char('Description', size=64,required=True),
    }
	
    def hapus_cuti(self,cr,uid,ids,context=None):
        dates=time.strftime('%Y-%m-%d')
        year1=datetime.strptime(dates,"%Y-%m-%d").year
        month1=datetime.strptime(dates,"%Y-%m-%d").month
        day1=datetime.strptime(dates,"%Y-%m-%d").day
        years =year1 - 1
        nilai = 'draft'
        tipe='add'
        palidate='validate'
        self_obj=self.pool.get('hr.holidays')
        src_obj=self_obj.search(cr,uid,[('type','=',tipe),('state','=',palidate)])
        obj = self_obj.browse(cr,uid,src_obj)   
        import pdb;pdb.set_trace()   
        for hapus in obj :
            date_from = hapus.date_from
            year=datetime.strptime(date_from,'%Y-%m-%d').year
            month=datetime.strptime(date_from,'%Y-%m-%d').month
            day=datetime.strptime(date_from,'%Y-%m-%d').day            
            if year == years :
                self.write(cr, uid,ids, {'state': nilai}, context=context)
                self.unlink(cr,uid,ids,context=None)
        return True
    
    def onchange_hol_status(self, cr, uid, ids, holiday_status_id, context=None):
        result = {}
        # cfimport pdb;pdb.set_trace()
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
        obj_contract = self.pool.get('hr.contract')
        #obj_holi = self.pool.get('hr.holidays.status')
        #src_holi = obj_holi.search(cr, uid, [('is_1_year','=',True)],)
        
        values = {}
        for emp in employs:
            src_contract = obj_contract.search(cr, uid, [('employee_id','=',emp.id),('is_have_allocation','=',1),], context=context)
            if src_contract:
                values = {
                    'name': _("Alokasi Cuti %s") % _(D_y),
                    'employee_id':emp.id,
                    'type':'add',       #Allocation-> 'add'
                    'holiday_status_id':1,
                    'number_of_days_temp':12,
                    #'holiday_type':'employee',
                    'notes':""
                    }
                self.create(cr,uid,values,context=context)
        return True    

    def leave_allocation_5(self, cr, uid, ids=None, context=None):
        
        """ Override to avoid automatic logging of creation """
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True) 

        obj_contract = self.pool.get('hr.contract')
        c_src = obj_contract.search(cr, uid, [],)
        contracts  = obj_contract.browse(cr, uid, c_src,)

        #obj_holi = self.pool.get('hr.holidays.status')
        #src_holi = obj_holi.search(cr, uid, [('is_5_years','=',True)],)
        
        for contract in contracts:
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
                            #'holiday_type':'employee',
                            'notes':""
                            }
                        self.create(cr,uid,values,context=context)
        return True 
    '''
    def purge_leave(self, cr, uid, ids, context=None):
        D_name = D_y #- 1
        cuti_th_lalu = _("Alokasi Cuti %s") % _(D_name)
        A = self.search(cr, uid, [('name','=',cuti_th_lalu),],)
        B = self.browse(cr, uid, A,)
        self.holidays_refuse(cr, uid, [x.id for x in B], context=context)
        return True
      
    def approveall(self, cr, uid, ids, context=None):
        A = self.search(cr, uid, [('state','=','confirm'),('type','=','add'),],)
        B = self.browse(cr, uid, A,)
        return self.write(cr, uid, [x.id for x in B], {'state':'validate'})
    '''
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
