from openerp.osv import fields, osv
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    _columns = {
        'shift_ids' : fields.one2many('hr.shift_karyawan','contract_id','Shift Working Schedule'),
        'shift_true' : fields.boolean('Shift Working Schedule'),
        }
hr_contract()

class shift(osv.osv):
    _name = "hr.shift_karyawan"
    _description = "record shift"

    _columns = {
        #'name'          : fields.char('Shift Name'),
        'contract_id'   : fields.many2one('hr.contract','Contract id'),
        'schedule_id'   : fields.many2one('resource.calendar','Schedule Shift'),
        'date_from'     : fields.date('Date From'),
        'date_to'	    : fields.date('Date To'),
    }
shift()
