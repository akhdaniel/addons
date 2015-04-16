from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)

class stock_partial_picking(osv.osv_memory):
	_name    = "stock.partial.picking"
	_inherit = "stock.partial.picking"

	
	#############################################################################
	# Proses Update Cost price product yang namanya sama
	#############################################################################
	def do_partial(self, cr, uid, ids, context=None):

		partial = self.browse(cr, uid, ids[0], context=context)
		product_obj = self.pool.get('product.product')

		picking_id = partial.move_ids[0].move_id.picking_id.id 
		res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)
		
		""" Cari Nama product dalam line wizard do_partial,
		    ambil dan lakukan pencarian product dengan nama tersebut
		    update nilai standard_price (Cost Price)
		    atau berdasarkan default_code ditambah 'X' di belakangnya
		"""
		
		for line in partial.move_ids:
			# import pdb;pdb.set_trace()
			if line.product_id.default_code!=False:
				product_ids = product_obj.search(cr,uid,[('default_code','=',line.product_id.default_code+'X')])
				if product_ids!=[] :
					for product in product_ids:
						product_obj.write(cr, uid, [product], {'standard_price': line.product_id.standard_price})

		return res 

