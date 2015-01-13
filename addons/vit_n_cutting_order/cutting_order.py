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

class vit_consumed_line(osv.osv):
	_name = "vit.consumed.line"
	_description = 'Consumed Line'
	_rec_name = 'material'
	_columns = {
		'cutting_order_id': fields.many2one('vit.cutting.order', 'Cutting Reference', required=True, ondelete='cascade', select=True),
		'material': fields.many2one('product.product', 'Material'),
		'type' : fields.selection([('main','Body'),('variation','Variation'),('accessories','Accessories')], 'Component Type'),
		'qty_total_material' : fields.float('Quantity Total'),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control"),

	}

	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['material'], context=context)
		product_obj = self.pool.get('product.product')
		#product_prod = product_obj.browse(cr,uid,reads).name

		res = []
		for record in reads:
			name = record['material'][1]
			if record['material'][1]:
				name = record['material'][1]
			res.append((record['id'], name))
		return res

vit_consumed_line()

class vit_usage_line(osv.osv):
	_name = "vit.usage.line"
	_description = 'Consumed Line'


	_columns = {
		'cutting_order_id': fields.many2one('vit.cutting.order', 'Cutting Reference',required=True, ondelete='cascade', select=True),
		'type' : fields.selection([('main','Body'),('variation','Variation')], 'Component Type'),
		'state_normal': fields.selection([('normal','Normal'),('minus','Minus')], 'Normal/Minus'),
		'qty_total_material' : fields.float('Quantity Total'),
		'product_id': fields.many2one('vit.consumed.line', 'Material',domain="[('cutting_order_id','=',parent.id)]"),
		'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control"),  
	}


	_defaults = {
        'type': lambda *a: 'main',
        'state_normal': lambda *a: 'normal',
    }

	def on_change_product_id(self, cr, uid, ids, product_id, name, context=None):
		uom = self.pool.get('vit.consumed.line').browse(cr, uid, product_id, context=context).material.uom_id.id
		
		if product_id!=False:
			return {
				'value' : {
					'product_uom' : uom,
				}
			}
		else:
			return {
				'value' : {
					'product_uom' : '',
				} 
			}

vit_usage_line()

class vit_cutting_order(osv.osv):
	_name = "vit.cutting.order"
	_description = 'Cutting Order'
	_rec_name = 'name'
	_order = 'name desc'
		
	def _calculate_order(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_order +  qty[0].m_order +  qty[0].l_order +  qty[0].xl_order +  qty[0].xxl_order 
		return res

	def _calculate_cut(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_cut +  qty[0].m_cut +  qty[0].l_cut +  qty[0].xl_cut +  qty[0].xxl_cut 
		return res

	def _calculate_cut_rej(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_cut_rej +  qty[0].m_cut_rej +  qty[0].l_cut_rej +  qty[0].xl_cut_rej +  qty[0].xxl_cut_rej 
		return res

	def _calculate_qc(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_qc +  qty[0].m_qc +  qty[0].l_qc +  qty[0].xl_qc +  qty[0].xxl_qc
		return res

	def _calculate_qc_rej(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_qc_rej +  qty[0].m_qc_rej +  qty[0].l_qc_rej +  qty[0].xl_qc_rej +  qty[0].xxl_qc_rej 
		return res

	_columns = {
		'name': fields.char('Order Cutting Reference', size=64, required=True,
            readonly=True, select=True),
		'state': fields.selection([
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('inprogres', 'Inprogres'),
            ('finish_cut', 'Cutting Finish'),
            ('finish_qc', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="", select=True),
		'type_product_id' : fields.many2one('vit.master.type', 'Model / Type', required=True , readonly=True,states={'draft': [('readonly', False)]}),
		'user_id'	:fields.many2one('res.users', 'Responsible',readonly=True,states={'draft': [('readonly', False)]}, select=True, track_visibility='onchange'),
		'date_start_cutting': fields.datetime('Start Date', select=True, readonly=True,states={'draft': [('readonly', False)]}),
		'date_end_cutting'	: fields.datetime('End Date',  select=True, readonly=True,states={'draft': [('readonly', False)]}),
		'component_main_qty'		: fields.integer('Body',readonly=True,states={'draft': [('readonly', False)]}),
		'component_variation_qty'	: fields.integer('Variation',readonly=True,states={'draft': [('readonly', False)]}),
		'category' : fields.char('Category', readonly=True,states={'draft': [('readonly', False)]}),
		'material' : fields.char('Material'),
		'variation' : fields.char('Variation'),
		'qty_total_material' : fields.float('Quantity Total'),
		'qty_total_variation' : fields.float('Quantity Total'),
		'consumed_line_ids': fields.one2many('vit.consumed.line', 'cutting_order_id', 'Cutting Lines'),
		'usage_line_ids': fields.one2many('vit.usage.line', 'cutting_order_id', 'Usage Lines'),
		's_order' : fields.float('S',readonly=True,states={'draft': [('readonly', False)]}),
		'm_order' : fields.float('M',readonly=True,states={'draft': [('readonly', False)]}),
		'l_order' : fields.float('L',readonly=True,states={'draft': [('readonly', False)]}),
		'xl_order' : fields.float('XL',readonly=True,states={'draft': [('readonly', False)]}),
		'xxl_order' : fields.float('XXL',readonly=True,states={'draft': [('readonly', False)]}),
		'qty_order' :fields.function(_calculate_order, string='Total',type="integer"),
		's_cut' : fields.float('S',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'm_cut' : fields.float('M',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'l_cut' : fields.float('L',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'xl_cut' : fields.float('XL',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'xxl_cut' : fields.float('XXL',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'qty_cut' :fields.function(_calculate_cut, string='Total',type="integer"),
		's_cut_rej' : fields.float('S',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'm_cut_rej' : fields.float('M',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'l_cut_rej' : fields.float('L',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'xl_cut_rej' : fields.float('XL',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'xxl_cut_rej' : fields.float('XXL',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'qty_cut_rej' :fields.function(_calculate_cut_rej, string='Total',type="integer"),
		's_qc' : fields.float('S',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'm_qc' : fields.float('M',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'l_qc' : fields.float('L',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'xl_qc' : fields.float('XL',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'xxl_qc' : fields.float('XXL',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'qty_qc' :fields.function(_calculate_qc, string='Total',type="integer"),
		's_qc_rej' : fields.float('S',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'm_qc_rej' : fields.float('M',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'l_qc_rej' : fields.float('L',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'xl_qc_rej' : fields.float('XL',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'xxl_qc_rej' : fields.float('XXL',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'qty_qc_rej' :fields.function(_calculate_qc_rej, string='Total',type="integer"),
		'count_list_mo' : fields.integer('Jumlah Makloon Order'),
		'count_list_internal_move' : fields.integer('Jumlah Internal Move'),



  
	}

	_defaults = {
        
        'date_start_cutting': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_end_cutting': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda self, cr, uid, c: uid,
        'name': lambda obj, cr, uid, context: '/',
        'state': 'draft',
        'count_list_mo' : 0,
        'count_list_internal_move' : 0,

      
    }


	def create(self, cr, uid, vals, context=None):
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'vit.cutting.order.seq') or '/'
		return super(vit_cutting_order, self).create(cr, uid, vals, context=context)

	def calculate(self, cr, uid, ids, context=None):
		
		self_obj = self.browse(cr,uid,ids,context=context)
		mrp_bom_obj = self.pool.get('mrp.bom')
		mrp_bom_obj_ids = mrp_bom_obj.search(cr,uid,[('name','=',self_obj[0].type_product_id.model_product)])

		loop_size = ['S','M','L','XL','XXL']
		ls_id_list = []
		for id_ls in loop_size:
			mrp_bom_obj_by_id_ls = mrp_bom_obj.search(cr,uid,[('master_model_id','=',self_obj[0].type_product_id.model_product),('size','=',id_ls)])
			
			if mrp_bom_obj_by_id_ls ==[]:
				raise osv.except_osv( 'Lengkapi BOM untuk produk ini, satu product memiliki 5 Ukuran [S,M,L,XL,XXL]' , 'Tidak Bisa Dikalkulasi/Proses')
			ls_id_list.append(mrp_bom_obj_by_id_ls[0])
		print ls_id_list
		
		bom_s_list = []
		bom_s = mrp_bom_obj.browse(cr,uid,ls_id_list[0],context =context)
		for bs in bom_s.bom_lines:
			#hanya yang non accesories yang di append
			if bs.component_type != 'accessories':
				bom_s_list.append({'material' : bs.product_id.id, 'type' : bs.component_type ,'qty_total_material': bs.product_qty * self_obj[0].s_order, 'product_uom':bs.product_uom.id})

		bom_m_list = []
		bom_m = mrp_bom_obj.browse(cr,uid,ls_id_list[1],context =context)
		for bm in bom_m.bom_lines:
			if bm.component_type != 'accessories':
				bom_m_list.append({'material' : bm.product_id.name,'type' : bs.component_type , 'qty_total_material': bm.product_qty * self_obj[0].m_order})

		bom_l_list = []
		bom_l = mrp_bom_obj.browse(cr,uid,ls_id_list[2],context =context)
		for bl in bom_l.bom_lines:
			if bl.component_type != 'accessories':
				bom_l_list.append({'material' : bl.product_id.name, 'type' : bs.component_type ,'qty_total_material': bl.product_qty * self_obj[0].l_order})

		bom_xl_list = []
		bom_xl = mrp_bom_obj.browse(cr,uid,ls_id_list[3],context =context)
		for bx in bom_xl.bom_lines:
			if bx.component_type != 'accessories':
				bom_xl_list.append({'material' : bx.product_id.name, 'type' : bs.component_type ,'qty_total_material': bx.product_qty * self_obj[0].xl_order})

		bom_xxl_list = []
		bom_xxl = mrp_bom_obj.browse(cr,uid,ls_id_list[4],context =context)
		for bxxl in bom_xxl.bom_lines:
			if bxxl.component_type != 'accessories':
				bom_xxl_list.append({'material' : bxxl.product_id.name, 'type' : bs.component_type ,'qty_total_material': bxxl.product_qty * self_obj[0].xxl_order})

		x_list = []
		for x in xrange(len(bom_s_list)):
			#import pdb;pdb.set_trace()
			# mat = bom_s_list[x]['material']+bom_m_list[x]['material']+bom_l_list[x]['material']+bom_xl_list[x]['material']+bom_xxl_list[x]['material']
			mat = bom_s_list[x]['material']
			tipe = bom_s_list[x]['type']
			qty = bom_s_list[x]['qty_total_material']+bom_m_list[x]['qty_total_material']+bom_l_list[x]['qty_total_material']+bom_xl_list[x]['qty_total_material']+bom_xxl_list[x]['qty_total_material']
			uom = bom_s_list[x]['product_uom']
			x_list.append({'material' : mat,'type' : tipe,'qty_total_material':qty, 'product_uom' : uom})
		print x_list

		if self_obj[0].consumed_line_ids != []:
			cr.execute('delete from vit_consumed_line where cutting_order_id = %d' %(ids[0]))
		
		for jk_item in x_list:
			self.write(cr,uid,ids,{'consumed_line_ids':[(0,0,{'material':jk_item['material'],'type':jk_item['type'],
				'qty_total_material':jk_item['qty_total_material'],'product_uom':jk_item['product_uom']})]})		

		####### Looping ID BOM yang telah di cari berdasarkan filter nama diatas #######
		# for x in mrp_bom_obj.browse(cr,uid,ls_id_list,context =None):
		# 	### Looping bom_lines ####	
		# 	for bom in x.bom_lines:
		# 		### Delete Dahulu saat Calculate ###
		# 		if self_obj[0].consumed_line_ids != []:
		# 			cr.execute('delete from vit_consumed_line where cutting_order_id = %d' %(ids[0]))

		# 		### Lewati Bila Ada Tipe Aksesoris ###
		# 		if self_obj[0].consumed_line_ids == []:
		# 			if  bom.component_type == 'accessories':
		# 				continue
					
		return True


	def action_sent(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'sent'}, context=context)

	def action_confirm(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'open'}, context=context)

	def action_inprogress(self, cr, uid, ids, context=None):
		lokasi_barang_jadi = 'Lokasi Bahan Baku Kain'
		lokasi_produksi = 'Lokasi Produksi'

		lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]
		lokasi_produksi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_produksi)])[0]

		### Buat Internal Move Dari Gudang Jadi ke Produksi ####
		########################################################
		### Create Dahulu ######################################
		sp_obj   = self.pool.get('stock.picking')
		sp_data1 = {
				'origin'			: self.browse(cr,uid,ids,context)[0].name,
			}

		sp_id_create = sp_obj.create(cr, uid, sp_data1, context=context)

		### Update move_lines nya ###############################
		for usage_line in self.browse(cr,uid,ids,context)[0].usage_line_ids:
			product_id = self.pool.get('vit.consumed.line').browse(cr, uid, usage_line.product_id.id, context=context).material.id
			data_line = { 
				'name'				: self.browse(cr,uid,ids,context)[0].name,
				'product_id'        : product_id,
				'product_qty'       : usage_line.qty_total_material,
				'product_uom'		: usage_line.product_uom.id,
				'location_id'       : lokasi_barang_jadi_id,
				'location_dest_id'  : lokasi_produksi_id
			}
			
			move_lines = [(0,0,data_line)]
			sp_data = {
				'move_lines'     	: move_lines,
			}
			sp_obj.write(cr, uid, sp_id_create, sp_data, context=context)
		### Lakukan Validate di Internal Move ####
		# sp_obj.draft_validate(cr,uid,[sp_id_create],context=context)
		return self.write(cr, uid, ids, {'state':'inprogres', 'count_list_internal_move':1}, context=context)

	def action_finish_cut(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'finish_cut'}, context=context)

	def action_finish_qc(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'finish_qc'}, context=context)

	def action_create_makloon(self, cr, uid, ids, context=None):
		makloon_obj = self.pool.get('vit.makloon.order').create(cr,uid,{'origin' : self.browse(cr,uid,ids[0],).id,
																		'model'  : self.browse(cr,uid,ids[0],).type_product_id.model_product,
																		})
		
		# for x in self.browse(cr,uid,ids[0],).consumed_line_ids:
		# 	if x.type == 'accessories':
		# 		continue
		# 	self.pool.get('vit.material.req.line').create(cr,uid,{'makloon_order_id' : makloon_obj, 'material':x.material.id,'type':x.type})
		self_obj = self.browse(cr,uid,ids,context=context)
		mrp_bom_obj = self.pool.get('mrp.bom')

		loop_size = ['S','M','L','XL','XXL']
		ls_id_list = []
		for id_ls in loop_size:
			mrp_bom_obj_by_id_ls = mrp_bom_obj.search(cr,uid,[('master_model_id','=',self_obj[0].type_product_id.model_product),('size','=',id_ls)])
			
			if mrp_bom_obj_by_id_ls ==[]:
				raise osv.except_osv( 'Lengkapi BOM untuk produk ini, satu product memiliki 5 Ukuran [S,M,L,XL,XXL]' , 'Tidak Bisa Dikalkulasi/Proses')
			ls_id_list.append(mrp_bom_obj_by_id_ls[0])
		print ls_id_list
		
		bom_s_list = []
		bom_s = mrp_bom_obj.browse(cr,uid,ls_id_list[0],context =context)

		for x in self.browse(cr,uid,ids[0],).consumed_line_ids:			
				#continue
				self.pool.get('vit.material.req.line').create(cr,uid,{'makloon_order_id' : makloon_obj, 'material':x.material.id,'type':x.type,'qty':x.qty_total_material})

		#tambahan accesories langsung di BoM
		for x in bom_s.bom_lines:
			if x.component_type == 'accessories':
				self.pool.get('vit.accessories.req.line').create(cr,uid,{'makloon_order_id' : makloon_obj, 'material':x.product_id.id,'type':x.component_type})

		## Update Field count_list_mo
		self.write(cr,uid,ids,{'count_list_mo': 1},context=context)
						  
		return  makloon_obj


	def action_view_makloon(self, cr, uid, ids, context=None):
		### Fungsi-fungsi untuk mengarahkan ke result list
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		## Arahkan Ke List Tree stock.picking.in dengan Ciri-ciri <record id="action_picking_tree4" model="ir.actions.act_window">
		result = mod_obj.get_object_reference(cr, uid, 'vit_n_cutting_order', 'action_makloon_tree')
# 
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		
		makl_ids = []
		spk_name = self.browse(cr,uid,ids[0],).name
		## Cari Id di makloon yang Sama dengan spk_name == origin
		makloon_obj = self.pool.get('vit.makloon.order')
		makloon_obj_ids = makloon_obj.search(cr,uid,[('origin','=',spk_name)])

		if len(makloon_obj_ids)>1:
			result['domain'] = "[('id','in',["+','.join(map(str, makloon_obj_ids))+"])]"
		else :
			makl_ids = makloon_obj_ids
			res = mod_obj.get_object_reference(cr, uid, 'vit_n_cutting_order', 'view_vit_makloon_order_form')
			result['views'] = [(res and res[1] or False, 'form')]
			result['res_id'] = makl_ids and makl_ids[0] or False

			## Cek dan Update dulu state_incoming dari incoming nya
			# self.update_state2(cr,uid,ids, pick_ids[0], context)

		return result

	def action_view_moves(self, cr, uid, ids, context=None):
		### Fungsi-fungsi untuk mengarahkan ke result list
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		## Arahkan Ke List Tree stock.picking.in dengan Ciri-ciri <record id="action_picking_tree4" model="ir.actions.act_window">
		result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree6')
# 
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		
		pick_ids = []
		spk_name = self.browse(cr,uid,ids[0],).name
		## Cari Id di incoming shipment yang Sama dengan spk_name == origin
		moves_obj = self.pool.get('stock.picking')
		moves_obj_ids = moves_obj.search(cr,uid,[('origin','=',spk_name)])

		if len(moves_obj_ids)>1:
			result['domain'] = "[('id','in',["+','.join(map(str, moves_obj_ids))+"])]"
		else :
			pick_ids = moves_obj_ids
			res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_form')
			result['views'] = [(res and res[1] or False, 'form')]
			result['res_id'] = pick_ids and pick_ids[0] or False

			## Cek dan Update dulu state_incoming dari incoming nya
			# self.update_state2(cr,uid,ids, pick_ids[0], context)

		return result

	def on_change_id(self, cr, uid, ids, type_product_id, context=None):

		vit_master_type_obj = self.pool.get('vit.master.type',)
		master_type = vit_master_type_obj.browse(cr, uid, type_product_id, context=context)

		# prod_categ_obj = self.pool.get('product.category')
		# name_prod_categ_obj = prod_categ_obj.browse(cr,uid,master_type.categ_id.id,context=context)
		return {
			'value' : {
				'category' : master_type.categ_id,
				'component_main_qty' 		: master_type.main_qty,
				'component_variation_qty' 	: master_type.variation_qty,
			}
		}

	def onchange_nominal(self, cr, uid, ids, nominal, context=None):
		# if nominal:
		# 	# terbilang = amount_to_text(nominal, 'id')
		terbilang = terbilang_func.terbilang(nominal,'IDR', 'id')
		return {'value':{'terbilang':terbilang}}
		# return "0"
	def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
		if partner_id:
			p = self.pool.get('res.partner').browse(cr, uid, partner_id)
			acc_id = p.property_account_receivable.id
			acc_id2 = p.property_account_payable.id
			
		return {'value':{'property_account_deb':acc_id,'property_account_cre':acc_id2}}


	
vit_cutting_order()