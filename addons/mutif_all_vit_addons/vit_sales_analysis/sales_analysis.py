from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class sales_analysis(osv.osv):
	_name 		= "vit_sales_analysis.sale_order_analysis"
	_columns 	= {
		'product_id'	: fields.many2one('product.product', 'Product'),
		'categ_id'      : fields.many2one("product.category", "Category"),
		'report_type'	: fields.char('Report Type'),
		'quantity' 	: fields.float("Qty"),
		'amount' 	: fields.float("Amount"),
		'sub1' 	: fields.char("Penjualan Kotor"),
		'sub2' 	: fields.char("Penjualan Bersih"),
		'sub3' 	: fields.char("Type Penjualan"),
		'partner_id' 	: fields.many2one('res.partner','Partner',readonly=True),

	}