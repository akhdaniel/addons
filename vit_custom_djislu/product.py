from openerp.osv import fields,osv
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import time

########Product##############
class product_product(osv.osv):
	
	_inherit = "product.product"

	def _get_qty_onhand_big(self, cr, uid, ids, field_names, arg=None, context=None):
		if not ids: return {}

		res = {}
		for sm in self.browse(cr, uid, ids, context=context):
			#import pdb;pdb.set_trace()
			if sm.uos_id.id :
				ratio = sm.uos_id.factor_inv
			if not sm.uos_id.id :
				ratio = 1
			qty = sm.qty_available
			product = sm.id
			state = 'done'

			if 'location' in context.keys():
				location = context['location']

				cr.execute ('select sum(product_qty) from stock_move '\
					'where location_dest_id = %s '\
					'and product_id = %s '\
					'and state = %s',(location,product,state))
				oz = cr.fetchone()
				zoz = list(oz or 0)#karena dlm bentuk tuple di list kan dulu
				zozo = zoz[0]
				if zozo is None:
					zozo = 0.00
					
				cr.execute ('select sum(product_qty) from stock_move '\
					'where location_id = %s '\
					'and product_id = %s '\
					'and state = %s',(location,product,state))
				az = cr.fetchone()
				zaz = list(az or 0)
				zaza = zaz[0] 
				if zaza is None:
					zaza = 0.00           
				zazo = zozo-zaza
				try:
					value = zazo/ratio
				except ValueError:
					value = 0

				res[sm.id] = value
				t_sale = zazo*sm.list_price
				t_cost = zazo*sm.standard_price

			else :
				try:
					value = qty/ratio
				except ValueError:
					value = 0
				res[sm.id] = value
				t_sale = qty*sm.list_price
				t_cost = qty*sm.standard_price

			self.write(cr,uid,sm.id,{'total_sale_price':t_sale,'total_cost_price':t_cost},context=context)	
				
		return res

	def _get_qty_forcasted_big(self, cr, uid, ids, field_names, arg=None, context=None):
		if not ids: return {}

		res = {}
		for sm in self.browse(cr, uid, ids, context=context):
			#import pdb;pdb.set_trace()
			if sm.uos_id.id :
				ratio = sm.uos_id.factor_inv
			if not sm.uos_id.id :
				ratio = 1
			qty = sm.qty_available
			product = sm.id
			state = 'done'
			state2 = 'waiting'
			state3 = 'confirmed'	
			state4 = 'assigned'	

			if 'location' in context.keys():
				location = context['location']

				cr.execute ('select sum(product_qty) from stock_move '\
					'where location_dest_id = %s '\
					'and product_id = %s '\
					'and (state = %s or state = %s or state = %s or state = %s)',
					(location,product,state,state2,state3,state4))
				oz = cr.fetchone()
				zoz = list(oz or 0)#karena dlm bentuk tuple di list kan dulu
				zozo = zoz[0]
				if zozo is None:
					zozo = 0.00
					
				cr.execute ('select sum(product_qty) from stock_move '\
					'where location_id = %s '\
					'and product_id = %s '\
					'and (state = %s or state = %s or state = %s or state = %s)',
					(location,product,state,state2,state3,state4))
				az = cr.fetchone()
				zaz = list(az or 0)
				zaza = zaz[0] 
				if zaza is None:
					zaza = 0.00           
				zazo = zozo-zaza
				try:
					value = zazo/ratio
				except ValueError:
					value = 0

				res[sm.id] = value

			else :
				try:
					value = qty/ratio
				except ValueError:
					value = 0
				res[sm.id] = value
				
		return res

	#cari harga sale price di master harga jual
	def _get_sale_price(self, cr, uid, ids, field_names, arg, context=None):

		result = {}
		skrg = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

		for x in self.browse(cr,uid,ids):
			cr.execute("""SELECT mhj.small_price
							FROM  master_harga_jual mhj
							LEFT JOIN master_type_partner mtp on mhj.type_partner_id = mtp.id
							WHERE is_reference = True
							AND %s >= mhj.date_from 
							AND %s <= mhj.date_to 
							AND mhj.product_id = """ + str(x.id) + """
				  		""",(skrg,skrg))

			hj = cr.fetchone()
			if hj is not None:
				result[x.id]=hj[0]
			else:
				result[x.id]= 0.00

		return result

	_columns  = {
		'default_code' : fields.char('Internal Reference', size=64, select=True, required=True),
		'new_product' : fields.boolean('New Product?'),
		'barcode' : fields.char('Barcode',size=32),
		# 'price_id' : fields.many2one('product.price','Daftar Harga'),
		# 'partner_id' : fields.many2one('res.partner','Supplier',domain=[('supplier','=',True)]),
		'list_price2' : fields.float('Harga MT'),
		'ppn' : fields.boolean('PPn ?'),
		'bonus' : fields.boolean('Bonus'),
		'uom_ids' : fields.one2many('master.uom','product_id','List UoM'),
		'onhand_big':fields.function(_get_qty_onhand_big,string ='Big Qty on Hand',readonly=True),
		'forecasted_big':fields.function(_get_qty_forcasted_big,string ='Big Forcasted Qty',readonly=True),
		'total_sale_price': fields.float(string="Total Sale Price",readonly=True),
		'total_cost_price': fields.float(string="Total Cost Price",readonly=True),
		'ratio_uos': fields.related('uos_id','factor_inv',relation="product.uom",type="float",readonly=True,string="Ratio"),
		'sale_price': fields.function(_get_sale_price,type='float',string='Sales Price'),

			}
	_sql_constraints = [
	   ('default_code_uniq', 'unique (default_code)', 'Internal Reference sudah ada!'),('barcode_uniq', 'unique (barcode)', 'Barcode sudah ada !')
	]

product_product()

class master_uom(osv.osv):
	_name = "master.uom"

	_columns ={
		'product_id' : fields.many2one('product.product','Product'),
		'uom_id' : fields.many2one('product.uom','UoM',required=True),
		'qty2' : fields.float('Qty',digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
		
		}

class master_type_cust_supp(osv.osv):

	_name = "master.type.cust.supp"
	_rec_name = 'code'

	_columns = {
		'code' : fields.char('Code',size=64,required=True),
		'name' : fields.char('Name',size=128,required=True),
		}

class master_code_price(osv.osv):

	_name = "master.code.price"
	_rec_name = 'code'

	_columns = {
		'code' : fields.char('Code',size=64,required=True),
		'name' : fields.char('Name',size=128,required=True),
		'date_from' : fields.date('Start Date',required=True),
		'date_to' : fields.date ('End Date',required=True),
		}

class master_harga_jual(osv.osv):
	_name = "master.harga.jual"
	_rec_name = "product_id"

	_columns = {
		'product_id' : fields.many2one('product.product',required=True, string="Code"),
		'type_partner_id' : fields.many2one('res.partner.category','Group Price',change_default=True,required=True),
		'big_price' : fields.float('Big Price',required=True),
		'small_price' : fields.float('Small Price',required=True),
		'date_from' : fields.date('Start Date',required=True),
		'date_to' : fields.date('End Date',required=True),
		}

	
class master_discount(osv.osv):
	_name = "master.discount"

	#default UoM
	def _get_uom_id(self, cr, uid, *args):
		try:
			proxy = self.pool.get('ir.model.data')
			result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
			return result[1]
		except Exception, ex:
			return False

	def _qty_all_1(self, cr, uid, ids, field_name, arg, context=None):
		result = {} 
	
		for line in self.browse(cr, uid, ids, context=context):
			qty = line.qty_2
			uom = line.uom_id2.factor_inv
			qty_all = round(qty*uom,3)
			result[line.id] = qty_all
		return result

	def _qty_all_2(self, cr, uid, ids, field_name, arg, context=None):
		result = {} 
	
		for line in self.browse(cr, uid, ids, context=context):
			qty = line.qty2_2
			uom = line.uom_id.factor_inv
			qty_all = round(qty*uom,3)
			result[line.id] = qty_all
		return result

	_columns = {
		'name' : fields.char('Name', required=True),
		'partner_id' : fields.many2one('res.partner','Principle',domain=[('supplier','=',True)],required=True),
		'product_id' : fields.many2one('product.product','Bonus Product'),
		'qty_2' : fields.float('Bonus Qty2', digits_compute=dp.get_precision('Product Unit of Measure')),
		'qty' : fields.function(_qty_all_1,type="float",string='Bonus Qty',digits_compute=dp.get_precision('Product Unit of Measure')),
		'uom_id' : fields.many2one('product.uom','UoM',required=True),
		'uom_id2' : fields.many2one('product.uom','UoM',required=True),
		'value' : fields.float('Price Value',domain=[('is_percent','=',False)]),
		'per_product' : fields.boolean('Per Product'),
		'persentase' : fields.float('Percent Value', digits_compute= dp.get_precision('Discount'),domain=[('is_percent','=',True)]),
		'multi' : fields.boolean('Multiples'),
		'is_active' : fields.boolean('Active?'),
		'date_from' : fields.date('Start Date', required=True),
		'date_to' : fields.date('End Date', required=True),
		'condition_ids' : fields.one2many('master.condition','discount_id','Value Condition'),
		'condition2_ids' : fields.one2many('master.condition2','discount_id','Product Condition'),
		'condition3_ids' : fields.one2many('master.condition3','discount_id','Product Condition 2'),
		'condition4_ids' : fields.one2many('master.condition4','discount_id','Product Condition 3'),
		'condition5_ids' : fields.one2many('master.condition5','discount_id','Product Condition 4'),
		'group_price_ids' : fields.many2many('res.partner.category', id1='discount_id', id2='category_id', string='Group Price Category'),
		'is_percent' : fields.boolean('Is Percent'),
		'is_flat' : fields.boolean('Flat'),
		'type' :fields.selection([('regular','Regular Discount'),('promo','Promo Discount'),('extra','Extra Discount'),('cash','Cash Discount'),('mix','Mix Discount')],string='Type Discount',required=True),
		'min_qty_product' : fields.float('Min. Product Item',digits_compute=dp.get_precision('Product Unit of Measure')),
		'multi2' : fields.boolean('Value Condition'),
		'multi3' : fields.boolean('Multiples for New Product'),
		# 'multi_sel' : fields.selection([('general','General Multiples'),('specific','Specific Multiples for New Product')],string="Multiples"),
		'product_id2' : fields.many2one('product.product','Bonus New Product'),
		'qty2_2' : fields.float('Bonus Qty', digits_compute=dp.get_precision('Product Unit of Measure')),
		'qty2' : fields.function(_qty_all_2,type="float",string='Bonus Qty',digits_compute=dp.get_precision('Product Unit of Measure')),
		'is_category': fields.boolean('Category Condition'),
		'location_ids' : fields.many2many('sale.shop',id1='discount_id',id2='location_id',string='Location'),
		
		} 

	_defaults = {
		'uom_id' : _get_uom_id,
		'uom_id2' : _get_uom_id,
		'qty' : 1,
	}           

	def create(self, cr, uid, vals, context=None):
		viv = vals['partner_id']
		viv_t = vals['type']
		viv_l = vals['location_ids']
		viva = self.pool.get('master.discount')
		viva_s = viva.search(cr,uid,[('partner_id','=',viv),('type','=',viv_t)])#,('location_ids','in',viv_l)])
		vival = viva.browse(cr,uid,viva_s)

		for v in vival:
			vivals = v.is_active
			if vivals :
				raise osv.except_osv(_('Error!'), _('Promo untuk Principle, Lokasi dan Type discount ini ada yang masih aktif!'))

		return super(master_discount, self).create(cr, uid, vals, context=context)   

class master_condition(osv.osv):
	_name = "master.condition"

	def _get_uom_id(self, cr, uid, *args):
		try:
			proxy = self.pool.get('ir.model.data')
			result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
			return result[1]
		except Exception, ex:
			return False    

	def _qty_all(self, cr, uid, ids, field_name, arg, context=None):
		result = {} 
	
		for line in self.browse(cr, uid, ids, context=context):
			qty = line.qty2
			uom = line.uom_id.factor_inv
			qty_all = round(qty*uom,3)
			result[line.id] = qty_all
		return result

	_columns = {
		'discount_id' : fields.many2one('master.discount','Diskon ID'),
		'product_id' : fields.many2one('product.product','Product', required=True),     
		'qty' : fields.function(_qty_all,type="float",string='Min Qty2',digits_compute=dp.get_precision('Product Unit of Measure')),
		'qty2' : fields.float('Min Qty',digits_compute= dp.get_precision('Product UoS'), required=True),
		'uom_id' : fields.many2one('product.uom','UoM',required=True),

		} 

	_defaults = {
		'uom_id' : _get_uom_id,
	}                   

class master_condition2(osv.osv):
	_name = "master.condition2"

	def _get_uom_id(self, cr, uid, *args):
		try:
			proxy = self.pool.get('ir.model.data')
			result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
			return result[1]
		except Exception, ex:
			return False   

	def _qty_all(self, cr, uid, ids, field_name, arg, context=None):
		result = {} 
	
		for line in self.browse(cr, uid, ids, context=context):
			qty = line.qty2
			uom = line.uom_id.factor_inv
			qty_all = round(qty*uom,3)
			result[line.id] = qty_all
		return result

	_columns = {
		'discount_id' : fields.many2one('master.discount','Diskon ID'),
		'product_id' : fields.many2one('product.product','Product', required=True),
		'qty' : fields.function(_qty_all,type="float",string='Min Qty',digits_compute=dp.get_precision('Product Unit of Measure')),
		'qty2' : fields.float('Min Qty2',digits_compute= dp.get_precision('Product UoS'), required=True),
		'uom_id' : fields.many2one('product.uom','UoM',required=True),

		} 

	_defaults = {
		'uom_id' : _get_uom_id,
	}                

class master_condition3(osv.osv):
	_name = "master.condition3"

	_columns = {
		'discount_id' : fields.many2one('master.discount','Diskon ID'),
		'min_value' : fields.float('Min. Value'),
		'max_value' : fields.float('Max. Value'),
		'value' : fields.float('Price Value'),
		'presentase' : fields.float('Percent Value', digits_compute= dp.get_precision('Discount')),
		'is_percent' : fields.boolean('Is Percent'),
		}

class master_condition4(osv.osv):
	_name = "master.condition4"

	_columns = {
		'discount_id' : fields.many2one('master.discount','Diskon ID'),
		'min_qty' : fields.float('Min. Qty'),
		'max_qty' : fields.float('Max. Qty'),
		'value' : fields.float('Price Value'),
		'presentase' : fields.float('Percent Value', digits_compute= dp.get_precision('Discount')),
		'is_percent' : fields.boolean('Is Percent'),
		}


class master_condition5(osv.osv):
	_name = "master.condition5"

	def _get_uom_id(self, cr, uid, *args):
		try:
			proxy = self.pool.get('ir.model.data')
			result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
			return result[1]
		except Exception, ex:
			return False   

	def _qty_all(self, cr, uid, ids, field_name, arg, context=None):
		result = {} 
	
		for line in self.browse(cr, uid, ids, context=context):
			qty = line.qty2
			uom = line.uom_id.factor_inv
			qty_all = round(qty*uom,3)
			result[line.id] = qty_all
		return result

	_columns = {
		'discount_id' : fields.many2one('master.discount','Diskon ID'),
		'category_id' : fields.many2one('product.category','Category'),
		'qty' : fields.function(_qty_all,type="float",string='Min Qty2',digits_compute=dp.get_precision('Product Unit of Measure')),
		'qty2' : fields.float('Min Qty',digits_compute= dp.get_precision('Product UoS'), required=True),
		'uom_id' : fields.many2one('product.uom','UoM',required=True),
		}

	_defaults = {
		'uom_id' : _get_uom_id,
	}  

class stock_move(osv.osv):
	_inherit = "stock.move"
	_name = "stock.move"

	_columns = {
		'origin': fields.char(size=64, string="Source"),
		}    	