from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class warehouse(osv.osv):
	_name 		= "stock.warehouse"
	_inherit 	= "stock.warehouse"
	_columns 	= {
		'state_id' 	: fields.related('partner_id', 'state_id' , type="many2one", 
			relation="res.country.state", string="State", store=True),

		'city' 	: fields.related('partner_id', 'city' , type="char", 
			relation="res.partner", string="City", 
			store=True,
			#store={'partner_id': (lambda self, cr, uid, ids, c={}: ids, ['street', 'city', 'state_id'], 50)} 
		),
		
		'street' 	: fields.related('partner_id', 'street' , type="char", 
			relation="res.partner", string="Street", store=True),		

		'phone' 	: fields.related('partner_id', 'phone' , type="char", 
			relation="res.partner", string="Phone", store=True),

		'bbm' 	: fields.related('partner_id', 'bbm' , type="char", 
			relation="res.partner", string="BBM", store=True),

	}

#############################################################
# tambah  id paket di SO dan invoice agar bisa di track
#############################################################
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