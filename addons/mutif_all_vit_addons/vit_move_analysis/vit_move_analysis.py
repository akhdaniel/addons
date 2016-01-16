from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class sale_move_analysis(osv.osv):
	_name 		= "vit.move.analysis"
	_columns 	= {
		'categ_id' 			: fields.many2one('product.category', 'Category'),
		'model_id' 			: fields.many2one('vit.master.type', 'Model'),
		'product_id'		: fields.many2one('product.product', 'Product'),
		'onhand_qty'      	: fields.integer('OnHand Qty'),
		'in_qty'			: fields.integer('Total In Qty'),
		'out_qty' 			: fields.integer('Total Out Qty'),
		'soh_qty' 			: fields.integer('Total SOH Qty'),
		'out_qty_cust' 		: fields.integer('Out Qty Customer'),
		'in_qty_qc' 		: fields.integer('In Qty QC'),
		'year'				: fields.char('Year'),
		'month'				: fields.char('Month'),
		'day'				: fields.char('Day'),
		'location_id' 		: fields.many2one('stock.location','Location'),
	}


class sale_move_analysis_onhand(osv.osv):
	_name 		= "vit.move.analysis.onhand"
	_columns 	= {
		'categ_id' 			: fields.many2one('product.category', 'Category'),
		'model_id' 			: fields.many2one('vit.master.type', 'Model'),
		'product_id'		: fields.many2one('product.product', 'Product'),
		'onhand_qty'      	: fields.integer('OnHand Qty'),
		'date' 				: fields.char("Date"),
		'location_id' 		: fields.many2one('stock.location','Location'),
	}					