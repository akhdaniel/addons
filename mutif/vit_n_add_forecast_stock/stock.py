from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


class stock_move(osv.osv):
	_name 		= "stock.move"
	_inherit 	= "stock.move"
	_order = 'kode_katalog asc'
	
	_columns = {  
        'sort_size_prod': fields.related('product_id','sort_size', type='float',
        	relation='product.product', string = "Sort Size", store=True , help='Untuk Sorting Berdasarkan Size'),
        'kode_katalog': fields.related('product_id','kode_katalog', type='float',
        	relation='product.product', string = "Kode Katalog", store=True , help='Untuk Sorting Berdasarkan Katalog'), 
        'stock': fields.related('product_id','qty_available', type='float',
        	relation='product.product', string = "Quantity On Hand", store=False ),
        'forecast': fields.related('product_id','virtual_available', type='float',
        	relation='product.product', string = "Forecasted Quantity", store=False ),
    }



class stock_partial_picking_line(osv.TransientModel):
	_name    = "stock.partial.picking.line"
	_inherit = "stock.partial.picking.line"
	
	_columns 	= {
		'order'  : fields.float("Order"),
		'stock'  : fields.float("Stock"),
		'forecast'  : fields.float("Forecast"),
		'can_be_ordered'  : fields.float("Can Be Ordered"),
	}

class stock_partial_picking(osv.osv_memory):
	_name    = "stock.partial.picking"
	_inherit = "stock.partial.picking"
	
	def _partial_move_for(self, cr, uid, move):
		sale_obj = self.pool.get('sale.order')
		sale_ids_obj=sale_obj.search(cr,uid,[('name','=',move.origin)])
		# import pdb;pdb.set_trace()
		## Berlaku hanya untuk delivery Order saja jika type=out
		partial_move = super(stock_partial_picking, self)._partial_move_for(cr, uid, move)	
		if move.picking_id.type =='out' :
			partial_move.update({'order' : move.product_qty,'forecast' : move.product_id.virtual_available,
				'stock' : move.product_id.qty_available ,
				 'quantity' : move.product_qty if move.state == 'assigned' and move.product_id.qty_available != 0.0 else 0})

		if sale_ids_obj != []:
			for x in sale_obj.browse(cr,uid,sale_ids_obj)[0].order_line:
				if move.product_id.id == x.product_id.id:
					partial_move.update({ 'can_be_ordered' : x.real_max_order, 'quantity' : x.real_max_order})	
		return partial_move
		

