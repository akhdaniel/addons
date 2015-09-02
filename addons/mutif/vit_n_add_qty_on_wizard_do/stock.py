from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)

class stock_partial_picking(osv.osv_memory):
	_name    = "stock.partial.picking"
	_inherit = "stock.partial.picking"

	_columns = {
		'quantity_total': fields.float("Quantity Total"),
	}
	

	def on_change_qty(self, cr, uid, ids, move_ids, context=None):
		quantity_total = 0.0
		for move_id in move_ids:
			# import pdb;pdb.set_trace()
			if not move_id[2]:
				continue
			else :
				quantity_total+= move_id[2]['quantity']
				
				## Ambil Nilai move_id yang merupakan id di stock move, yang menghubungkan id stock.picking nya 
				## Dan mengupdate secara realtime ke field qty_total_field di stock.picking
				move_id = move_id[2]['move_id']
				stock_move = self.pool.get('stock.move').browse(cr,uid,move_id,context=context)
				picking_id = stock_move.picking_id.id
				stock_pick =  self.pool.get('stock.picking').write(cr,uid,picking_id,{'qty_total_field':quantity_total},context=context)

		results = {
			'value' : {
				'quantity_total' :quantity_total,
			}
		}
		return results