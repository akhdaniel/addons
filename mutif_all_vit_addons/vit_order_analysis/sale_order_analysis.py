from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class sale_order_analysis(osv.osv):
	_name 		= "vit_order_analysis.sale_order_analysis"
	_columns 	= {
		'order_id' 		: fields.many2one('sale.order', 'Sale Order'),
		'order_date' 	: fields.related('order_id', 'date_order' , 
						type="char", relation="sale.order", string="Order Date", store=True),
		'product_id'	: fields.many2one('product.product', 'Product'),
		'categ_id'      : fields.related('product_id', 'categ_id' , type="many2one", 
						relation="product.category", string="Category", store=True),
		'name_template'	: fields.char("Product Name"),
		'real_order' 	: fields.float("Real Order"),
		'qty_order' 	: fields.float("Qty Order"),
		'delivered' 	: fields.float("Delivered"),
		'back_order' 	: fields.float("Back Order"),
		'unfilled'      : fields.float("Un-Filled"),
		'partner_id' 	: fields.many2one('res.partner','Partner',readonly=True),
		'age'			: fields.integer('Age (Days)'),	
		'status' 		: fields.related('order_id', 'state' , 
						type="char", string="Status", store=True),
		'qty_invoice' 	: fields.float("Qty in Invoice"),
	}