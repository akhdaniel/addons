from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class res_partner(osv.osv):
	_inherit 		= "res.partner"
	_columns 	= {
		'partner_product_ids' : fields.one2many('reliance.partner_product','partner_id','Partner Products', ondelete="cascade", select=1),
	}


class partner_product(osv.osv):
	_name = "reliance.partner_product"
	_columns 	= {
		'partner_id' : fields.many2one('res.partner', 'Partner')
		'product_id' : fields.many2one('product.product', 'Product')
	}

