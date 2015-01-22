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
		'uom_id' : fields.many2one('product.uom','Satuan'),

		#### fiel bayangan untuk mempermudah perhitungan di form makloon ####     
		'size_s' : fields.float('Size S', readonly=True),
		'size_m' : fields.float('Size M', readonly=True),
		'size_l' : fields.float('Size L', readonly=True),
		'size_xl' : fields.float('Size XL', readonly=True),
		'size_xxl' : fields.float('Size XXL', readonly=True),
		######################################################################
	}

class vit_grade(osv.Model):
	_name = "vit.grade"
	_rec_name = "date"

	_columns = {
		'makloon_order_id': fields.many2one('vit.makloon.order', 'Makloon Reference',ondelete='cascade'),
		'date' : fields.date('Tanggal',required=True),
		'size_s' : fields.integer('Size S'),
		'size_m' : fields.integer('Size M'),
		'size_l' : fields.integer('Size L'),
		'size_xl' : fields.integer('Size XL'),
		'size_xxl' : fields.integer('Size XXL'),
		'picking_ids' : fields.many2one('stock.picking','Internal Move'),
	}

	_defaults = {
		'date' : fields.date.context_today,
	}

class vit_makloon_order(osv.osv):
	_name = "vit.makloon.order"
	_description = 'Makloon Order'
	_rec_name = 'name'
	_order = 'name desc'
		
	def _calculate_order(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		for x in qty:
			res[x.id] = x.s_order +  x.m_order +  x.l_order +  x.xl_order +  x.xxl_order 
		return res

	def qty_acc_reload(self, cr, uid, ids, context=None):
		# import pdb;pdb.set_trace()
		if context is None:
			context = {}
		else: 
			my_obj = self.browse(cr,uid,ids[0],context=context)
			s_odr = my_obj.s_order
			m_odr = my_obj.m_order
			l_odr = my_obj.l_order
			xl_odr = my_obj.xl_order
			xxl_odr = my_obj.xxl_order

			acc_obj = self.pool.get('vit.accessories.req.line')
			acc_sch = acc_obj.search(cr,uid,[('makloon_order_id','=',ids[0])],context=context)
			acc_bro = acc_obj.browse(cr,uid,acc_sch,context=context)

			#w: looping setiap baris accessories line
			for x in acc_bro:
				x_id = x.id

				#w: qty ukuran = qty per ukuran(s,m,l,xl,xxl) pada bom * jml berdasarkan ukuran(s,m,l,xl,xxl) yg di input
				qty_s = (x.size_s*s_odr)
				qty_m = (x.size_m*m_odr)
				qty_l = (x.size_l*l_odr)
				qty_xl = (x.size_xl*xl_odr)
				qty_xxl = (x.size_xxl*xxl_odr)

				#w: setelah dapat total bahan per ukuran(s,m,l,xl,xxl), jumlahkan total ke lima ukuran tsb
				qty_total = qty_s+qty_m+qty_l+qty_xl+qty_xxl
				acc_obj.write(cr,uid,x_id,{'qty':qty_total},context=context)

		return True

	def _get_int_move(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}

		my_form = self.browse(cr,uid,ids[0],context=context)
		makloon_no = my_form.name
		makloon_id = my_form.id

		pick_obj = self.pool.get('stock.picking')
		pick_ids = pick_obj.search(cr, uid, [
			('origin','=',makloon_no)], context=context)
		if pick_ids == []:
			return result		
		result[makloon_id] = pick_ids
		return result

	def _get_receive(self,cr,uid,ids,field,args,context=None):
		result = {}
		#import pdb;pdb.set_trace()
		#merubah state form makloon menjadi done
		for res in self.browse(cr,uid,ids):
			pick_obj = self.pool.get('stock.picking.in')
			cari_pick =  pick_obj.search(cr,uid,[('origin','=',res.name)],context=context)
			if cari_pick != [] :
				pick_state = pick_obj.browse(cr,uid,cari_pick,context=context)
				for x in pick_state :
					if x.state != 'done':
						return result

				self.write(cr,uid,ids[0],{'state':'done'},context=context)

		return result

	_columns = {
		'name': fields.char('Order Makloon Reference', size=64, required=True,
			readonly=True, select=True),
		'state': fields.selection([
			('draft', 'Draft'),
			('open', 'Open'),
			('inprogres', 'Inprogres'),
			('tobereceived', 'To Be Received'),
			('grade', 'Split Grade'),
			('split', 'Finish Split'),
			('done', 'Done'),
			], 'Status', readonly=True, track_visibility='onchange',
			help="", select=True),
		'partner_id'	:fields.many2one('res.partner', 'Makloon', select=True, track_visibility='onchange',readonly=True,states={'draft': [('readonly', False)]}),
		'date_taking': fields.datetime('Tanggal Pengambilan', select=True,readonly=True,states={'draft': [('readonly', False)]}),
		'date_end_completion'	: fields.datetime('Tanggal Penyelesaian', select=True,readonly=True,states={'draft': [('readonly', False)]}),
		'address' : fields.char('Alamat', size=128,readonly=True,states={'draft': [('readonly', False)]}),
		# 'origin'  :fields.char('SPK Cutting', size=64),
		'origin'	:fields.many2one('vit.cutting.order', 'SPK Cutting',readonly=True,states={'draft': [('readonly', False)]}),
		'model'   :fields.char('Model', size=64,readonly=True),#states={'draft': [('readonly', False)]}),
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
		'is_receive' : fields.function(_get_receive,type="boolean",string='Receive'),
		'invoice_id': fields.many2one('account.invoice', 'Invoice',domain=[('type', '=','in_invoice')], readonly=True,),
		'int_move_ids' : fields.function(_get_int_move, type='many2many', relation="stock.picking", string="Internal Move"),
		'grade_ids' : fields. one2many('vit.grade','makloon_order_id', 'Grade'),
  
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

	def write(self, cr, uid, ids, vals, context=None):
		
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		for x in self.browse(cr, uid, ids, context=context):
			s_qc = x.origin.s_qc
			m_qc = x.origin.m_qc
			l_qc = x.origin.l_qc
			xl_qc = x.origin.xl_qc
			xxl_qc = x.origin.xxl_qc

			#antisipasi penghitungan jmh yg di input untuk makloon harus di bawah atau sama dengan dr QC cutting dan tdk boleh minus
			if 's_order' in vals :
				if vals['s_order'] > s_qc :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran S yang di input untuk makloon melebihi proses QC Qutting!')
				elif vals['s_order'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran S yang di input tidak boleh minus!')					
			if 'm_order' in vals :
				if vals['m_order'] > m_qc :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran M yang di input untuk makloon melebihi proses QC Qutting!')
				elif vals['m_order'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran M yang di input tidak boleh minus!')					
			if 'l_order' in vals :
				if vals['l_order'] > l_qc :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran L yang di input untuk makloon melebihi proses QC Qutting!')
				elif vals['l_order'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran L yang di input tidak boleh minus!')
			if 'xl_order' in vals :
				if vals['xl_order'] > xl_qc :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XL yang di input untuk makloon melebihi proses QC Qutting!')
				elif vals['xl_order'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XL yang di input tidak boleh minus!')
			if 'xxl_order' in vals :
				if vals['xxl_order'] > xxl_qc :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXL yang di input untuk makloon melebihi proses QC Qutting!')																				
				elif vals['xxl_order'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXL yang di input tidak boleh minus!')

		return super(vit_makloon_order, self).write(cr, uid, ids, vals, context=context)

	def action_confirm(self, cr, uid, ids, context=None):																	
		#set to "confirmed" state
		self.write(cr, uid, ids, {'state':'open'}, context=context)
		return True

	def action_inprogress(self, cr, uid, ids, context=None):
		#search jurnal purchase
		jurnal = self.pool.get('account.journal').search(cr,uid,[('type','=','purchase')],context=context)[0]
		#create juga supplier invoicenya
		inv_makloon = self.pool.get('account.invoice').create(cr,uid,{'partner_id' : self.browse(cr,uid,ids[0],).partner_id.id,
																'origin'  : self.browse(cr,uid,ids[0],).name,
																'account_id' : self.browse(cr,uid,ids[0],).partner_id.property_account_payable.id,
																'journal_id' : jurnal,
																'type' : 'in_invoice',
																})

		#search product (id 1 bawaan dari openerp pasti product service)
		prod_name = self.pool.get('product.product').browse(cr,uid,1,context=context).name		
		self.pool.get('account.invoice.line').create(cr,uid,{'invoice_id' : inv_makloon,
																'product_id':1,
																'name':prod_name,
																'price_unit':self.browse(cr,uid,ids[0],).origin.type_product_id.cost_model})			
		#set to "inprogress" state
		self.write(cr, uid, ids, {'state':'inprogres','invoice_id':inv_makloon}, context=context)
		return True

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
								x = 0
								#w: jika int_move yg terakhir di looping draft, maka form makloon jd sraft juga
								#self.write(cr,uid,ids,{'state' : stock_in_obj.state},context=context)
		
		# if stock_in_obj.state == 'done':
		# 	self.write(cr,uid,ids,{'state' : stock_in_obj.state},context=context)
		return self.write(cr,uid,ids,{'state_incoming' : stock_in_obj.state},context=context)

	def action_split_grade(self, cr, uid, ids, context=None):																	
		#set to "confirmed" state
		self.write(cr, uid, ids, {'state':'grade'}, context=context)
		return True

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