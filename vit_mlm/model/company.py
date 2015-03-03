from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class company(osv.osv):
	_name 		= "res.company"
	_inherit 	= "res.company"
	_columns 	= {
		'mlm_plan_id'  :  fields.many2one('mlm.mlm_plan', 'MLM Plan'),
		'ap_coa_id'  :  fields.many2one('account.account', 'AP COA for member bonus'),
	}