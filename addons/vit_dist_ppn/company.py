from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class res_company(osv.osv):
	_name 		= "res.company"
	_inherit    = "res.company"
	_columns 	= {
	    'tax_responsible_id' : fields.many2one('res.partner', 'Tax Responsible'),
	    'tax_job_position'   : fields.char('Tax Responsible Position'),
		'date_pkp'	         : fields.date('Tanggal Pengukuhan PKP'),	    
	}
