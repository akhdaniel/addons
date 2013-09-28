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
import pprint

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
    def _get_number_of_days(self,date_from, date_to):

        """Returns a float equals to the timedelta between two dates given as string."""
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
         
hr_holidays()
