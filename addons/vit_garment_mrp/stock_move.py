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
	_columns 	= {
		'product_qty_onhand'  : fields.related('product_id', 
			'qty_available' , type="float", 
			relation="product.product", 
			string="Qty On-hand", store=True)
	}