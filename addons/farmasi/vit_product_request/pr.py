from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class purchase_requisition_line(osv.osv):
	_name 		= "purchase.requisition.line"
	_inherit 	= "purchase.requisition.line"
	_columns 	= {
		'description' : fields.char('Description')
	}


class purchase_requisition(osv.osv):
	_name 		= "purchase.requisition"
	_inherit 	= "purchase.requisition"

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
			for line in pr.line_ids:
				product_names.append( "%s/%s" % (line.product_id.name , line.description) )
			results[pr.id] = ",".join(product_names)
		return results	

	_columns 	= {
		'product_names' : fields.function(_product_names, type='char', string="Products"),
	}