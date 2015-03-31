from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mlm_bonus(osv.osv):
	_name 		= "mlm.bonus"
	_columns 	= {
		'code'		: fields.char('Code',required=True),
		'name'		: fields.char('Name',required=True),
		'coa_id' 	: fields.many2one('account.account', 'Related COA', help="Related invoicing COA/ AP to members"),
	}