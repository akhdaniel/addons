from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class product_template(osv.osv):
	_name 		= "product.template"
	_inherit 	= "product.template"
	_columns 	= {
        'is_makloon': fields.boolean("Is Makloon"),
        'makloon_partner_id': fields.many2one('res.partner', 
            'Makloon Partner', domain=[('category_id','ilike','makloon')],
            help="Partner with category makloon"),	
	}