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
    	'jenis_tunjangan'		: fields.many2one('hr.contract_tunjangan', 'Golongan'),
        "tunj_jabatan"          : fields.float("Tunjangan Jabatan"),
        "tunj_makan"            : fields.float("Tunjangan Makan"),
        "tunj_transport"        : fields.float("Tunjangan Transport"),
        "tunj_komunikasi"       : fields.float("Tunjangan Komunikasi"),
        "zakat" : fields.boolean("Zakat Penghasilan")
    }
    
hr_contract()


class hr_contract_tunjangan(osv.osv):
    _name = 'hr.contract_tunjangan'

    _columns = {
    	"name"              : fields.char("Golongan"),
        "tunj_jabatan"      : fields.float("Tunjangan Jabatan"),
        "tunj_makan"        : fields.float("Tunjangan Makan"),
        "tunj_transport"    : fields.float("Tunjangan Transport"),
        "tunj_komunikasi"   : fields.float("Tunjangan Komunikasi"),
    }

hr_contract_tunjangan()