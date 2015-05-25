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
						product_qty = op.product_qty // int(picking.log_qty)
						qty = op.product_qty//int(picking.log_qty)+((op.product_qty/int(picking.log_qty)- op.product_qty//int(picking.log_qty)) * int(picking.log_qty))
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
						if x == (picking.log_qty - 2) :
							product_qty = op.product_qty - (op.product_qty//int(picking.log_qty) * (int(picking.log_qty) - 1))
							# product_qty = op.product_qty//int(picking.log_qty)+((op.product_qty/int(picking.log_qty)- op.product_qty//int(picking.log_qty)) * int(picking.log_qty))
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
		# import pdb;pdb.set_trace()

		res.update(packop_ids=packs)
		return res

#----------------------------------------------------------
# Stock Move
#----------------------------------------------------------

class stock_move(osv.osv):
	_name = "stock.move"
	_inherit = "stock.move"

	_columns = {
		'log_qty' : fields.float('Log Quantity')
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
