from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class espt(osv.osv):
	_name 		= "vit_dist_ppn.espt"
	_columns 	= {
        'invoice_id' : fields.many2one('account.invoice', 'Customer Invoice', required=True),
        'amount'     : fields.float("Amount Total"),
        'date'       : fields.date("Date"),
        'tax_number' : fields.char('Tax Number', length=120),
        'customer'   : fields.char('Customer'),
        'npwp'		 : fields.char('NPWP'),
	}