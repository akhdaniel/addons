from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.osv import fields, osv


#----------------------------------------------------------
# stock_transfer_details
#----------------------------------------------------------


class stock_transfer_details(models.TransientModel):
	_name = 'stock.transfer_details'
	_inherit = 'stock.transfer_details'
	_description = 'Picking wizard'

	_columns = {
		# 'product_qty_nett'  : fields.float("Nett Quantity"),
		# 'product_qty_diff'  : fields.float("Diff/Loss Quantity"),
		# 'weight' : fields.float('Weight'),
		# 'length' : fields.float('Length'),
		# 'height' : fields.float('Height'),

	}


	def default_get(self, cr, uid, fields, context=None):
		"""
		Modifikasi wizard sehingga bila ada n log dari stock.picking, akan memecah list di wizard tranfer sejumlah n 
		Juga, serta nilai product quantity mengikuti
		Konsep :
		for x in range(n):
			if (product_qty %'n == 0):
				print 75.00 /n
			else:
				if x==n-2:
					print 75 - (75//n * (n-1))
					break

		"""
		res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
		picking_ids = context.get('active_ids', [])
		active_model = context.get('active_model')
		if not picking_ids or len(picking_ids) != 1:
			# Partial Picking Processing may only be done for one picking at a time
			return res
		assert active_model in ('stock.picking'), 'Bad context propagation'
		picking_id, = picking_ids
		picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
		items = []
		packs = []
		if not picking.pack_operation_ids:
			picking.do_prepare_partial()
		if picking.log_qty != 0.0:
			for x,y in zip(range(int(picking.log_qty)),range(int(picking.log_qty))):
				for op in picking.pack_operation_ids:
					if (op.product_qty%int(picking.log_qty) == 0):
						product_qty = op.product_qty // int(picking.log_qty)
						item = {
							'packop_id': op.id,
							'product_id': op.product_id.id,
							'product_uom_id': op.product_uom_id.id,
							'quantity': product_qty,
							'package_id': op.package_id.id,
							'lot_id': op.lot_id.id,
							'sourceloc_id': op.location_id.id,
							'destinationloc_id': op.location_dest_id.id,
							'result_package_id': op.result_package_id.id,
							'date': op.date, 
							'owner_id': op.owner_id.id,
						}
						if op.product_id:
							items.append(item)
						elif op.package_id:
							packs.append(item)
					else:

						""" Karena n log, pada default nya membentuk 'packop_id': op.id, ini akan
							Mengakibatkan n list di wizard dengan packop_id yang sama, ternyata akan berperngaruh terhadap
							jumlah quantity yang akan tranfer, jadi bila jumlah n list di wizard masing2 mempunyai packop_id yang sama
							akan masuk 1 n list,logic nya lebih baik buat satu list saja yang memiliki packop_id
							logic : if x == 0, isi 'packop_id': op.id, else 'packop_id' :''
									(op_id =  op.id if (x == 0) else '')
						"""
						
						product_qty = op.product_qty // int(picking.log_qty)
						qty = op.product_qty//int(picking.log_qty)+((op.product_qty/int(picking.log_qty)- op.product_qty//int(picking.log_qty)) * int(picking.log_qty))
						op_id =  op.id if (x == 0) else ''
						item = {
								'packop_id': op_id,
								'product_id': op.product_id.id,
								'product_uom_id': op.product_uom_id.id,
								'quantity': product_qty,
								'package_id': op.package_id.id,
								'lot_id': op.lot_id.id,
								'sourceloc_id': op.location_id.id,
								'destinationloc_id': op.location_dest_id.id,
								'result_package_id': op.result_package_id.id,
								'date': op.date, 
								'owner_id': op.owner_id.id,
							}
						if x == (picking.log_qty - 2) :
							product_qty = op.product_qty - (op.product_qty//int(picking.log_qty) * (int(picking.log_qty) - 1))
							# product_qty = op.product_qty//int(picking.log_qty)+((op.product_qty/int(picking.log_qty)- op.product_qty//int(picking.log_qty)) * int(picking.log_qty))
							item = {
								# 'packop_id': op.id,
								'product_id': op.product_id.id,
								'product_uom_id': op.product_uom_id.id,
								'quantity': product_qty,
								'package_id': op.package_id.id,
								'lot_id': op.lot_id.id,
								'sourceloc_id': op.location_id.id,
								'destinationloc_id': op.location_dest_id.id,
								'result_package_id': op.result_package_id.id,
								'date': op.date, 
								'owner_id': op.owner_id.id,
							}
							if op.product_id:
								items.append(item)
							elif op.package_id:
								packs.append(item)
							break

						if op.product_id:
							items.append(item)
						elif op.package_id:
							packs.append(item)
		else:
			for op in picking.pack_operation_ids:
					item = {
						'packop_id': op.id,
						'product_id': op.product_id.id,
						'product_uom_id': op.product_uom_id.id,
						'quantity': op.product_qty,
						'package_id': op.package_id.id,
						'lot_id': op.lot_id.id,
						'sourceloc_id': op.location_id.id,
						'destinationloc_id': op.location_dest_id.id,
						'result_package_id': op.result_package_id.id,
						'date': op.date, 
						'owner_id': op.owner_id.id,
					}
					if op.product_id:
						items.append(item)
					elif op.package_id:
						packs.append(item)


		res.update(item_ids=items)
		res.update(packop_ids=packs)

		return res


class stock_transfer_details_items(models.TransientModel):
	_name = 'stock.transfer_details_items'
	_inherit = 'stock.transfer_details_items'
	_description = 'Picking wizard items'

	_columns = {
		'product_qty_nett'  : fields.float("Nett Quantity"),
		'product_qty_diff'  : fields.float("Diff/Loss Quantity"),
		'weight_log' : fields.float('Weight'),
		'length_log' : fields.float('Length'),
		'height_log' : fields.float('Height'),

	}

	@api.onchange('weight_log', 'length_log','height_log') # if these fields are changed, call method
	def on_change_nett_diff(self):
		self.product_qty_nett = self.weight_log * self.length_log * self.height_log
		self.product_qty_diff = self.quantity - self.product_qty_nett 
	

#----------------------------------------------------------
# Stock Move
#----------------------------------------------------------

class stock_move(osv.osv):
	_name = "stock.move"
	_inherit = "stock.move"
	_description = "Stock Move"

	_columns = {
		'log_qty' : fields.float('Log Quantity'),
		'product_qty_nett'  : fields.float("Nett Quantity"),
		'product_qty_diff'  : fields.float("Diff/Loss Quantity"),
	}


#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------

class stock_picking(osv.osv):
	_name = "stock.picking"
	_inherit = "stock.picking"
	_description = "Picking List"

	_columns = {
		'log_qty' : fields.float('Log Quantity')
	}


	@api.cr_uid_ids_context
	def do_transfer(self, cr, uid, picking_ids, context=None):
		res = super(stock_picking, self).do_transfer(cr, uid, picking_ids, context=context)
		# import pdb;pdb.set_trace()
		return res	
