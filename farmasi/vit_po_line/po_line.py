from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class order_line(osv.osv):
	_inherit 		= "purchase.order.line"


	#######################################################################
	# cari total qty yang sudah received, dari move_ids yg status = done
	#######################################################################
	def _get_total_received(self, cr, uid, ids, field, arg, context=None):
		results = {}

		for po_line in self.browse(cr, uid, ids , context=context):
			total = 0.0
			results[po_line.id] = total

			for move_line in po_line.move_ids:
				if move_line.state == 'done':
					total += move_line.product_uom_qty 
			results[po_line.id] = total			

		return results	

	#######################################################################
	# cari total outstanding qty 
	#######################################################################
	def _get_outstanding(self, cr, uid, ids, field, arg, context=None):
		results = {}

		for po_line in self.browse(cr, uid, ids , context=context):
			total = 0.0
			results[po_line.id] = po_line.product_qty

			for move_line in po_line.move_ids:
				if move_line.state == 'done':
					total += move_line.product_uom_qty
			results[po_line.id] = po_line.product_qty - total			

		return results	

	_columns 	= {
		'total_qty_received' 	: fields.function(_get_total_received, type='float', string="Received Qty"),
		'outstanding_qty' 		: fields.function(_get_outstanding, type='float', string="Outstanding Qty"),
	}

