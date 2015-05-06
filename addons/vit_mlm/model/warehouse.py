from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class sale_order(osv.osv):
	_name 		= "sale.order"
	_inherit 	= "sale.order"
	_columns 	= {
		'paket_id' 	: fields.many2one('mlm.paket', 'Paket' , readonly=True), 

		}	
	##########################################################
	#tambahkan id paket di invoice sesuai paket di SO
	##########################################################
	def _prepare_invoice(self, cr, uid, order, lines, context=None):
		res 			= super(sale_order,self)._prepare_invoice(cr, uid, order, lines, context=context)
		res['paket_id']	= order.paket_id.id
		result 			= dict(res.items())
		return result

class account_invoice(osv.osv):
	_name 		= "account.invoice"
	_inherit 	= "account.invoice"
	_columns 	= {
		'paket_id' 	: fields.many2one('mlm.paket', 'Paket' , readonly=True), 

		}			