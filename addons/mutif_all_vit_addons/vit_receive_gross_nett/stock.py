from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)

class stock_move(osv.osv):
	_name 		= "stock.move"
	_inherit 	= "stock.move"
	_columns 	= {
		'product_qty_nett'  : fields.float("Nett Quantity"),
		'product_qty_diff'  : fields.float("Loss"),
	}

	###################################################################
	# waktu create new receiving
	###################################################################
	def create(self, cr, uid, vals, context=None):
		vals['product_qty_nett'] = vals['product_qty']
		res = super(stock_move, self).create(cr, uid, vals, context=context)	
		return res

	###################################################################
	# waktu ada backorder, dia create new receiving, tapi dibuat sebg 
	# old receiving, yang receicing lama dianggal sbg new receivng
	###################################################################
	def write(self, cr, uid, ids, vals, context=None):
		m = self.browse(cr, uid, ids, context=context)
		return  super(stock_move, self).write(cr, uid, ids, vals, context=context)


class stock_partial_picking_line(osv.TransientModel):
	_name    = "stock.partial.picking.line"
	_inherit = "stock.partial.picking.line"
	_columns 	= {
		'product_qty_nett'  : fields.float("Nett Quantity"),
		'product_qty_diff'  : fields.float("Loss"),
	}

	def on_change_qty(self, cr, uid, ids, quantity, context=None):
		results = {
			'value' : {
				'product_qty_nett' : quantity,
				'product_qty_diff' : 0.0 
			}
		}
		return results

	def on_change_nett_qty(self, cr, uid, ids, product_qty_nett, quantity, context=None):
		results = {
			'value' : {
				'product_qty_diff' : quantity-product_qty_nett 
			}
		}
		return results

class stock_partial_picking(osv.osv_memory):
	_name    = "stock.partial.picking"
	_inherit = "stock.partial.picking"

	#untuk ngisi default value gross = qty 
	def _partial_move_for(self, cr, uid, move):
		partial_move = super(stock_partial_picking, self)._partial_move_for(cr, uid, move)	
		partial_move.update({'product_qty_nett' : move.product_qty_nett })
		return partial_move

	#############################################################################
	# proses partial 
	# - masukkan semua qty ke stock
	# kalau ada difference:
	# - move product sebanyak diff ke scraped location
	# - sehingga terbentuk diff jurnal: inventory - biaya
	#############################################################################
	def do_partial(self, cr, uid, ids, context=None):

		partial = self.browse(cr, uid, ids[0], context=context)


		picking_id = partial.move_ids[0].move_id.picking_id.id 
		res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)	

		# kalau ada diff di masing-masing line:
		# - buang ke scrapped
		move_obj= self.pool.get('stock.move')
		for line in partial.move_ids:
			if line.product_qty_diff != 0:
				# print "partial processing gross & nett "
				#############################################################################
				# proteksi
				# - quantity = nett + diff
				# - quantity >= nett 
				#############################################################################
				if line.quantity != line.product_qty_nett + line.product_qty_diff :
					raise osv.except_osv(_('Error'),_("Total Quantity is not the same as Nett and Difference") ) 

				if line.quantity < line.product_qty_nett:
					raise osv.except_osv(_('Error'),_("Quantity must be bigger than Nett") ) 

				#create diff jurnal
				# product_id = line.move_id.product_id
				self.move_to_scrap(cr, uid, line, context=context)

				#update nett dan diff qty
				data = {'product_qty_nett': line.product_qty_nett,
					'product_qty_diff': line.product_qty_diff
				}
				move_obj.write(cr, uid, [line.move_id.id], data, context=context)

			else:
				m = move_obj.browse(cr, uid, line.move_id.id, context=context)
				data = {'product_qty_nett': m.product_qty,
					'product_qty_diff': 0.0
				}
				move_obj.write(cr, uid, [line.move_id.id], data, context=context)

		return res 

	#############################################################################
	# move product sebanyak diff qty ke location scrapped
	# supaya terbentuk journal 
	# di scrapped harus set coa nya biaya gross/nett
	#############################################################################
	def move_to_scrap(self, cr, uid, line, context=None):
		sm_obj = self.pool.get('stock.move')
		location_dest_id = self.pool.get('stock.location').search(cr, uid, [('name','ilike','Scrapped')], context=context)
		if not location_dest_id:
			raise osv.except_osv(_('Error'),_("No scrapped location, please set one") ) 

		data = { 
			'product_id'     : line.product_id.id,
			'product_qty'    : line.product_qty_diff,
			'product_uom'    : line.product_id.uom_id.id,
			'picking_id'     : line.move_id.picking_id.id, 
			'name'           : '%s - Gross/Nett Difference - %s'  % (line.move_id.picking_id.name , line.product_id.name),
			'location_id'    : line.move_id.location_dest_id.id, # stock 
			'location_dest_id' : location_dest_id[0] ,           # scraped
			'date_expected'  : line.move_id.date_expected,
			'type '          : 'out'
		}
		id = sm_obj.create(cr, uid, data, context=context)
		sm_obj.action_done(cr, uid, [id], context=context)

