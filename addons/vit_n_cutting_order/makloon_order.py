from osv import osv, fields
import platform
import os
import csv
import logging
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.addons.vit_upi_uang_persediaan import terbilang_func

_logger = logging.getLogger(__name__)

class vit_material_req_line(osv.osv):
	_name = "vit.material.req.line"
	_description = 'Material Requirements Lines'
	_columns = {
		'makloon_order_id': fields.many2one('vit.makloon.order', 'Makloon Reference',ondelete='cascade'),
		'material': fields.many2one('product.product', 'Material'),
		'type' : fields.selection([('main','Body'),('variation','Variation'),('accessories','Accessories')], 'Component Type'),
		'qty'  : fields.float('Quantity'),         
	}

class vit_accessories_req_line(osv.osv):
	_name = "vit.accessories.req.line"
	_description = 'Accessories Requirements Lines'
	_columns = {
		'makloon_order_id': fields.many2one('vit.makloon.order', 'Makloon Reference',ondelete='cascade'),
		'material': fields.many2one('product.product', 'Material'),
		'type' : fields.selection([('main','Body'),('variation','Variation'),('accessories','Accessories')], 'Component Type'),
		'qty'  : fields.float('Quantity'),        
	}



class vit_makloon_order(osv.osv):
	_name = "vit.makloon.order"
	_description = 'Makloon Order'
	_rec_name = 'name'
		
	def _calculate_order(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_order +  qty[0].m_order +  qty[0].l_order +  qty[0].xl_order +  qty[0].xxl_order 
		return res

	_columns = {
		'name': fields.char('Order Makloon Reference', size=64, required=True,
            readonly=True, select=True),
		'state': fields.selection([
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('inprogres', 'Inprogres'),
            ('tobereceived', 'To Be Received'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="", select=True),
		'partner_id'	:fields.many2one('res.partner', 'Makloon', select=True, track_visibility='onchange',readonly=True,states={'draft': [('readonly', False)]}),
		'date_taking': fields.datetime('Tanggal Pengambilan', select=True,readonly=True,states={'draft': [('readonly', False)]}),
		'date_end_completion'	: fields.datetime('Tanggal Penyelesaian', select=True,readonly=True,states={'draft': [('readonly', False)]}),
		'address' : fields.char('Alamat', size=128,readonly=True,states={'draft': [('readonly', False)]}),
		# 'origin'  :fields.char('SPK Cutting', size=64),
		'origin'	:fields.many2one('vit.cutting.order', 'SPK Cutting',readonly=True,states={'draft': [('readonly', False)]}),
		'model'   :fields.char('Model', size=64,readonly=True,states={'draft': [('readonly', False)]}),
		'material_req_line_ids': fields.one2many('vit.material.req.line', 'makloon_order_id', 'Material Requirements Lines'),
		'accessories_req_line_ids': fields.one2many('vit.accessories.req.line', 'makloon_order_id', 'Accessories Requirements Lines'),
		's_order' : fields.float('S',readonly=True,states={'draft': [('readonly', False)]}),
		'm_order' : fields.float('M',readonly=True,states={'draft': [('readonly', False)]}),
		'l_order' : fields.float('L',readonly=True,states={'draft': [('readonly', False)]}),
		'xl_order' : fields.float('XL',readonly=True,states={'draft': [('readonly', False)]}),
		'xxl_order' : fields.float('XXL',readonly=True,states={'draft': [('readonly', False)]}),
		'qty_order' :fields.function(_calculate_order, string='Total',type="integer"),
		'user_id'	:fields.many2one('res.users', 'Approved', select=True, track_visibility='onchange'),
		'patner_checker_id'	:fields.many2one('res.users', 'Checked By', select=True, track_visibility='onchange'),
		'state_incoming' : fields.selection([
			('not', 'Belum Create'),
			('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Transfer'),
            ('done', 'Transferred'),
            ], 'Status Incoming', readonly=True, track_visibility='onchange',
            help="", select=True),
		# 'picking_ids': fields.one2many('stock.picking.in', 'makloon_order_id', 'Related Picking', readonly=True, help="This is a list of delivery orders that has been generated for this sales order."),


  
	}

	_defaults = {
        
        'date_taking': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_end_completion': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda self, cr, uid, c: uid,
        'name': lambda obj, cr, uid, context: '/',
        'state': 'draft',
        'state_incoming': 'not',
   
    }


	def create(self, cr, uid, vals, context=None):
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'vit.makloon.order.seq') or '/'
		return super(vit_makloon_order, self).create(cr, uid, vals, context=context)

	def action_confirm(self, cr, uid, ids, context=None):
		#set to "confirmed" state
		return self.write(cr, uid, ids, {'state':'open'}, context=context)

	def action_inprogress(self, cr, uid, ids, context=None):
		#set to "confirmed" state
		return self.write(cr, uid, ids, {'state':'inprogres'}, context=context)

	def action_view_receive(self, cr, uid, ids, context=None):
		### Fungsi-fungsi untuk mengarahkan ke result list
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		## Arahkan Ke List Tree stock.picking.in dengan Ciri-ciri <record id="action_picking_tree4" model="ir.actions.act_window">
		result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree4')
# 
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		
		pick_ids = []
		spk_name = self.browse(cr,uid,ids[0],).name
		## Cari Id di incoming shipment yang Sama dengan spk_name == origin
		incoming_obj = self.pool.get('stock.picking.in')
		incoming_obj_ids = incoming_obj.search(cr,uid,[('origin','=',spk_name)])

		if len(incoming_obj_ids)>1:
			result['domain'] = "[('id','in',["+','.join(map(str, incoming_obj_ids))+"])]"
			## Cek dan Update dulu state_incoming dari incoming nya Dari List nya
			self.update_state3(cr,uid,ids, incoming_obj_ids, context)
		else :
			pick_ids = incoming_obj_ids
			res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_form')
			result['views'] = [(res and res[1] or False, 'form')]
			result['res_id'] = pick_ids and pick_ids[0] or False

			## Cek dan Update dulu state_incoming dari incoming 
			self.update_state2(cr,uid,ids, pick_ids[0], context)

		return result

	def action_receive(self, cr, uid, ids, context=None):
		lokasi_makloon = 'Lokasi Makloon'
		lokasi_barang_jadi = 'Lokasi Barang Jadi'

		lokasi_makloon_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_makloon)])[0]
		lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]

		### Create Dahulu di stock.picking.in
		stock_in_objs = self.pool.get('stock.picking.in')
		stock_in_obj = stock_in_objs.create(cr,uid,{'partner_id' : self.browse(cr,uid,ids[0],).partner_id.id,	
													'origin' : self.browse(cr,uid,ids[0],).name,})

		### Pencarian Id untuk field model
		master_type_obj = self.pool.get('vit.master.type')
		master_type_obj_ids = master_type_obj.search(cr,uid,[('model_product','=',self.browse(cr,uid,ids[0],).model)])

		## Cari Product Id Di BOM dengan search dari master_model_id == master_type_obj_ids[0]
		mrp_bom_obj = self.pool.get('mrp.bom')
		mrp_bom_obj_ids = mrp_bom_obj.search(cr,uid,[('master_model_id','=',master_type_obj_ids[0])])

		loop_size = ['S','M','L','XL','XXL']
		ls_id_list = []

		for mrp_id in mrp_bom_obj_ids:
			obj_mrp = mrp_bom_obj.browse(cr,uid,mrp_id,)
			for ls in loop_size:
				if obj_mrp.size == ls:
					if obj_mrp.size == 'S':
						size = self.browse(cr,uid,ids,context)[0].s_order
					elif obj_mrp.size == 'M':
						size = self.browse(cr,uid,ids,context)[0].m_order
					elif obj_mrp.size == 'L':
						size = self.browse(cr,uid,ids,context)[0].l_order
					elif obj_mrp.size == 'XL':
						size = self.browse(cr,uid,ids,context)[0].xl_order
					else :
						size = self.browse(cr,uid,ids,context)[0].xxl_order

					if size == 0.0:
						continue
					
					data_line = {
							'name'				: obj_mrp.product_id.name, 
							'product_id'        : obj_mrp.product_id.id,
							'product_qty'       : size,
							'product_uom'		: obj_mrp.product_id.uom_id.id,
							'location_id'       : lokasi_makloon_id,
							'location_dest_id'  : lokasi_barang_jadi_id,
							}
							
					move_lines = [(0,0,data_line)]
					stock_data = {
						'move_lines'     	: move_lines,
						}

					stock_in_objs.write(cr, uid, stock_in_obj, stock_data, context=context)

		## Update Status Incoming 
		self.update_state(cr,uid,ids,context)

		### Fungsi-fungsi untuk mengarahkan ke result list
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		## Arahkan Ke List Tree stock.picking.in dengan Ciri-ciri <record id="action_picking_tree4" model="ir.actions.act_window">
		result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree4')

		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]

		return True


	def update_state(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'tobereceived', 'state_incoming' : 'draft'},context=context)

	def update_state2(self,cr,uid,ids,pick_id,context=None):
		stock_in_objs = self.pool.get('stock.picking.in')
		stock_in_obj = stock_in_objs.browse(cr,uid,pick_id,context=context)
		
		if stock_in_obj.state == 'done':
			self.write(cr,uid,ids,{'state' : stock_in_obj.state},context=context)
		return self.write(cr,uid,ids,{'state_incoming' : stock_in_obj.state},context=context)

	def update_state3(self,cr,uid,ids,pick_id,context=None):
		stock_in_objs = self.pool.get('stock.picking.in')
		
		for x in pick_id:
			stock_in_obj = stock_in_objs.browse(cr,uid,x,context=context)
			if stock_in_obj.state != 'done':
				if stock_in_obj.state != 'assigned':
					if stock_in_obj.state != 'cancel':
						if stock_in_obj.state != 'auto':
							if stock_in_obj.state != 'confirmed':
								self.write(cr,uid,ids,{'state' : stock_in_obj.state},context=context)
		
		if stock_in_obj.state == 'done':
			self.write(cr,uid,ids,{'state' : stock_in_obj.state},context=context)
		return self.write(cr,uid,ids,{'state_incoming' : stock_in_obj.state},context=context)


	def on_partner_id(self, cr, uid, ids, partner_id, context=None):
		if partner_id != False:
			partner_obj = self.pool.get('res.partner',)
			partner = partner_obj.browse(cr, uid, partner_id, context=context)
			return {
				'value' : {
					'address' : partner.street,
				}
			}
		else:
			return {
				'value' : {
					'address' : '',
				}
			}


	def on_change_id(self, cr, uid, ids, type_product_id, context=None):

		vit_master_type_obj = self.pool.get('vit.master.type',)
		master_type = vit_master_type_obj.browse(cr, uid, type_product_id, context=context)

		prod_categ_obj = self.pool.get('product.category')
		name_prod_categ_obj = prod_categ_obj.browse(cr,uid,master_type.categ_id.id,context=context)
		return {
			'value' : {
				'category' : name_prod_categ_obj.name,
				'component_main_qty' 		: master_type.main_qty,
				'component_variation_qty' 	: master_type.variation_qty,
			}
		}

vit_makloon_order()









	