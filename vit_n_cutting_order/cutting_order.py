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
		'partner_id' : fields.many2one('res.partner','Supplier',domain=[('supplier','=',True)]),
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
		#'product_id': fields.many2one('vit.consumed.line', 'Material',domain="[('cutting_order_id','=',parent.id)]"),
		'product_id': fields.many2one('product.product', 'Material',required=True),
		'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control"),  
	}


	_defaults = {
		#'type': lambda *a: 'main',
		'state_normal': lambda *a: 'normal',
	}

	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['product_id'], context=context)

		res = []
		for record in reads:
			name = record['product_id'][1]
			if record['product_id'][1]:
				name = record['product_id'][1]
			res.append((record['id'], name))
		return res

	def on_change_product_id(self, cr, uid, ids, product_id, name, context=None):
		uom = self.pool.get('product.product').browse(cr, uid, product_id, context=context).uom_id.id
		#type_brg = self.pool.get('vit.consumed.line').browse(cr, uid, product_id, context=context).type
		
		if product_id!=False:
			return {
				'value' : {
					'product_uom' : uom,
					#'type' : type_brg,
				}
			}
		else:
			return {
				'value' : {
					'product_uom' : '',
				} 
			}

vit_usage_line()


class vit_accessories_line(osv.osv):
	_name = "vit.accessories.line"
	_rec_name = 'material'
	_columns = {
		'cutting_order_id': fields.many2one('vit.cutting.order', 'Cutting Reference', required=True, ondelete='cascade', select=True),
		'material': fields.many2one('product.product', 'Material'),
		'type' : fields.selection([('main','Body'),('variation','Variation'),('accessories','Accessories')], 'Component Type'),
		'qty_total_material' : fields.float('Quantity Total'),
		'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control"),
	}


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

	def _get_default_majun(self, cr, uid, context=None):
		
		product = self.pool.get('product.product').search(cr,uid,[('name','=','Majun')])
		if product != []:
			prod = self.pool.get('product.product').browse(cr,uid,product)[0]
			prod_id = prod.id
			return prod_id
		return False

	def _get_default_majun_uom(self, cr, uid, context=None):
		
		product = self.pool.get('product.product').search(cr,uid,[('name','=','Majun')])
		if product != []:
			prod = self.pool.get('product.product').browse(cr,uid,product)[0]
			uom_id = prod.uom_id.id
			return uom_id
		return False

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
		'accessories_line_ids': fields.one2many('vit.accessories.line', 'cutting_order_id', 'Accessories Lines'),
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
		'picking_id' : fields.many2one('stock.picking','Internal Move Sisa Cutting',readonly=True),
		'product_id' : fields.many2one('product.product','Majun',readonly=True),
		'uom_id' : fields.many2one('product.uom','Satuan',readonly=True),
		'qty': fields.float('Qty'),
		'sisa_ids':fields.one2many('product.sisa','cutting_order_id','Bahan Sisa'),

	}

	_defaults = {
		
		'date_start_cutting': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'date_end_cutting': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'user_id': lambda self, cr, uid, c: uid,
		'name': lambda obj, cr, uid, context: '/',
		'state': 'draft',
		'count_list_mo' : 0,
		'count_list_internal_move' : 0,
		'product_id' : _get_default_majun,
		'uom_id' : _get_default_majun_uom,
	}


	def create(self, cr, uid, vals, context=None):
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'vit.cutting.order.seq') or '/'
		return super(vit_cutting_order, self).create(cr, uid, vals, context=context)

	def write(self, cr, uid, ids, vals, context=None):
		#import pdb;pdb.set_trace()
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		for x in self.browse(cr, uid, ids, context=context):

			#perhitungan reject cutting
			if 's_cut' in vals :
				s_order = x.s_order
				#presentase max kelebihan yang di input 10%
				presentase = (s_order*10)/100 
				s_cut_reject = s_order - vals['s_cut']
				if s_cut_reject < (-presentase) :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran S yang di input cutting melebihi (10%) dari proses qty order!')
				if s_cut_reject <= 0:
					s_cut_reject = 0.00
				if vals['s_cut'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran S yang di input cutting tidak boleh minus')
				s_cut_rej = {'s_cut_rej':s_cut_reject}
				vals = dict(vals.items()+s_cut_rej.items()) 
			if 'm_cut' in vals :
				m_order = x.m_order
				#presentase max kelebihan yang di input 10%
				presentase = (m_order*10)/100 				
				m_cut_reject = m_order - vals['m_cut']
				if m_cut_reject < (-presentase) :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran M yang di input cutting melebihi (10%) dari proses qty order!')
				if m_cut_reject <= 0:
					m_cut_reject = 0.00		
				if vals['m_cut'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran M yang di input cutting tidak boleh minus')								
				m_cut_rej = {'m_cut_rej':m_cut_reject}
				vals = dict(vals.items()+m_cut_rej.items()) 	
			if 'l_cut' in vals :
				l_order = x.l_order
				#presentase max kelebihan yang di input 10%
				presentase = (l_order*10)/100 				
				l_cut_reject = l_order - vals['l_cut']
				if l_cut_reject < (-presentase) :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran L yang di input cutting melebihi (10%) dari proses qty order!')
				if l_cut_reject <= 0:
					l_cut_reject = 0.00	
				if vals['l_cut'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran l yang di input cutting tidak boleh minus')				
				l_cut_rej = {'l_cut_rej':l_cut_reject}
				vals = dict(vals.items()+l_cut_rej.items())	
			if 'xl_cut' in vals :
				xl_order = x.xl_order
				#presentase max kelebihan yang di input 10%
				presentase = (xl_order*10)/100 				
				xl_cut_reject = xl_order - vals['xl_cut']
				if xl_cut_reject < (-presentase) :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XL yang di input cutting melebihi (10%) dari proses qty order!')
				if xl_cut_reject <= 0:
					xl_cut_reject = 0.00
				if vals['xl_cut'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XL yang di input cutting tidak boleh minus')										
				xl_cut_rej = {'xl_cut_rej':xl_cut_reject}
				vals = dict(vals.items()+xl_cut_rej.items())
			if 'xxl_cut' in vals :
				xxl_order = x.xxl_order
				#presentase max kelebihan yang di input 10%
				presentase = (xxl_order*10)/100 				
				xxl_cut_reject = xxl_order - vals['xxl_cut']
				if xxl_cut_reject < (-presentase) :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXL yang di input cutting melebihi (10%) dari proses qty order!')
				if xxl_cut_reject <= 0:
					xxl_cut_reject = 0.00
				if vals['xxl_cut'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXL yang di input cutting tidak boleh minus')									
				xxl_cut_rej = {'xxl_cut_rej':xxl_cut_reject}
				vals = dict(vals.items()+xxl_cut_rej.items())	

			#perhitungan reject QC cutting
			if 's_qc' in vals :
				sqc_order = x.s_cut
				s_qc_reject = sqc_order - vals['s_qc']
				if s_qc_reject < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran S yang di input QC cutting melebihi proses cutting!')
				if vals['s_qc'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran S yang di input QC cutting tidak boleh minus')					
				s_qc_rej = {'s_qc_rej':s_qc_reject}
				vals = dict(vals.items()+s_qc_rej.items()) 
			if 'm_qc' in vals :
				mqc_order = x.m_cut
				m_qc_reject = mqc_order - vals['m_qc']
				if m_qc_reject < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran M yang di input QC cutting melebihi proses cutting!')
				if vals['m_qc'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran M yang di input QC cutting tidak boleh minus')					
				m_qc_rej = {'m_qc_rej':m_qc_reject}
				vals = dict(vals.items()+m_qc_rej.items()) 	
			if 'l_qc' in vals :
				lqc_order = x.l_cut
				l_qc_reject = lqc_order - vals['l_qc']
				if l_qc_reject < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran L yang di input QC cutting melebihi proses cutting!')
				if vals['l_qc'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran L yang di input QC cutting tidak boleh minus')
				l_qc_rej = {'l_qc_rej':l_qc_reject}
				vals = dict(vals.items()+l_qc_rej.items()) 
			if 'xl_qc' in vals :
				xlqc_order = x.xl_cut
				xl_qc_reject = xlqc_order - vals['xl_qc']
				if xl_qc_reject < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XL yang di input QC cutting melebihi proses cutting!')
				if vals['xl_qc'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XL yang di input QC cutting tidak boleh minus')					
				xl_qc_rej = {'xl_qc_rej':xl_qc_reject}
				vals = dict(vals.items()+xl_qc_rej.items()) 
			if 'xxl_qc' in vals :
				xxlqc_order = x.xxl_cut
				xxl_qc_reject = xxlqc_order - vals['xxl_qc']
				if xxl_qc_reject < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXL yang di input QC cutting melebihi proses cutting!')
				if vals['xxl_qc'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXL yang di input QC cutting tidak boleh minus')					
				xxl_qc_rej = {'xxl_qc_rej':xxl_qc_reject}
				vals = dict(vals.items()+xxl_qc_rej.items()) 

		return super(vit_cutting_order, self).write(cr, uid, ids, vals, context=context)

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
		s_list = []
		bom_s = mrp_bom_obj.browse(cr,uid,ls_id_list[0],context =context)
		for bs in bom_s.bom_lines:
			#w: hanya yang non accesories yang di append
			if bs.component_type != 'accessories':
				bom_s_list.append({'material' : bs.product_id.id, 'type' : bs.component_type ,'qty_total_material': bs.product_qty * self_obj[0].s_order, 'product_uom':bs.product_uom.id})
			#w: satu lagi hanya yang yang accesories yang di append
			if bs.component_type == 'accessories':
				s_list.append({'material' : bs.product_id.id, 'type' : bs.component_type ,'qty_total_material': bs.product_qty * self_obj[0].s_order, 'product_uom':bs.product_uom.id})

		bom_m_list = []
		m_list = []
		bom_m = mrp_bom_obj.browse(cr,uid,ls_id_list[1],context =context)
		for bm in bom_m.bom_lines:
			if bm.component_type != 'accessories':
				bom_m_list.append({'material' : bm.product_id.id,'type' : bs.component_type , 'qty_total_material': bm.product_qty * self_obj[0].m_order})
			if bm.component_type == 'accessories':
				m_list.append({'material' : bm.product_id.id,'type' : bs.component_type , 'qty_total_material': bm.product_qty * self_obj[0].m_order})


		bom_l_list = []
		l_list = []
		bom_l = mrp_bom_obj.browse(cr,uid,ls_id_list[2],context =context)
		for bl in bom_l.bom_lines:
			if bl.component_type != 'accessories':
				bom_l_list.append({'material' : bl.product_id.id, 'type' : bs.component_type ,'qty_total_material': bl.product_qty * self_obj[0].l_order})
			if bl.component_type == 'accessories':
				l_list.append({'material' : bl.product_id.id, 'type' : bs.component_type ,'qty_total_material': bl.product_qty * self_obj[0].l_order})

		bom_xl_list = []
		xl_list = []
		bom_xl = mrp_bom_obj.browse(cr,uid,ls_id_list[3],context =context)
		for bx in bom_xl.bom_lines:
			if bx.component_type != 'accessories':
				bom_xl_list.append({'material' : bx.product_id.id, 'type' : bs.component_type ,'qty_total_material': bx.product_qty * self_obj[0].xl_order})
			if bx.component_type == 'accessories':
				xl_list.append({'material' : bx.product_id.id, 'type' : bs.component_type ,'qty_total_material': bx.product_qty * self_obj[0].xl_order})


		bom_xxl_list = []
		xxl_list = []
		bom_xxl = mrp_bom_obj.browse(cr,uid,ls_id_list[4],context =context)
		for bxxl in bom_xxl.bom_lines:
			if bxxl.component_type != 'accessories':
				bom_xxl_list.append({'material' : bxxl.product_id.id, 'type' : bs.component_type ,'qty_total_material': bxxl.product_qty * self_obj[0].xxl_order})
			if bxxl.component_type == 'accessories':
				xxl_list.append({'material' : bxxl.product_id.id, 'type' : bs.component_type ,'qty_total_material': bxxl.product_qty * self_obj[0].xxl_order})

		x_list = []#material
		acc_list = []#accessories
		
		#w: sorting dulu kombinasi BoM, agar struktur BoM_line sama di semua ukuran (s,m,l,xl,xxl)
		sort_s 		= sorted(bom_s_list)
		sort_m 		= sorted(bom_m_list)
		sort_l 		= sorted(bom_l_list)
		sort_xl 	= sorted(bom_xl_list)
		sort_xxl 	= sorted(bom_xxl_list)

		acc_s 		= sorted(s_list)
		acc_m 		= sorted(m_list)
		acc_l 		= sorted(l_list)
		acc_xl 		= sorted(xl_list)
		acc_xxl 	= sorted(xxl_list)

		for x in xrange(len(sort_s)):
			# mat = bom_s_list[x]['material']+bom_m_list[x]['material']+bom_l_list[x]['material']+bom_xl_list[x]['material']+bom_xxl_list[x]['material']
			mat = sort_s[x]['material']
			tipe = sort_s[x]['type']
			qty = sort_s[x]['qty_total_material']+sort_m[x]['qty_total_material']+sort_l[x]['qty_total_material']+sort_xl[x]['qty_total_material']+sort_xxl[x]['qty_total_material']
			uom = sort_s[x]['product_uom']
			x_list.append({'material' : mat,'type' : tipe,'qty_total_material':qty, 'product_uom' : uom})
		print x_list

		for x in xrange(len(acc_s)):
			# mat = bom_s_list[x]['material']+bom_m_list[x]['material']+bom_l_list[x]['material']+bom_xl_list[x]['material']+bom_xxl_list[x]['material']
			mat = acc_s[x]['material']
			tipe = acc_s[x]['type']
			qty = acc_s[x]['qty_total_material']+acc_m[x]['qty_total_material']+acc_l[x]['qty_total_material']+acc_xl[x]['qty_total_material']+acc_xxl[x]['qty_total_material']
			uom = acc_s[x]['product_uom']
			acc_list.append({'material' : mat,'type' : tipe,'qty_total_material':qty, 'product_uom' : uom})

		if self_obj[0].consumed_line_ids != []:
			cr.execute('delete from vit_consumed_line where cutting_order_id = %d' %(ids[0]))
		if self_obj[0].accessories_line_ids != []:
			cr.execute('delete from vit_accessories_line where cutting_order_id = %d' %(ids[0]))	

		for jk_item in x_list:
			self.write(cr,uid,ids,{'consumed_line_ids':[(0,0,{'material':jk_item['material'],'type':jk_item['type'],
				'qty_total_material':jk_item['qty_total_material'],'product_uom':jk_item['product_uom']})]})		
		for jk_item in acc_list:
			self.write(cr,uid,ids,{'accessories_line_ids':[(0,0,{'material':jk_item['material'],'type':jk_item['type'],
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
		#import pdb;pdb.set_trace()
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
			product_id = self.pool.get('product.product').browse(cr, uid, usage_line.product_id.id, context=context).id
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
		lokasi_barang_jadi = 'Lokasi Bahan Baku Kain'
		lokasi_produksi = 'Lokasi Produksi'

		lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]
		lokasi_produksi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_produksi)])[0]
		move_obj = self.pool.get('stock.move')
		my_form = self.browse(cr,uid,ids[0])

		if my_form.sisa_ids != []:
			#if pick_obj.browse(cr,uid,int_move,context=context)[0].state == 'done':
			#import pdb;pdb.set_trace()
			### Buat Internal Move Balik Dari Producksi ke Gudang Jadi (dibalik)####
			########################################################
			### Create Dahulu ######################################
			sp_obj   = self.pool.get('stock.picking')
			sp_data1 = {
					'origin'			: my_form.name,
					'note'				: 'Bahan Sisa Cutting',
				}

			sp_id_create = sp_obj.create(cr, uid, sp_data1, context=context)
			
			### Update move_lines nya ###############################
			for sisa in self.browse(cr,uid,ids,context)[0].sisa_ids:
				data_line = { 
					'name'				: sisa.product_id.product_id.name,
					'product_id'        : sisa.product_id.product_id.id,
					'product_qty'       : sisa.qty,
					'product_uom'		: sisa.uom_id.id,
					'location_id'       : lokasi_produksi_id,
					'location_dest_id'  : lokasi_barang_jadi_id,
				}
				
				move_lines = [(0,0,data_line)]
				sp_data = {
					'move_lines'     	: move_lines,
				}
				sp_obj.write(cr, uid, sp_id_create, sp_data, context=context)

			#tambahkan move jika qty majun di isi
			if my_form.product_id.id is not False:
				if my_form.qty > 0.00 :
					move_obj.create(cr,uid,{'picking_id'		: sp_id_create,
											'product_id'		: my_form.product_id.id,
											'name'				: my_form.product_id.name,
											'product_qty'       : my_form.qty,
											'product_uom'		: my_form.uom_id.id,
											'location_id'       : lokasi_produksi_id,
											'location_dest_id'  : lokasi_barang_jadi_id,											
											}, context=context)

			self.write(cr, uid, ids[0], {'picking_id':sp_id_create}, context=context)
		#jika belum Done, edit qty tiap line nya
			# if int_move[0].state != 'done':
			# 	int_move_id = int_move.id
			# 	move_lines = self.pool.get('stock.move').search(cr,uid,[('picking_id','=',int_move_id)])
			# 	browse_ml = self.pool.get('stock.move').browse(cr,uid,move_lines,context=context)
			# 	for mv in browse_ml:
			# 		if mv.state != 'done':
			# 			move_id = mv.id
			# 			self.pool.get('stock.move').write(cr,uid,move_id,{'product_qty'})

	
		#cek dahulu apakah di sisa cutting ada yang di input tapi qtynya nol
		for x in self.browse(cr,uid,ids[0]).sisa_ids:
			if x.qty <= 0 :
				raise osv.except_osv('Warning!' , 'Sisa QC/Cutting tidak boleh dinput nol atau kurang dari nol!')

		self.write(cr, uid, ids, {'state':'finish_qc'}, context=context)
		return True

	def action_create_makloon(self, cr, uid, ids, context=None):
		#import pdb;pdb.set_trace()
		makloon_obj = self.pool.get('vit.makloon.order').create(cr,uid,{'origin' : self.browse(cr,uid,ids[0],).id,
																		'model'  : self.browse(cr,uid,ids[0],).type_product_id.model_product,
																		's_order' : self.browse(cr,uid,ids[0],).s_qc,
																		'm_order' : self.browse(cr,uid,ids[0],).m_qc,
																		'l_order' : self.browse(cr,uid,ids[0],).l_qc,
																		'xl_order' : self.browse(cr,uid,ids[0],).xl_qc,
																		'xxl_order' : self.browse(cr,uid,ids[0],).xxl_qc,
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
		

		########################################################################################################
		#w: tambahan accesories langsung dr BoM
		#w: standard create makloon order dari yg ukuran S, sisanya(m,l,xl,xxl) pakai fungsi write
		#w: di object vit.accessories.req.line di tambahkan field bayangan size_s,size_m,size_l,size_xl,size_xxl
		#	untuk mempermudah perhitungan qty accessories di form makloon
		########################################################################################################

		#w: size S
		for line in bom_s.bom_lines:
			if line.component_type == 'accessories':
				acc_line = self.pool.get('vit.accessories.req.line').create(cr,uid,{'makloon_order_id' : makloon_obj, 'material':line.product_id.id,'type':line.component_type,'uom_id':line.product_uom.id,'size_s':line.product_qty})
				# size M
				bom_m = mrp_bom_obj.browse(cr,uid,ls_id_list[1],context =context)
				for m in bom_m.bom_lines:
					if line.product_id.id == m.product_id.id:
						self.pool.get('vit.accessories.req.line').write(cr,uid,acc_line,{'size_m':m.product_qty})
				# size L
				bom_l = mrp_bom_obj.browse(cr,uid,ls_id_list[2],context =context)
				for l in bom_l.bom_lines:
					if line.product_id.id == l.product_id.id:
						self.pool.get('vit.accessories.req.line').write(cr,uid,acc_line,{'size_l':l.product_qty})
				# size XL
				bom_xl = mrp_bom_obj.browse(cr,uid,ls_id_list[3],context =context)
				for xl in bom_xl.bom_lines:
					if line.product_id.id == xl.product_id.id:
						self.pool.get('vit.accessories.req.line').write(cr,uid,acc_line,{'size_xl':xl.product_qty})
				# size XXL
				bom_xxl = mrp_bom_obj.browse(cr,uid,ls_id_list[4],context =context)
				for xxl in bom_xxl.bom_lines:
					if line.product_id.id == xxl.product_id.id:
						self.pool.get('vit.accessories.req.line').write(cr,uid,acc_line,{'size_xxl':xxl.product_qty})

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


#class u/ menampung sisa bahan dari cutting
class product_sisa(osv.Model):
	_name = "product.sisa"

	def on_change_product_id(self, cr, uid, ids, product_id, name, context=None):
		uom_id = self.pool.get('vit.usage.line').browse(cr, uid, product_id, context=context).product_id.uom_id.id
	
		if product_id!=False:
			return {
				'value' : {
					'uom_id' : uom_id,
				}
			}
		else:
			return {
				'value' : {
					'uom_id' : '',
				} 
			}

	_columns = {
		'cutting_order_id' : fields.many2one('vit.cutting.order','No. Cutting'),
		'product_id': fields.many2one('vit.usage.line', 'Material',domain="[('cutting_order_id','=',parent.id)]",required=True),
		'qty' : fields.float('Qty',required=True),
		'uom_id': fields.many2one('product.uom','Satuan',required=True),
	}

	_defaults = {
		'qty': False,
	}

product_sisa()	