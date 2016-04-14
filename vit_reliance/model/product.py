from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class product_product(osv.osv):
	_name 		= "product.product"
	_inherit	= "product.product"
	_columns 	= {
		'owner_id'	: fields.many2one('res.company', 'Company')
	}