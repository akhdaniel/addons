from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class product_category(osv.osv):
	_name 		= "product.category"
	_inherit 	= "product.category"
	_columns 	= {
		'sediaan_id' : fields.many2one('vit.sediaan', 'Sediaan')
	}

class sediaan(osv.osv):
	_name 		= "vit.sediaan"
	_columns 	= {
		'name' 	: fields.char("Sediaan"),
		'code' 	: fields.char("Code"),
		'max_batch_per_week': fields.integer("Max Batch per Week")
	}