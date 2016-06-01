from openerp.osv import fields, osv
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
#import pprint

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    _columns = {
    	'jenis_tunjangan'		: fields.many2one('hr.master.tunjangan', 'Jenis Tunjangan'),
    }
hr_contract()

class hr_contract_type(osv.osv):
    _name = 'hr.contract.type'
    _inherit= 'hr.contract.type'

    _columns = {
    	"jams1":fields.float('Tunjangan BPJS ketenagakerjaan (%)'),
        "jams2":fields.float('Potongan BPJS ketenagakerjaan (%)'),
        "jams3":fields.float('Tunjangan BPJS kesehatan (%)'),
        "jams4":fields.float('Potongan BPJS kesehatan (%)'),
    }
hr_contract_type()

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    _columns = {
        'hari_kerja' : fields.float('Jumlah Hari Kerja')
    }
hr_contract()

class resource_calendar(osv.osv):
    _name = 'resource.calendar'
    _inherit = 'resource.calendar'

    _columns = {
        'shift_gt_hr' : fields.boolean('Shift Ganti Hari')
    }
resource_calendar()
