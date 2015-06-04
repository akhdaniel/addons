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
					if (op.product_qty%int(picking.log_qty) == 0): #Genap
						product_qty = op.product_qty // int(picking.log_qty)
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
			# res.update(item_ids=items)
			# res.update(packop_ids=packs)

		else:
			# import pdb;pdb.set_trace()

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
					# import pdb;pdb.set_trace()
					if op.product_id:
						items.append(item)
					elif op.package_id:
						packs.append(item)

			# res.update(item_ids=items)
			# res.update(packop_ids=packs)
		res.update(item_ids=items)
		res.update(packop_ids=packs)

		return res

	@api.one
	def do_detailed_transfer(self):
		# res = super(stock_transfer_details, self).do_detailed_transfer()
		processed_ids = []
		# Create new and update existing pack operations
		for lstits in [self.item_ids, self.packop_ids]:
			""" Jika on_formula di uom == True maka gunakan quantity dari nett nya"""
			for prod in lstits:

				# if prod.product_id.uom_id.on_formula and self.picking_id.log_qty:
				if self.picking_id.log_qty:
					qty = prod.product_qty_nett
				else:
					qty = prod.quantity
				# import pdb;pdb.set_trace()
				pack_datas = {
					'product_id': prod.product_id.id,
					'product_uom_id': prod.product_uom_id.id,
					'product_qty': qty,
					# 'product_qty': prod.product_qty_nett,
					'package_id': prod.package_id.id,
					'lot_id': prod.lot_id.id,
					'location_id': prod.sourceloc_id.id,
					'location_dest_id': prod.destinationloc_id.id,
					'result_package_id': prod.result_package_id.id,
					'date': prod.date if prod.date else datetime.now(),
					'owner_id': prod.owner_id.id,
				}
				if prod.packop_id:
					# import pdb;pdb.set_trace()
					prod.packop_id.write(pack_datas)
					processed_ids.append(prod.packop_id.id)
				else:
					pack_datas['picking_id'] = self.picking_id.id
					packop_id = self.env['stock.pack.operation'].create(pack_datas)
					# import pdb;pdb.set_trace()
					processed_ids.append(packop_id.id)

		# Delete the others
		packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
		for packop in packops:
			packop.unlink()

		
		""" Update Stock picking:
			1. Update Stock Move nya, Berdasarkan list item dari stock_transfer_details_items
		"""
		item_ids = self.item_ids
		if self.picking_id.log_qty !=0.0:	
			self.update_stock_picking(item_ids)
		
		# Execute the transfer of the picking
		self.picking_id.do_transfer()

		return True	

	@api.cr_uid_ids_context
	def update_stock_picking(self, cr, uid, ids, item_ids, context=None):
		# item_ids[0].transfer_id.picking_id.move_lines
		for item in item_ids:
			# for sm_id in item.transfer_id.picking_id.move_lines:
				# Create Lagi Stock Move berdasarkan item_ids
			stock_move_obj = self.pool.get('stock.move')
			datas = {
				'name'				: item.product_id.name,
				'product_id'		: item.product_id.id,
				'product_uom_qty'	: item.product_qty_nett,
				'product_uom'		: item.product_uom_id.id,
				'date'				: item.date,
				'date_expected'		: item.transfer_id.picking_id.min_date,
				'location_id'		: item.sourceloc_id.id,
				'location_dest_id'	: item.destinationloc_id.id,
				'partner_id'		: item.transfer_id.picking_id.partner_id.id,
				'company_id'		: item.transfer_id.picking_id.company_id.id,
				'procure_method'	: 'make_to_stock',
				'product_qty_nett'  : item.product_qty_nett,
				'product_qty_diff'  : item.product_qty_diff,
				'weight_log' 		: item.weight_log,
				'length_log'		: item.length_log,
				'height_log' 		: item.height_log,
				'diameter_log'		: item.diameter_log,
				'picking_id'		: item.transfer_id.picking_id.id,
				'state'				: 'done'
			}

			stock_move_obj.create(cr, uid, datas, context=context)
	
		# for item in item_ids:
		# 	for sm_id in item.transfer_id.picking_id.move_lines:
		# 		cr.execute('delete from stock_move where id = %d' %(sm_id))


class stock_transfer_details_items(models.TransientModel):
	_name = 'stock.transfer_details_items'
	_inherit = 'stock.transfer_details_items'
	_description = 'Picking wizard items'

	_columns = {
		'product_qty_nett'  : fields.float("Nett Quantity" ,store=True),
		'product_qty_diff'  : fields.float("Diff/Loss Quantity" , store=True),
		'weight_log' : fields.float('Weight'),
		'length_log' : fields.float('Length'),
		'height_log' : fields.float('Height'),
		'diameter_log' : fields.float('Diameter'),

	}

	@api.onchange('weight_log', 'length_log','height_log','diameter_log') # if these fields are changed, call method
	def on_change_nett_diff(self):
		# import pdb;pdb.set_trace()
		if self.product_id.uom_id == "Cylindrical" :
			self.product_qty_nett = self.diameter_log * self.length_log
		else:
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
		'product_qty_nett'  : fields.float("Nett Quantity", store=True),
		'product_qty_diff'  : fields.float("Diff/Loss Quantity", store=True),
		'weight_log' : fields.float('Weight'),
		'length_log' : fields.float('Length'),
		'height_log' : fields.float('Height'),
		'diameter_log' : fields.float('Diameter'),

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


	# @api.cr_uid_ids_context
	# def do_transfer(self, cr, uid, picking_ids, context=None):
	# 	res = super(stock_picking, self).do_transfer(cr, uid, picking_ids, context=context)
	# 	return res	




class product_uom(osv.osv):
	_name = 'product.uom'
	_inherit = 'product.uom'
	_description = 'Product Unit of Measure'

	_columns = {
		'on_formula' : fields.boolean('On Formulation (m3)')
	}
