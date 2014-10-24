from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
_logger = logging.getLogger(__name__)

class account_invoice(osv.osv):
	_inherit = "account.invoice"
	_name = "account.invoice"

	_columns = {
		'is_cn' : fields.related('journal_id','is_cn',type='boolean',relation='account.journal',string='CN Confirmation'),
		'is_draft_lph' : fields.boolean('Is Draft'),
			}

account_invoice()