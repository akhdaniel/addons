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
import math

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


class hr_holidays(osv.osv):
    _name = "hr.holidays"
    _description = "Leave"
    _inherit = "hr.holidays"
    
    _columns = {
        'bln_libur_id':fields.many2one('hr.bln_libur',''),
        'libur_bersih':fields.boolean('Hitung Tanggal Merah'),
		'is_libur':fields.boolean('Libur'),
    }
 
    def _get_holi_status(self, cr, uid, context=None):
        obj_model = self.pool.get('ir.model.data')
        res = False
        data_id = obj_model.search(cr, uid, [('model', '=', 'hr.holidays.status'), ('name', '=','holiday_status_cl')])
        if data_id:
            res = obj_model.browse(cr, uid, data_id[0], context=context).res_id
        return res 
        
    _defaults={
        'holiday_status_id': _get_holi_status,
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
            
    def onchange_date_from2(self, cr, uid, ids, date_to, date_from,libur_bersih):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        '''
        import pdb;pdb.set_trace()
        obj_ = self.pool.get('hr.holidays')
        s=obj_.search(cr, uid, [('user_id', '=', uid)])
        st=obj_.browse(cr,uid,ids)
        hol_stat=st.holiday_status_id.libur_bersih       
        # date_to has to be greater than date_from
        '''
        #import pdb;pdb.set_trace()
        x=libur_bersih
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = datetime.datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
            result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to) and ( x != 1):
            diff_day = self._get_number_of_days2(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
                    
        if (date_to and date_from) and (date_from <= date_to) and (x == 1):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
                        
        else:
            diff_day = self._get_number_of_days2(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1         
            #result['value']= 0
        return result

    def onchange_date_to2(self, cr, uid, ids, date_to, date_from,libur_bersih):
        """
        Update the number_of_days.
        """
        '''
        import pdb;pdb.set_trace()
        st=self.browse(cr,uid,ids,)
        hol_stat=st.holiday_status_id.libur_bersih 
        '''
        #import pdb;pdb.set_trace()
        x=libur_bersih
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to) and (x != 1):
            diff_day = self._get_number_of_days2(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1 
        
        if (date_to and date_from) and (date_from <= date_to) and (x == 1):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
            
           
        else:
            diff_day = self._get_number_of_days2(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1         
            #result['value']['number_of_days_temp'] = 0

        return result
  
hr_holidays()
