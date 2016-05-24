from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class purchase_order(osv.osv):
	_name 		= "purchase.order"
	_inherit 	= "purchase.order"
	_columns 	= {
		'cancel_reason': fields.text("Cancel Reason", help="Please enter when cancelling PO"),
	}

	def action_cancel(self,cr,uid,ids,context=None):
		for po in self.browse(cr, uid, ids, context=context):
			if not po.cancel_reason :
				raise osv.except_osv(_('Warning'),_("Please fill cancelling reason") ) 
		return super(purchase_order, self).action_cancel(cr, uid, ids, context=context)
