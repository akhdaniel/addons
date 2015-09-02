from osv import osv, fields
import platform
import os
import csv
import logging
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.addons.vit_upi_uang_persediaan import terbilang_func
import datetime 

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
		'total_harga' :  fields.float('Total Harga'),
		# 'qty_total_harga': fields.function(_qty_total_harga, string='Total', type='float'),
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
		list_price = self.pool.get('product.product').browse(cr, uid, product_id, context=context).list_price	
		qty = 0				
		if product_id!=False:
			return {
				'value' : {
					'product_uom' : uom,
					# 'total_harga' : list_price * qty_total_material
				}
			}
		else:
			return {
				'value' : {
					'product_uom' : '',
				} 
			}



	## ** Fungsi untuk mengalikan total harga dengan standard price ** ##
	def on_change_qty_total(self, cr, uid, ids, product_id, qty, name, context=None):
		list_price = self.pool.get('product.product').browse(cr, uid, product_id, context=context).list_price
		standard_price = self.pool.get('product.product').browse(cr, uid, product_id, context=context).standard_price
		# import pdb;pdb.set_trace()
		

		if product_id!=False:
			return {
				'value' : {
					# 'product_uom' : uom,
					'total_harga' : standard_price * qty
				}
			}
		else:
			return {
				'value' : {
					# 'product_uom' : '',
					'total_harga' : ''
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
		res[qty[0].id] = qty[0].s_order +  qty[0].m_order +  qty[0].l_order +  qty[0].xl_order +  qty[0].xxl_order +  qty[0].xxxl_order 
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

	def _get_default_journal(self, cr, uid, context=None):
		if context is None:
			context = {}
		jurnal_value_ids = []
		ir_model_id   = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
		master_journal_obj   = self.pool.get('vit.master.journal')
		master_ids   = master_journal_obj.search(cr, uid,[('appeareance','=',ir_model_id[0])])
		for master_id in master_ids:
			jurnal_value_ids.append((0,0,{'master_jurnal_id':master_id,'value':0}))
		return jurnal_value_ids

	

	def _qty_total_harga_consumed_line(self, cr, uid, ids, field_name, arg, context):
	 	res = {}
		for i in ids:
			val = 0.0
			for line in self.browse(cr, uid, i, context=context).usage_line_ids:
				val += line.total_harga
			res[i] = val
		return res

	def _qty_total_harga_sisa_line(self, cr, uid, ids, field_name, arg, context):
	 	res = {}
		for i in ids:
			val = 0.0
			for line in self.browse(cr, uid, i, context=context).sisa_ids:
				val += line.total_harga
			res[i] = val
		return res

	def _qty_total_journal_value_line(self, cr, uid, ids, field_name, arg, context):
	 	res = {}
		for i in ids:
			val = 0.0
			for line in self.browse(cr, uid, i, context=context).jurnal_value_ids:
				val += line.value
			res[i] = val
		return res
	
	def _qty_total_harga_journal_value_all_pcs(self, cr, uid, ids, field_name, arg, context):
	 	res = {}
		x = self.browse(cr,uid,ids,context=context)
	 	res[x[0].id] = x[0].qty_order * x[0].qty_total_harga_journal_value
		return res
	
	def _avg_qty_total(self, cr, uid, ids, name, arg, context=None):
	 	res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	if x[0].qty_total_harga_consumed_line!=0 and x[0].qty_order!=0:
	 		res[x[0].id] = x[0].qty_total_harga_consumed_line / x[0].qty_order
	 	else:
	 		res[x[0].id] = 0
		return res

	
	def _qty_total_wip_material(self, cr, uid, ids, name, arg, context=None):
	 	res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	res[x[0].id] = x[0].qty_total_harga_consumed_line
	 
	def _qty_total_wip(self, cr, uid, ids, name, arg, context=None):
	 	res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	# res[x[0].id] = x[0].qty_total_harga_consumed_line + (x[0].direct_labour * x[0].qty_order)+(x[0].electricity_cost * x[0].qty_order) + (x[0].factory_rent_cost* x[0].qty_order) + (x[0].cutting_cost * x[0].qty_order) + (x[0].sewing_cost* x[0].qty_order)
	 	if  x[0].qty_total_harga_consumed_line !=0 and x[0].qty_order !=0:
	 		res[x[0].id] = x[0].qty_total_harga_consumed_line + (x[0].qty_total_harga_journal_value*x[0].qty_order) -  x[0].qty_total_harga_sisa_line
	 	else:
	 		res[x[0].id]=0
		return res

	def _avg_qty_total_wip(self, cr, uid, ids, name, arg, context=None):
	 	res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	if x[0].qty_total_harga_consumed_line!=0 and x[0].qty_order!=0:
	 		res[x[0].id] = x[0].qty_total_wip / x[0].qty_order
	 	else:
	 		res[x[0].id] = 0
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
		'date_start_cutting': fields.date('Start Date', select=True, readonly=True,states={'draft': [('readonly', False)]}),
		'date_end_cutting'	: fields.date('End Date',  select=True, readonly=True,states={'draft': [('readonly', False)]}),
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
		's_order' : fields.float('S/2',readonly=True,states={'draft': [('readonly', False)]}),
		'm_order' : fields.float('M/4',readonly=True,states={'draft': [('readonly', False)]}),
		'l_order' : fields.float('L/6',readonly=True,states={'draft': [('readonly', False)]}),
		'xl_order' : fields.float('XL/8',readonly=True,states={'draft': [('readonly', False)]}),
		'xxl_order' : fields.float('XXL/10',readonly=True,states={'draft': [('readonly', False)]}),
		'xxxl_order' : fields.float('LM 12',readonly=True,states={'draft': [('readonly', False)]}),
		'qty_order' :fields.function(_calculate_order, string='Total',type="integer"),
		's_cut' : fields.float('S/2',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'm_cut' : fields.float('M/4',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'l_cut' : fields.float('L/6',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'xl_cut' : fields.float('XL/8',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'xxl_cut' : fields.float('XXL/10',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'xxxl_cut' : fields.float('LM 12',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'qty_cut' :fields.function(_calculate_cut, string='Total',type="integer"),
		's_cut_rej' : fields.float('S/2',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'm_cut_rej' : fields.float('M/4',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'l_cut_rej' : fields.float('L/6',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'xl_cut_rej' : fields.float('XL/8',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'xxl_cut_rej' : fields.float('XXL/10',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'xxxl_cut_rej' : fields.float('LM 12',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)]}),
		'qty_cut_rej' :fields.function(_calculate_cut_rej, string='Total',type="integer"),
		's_qc' : fields.float('S/2',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'm_qc' : fields.float('M/4',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'l_qc' : fields.float('L/6',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'xl_qc' : fields.float('XL/8',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'xxl_qc' : fields.float('XXL/10',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'xxxl_qc' : fields.float('LM 12',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'qty_qc' :fields.function(_calculate_qc, string='Total',type="integer"),
		's_qc_rej' : fields.float('S/2',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'm_qc_rej' : fields.float('M/4',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'l_qc_rej' : fields.float('L/6',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'xl_qc_rej' : fields.float('XL/8',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'xxl_qc_rej' : fields.float('XXL/10',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'xxxl_qc_rej' : fields.float('LM 12',readonly=True,states={'draft': [('readonly', False)],'open': [('readonly', False)],'inprogres': [('readonly', False)],'finish_cut': [('readonly', False)]}),
		'qty_qc_rej' :fields.function(_calculate_qc_rej, string='Total',type="integer"),
		'count_list_mo' : fields.integer('Jumlah Makloon Order'),
		'count_list_internal_move' : fields.integer('Jumlah Internal Move'),
		'picking_id' : fields.many2one('stock.picking','Internal Move Sisa Cutting',readonly=True),
		'product_id' : fields.many2one('product.product','Majun',readonly=True),
		'uom_id' : fields.many2one('product.uom','Satuan',readonly=True),
		'qty': fields.float('Qty'),
		'sisa_ids':fields.one2many('product.sisa','cutting_order_id','Bahan Sisa'),
		'jurnal_value_ids':fields.one2many('vit.jurnal.value','cutting_order_id','Jurnal Value'),
		# 'sisa_line_ids':fields.one2many('vit.sisa.line','cutting_order_id','Bahan Sisa'),
		# 'sisa_ids':fields.one2many('product.sisa','cutting_order_id','Bahan Sisa'),
		'direct_labour' : fields.float('Direct Labour/Pcs'),
		'electricity_cost' : fields.float('Electricity Cost/Pcs'),
		'factory_rent_cost' : fields.float('Factory Rent Cost/Pcs'),
		'cutting_cost'		: fields.related('type_product_id','cost_cut', type="float", relation='vit.master.type', string="Cutting External Cost/Pcs", store=True),
		'sewing_cost'		: fields.related('type_product_id','cost_makl', type="float", relation='vit.master.type', string="Makloon Cost/Pcs", store=True),
		'qty_total_harga_consumed_line': fields.function(_qty_total_harga_consumed_line, string='Total Usage Material', type='float',store=True),
		'qty_total_harga_journal_value': fields.function(_qty_total_journal_value_line, string='Total Overhead/Pcs', type='float',store=True),
		'qty_total_harga_journal_value_all_pcs': fields.function(_qty_total_harga_journal_value_all_pcs, string='Total Overheads * Total Pcs', type='float',store=True),
		'qty_total_wip': fields.function(_qty_total_wip, string='Total WIP', type='float',store=True),
		'avg_qty_total' : fields.function(_avg_qty_total, string='Harga Rata-rata', type='float'),
		'avg_qty_total_wip' : fields.function(_avg_qty_total_wip, string='Harga WIP/Pcs', type='float'),
		'qty_total_harga_sisa_line': fields.function(_qty_total_harga_sisa_line, string='Total Sisa Material', type='float',store=True),
		# 'factory_rent_cost' : fields.float('Factory Rent Cost/Pcs'),


	}

	_defaults = {
		
		'date_start_cutting': lambda *a: (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),
		'date_end_cutting': lambda *a: (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),
		'user_id': lambda self, cr, uid, c: uid,
		'name': lambda obj, cr, uid, context: '/',
		'state': 'draft',
		'count_list_mo' : 0,
		'count_list_internal_move' : 0,
		'product_id' : _get_default_majun,
		'uom_id' : _get_default_majun_uom,
		'jurnal_value_ids' : _get_default_journal
	}


	def create(self, cr, uid, vals, context=None):
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'vit.cutting.order.seq') or '/'
		return super(vit_cutting_order, self).create(cr, uid, vals, context=context)

	def write(self, cr, uid, ids, vals, context=None):
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
			if 'xxxl_cut' in vals :
				xxxl_order = x.xxxl_order
				#presentase max kelebihan yang di input 10%
				presentase = (xxxl_order*10)/100 				
				xxxl_cut_reject = xxxl_order - vals['xxxl_cut']
				if xxxl_cut_reject < (-presentase) :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXXL yang di input cutting melebihi (10%) dari proses qty order!')
				if xxxl_cut_reject <= 0:
					xxxl_cut_reject = 0.00
				if vals['xxxl_cut'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXXL yang di input cutting tidak boleh minus')									
				xxxl_cut_rej = {'xxxl_cut_rej':xxxl_cut_reject}
				vals = dict(vals.items()+xxxl_cut_rej.items())		

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
			if 'xxxl_qc' in vals :
				xxxlqc_order = x.xxxl_cut
				xxxl_qc_reject = xxxlqc_order - vals['xxxl_qc']
				if xxxl_qc_reject < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXXL yang di input QC cutting melebihi proses cutting!')
				if vals['xxxl_qc'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXXL yang di input QC cutting tidak boleh minus')					
				xxxl_qc_rej = {'xxxl_qc_rej':xxxl_qc_reject}
				vals = dict(vals.items()+xxxl_qc_rej.items())  

		return super(vit_cutting_order, self).write(cr, uid, ids, vals, context=context)

	
	def conf_categ_id(self,cr,uid, category,context=None):
		# import pdb;pdb.set_trace()
		conf_cutting_pool = self.pool.get('conf.cutting')
		product_category_ids = self.pool.get('product.category').search(cr,uid,[('name','=',category)])
		conf_ids = conf_cutting_pool.search(cr,uid,[('categ_id','=',product_category_ids[0])])
		conf_size = conf_cutting_pool.browse(cr,uid,conf_ids[0],context=context).loop_size
		return conf_size

	def calculate(self, cr, uid, ids, context=None):
		
		self_obj = self.browse(cr,uid,ids,context=context)
		mrp_bom_obj = self.pool.get('mrp.bom')
		mrp_bom_obj_ids = mrp_bom_obj.search(cr,uid,[('name','=',self_obj[0].type_product_id.model_product)])


		# len_size = self.conf_categ_id(cr,uid, self_obj[0].category,context)
		try:
			self.conf_categ_id(cr,uid, self_obj[0].category,context)
		except Exception, e:
			raise osv.except_osv( 'Warning!' , 'Lakukan Pengaturan dulu di Configuration Cutting, Loop size : 5 dengan Category  : Mutif, dan Loop size : 6 dengan Category : Little Mutif')	
		else:
			len_size = self.conf_categ_id(cr,uid, self_obj[0].category,context)
			
		if self.conf_categ_id(cr,uid, self_obj[0].category,context) == []:
			raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXXL yang di input QC cutting tidak boleh minus')	

		if len_size == 5:
			loop_size = ['S','M','L','XL','XXL']
			ls_id_list = []
			for id_ls in loop_size:
				mrp_bom_obj_by_id_ls = mrp_bom_obj.search(cr,uid,[('master_model_id','=',self_obj[0].type_product_id.model_product),('size','=',id_ls)])
				
				if mrp_bom_obj_by_id_ls ==[]:
					raise osv.except_osv( 'Lengkapi BOM untuk produk ini, satu product memiliki 5 Ukuran [S,M,L,XL,XXL]' , 'Tidak Bisa Dikalkulasi/Proses')
				ls_id_list.append(mrp_bom_obj_by_id_ls[0])
			# import pdb;pdb.set_trace()
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
				### Karena dalam lima ukuran tiap bom nya sama maka dapat diambil nilai id product pada salah satu ukuran saja misal s ###
				if acc_s[x]['material'] == acc_m[x]['material']:
					mat = acc_s[x]['material']
					tipe = acc_s[x]['type']
					qty = acc_s[x]['qty_total_material']+acc_m[x]['qty_total_material']+acc_l[x]['qty_total_material']+acc_xl[x]['qty_total_material']+acc_xxl[x]['qty_total_material']
					uom = acc_s[x]['product_uom']
					acc_list.append({'material' : mat,'type' : tipe,'qty_total_material':qty, 'product_uom' : uom})
				
			## ** Update 03/17/15 ** ##
			## Check Bom yang ternyata tidak sama tiap ukurannya misal  Label Mutif Size S, Label Mutif Size M, dll
			acc_list2 = []
			if len(acc_s) == len(acc_m) == len(acc_l) == len(acc_xl)== len(acc_xxl):			
				for x in xrange(len(acc_s)):
					# for y in xrange(len(acc_m)):
					if acc_s[x]['material'] != acc_m[x]['material'] !=  acc_l[x]['material'] != acc_xl[x]['material'] != acc_xxl[x]['material'] :
						acc = [acc_s[x]['material'],acc_m[x]['material'],acc_l[x]['material'],acc_xl[x]['material'],acc_xxl[x]['material']]
						qty_list = [acc_s[x]['qty_total_material'],acc_m[x]['qty_total_material'],acc_l[x]['qty_total_material'],acc_xl[x]['qty_total_material'],acc_xxl[x]['qty_total_material']]
						
						for product_id in acc:
							acc_list2.append({'material' : product_id,'type' : tipe, 'product_uom' : uom})
						acc_list2[0].update({'qty_total_material':qty_list[0]})
						acc_list2[1].update({'qty_total_material':qty_list[1]})
						acc_list2[2].update({'qty_total_material':qty_list[2]})
						acc_list2[3].update({'qty_total_material':qty_list[3]})
						acc_list2[4].update({'qty_total_material':qty_list[4]})

			##  Jika acc_list2 ada maka tambahkan ke acc_list
			if acc_list2 != []:
				acc_list+=acc_list2
			# import pdb;pdb.set_trace()
			## ** ##

		
			### Bila Recalulate lebih dari satu kali, lakukan delete terlebih dahulu vit_consumed_line dan vit_accessories_line ###
			### Supaya tidak double write ###
			if self_obj[0].consumed_line_ids != []:
				cr.execute('delete from vit_consumed_line where cutting_order_id = %d' %(ids[0]))
			if self_obj[0].accessories_line_ids != []:
				cr.execute('delete from vit_accessories_line where cutting_order_id = %d' %(ids[0]))	

			for jk_item in x_list:
				self.write(cr,uid,ids,{'consumed_line_ids':[(0,0,{'material':jk_item['material'],'type':jk_item['type'],
					'qty_total_material':jk_item['qty_total_material'],'product_uom':jk_item['product_uom']})]})		
			for jk_item in acc_list:
				# import pdb;pdb.set_trace()

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
		# elif self_obj[0].category == 'Little Mutif':
		elif len_size == 6:
			loop_size = ['S','M','L','XL','XXL','XXXL']
			# loop_size = ['2','4','6','8','10','12']

			ls_id_list = []
			for id_ls in loop_size:
				mrp_bom_obj_by_id_ls = mrp_bom_obj.search(cr,uid,[('master_model_id','=',self_obj[0].type_product_id.model_product),('size','=',id_ls)])
				
				if mrp_bom_obj_by_id_ls ==[]:
					raise osv.except_osv( 'Lengkapi BOM untuk produk ini, satu product memiliki 6 Ukuran [2,4,6,8,10,12]' , 'Tidak Bisa Dikalkulasi/Proses')
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

			bom_xxxl_list = []
			xxxl_list = []
			bom_xxxl = mrp_bom_obj.browse(cr,uid,ls_id_list[5],context =context)
			for bxxxl in bom_xxxl.bom_lines:
				if bxxxl.component_type != 'accessories':
					bom_xxxl_list.append({'material' : bxxxl.product_id.id, 'type' : bs.component_type ,'qty_total_material': bxxxl.product_qty * self_obj[0].xxxl_order})
				if bxxxl.component_type == 'accessories':
					xxxl_list.append({'material' : bxxxl.product_id.id, 'type' : bs.component_type ,'qty_total_material': bxxxl.product_qty * self_obj[0].xxxl_order})
		
			x_list = []#material
			acc_list = []#accessories
			
			#w: sorting dulu kombinasi BoM, agar struktur BoM_line sama di semua ukuran (s,m,l,xl,xxl)
			sort_s 		= sorted(bom_s_list)
			sort_m 		= sorted(bom_m_list)
			sort_l 		= sorted(bom_l_list)
			sort_xl 	= sorted(bom_xl_list)
			sort_xxl 	= sorted(bom_xxl_list)
			sort_xxxl 	= sorted(bom_xxxl_list)

			acc_s 		= sorted(s_list)
			acc_m 		= sorted(m_list)
			acc_l 		= sorted(l_list)
			acc_xl 		= sorted(xl_list)
			acc_xxl 	= sorted(xxl_list)
			acc_xxxl 	= sorted(xxxl_list)

			for x in xrange(len(sort_s)):
				# mat = bom_s_list[x]['material']+bom_m_list[x]['material']+bom_l_list[x]['material']+bom_xl_list[x]['material']+bom_xxl_list[x]['material']
				mat = sort_s[x]['material']
				tipe = sort_s[x]['type']
				qty = sort_s[x]['qty_total_material']+sort_m[x]['qty_total_material']+sort_l[x]['qty_total_material']+sort_xl[x]['qty_total_material']+sort_xxl[x]['qty_total_material']+sort_xxxl[x]['qty_total_material']
				uom = sort_s[x]['product_uom']
				x_list.append({'material' : mat,'type' : tipe,'qty_total_material':qty, 'product_uom' : uom})
			print x_list

			for x in xrange(len(acc_s)):
				# mat = bom_s_list[x]['material']+bom_m_list[x]['material']+bom_l_list[x]['material']+bom_xl_list[x]['material']+bom_xxl_list[x]['material']
				if acc_s[x]['material'] == acc_m[x]['material']:
					mat = acc_s[x]['material']
					tipe = acc_s[x]['type']

					qty = acc_s[x]['qty_total_material']+acc_m[x]['qty_total_material']+acc_l[x]['qty_total_material']+acc_xl[x]['qty_total_material']+acc_xxl[x]['qty_total_material']+acc_xxxl[x]['qty_total_material']
					uom = acc_s[x]['product_uom']
					acc_list.append({'material' : mat,'type' : tipe,'qty_total_material':qty, 'product_uom' : uom})

			## ** Update 03/17/15 ** ##s
			## Check Bom yang ternyata tidak sama tiap ukurannya misal  Label Mutif Size S, Label Mutif Size M, dll
			acc_list2 = []
			if len(acc_s) == len(acc_m) == len(acc_l) == len(acc_xl)== len(acc_xxl)== len(acc_xxxl):			
				for x in xrange(len(acc_s)):
					# for y in xrange(len(acc_m)):
					if acc_s[x]['material'] != acc_m[x]['material'] !=  acc_l[x]['material'] != acc_xl[x]['material'] != acc_xxl[x]['material'] != acc_xxxl[x]['material'] :
						acc = [acc_s[x]['material'],acc_m[x]['material'],acc_l[x]['material'],acc_xl[x]['material'],acc_xxl[x]['material'],acc_xxxl[x]['material']]
						qty_list = [acc_s[x]['qty_total_material'],acc_m[x]['qty_total_material'],acc_l[x]['qty_total_material'],acc_xl[x]['qty_total_material'],acc_xxl[x]['qty_total_material'],acc_xxxl[x]['qty_total_material']]
						
						for product_id in acc:
							acc_list2.append({'material' : product_id,'type' : tipe, 'product_uom' : uom})
						acc_list2[0].update({'qty_total_material':qty_list[0]})
						acc_list2[1].update({'qty_total_material':qty_list[1]})
						acc_list2[2].update({'qty_total_material':qty_list[2]})
						acc_list2[3].update({'qty_total_material':qty_list[3]})
						acc_list2[4].update({'qty_total_material':qty_list[4]})
						acc_list2[5].update({'qty_total_material':qty_list[5]})

			##  Jika acc_list2 ada maka tambahkan ke acc_list
			if acc_list2 != []:
				acc_list+=acc_list2
			# import pdb;pdb.set_trace()
			## ** ##




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
		else:
			raise osv.except_osv(self_obj[0].category +' '+'Harus Dalam Develop' , 'Tidak Bisa Dikalkulasi/Proses')	
		return True


	def action_sent(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'sent'}, context=context)

	def action_confirm(self, cr, uid, ids, context=None):
		if self.browse(cr,uid,ids,context)[0].s_order  == 0 and self.browse(cr,uid,ids,context)[0].m_order == 0 \
			and self.browse(cr,uid,ids,context)[0].l_order  == 0  and self.browse(cr,uid,ids,context)[0].xl_order  == 0  \
			and self.browse(cr,uid,ids,context)[0].xxl_order == 0:
			raise osv.except_osv('Lengkapi dan isi Order Quantity','Tap Order Quantity')
		if self.browse(cr,uid,ids,context)[0].consumed_line_ids == [] :
			raise osv.except_osv('Calculate Belum Dilakukan','Klik Tombol Calculate')
		return self.write(cr, uid, ids, {'state':'open'}, context=context)

	def action_inprogress(self, cr, uid, ids, context=None):

		# lokasi_barang_jadi = 'Lokasi Bahan Baku Kain'
		# # lokasi_produksi = 'Lokasi Produksi'
		# virtual_production = 'Production'
		# try:
		# 	lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]
		# 	# lokasi_produksi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_produksi)])[0]
		# except Exception, e:
		# 	raise osv.except_osv('Tidak Ditemukan' , lokasi_barang_jadi+' atau'+ lokasi_produksi)	
		
		# lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]
		# # lokasi_produksi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_produksi)])[0]
		# virtual_production_id = self.pool.get('stock.location').search(cr,uid,[('name','=',virtual_production)])[0]

		# ### Buat Internal Move Dari Gudang Jadi ke Produksi ####
		# ########################################################
		# ### Create Dahulu ######################################
		# sp_obj   = self.pool.get('stock.picking')
		# sp_data1 = {
		# 		'origin'			: self.browse(cr,uid,ids,context)[0].name,
		# 	}

		# sp_id_create = sp_obj.create(cr, uid, sp_data1, context=context)

		# ### Update move_lines nya ###############################
		# for usage_line in self.browse(cr,uid,ids,context)[0].usage_line_ids:
		# 	product_id = self.pool.get('product.product').browse(cr, uid, usage_line.product_id.id, context=context).id
		# 	data_line = { 
		# 		'name'				: self.browse(cr,uid,ids,context)[0].name,
		# 		'product_id'        : product_id,
		# 		'product_qty'       : usage_line.qty_total_material,
		# 		'product_uom'		: usage_line.product_uom.id,
		# 		'location_id'       : lokasi_barang_jadi_id,
		# 		'location_dest_id'  : virtual_production_id
		# 	}
			
		# 	move_lines = [(0,0,data_line)]
		# 	sp_data = {
		# 		'move_lines'     	: move_lines,
		# 	}
		# 	sp_obj.write(cr, uid, sp_id_create, sp_data, context=context)
		### Lakukan Validate di Internal Move ####
		# sp_obj.draft_validate(cr,uid,[sp_id_create],context=context)

			### ** Lakukan Juga Perhitungan sale_price tiap product di kali quantity nya ### **

		return self.write(cr, uid, ids, {'state':'inprogres'}, context=context)

	def action_finish_cut(self, cr, uid, ids, context=None):

		lokasi_barang_jadi = 'Lokasi Bahan Baku Kain'
		# lokasi_produksi = 'Lokasi Produksi'
		virtual_production = 'Production'
		try:
			lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]
			# lokasi_produksi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_produksi)])[0]
		except Exception, e:
			raise osv.except_osv('Tidak Ditemukan' , lokasi_barang_jadi+' atau'+ lokasi_produksi)	
		
		lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]
		# lokasi_produksi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_produksi)])[0]
		virtual_production_id = self.pool.get('stock.location').search(cr,uid,[('name','=',virtual_production)])[0]

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
				'location_dest_id'  : virtual_production_id
			}
			
			move_lines = [(0,0,data_line)]
			sp_data = {
				'move_lines'     	: move_lines,
			}
			sp_obj.write(cr, uid, sp_id_create, sp_data, context=context)

		
		if self.browse(cr,uid,ids,context)[0].usage_line_ids == []:
			raise osv.except_osv('Lengkapi dan isi Penggunaan Material yang akan dipakai','Tap Usage Material')
		if self.browse(cr,uid,ids,context)[0].s_cut  == 0 and self.browse(cr,uid,ids,context)[0].m_cut == 0 \
			and self.browse(cr,uid,ids,context)[0].l_cut  == 0  and self.browse(cr,uid,ids,context)[0].xl_cut == 0  \
			and self.browse(cr,uid,ids,context)[0].xxl_cut == 0:
			raise osv.except_osv('Lengkapi dan isi Penggunaan Cutting','Tap Cutting')
		return self.write(cr, uid, ids, {'state':'finish_cut', 'count_list_internal_move':1}, context=context)

	
	## Disini Ada Eksekusi untuk membuat jurnal direct labour,electricity, factory rent dll
	def action_finish_qc(self, cr, uid, ids, context=None):
		if self.browse(cr,uid,ids,context)[0].s_qc  == 0 and self.browse(cr,uid,ids,context)[0].m_qc == 0 \
			and self.browse(cr,uid,ids,context)[0].l_qc  == 0  and self.browse(cr,uid,ids,context)[0].xl_qc== 0  \
			and self.browse(cr,uid,ids,context)[0].xxl_qc == 0:
			raise osv.except_osv('Lengkapi dan isi Qc Cutting','Tap QC Cutting')

		if self.browse(cr,uid,ids,context)[0].qty_total_harga_journal_value  == 0 :
			raise osv.except_osv('Lengkapi dan isi Nilai Overheads','Tap Accounting')

		self.journal_overheads(cr,uid,ids,context)
		lokasi_bahan_jadi = 'Lokasi Barang Jadi'
		customer = 'Customers'
		lokasi_bahan_baku_kain = 'Lokasi Bahan Baku Kain'
		lokasi_produksi = 'Lokasi Produksi'
		virtual_production = 'Production'
		lokasi_bahan_sisa = 'Lokasi Bahan Sisa'


		try:
			lokasi_bahan_baku_kain_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_bahan_baku_kain)])[0]
			# lokasi_produksi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_produksi)])[0]
			lokasi_bahan_sisa_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_bahan_sisa)])[0]
		except Exception, e:
			raise osv.except_osv('Tidak Ditemukan' , lokasi_bahan_baku_kain+' atau '+ lokasi_produksi+' atau '+lokasi_bahan_sisa)	

		lokasi_bahan_baku_kain_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_bahan_baku_kain)])[0]
		# lokasi_produksi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_produksi)])[0]
		lokasi_bahan_sisa_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_bahan_sisa)])[0]
		lokasi_bahan_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_bahan_jadi)])[0]
		customer_id = self.pool.get('stock.location').search(cr,uid,[('name','=',customer)])[0]
		virtual_production_id = self.pool.get('stock.location').search(cr,uid,[('name','=',virtual_production)])[0]
		move_obj = self.pool.get('stock.move')
		my_form = self.browse(cr,uid,ids[0])
		if my_form.sisa_ids != []:
			#if pick_obj.browse(cr,uid,int_move,context=context)[0].state == 'done':
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
					# 'name'				: sisa.product_id.product_id.name,
					'name'				: sisa.product_id.name, # Pada product.product
					# 'product_id'        : sisa.product_id.product_id.id,
					'product_id'        : sisa.product_id.id,
					'product_qty'       : sisa.qty,
					'product_uom'		: sisa.uom_id.id,
					'location_id'       : virtual_production_id,
					'location_dest_id'  : lokasi_bahan_sisa_id, #Barang Jadi Sisa
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
											'location_id'       : virtual_production_id,
											'location_dest_id'  : lokasi_bahan_sisa_id,											
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

			
	#################################################################################
	## Membuat Jurnal overheads --> Direct Labour dan Gedung #######################################
	#################################################################################
	def journal_overheads(self, cr, uid, ids, context=None):

		##############################################################################
		# ambil master journal
		##############################################################################
		ir_model_obj = self.pool.get('ir.model')
		ir_model_ids = ir_model_obj.search(cr, uid, 
			[('model','=', self._name)], context=context) # dapat model_id dari cutting_order ex : [486]

		ir_model_fields_obj = self.pool.get('ir.model.fields')
		ir_model_fields_ids = ir_model_fields_obj.search(cr, uid, 
			[('model_id','=', ir_model_ids[0])], context=context) # dapat id dari ir.model.fields filter dari ir_model_ids (misal cutting_order)

		master_journal_obj   = self.pool.get('vit.master.journal')
		 
		# self.browse(cr,uid,ids[0],).jurnal_value_ids[0].master_jurnal_id.target_field.id #Id Field dari jurnal_value_ids misal : 4332 
		## Loop jurnal_value_ids
		for jurnal_value_id in self.browse(cr,uid,ids[0],).jurnal_value_ids:
			# master_ids   = master_journal_obj.search(cr, uid, 
			# 	[('is_active','=', True),('target_field','=',jurnal_value_id.master_jurnal_id.target_field.id)], context=context)
			master_ids   = master_journal_obj.search(cr, uid, 
				[('is_active','=', True),('name','=',jurnal_value_id.master_jurnal_id.name)], context=context)
			# import pdb;pdb.set_trace()
			for master_id in master_ids:
				master = master_journal_obj.browse(cr,uid,master_id)
				########################################################################
				# create account move utk point
				#########################################################################
				if context==None:
					context={}
				context['account_period_prefer_normal']= True
				period_id 	= self.pool.get('account.period').find(cr,uid, self.browse(cr,uid,ids[0],).date_start_cutting, context)[0]
				debit = {
					'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.debit_account_id.id,
					'debit'      : jurnal_value_id.value * self.browse(cr,uid,ids[0],).qty_order,
					'credit'     : 0.0 
				}
				
				credit = {
					'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.credit_account_id.id,
					'debit'      : 0.0 ,
					'credit'     : jurnal_value_id.value * self.browse(cr,uid,ids[0],).qty_order ,
					}

				lines = [(0,0,debit), (0,0,credit)]
				am_obj            = self.pool.get('account.move')
				am_data = {
					'journal_id'   : master.journal_id.id,
					'date'         :  self.browse(cr,uid,ids[0],).date_start_cutting,
					'ref'          : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'period_id'    : period_id,
					'line_id'      : lines ,
					}

				am_id = am_obj.create(cr, uid, am_data, context=context)
				# am_obj.button_validate(cr, uid, [am_id], context=context)



		# for master_id in master_ids:
		# 	master = master_journal_obj.browse(cr,uid,master_id)
		# 	#########################################################################
		# 	# create account move utk point
		# 	#########################################################################
		# 	if context==None:
		# 		context={}
		# 	context['account_period_prefer_normal']= True
		# 	period_id 	= self.pool.get('account.period').find(cr,uid, self.browse(cr,uid,ids[0],).date_start_cutting, context)[0]
			
		# 	if master.target_field.name == 'factory_rent_cost':
		# 		debit = {
		# 			'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
		# 			'name'       : self.browse(cr,uid,ids[0],).name,
		# 			'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
		# 			#'ref'        : 'Upah Direct Labour %s' % (self.browse(cr,uid,ids[0],).name),
		# 			'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
		# 			'account_id' : master.debit_account_id.id,
		# 			'debit'      : (self.browse(cr,uid,ids[0],).electricity_cost * self.browse(cr,uid,ids[0],).qty_order)+(self.browse(cr,uid,ids[0],).factory_rent_cost * self.browse(cr,uid,ids[0],).qty_order),
		# 			'credit'     : 0.0 
		# 		}
		# 		credit = {
		# 			'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
		# 			'name'       : self.browse(cr,uid,ids[0],).name,
		# 			'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
		# 			'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
		# 			'account_id' : master.credit_account_id.id,
		# 			'debit'      : 0.0 ,
		# 			'credit'     : self.browse(cr,uid,ids[0],).electricity_cost * self.browse(cr,uid,ids[0],).qty_order ,
		# 			}

		# 		credit2 = {
		# 			'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
		# 			'name'       : self.browse(cr,uid,ids[0],).name,
		# 			'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
		# 			'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
		# 			'account_id' : master.credit_account_id2.id,
		# 			'debit'      : 0.0 ,
		# 			'credit'     : self.browse(cr,uid,ids[0],).factory_rent_cost * self.browse(cr,uid,ids[0],).qty_order ,
		# 			}
		# 	else :
		# 		debit = {
		# 			'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
		# 			'name'       : self.browse(cr,uid,ids[0],).name,
		# 			'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
		# 			'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
		# 			'account_id' : master.debit_account_id.id,
		# 			'debit'      : self.browse(cr,uid,ids[0],).direct_labour * self.browse(cr,uid,ids[0],).qty_order ,
		# 			'credit'     : 0.0 
		# 			}
				
		# 		credit = {
		# 			'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
		# 			'name'       : self.browse(cr,uid,ids[0],).name,
		# 			'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
		# 			'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
		# 			'account_id' : master.credit_account_id.id,
		# 			'debit'      : 0.0 ,
		# 			'credit'     : self.browse(cr,uid,ids[0],).direct_labour * self.browse(cr,uid,ids[0],).qty_order ,
		# 			}

		# 	if master.credit_account_id2.id:
		# 		lines = [(0,0,debit), (0,0,credit),(0,0,credit2)]
		# 	else:
		# 		lines = [(0,0,debit), (0,0,credit)]

		# 	am_obj            = self.pool.get('account.move')
		# 	am_data = {
		# 		'journal_id'   : master.journal_id.id,
		# 		'date'         :  self.browse(cr,uid,ids[0],).date_start_cutting,
		# 		'ref'          : master.name +' '+self.browse(cr,uid,ids[0],).name,
		# 		'period_id'    : period_id,
		# 		'line_id'      : lines ,
		# 		}

		# 	am_id = am_obj.create(cr, uid, am_data, context=context)
		# 	# am_obj.button_validate(cr, uid, [am_id], context=context)

		return True



	#################################################################################
	## Membuat Jurnal Direct Labour dan Gedung #######################################
	#################################################################################
	def journal_direct_labour2(self, cr, uid, ids, context=None):
		##############################################################################
		# ambil master journal
		##############################################################################
		master_journal_obj   = self.pool.get('vit.master.journal')
		master_ids   = master_journal_obj.search(cr, uid, 
			[('is_active','=', True)], context=context)

		for master_id in master_ids:
			master = master_journal_obj.browse(cr,uid,master_id)
			#########################################################################
			# create account move utk point
			#########################################################################
			if context==None:
				context={}
			context['account_period_prefer_normal']= True
			period_id 	= self.pool.get('account.period').find(cr,uid, self.browse(cr,uid,ids[0],).date_start_cutting, context)[0]
			
			if master.target_field.name == 'factory_rent_cost':
				debit = {
					'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					#'ref'        : 'Upah Direct Labour %s' % (self.browse(cr,uid,ids[0],).name),
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.debit_account_id.id,
					'debit'      : (self.browse(cr,uid,ids[0],).electricity_cost * self.browse(cr,uid,ids[0],).qty_order)+(self.browse(cr,uid,ids[0],).factory_rent_cost * self.browse(cr,uid,ids[0],).qty_order),
					'credit'     : 0.0 
				}
				credit = {
					'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.credit_account_id.id,
					'debit'      : 0.0 ,
					'credit'     : self.browse(cr,uid,ids[0],).electricity_cost * self.browse(cr,uid,ids[0],).qty_order ,
					}

				credit2 = {
					'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.credit_account_id2.id,
					'debit'      : 0.0 ,
					'credit'     : self.browse(cr,uid,ids[0],).factory_rent_cost * self.browse(cr,uid,ids[0],).qty_order ,
					}
			else :
				debit = {
					'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.debit_account_id.id,
					'debit'      : self.browse(cr,uid,ids[0],).direct_labour * self.browse(cr,uid,ids[0],).qty_order ,
					'credit'     : 0.0 
					}
				
				credit = {
					'date'       : self.browse(cr,uid,ids[0],).date_start_cutting,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.credit_account_id.id,
					'debit'      : 0.0 ,
					'credit'     : self.browse(cr,uid,ids[0],).direct_labour * self.browse(cr,uid,ids[0],).qty_order ,
					}

			if master.credit_account_id2.id:
				lines = [(0,0,debit), (0,0,credit),(0,0,credit2)]
			else:
				lines = [(0,0,debit), (0,0,credit)]

			am_obj            = self.pool.get('account.move')
			am_data = {
				'journal_id'   : master.journal_id.id,
				'date'         :  self.browse(cr,uid,ids[0],).date_start_cutting,
				'ref'          : master.name +' '+self.browse(cr,uid,ids[0],).name,
				'period_id'    : period_id,
				'line_id'      : lines ,
				}

			am_id = am_obj.create(cr, uid, am_data, context=context)
			# am_obj.button_validate(cr, uid, [am_id], context=context)

		return True

	def action_create_makloon(self, cr, uid, ids, context=None):
		makloon_obj = self.pool.get('vit.makloon.order').create(cr,uid,{'origin' : self.browse(cr,uid,ids[0],).id,
																		'model'  : self.browse(cr,uid,ids[0],).type_product_id.model_product,
																		'type_product_id' : self.browse(cr,uid,ids[0],).type_product_id.id,
																		's_order' : self.browse(cr,uid,ids[0],).s_qc,
																		'm_order' : self.browse(cr,uid,ids[0],).m_qc,
																		'l_order' : self.browse(cr,uid,ids[0],).l_qc,
																		'xl_order' : self.browse(cr,uid,ids[0],).xl_qc,
																		'xxl_order' : self.browse(cr,uid,ids[0],).xxl_qc,
																		'xxxl_order' : self.browse(cr,uid,ids[0],).xxxl_qc,
																		'direct_labour'  : self.browse(cr,uid,ids[0],).direct_labour,
																		'electricity_cost'  : self.browse(cr,uid,ids[0],).electricity_cost,
																		'factory_rent_cost'  : self.browse(cr,uid,ids[0],).factory_rent_cost,
																		'sewing_cost'  : self.browse(cr,uid,ids[0],).sewing_cost,
																		'cutting_cost'  : self.browse(cr,uid,ids[0],).cutting_cost,
																		'avg_qty_material_total'  : self.browse(cr,uid,ids[0],).avg_qty_total,
																		'qty_total_wip_spk_cut'   : self.browse(cr,uid,ids[0],).qty_total_wip,
																		'avg_qty_total_wip_spk_cut': self.browse(cr,uid,ids[0],).avg_qty_total_wip,
																		# 'qty_total_wip' : self.browse(cr,uid,ids[0],).qty_total_wip,
																		})

		# for x in self.browse(cr,uid,ids[0],).consumed_line_ids:
		# 	if x.type == 'accessories':
		# 		continue
		# 	self.pool.get('vit.material.req.line').create(cr,uid,{'makloon_order_id' : makloon_obj, 'material':x.material.id,'type':x.type})
		self_obj = self.browse(cr,uid,ids,context=context)
		mrp_bom_obj = self.pool.get('mrp.bom')

		if self_obj[0].category == 'Little Mutif':
			loop_size = ['S','M','L','XL','XXL','XXXL']
		else :
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
		
		for x in self.browse(cr,uid,ids[0],).accessories_line_ids:
			self.pool.get('vit.accessories.req.line').create(cr,uid,{'makloon_order_id' : makloon_obj, 'material':x.material.id,'uom_id':x.material.uom_id.id,'type':x.type,'qty':x.qty_total_material})

		########################################################################################################
		#w: tambahan accesories langsung dr BoM
		#w: standard create makloon order dari yg ukuran S, sisanya(m,l,xl,xxl) pakai fungsi write
		#w: di object vit.accessories.req.line di tambahkan field bayangan size_s,size_m,size_l,size_xl,size_xxl
		#	untuk mempermudah perhitungan qty accessories di form makloon
		########################################################################################################

		#w: size S
		# for line in bom_s.bom_lines:
		# 	if line.component_type == 'accessories':
		# 		acc_line = self.pool.get('vit.accessories.req.line').create(cr,uid,{'makloon_order_id' : makloon_obj, 'material':line.product_id.id,'type':line.component_type,'uom_id':line.product_uom.id,'size_s':line.product_qty})
		# 		# size M
		# 		bom_m = mrp_bom_obj.browse(cr,uid,ls_id_list[1],context =context)
		# 		for m in bom_m.bom_lines:
		# 			if line.product_id.id == m.product_id.id:
		# 				self.pool.get('vit.accessories.req.line').write(cr,uid,acc_line,{'size_m':m.product_qty})
		# 		# size L
		# 		bom_l = mrp_bom_obj.browse(cr,uid,ls_id_list[2],context =context)
		# 		for l in bom_l.bom_lines:
		# 			if line.product_id.id == l.product_id.id:
		# 				self.pool.get('vit.accessories.req.line').write(cr,uid,acc_line,{'size_l':l.product_qty})
		# 		# size XL
		# 		bom_xl = mrp_bom_obj.browse(cr,uid,ls_id_list[3],context =context)
		# 		for xl in bom_xl.bom_lines:
		# 			if line.product_id.id == xl.product_id.id:
		# 				self.pool.get('vit.accessories.req.line').write(cr,uid,acc_line,{'size_xl':xl.product_qty})
		# 		# size XXL
		# 		bom_xxl = mrp_bom_obj.browse(cr,uid,ls_id_list[4],context =context)
		# 		for xxl in bom_xxl.bom_lines:
		# 			if line.product_id.id == xxl.product_id.id:
		# 				self.pool.get('vit.accessories.req.line').write(cr,uid,acc_line,{'size_xxl':xxl.product_qty})
				
		# 		# size XXXL
		# 		## Cek Dahulu loop_size nya bila 6 berarti little mutif
		# 		if len(loop_size) == 6:
		# 			bom_xxxl = mrp_bom_obj.browse(cr,uid,ls_id_list[5],context =context)
		# 			for xxxl in bom_xxxl.bom_lines:
		# 				if line.product_id.id == xxxl.product_id.id:
		# 					self.pool.get('vit.accessories.req.line').write(cr,uid,acc_line,{'size_xxxl':xxxl.product_qty})

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
	# _description = 'Consumed Line'

	_columns = {
		# 'cutting_order_id' : fields.many2one('vit.cutting.order','No. Cutting'),
		'cutting_order_id': fields.many2one('vit.cutting.order', 'Cutting Reference',required=True, ondelete='cascade', select=True),
		# 'product_id': fields.many2one('vit.usage.line', 'Material',required=True),
		'product_id': fields.many2one('product.product', 'Material',required=True),
		'qty' : fields.float('Qty',required=True),
		'uom_id': fields.many2one('product.uom','Satuan',required=True),
		'total_harga' :  fields.float('Total Harga'),
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

	def on_change_product_id2(self, cr, uid, ids, product_id, name, context=None):
		# import pdb;pdb.set_trace()

		# uom_id = self.pool.get('vit.usage.line').browse(cr, uid, product_id, context=context).product_id.uom_id.id
		uom_id = self.pool.get('product.product').browse(cr, uid, product_id, context=context).uom_id.id
	
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

	## ** Fungsi untuk mengalikan total harga dengan standard price ** ##
	def on_change_qty_total(self, cr, uid, ids, product_id, qty, name, context=None):
		list_price = self.pool.get('product.product').browse(cr, uid, product_id, context=context).list_price
		standard_price = self.pool.get('product.product').browse(cr, uid, product_id, context=context).standard_price

		if product_id!=False:
			return {
				'value' : {
					# 'product_uom' : uom,
					'total_harga' : standard_price * qty
				}
			}
		else:
			return {
				'value' : {
					# 'product_uom' : '',
					'total_harga' : ''
				} 
			}
		# return self.write(cr,uid,ids,{'loaded_acc':True},context=context)
	# _defaults = {
	# 	'qty': False,
	# }

product_sisa()


#class untuk value jurnal-jurnal tambahan dalam cutting relasi dengan master jurnal
class jurnal_value(osv.Model):
	_name = "vit.jurnal.value"

	_columns = {
		'cutting_order_id': fields.many2one('vit.cutting.order', 'Cutting Reference',required=True, ondelete='cascade', select=True),
		'master_jurnal_id': fields.many2one('vit.master.journal', 'Overheads',required=True),
		'value' : fields.float('Overhead Per Pcs',required=True),
	}


	def name_get(self, cr, uid, ids, context=None):
		# import pdb;pdb.set_trace()
		if not ids:
			return []
		if isinstance(ids, (int, long)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['master_jurnal_id'], context=context)

		res = []
		for record in reads:
			name = record['master_jurnal_id'][1]
			if record['master_jurnal_id'][1]:
				name = record['master_jurnal_id'][1]
			res.append((record['id'], name))
		return res
jurnal_value()


# class vit_sisa_line(osv.osv):
# 	_name = "vit.sisa.line"
# 	_description = 'Sisa Line'


# 	_columns = {
# 		'cutting_order_id': fields.many2one('vit.cutting.order', 'Cutting Reference',required=True, ondelete='cascade', select=True),
# 		'product_id': fields.many2one('product.product', 'Material',required=True),
# 		'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control"),  
# 		'qty' : fields.float('Quantity'),
# 	}

# 	def name_get(self, cr, uid, ids, context=None):
# 		# import pdb;pdb.set_trace()
# 		if not ids:
# 			return []
# 		if isinstance(ids, (int, long)):
# 			ids = [ids]
# 		reads = self.read(cr, uid, ids, ['product_id'], context=context)

# 		res = []
# 		for record in reads:
# 			name = record['product_id'][1]
# 			if record['product_id'][1]:
# 				name = record['product_id'][1]
# 			res.append((record['id'], name))
# 		return res

# 	def on_change_product_id3(self, cr, uid, ids, product_id, name, context=None):
# 		uom = self.pool.get('product.product').browse(cr, uid, product_id, context=context).uom_id.id
# 		#type_brg = self.pool.get('vit.consumed.line').browse(cr, uid, product_id, context=context).type
		
# 		if product_id!=False:
# 			return {
# 				'value' : {
# 					'product_uom' : uom,
# 					#'type' : type_brg,
# 				}
# 			}
# 		else:
# 			return {
# 				'value' : {
# 					'product_uom' : '',
# 				} 
# 			}

# vit_sisa_line()	