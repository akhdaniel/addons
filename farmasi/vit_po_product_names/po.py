from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class purchase_order(osv.osv):
	_name 		= "purchase.order"
	_inherit 	= "purchase.order"

	def _product_names(self, cr, uid, ids, field, arg, context=None):
		results = {}
		# return harus berupa dictionary dengan key id session
		# contoh kalau 3 records:
		# {
		#      1 : 50.8,
		#      2 : 25.5,
		#      3 : 10.0
		# }

		for pr in self.browse(cr, uid, ids, context=context):
			product_names = []
			for line in pr.order_line:
				product_names.append(line.product_id.name)
			results[pr.id] = ",".join(product_names)
		return results	

	_columns 	= {
		'product_names': fields.function(_product_names, type='char', string="Products"),
	}