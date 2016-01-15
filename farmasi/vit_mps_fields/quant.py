from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class stock_quant(osv.osv):
	_inherit = "stock.quant"

	_columns = {
		'uom_id': fields.related('product_id', 'uom_id' , type="many2one", 
			relation="product.uom", string="Uom", store=True),
		'life_date':fields.related('lot_id', 'life_date', type='datetime', relation='stock.production.lot', string='Life Date', readonly=True, store=False),
	}