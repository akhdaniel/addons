from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

import datetime

import sets

class sale_order_line(osv.osv):
	_inherit = "sale.order.line"

	def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
			
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		res = {}
		if context is None:
			context = {}	

		
		for line in self.browse(cr, uid, ids, context=context):

			#####################################################################
			#mengakali QTY besar dan kecil
			#####################################################################
			#konversi untuk di write ke product uom/ous qty
			cf = line.product_id.uos_coeff
			sm_uom = line.qty_small * cf
			bg_uos = line.qty_big / cf
			bg = line.qty_big
			ratio =  line.product_uos.factor_inv

			sm = line.qty_small

			uom = (sm)+ round(bg*ratio,3)
			#uom =  bg_uos + sm
			
			gro = line.price_unit * uom

			if uom == 0.00:
				uom = 1

			uos = sm_uom + bg

			#harus di bagi uom qty dulu
			discv = line.disc_value /uom
			discv2 = line.p_disc_value/uom
			discv3 = line.p_disc_value_x/uom
			discv4 = line.p_disc_value_c/uom
			discv5 = line.p_disc_value_m/uom
			#reg discount
			pri = (line.price_unit-discv) * (1 - (line.discount or 0.0) / 100.0)
			#promo discount

			pric = ((pri - discv2) * (1 - (line.p_disc_pre or 0.0) / 100.0))
			#xtra discount

			pric2 = ((pric - discv3) * (1 - (line.p_disc_pre_x or 0.0) / 100.0))
			#cash discount

			pric3 = ((pric2 - discv4) * (1 - (line.p_disc_pre_c or 0.0) / 100.0))
			#mix discount

			price = ((pric3 - discv5) * (1 - (line.p_disc_pre_m or 0.0) / 100.0))	

			# #harus di bagi uom qty dulu
			# dis = line.disc_value
			# dis2 = line.p_disc_value
			# dis3 = line.p_disc_value_x
			# dis4 = line.p_disc_value_c
			# dis5 = line.p_disc_value_m


			# if line.p_discount == 0.00:
			# 	per1 == 0.00
			# per1 = gro*line.p_discount/100

			# if line.p_disc_pre == 0.00:
			# 	per2 == 0.00
			# per2 = gro*line.p_disc_pre/100

			# if line.p_disc_pre_x == 0.00:
			# 	per1 == 0.00
			# per_1 = gro*line.p_disc_pre/100

			# if line.p_disc_pre == 0.00:
			# 	per1 == 0.00
			# per_1 = gro*line.p_disc_pre/100

			# #reg discount
			# pr = gro - dis - (gro*line.p_disc_pre/100) #* (1 - (line.discount or 0.0) / 100.0)
			# #promo discount

			# pric = ((pri - discv2) * (1 - (line.p_disc_pre or 0.0) / 100.0))
			# #xtra discount

			# pric2 = ((pric - discv3) * (1 - (line.p_disc_pre_x or 0.0) / 100.0))
			# #cash discount

			# pric3 = ((pric2 - discv4) * (1 - (line.p_disc_pre_c or 0.0) / 100.0))
			# #mix discount

			# price = ((pric3 - discv5) * (1 - (line.p_disc_pre_m or 0.0) / 100.0))
			
			gross = self.write(cr, uid,line.id, {'gross_tot': gro},context=context)	
			#import pdb;pdb.set_trace()				
			taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, uom, line.product_id, line.order_id.partner_id)
			cur = line.order_id.pricelist_id.currency_id
			res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
			self.write(cr,uid,line.id,{'tes':taxes['total']},context=context)
		return res


	_columns = {
		'volume' : fields.float('Volume (m3)'),
		'volume2' : fields.related('product_id','volume',string ='Vlm'),
		'coeff' : fields.float('Ratio Uos'),
		'uos2' :fields.char('Satuan Besar'),
		'tax_id': fields.many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes'),
		'disc_value' : fields.float('R.Disc (Price)'),
		'gross_tot' : fields.float('Gross Total'),
		'discount': fields.float('R.Disc (%)', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}),
		'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
		'partner_id' : fields.many2one('res.partner','Principle'),# field bayangan principle sesuai dg sale order
		#'product_id': fields.many2one('product.product', 'Product', domain="[('seller_ids[0].name.id','=',order_id)]", change_default=True),
		#regular disc		
		'r_flat' : fields.boolean('R.Flat'),
		#promo discount
		'p_disc_value' : fields.float('P.Disc (Price)'),
		'p_disc_pre' : fields.float('P.Disc (%)',digits_compute= dp.get_precision('Discount')),
		'p_flat' : fields.boolean('P.Flat'),
		#extra discount
		'p_disc_value_x' : fields.float('X.Disc (Price)'),
		'p_disc_pre_x' : fields.float('X.Disc (%)',digits_compute= dp.get_precision('Discount')),
		'x_flat' : fields.boolean('X.Flat'),
		#cash discount
		'p_disc_value_c' : fields.float('C.Disc (Price)'),
		'p_disc_pre_c' : fields.float('C.Disc (%)',digits_compute= dp.get_precision('Discount')),
		'c_flat' : fields.boolean('C.Flat'),
		#mix  discount
		'p_disc_value_m' : fields.float('M.Disc (Price)'),
		'p_disc_pre_m' : fields.float('M.Disc (%)',digits_compute= dp.get_precision('Discount')),
		'm_flat' : fields.boolean('M.Flat'),	

		'qty_small':fields.float('Small Qty',digits_compute=dp.get_precision('Product Unit of Measure')),
		'qty_big':fields.float('Big Qty',digits_compute= dp.get_precision('Product UoS'),required=True),	

		'tes' :fields.float('tes'),				

	}

	# _defaults ={
	# 	'partner_id':_get_principle,
	# 	}	

	def _get_line_qty2_big(self, cr, uid, line, context=None):

		return line.qty_big

	def _get_line_qty2(self, cr, uid, line, context=None):

		return line.qty_small

	def _get_line_uom2(self, cr, uid, line, context=None):

		return line.product_uom.id

	def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
		"""   invoice generation (making sure to call super() to establish
		   a clean extension chain).

		   :param browse_record line: sale.order.line record to invoice
		   :param int account_id: optional ID of a G/L account to force
			   (this is used for returning products including service)
		   :return: dict of values to create() the invoice line
		"""
		res = {}
		if not line.invoiced:
			if not account_id:
				if line.product_id:
					account_id = line.product_id.property_account_income.id
					if not account_id:
						account_id = line.product_id.categ_id.property_account_income_categ.id
					if not account_id:
						raise osv.except_osv(_('Error!'),
								_('Please define income account for this product: "%s" (id:%d).') % \
									(line.product_id.name, line.product_id.id,))
				else:
					prop = self.pool.get('ir.property').get(cr, uid,
							'property_account_income_categ', 'product.category',
							context=context)
					account_id = prop and prop.id or False
			uosqty = self._get_line_qty2_big(cr, uid, line, context=context)
			uos_id = self._get_line_uom(cr, uid, line, context=context)

			#cari small uom
			uomqty = self._get_line_qty2(cr, uid, line, context=context)
			uom_id = self._get_line_uom2(cr, uid, line, context=context)

			pu = 0.0
			pu2 = 0.0
			if uosqty:
				pu = round(line.price_unit * line.product_uom_qty / uosqty,
						self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))

			if uomqty:
				pu2 = round(line.price_unit,
						self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))

			t_disc = round(line.gross_tot - line.price_subtotal,3)

			u_price = line.price_subtotal/line.product_uom_qty

			fpos = line.order_id.fiscal_position or False
			account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
			if not account_id:
				raise osv.except_osv(_('Error!'),
							_('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
			res = {
				'name': line.name,
				'sequence': line.sequence,
				'origin': line.order_id.name,
				'account_id': account_id,
				'price_unit': u_price,
				'qty': uosqty,
				'discount': line.discount,
				'disc_tot':t_disc,
				'uos_id': uos_id,
				'quantity2':uomqty,
				'uom_id':uom_id,
				'product_id': line.product_id.id or False,
				'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
				'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
			}

		return res

	def onchange_uos(self, cr, uid, vals,coeff,product_uos_qty, context=None):
		if coeff == 0.00 :
			coeff = 1 
		if coeff != [] :
			uosm = {'product_uom_qty': round(product_uos_qty/ coeff,3)}#pembulatan 3 digit sesudah koma
			return {'value': uosm}
		return True	  	

	def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
			uom=False, qty_uos=0, uos=False, name='', partner_id=False,
			lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
		context = context or {}
		lang = lang or context.get('lang',False)
		if not  partner_id:
			raise osv.except_osv(_('Customer belum di isi!'), _('Sebelum pilih produk,\n isi dulu customernya.'))
			return True
		warning = {}
		
		product_uom_obj = self.pool.get('product.uom')
		partner_obj = self.pool.get('res.partner')
		product_obj = self.pool.get('product.product')
		context = {'lang': lang, 'partner_id': partner_id}    

		if partner_id:
			lang = partner_obj.browse(cr, uid, partner_id).lang
		context_partner = {'lang': lang, 'partner_id': partner_id}

		if not product:
			return {'value': {'th_weight': 0,
				'product_uos_qty': qty}, 'domain': {'product_uom': [],
				   'product_uos': []}}
		if not date_order:
			date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

		result = {}
		warning_msgs = ''
		product_obj = product_obj.browse(cr, uid, product, context=context_partner)

		uom2 = False
		if uom:
			uom2 = product_uom_obj.browse(cr, uid, uom)
			if product_obj.uom_id.category_id.id != uom2.category_id.id:
				uom = False
		if uos:
			if product_obj.uos_id:
				uos2 = product_uom_obj.browse(cr, uid, uos)
				if product_obj.uos_id.category_id.id != uos2.category_id.id:
					uos = False
			else:
				uos = False
		fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
		if update_tax: #The quantity only have changed
			result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

		if not flag:
			result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
			if product_obj.description_sale:
				result['name'] += '\n'+product_obj.description_sale
		domain = {}
		if (not uom) and (not uos):
			result['product_uom'] = product_obj.uom_id.id
			if product_obj.uos_id:
				result['product_uos'] = product_obj.uos_id.id
				result['product_uos_qty'] = qty * product_obj.uos_coeff
				uos_category_id = product_obj.uos_id.category_id.id
			else:
				result['product_uos'] = False
				result['product_uos_qty'] = qty
				uos_category_id = False
			result['th_weight'] = qty * product_obj.weight
			result['volume'] = qty * product_obj.volume
			domain = {'product_uom':
						[('category_id', '=', product_obj.uom_id.category_id.id)],
						'product_uos':
						[('category_id', '=', uos_category_id)]}
		elif uos and not uom: # only happens if uom is False
			result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
			result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
			result['th_weight'] = result['product_uom_qty'] * product_obj.weight
			result['volume'] = result['product_uom_qty'] * product_obj.volume
		elif uom: # whether uos is set or not
			default_uom = product_obj.uom_id and product_obj.uom_id.id
			q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
			if product_obj.uos_id:
				result['product_uos'] = product_obj.uos_id.id
				result['product_uos_qty'] = qty * product_obj.uos_coeff
			else:
				result['product_uos'] = False
				result['product_uos_qty'] = qty
			result['th_weight'] = q * product_obj.weight        # Round the quantity up
			result['volume'] = q * product_obj.volume        # Round the quantity up
			result['coeff']= product_obj.uos_coeff
			result['uos2']= product_obj.uos_id.name

		if not uom2:
			uom2 = product_obj.uom_id
		# get unit price

		if not pricelist:
			warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
					'Please set one before choosing a product.')
			warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
		else:
			price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
					product, qty or 1.0, partner_id, {
						'uom': uom or result.get('product_uom'),
						'date': date_order,
						})[pricelist]
			if price is False:
				warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
						"You have to change either the product, the quantity or the pricelist.")

				warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
			else:
				result.update({'price_unit': price})
						
		if warning_msgs:
			warning = {
					   'title': _('Configuration Error!'),
					   'message' : warning_msgs
					}

		cust = partner_obj.browse(cr,uid,partner_id)
		prod_supplier = product_obj.seller_ids
		group = cust.type_partner_id.id

		#jika product tidak mempunyai supplier
		if prod_supplier == [] :
			raise osv.except_osv(_('Error!'), _('Product ini tidak punya principal'))

		#import pdb;pdb.set_trace()
		if prod_supplier != [] :	
			su = prod_supplier[0].id    	
		if not group :
			raise osv.except_osv(_('Error!'), _('Customer ini tidak mempunyai group harga yang sesuai'))

		if group:	    		
		
			price = self.pool.get('master.harga.jual')

			#inisialisasi tanggal aktif(sekarang)
			skrg = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

			#cari  di tabel harga jual yang masih berlaku
			u_price = price.search(cr,uid,[('product_id','=',product),('type_partner_id','=',group),('date_from','<=',skrg),('date_to','>=',skrg)])
			if u_price == []:
				raise osv.except_osv(_('Error!'), _('Harga untuk product yang dipilih tidak ada / sudah tidak berlaku !'))
			if u_price != []:
				u_prc = u_price[0]
				list_prc = price.browse(cr,uid,u_prc)
				small_price = list_prc.small_price 
			result.update({'price_unit': small_price})
		   
		return {'value': result, 'domain': domain, 'warning': warning}


class sale_order(osv.osv):
	_inherit = "sale.order"	
	_name = "sale.order"
	#_rec_name = "partner_id2"

	def _amount_alll(self, cr, uid, ids, field_name, arg, context=None):
		cur_obj = self.pool.get('res.currency')
		res = {}
		#import pdb;pdb.set_trace()
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'amount_untaxed': 0.0,
				'amount_tax': 0.0,
				'amount_total': 0.0,
			}
			val = val1 = 0.0
			cur = order.pricelist_id.currency_id
			for line in order.order_line:
				val1 += line.price_subtotal
				val += self._amount_line_tax(cr, uid, line, context=context)
			res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
			res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
			res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
		return res

	def _get_order(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
			result[line.order_id.id] = True
		return result.keys()

	def create(self, cr, uid, vals, context=None):

		viv = vals['partner_id']
		vivals = self.pool.get('res.partner').browse(cr,uid,viv).trouble
		if vivals :
			raise osv.except_osv(_('Error!'), _('Customer ini sudah ditandai sebagai customer yang bermasalah!'))
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
		return super(sale_order, self).create(cr, uid, vals, context=context)	

	#default shop sesuai cabang di master employee log in
	def _get_default_werehouse(self, cr, uid, context=None):
		
		emplo = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		if not emplo:
			raise osv.except_osv(_('Error!'), _('User tidak di link kan ke master pegawai!'))
		emp = self.pool.get('hr.employee').browse(cr,uid,emplo)[0]
		em = emp.location_id.id

		return em

		#mengakali penambahan kode gudang/cabang pada SO
	def _get_default_lo(self, cr, uid, context=None):
		
		emplo = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		if not emplo:
			raise osv.except_osv(_('Error!'), _('User tidak di link kan ke master pegawai!'))
		emp = self.pool.get('hr.employee').browse(cr,uid,emplo)[0]
		em = emp.location_id.code

		return em

		#tambah kode (NIK) pegawai/salesman pada SO
	def _get_nik(self, cr, uid, context=None):
		
		emplo = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		ni = self.pool.get('hr.employee').browse(cr,uid,emplo)[0]
		nik = ni.nik

		return nik

	#tambahkan gudang di invoice sesuai gudang di PO
	def _prepare_invoice(self, cr, uid, order, lines, context=None):
		#import pdb;pdb.set_trace()
		res=super(sale_order,self)._prepare_invoice(cr, uid, order, lines, context=context)
		# if order.warehouse_id :
		res['location_id']=order.location_id.id
		res['date_invoice']=order.date_order
		res['nik']=order.nik
		res['volume']=order.volume_tot
		return res
	

	#hitung kubikasi per SO
	def _compute_volume(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'volume_tot': 0.0,
				}
		val =  0.0
		for line in order.order_line:
			val += line.volume
		res[order.id]['volume_tot'] = val
		return res

	#hitung berat total per SO
	# def _compute_tonase(self, cr, uid, ids, field_name, arg, context=None):
	# 	import pdb;pdb.set_trace()
	# 	res = {}
	# 	for orde in self.browse(cr, uid, ids, context=context):
	# 		res[orde.id] = {
	# 			'tonase_tot': 0.0,
	# 			}
	# 	vala =  0.0
	# 	for ine in orde.order_line:
	# 		vala += ine.th_weight
	# 	res[orde.id]['tonase_tot'] = vala
	# 	return res	


	_columns = {
		'partner_id2' : fields.many2one('limit.customer','Principal',domain="[('partner_id2','=',partner_id)]",required=True),
		'discount2' : fields.float('Promo',readonly=True),	
		'volume_tot' : fields.function(_compute_volume,string="Total Volume", type="float",multi="sums"),
		#'tonase_tot' :fields.function(_compute_tonase,string="Berat Total", type="float"),

		'date_order': fields.date('Date', required=True, readonly=True, select=True),
		'warehouse_id' : fields.many2one('stock.warehouse','Location',readonly=True),

		'credit' : fields.related('partner_id','credit',type="float",string="Total AR",readonly=True),
		'credit_limit' : fields.related('partner_id','credit_limit',type="float",string="Limit",readonly=True),

		'property_payment_term' : fields.related('partner_id','property_payment_term',type="many2one",relation="account.payment.term",string="Payment Term",readonly=True),
		'nik' :fields.char('Kode Sales',readonly=True),

		'partner_code':fields.related('partner_id','code',type="char",string=' ',readonly="True"),
		'location_id' : fields.many2one('stock.location','Location',readonly=True),

		'loc_code': fields.char('Code',sixe=15,readonly=True),
		'name_bayangan': fields.char('Nm', readonly=True),

		'due_date' : fields.date('Due Date',readonly=True),
		#'company_id': fields.many2one('res.company', 'Company', required=True, select=True,),
		'amount_untaxed': fields.function(_amount_alll, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
			},
			multi='sums', help="The amount without tax.", track_visibility='always'),
		'amount_tax': fields.function(_amount_alll, digits_compute=dp.get_precision('Account'), string='Taxes',
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
			},
			multi='sums', help="The tax amount."),
		'amount_total': fields.function(_amount_alll, digits_compute=dp.get_precision('Account'), string='Total',
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
			},
			multi='sums', help="The total amount."),

		# 'order_policy': fields.selection([
		# 		('prepaid','Buat invoice sebelum di kirim'),('manual', 'On Demand'),('picking','On Delivery Order'),
		# 	], 'Create Invoice', required=True, readonly=True,)# states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
			#help="""This field controls how invoice and delivery operations are synchronized."""),

			}

	_defaults ={
		'loc_code' : _get_default_lo,
		'location_id' : _get_default_werehouse,
		'user_id': lambda obj, cr, uid, context: uid,
		'order_policy':'prepaid',
		'nik':_get_nik,
		#'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'stock.inventory', context=c)
		}	

	def onchange_partner_id(self, cr, uid, ids, part, context=None):
		
		if not part:
			return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}
		
		part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
		addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
		pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
		payment_term = part.property_payment_term and part.property_payment_term.id or False
		fiscal_position = part.property_account_position and part.property_account_position.id or False
		dedicated_salesman = part.user_id and part.user_id.id or uid

		val = {
			'partner_invoice_id': addr['invoice'],
			'partner_shipping_id': addr['delivery'],
			'payment_term': payment_term,
			'fiscal_position': fiscal_position,
			'user_id': dedicated_salesman,
			'term_id' : part.cust_term_id.id,
			}
		# if pricelist:
		# 	val['pricelist_id'] = pricelist
		return {'value': val}	    

	def _get_children_grup(self, cr, uid, ids, context=None):
		#this function search for all the customer of the given category ids
		ids2 = self.pool.get('master.type.partner').search(cr, uid, [('', 'in', ids),], context=context)
		return ids2   	

	# Cek Diskon di SO
	def compute_discount(self,cr, uid, vals=None, context=None): 

		rr = self.browse(cr,uid,vals,context)
		
		if context is None:
			context = {}

		#browse order line pada form SO yang aktif
		lin = self.browse(cr,uid,vals)[0]
		prin = lin.partner_id2.partner_id.id
		#channel = lin.partner_id.type_partner_id.id
		channel = lin.partner_id.category_id[0].id

		# ch = lin.partner_id.limit_ids
		# #cari cahnel sesuai supplier di customer tsb
		# for c in ch:
		# 	cp = c.partner_id.id
		# 	if cp == prin :
		# 		channel = c.type_partner_id.id			

		line = lin.order_line

		princip = self.pool.get('master.discount')
		xx = self.pool.get('sale.order.line')

		skrg = time.strftime(DEFAULT_SERVER_DATE_FORMAT)	
				

		#####################################################################
		#mengakali penomoran SO
		#buat dari dua field, setelah di compute jadi satu field
		#
		#####################################################################
		cd = lin.loc_code
		nam = lin.name
		self.write(cr, uid, vals[0], {'name': cd+nam,'name_bayangan':nam}, context=context)


########################################################################################################################################################################

		#################################################
		#diskon all
		#################################################

		disc_obj = self.pool.get("master.discount")

		#cari di master disc yang masih berlaku (group price ada nilainya)
		disc_search1 = disc_obj.search(cr,uid,[('partner_id','=',prin),('group_price_id','=',channel),('date_from','<=',skrg),('date_to','>=',skrg),('is_active','=',True)],context=context)	
		#cari di master disc yang masih berlaku (group price kosong/false)
		disc_search2 = disc_obj.search(cr,uid,[('partner_id','=',prin),('group_price_id','=',False),('date_from','<=',skrg),('date_to','>=',skrg),('is_active','=',True)],context=context)	

		disc_search = disc_search1 + disc_search2

		#disc yang sesuai
		disc_browse = disc_obj.browse(cr,uid,disc_search) 
		
		#looping sale order line yang aktif
		gr_tot = 0.00
		qty_tot = 0.00
		gr_tot_mx = []
		for x in line :
			#one2many principal/supplier pada product
			princ = x.product_id.seller_ids
			prima = x.product_id.id
			bns = x.product_id.bonus
			princ_p = x.product_id.name
			gt = x.gross_tot
			#qty = sale.qty_big * sale.coeff + sale.qty_small		

			bg = x.qty_big
			ratio =  x.product_uos.factor_inv

			sm = x.qty_small

			uom = (sm)+ round(bg*ratio,3)
			#uom =  bg_uos + sm
			
			gro = x.price_unit * uom

			if uom == 0.00:
				uom = 1

			uos = bg + round(sm/ratio,3)
			#uos = sm_uom + bg

			gr_tot += gt
			qty_tot += uom
			gr_tot_mx.append(prima)	

			xx.write(cr,uid,x.id,{'product_uom_qty': uom,'product_uos_qty': uos},context=context)

			#jika ada product bonus harus di hapus dulu
			if bns :
				raise osv.except_osv(_('Error'), _('Product %s merupakan product bonus!')%(princ_p))

			#jika product tidak punya principal
			if not princ :
				raise osv.except_osv(_('Error'), _('Product %s tidak punya supplier!')%(princ_p))
			if princ :
				#yang di akui sbg supplier hanya array yang pertama saja
				princi = princ[0].name.id

		#looping semua disc yang ada/sesuai
		for gb in disc_browse :
			
			type_disc = gb.type
			nma = gb.name
			qty_p = gb.qty
			qty_p2 = gb.qty2
			valu = gb.value
			pre = gb.persentase
			pree = str(pre)
			is_p = gb.is_percent
			flat = gb.is_flat
			multi = gb.multi
			multi2 = gb.multi2
			is_categ = gb.is_category

			if gb.product_id.id :
				produc_id = gb.product_id.id
				p_name = gb.product_id.name
				us_id = gb.product_id.uos_id.id		
				uo_id = gb.uom_id2.id				
				cf = gb.product_id.uos_id.factor_inv
				us_qty = qty_p/cf	

			if gb.product_id2.id :
				produc_id2 = gb.product_id2.id
				p_name2 = gb.product_id2.name
				us_id2 = gb.product_id2.uos_id.id		
				uo_id2 = gb.uom_id2.id				
				cf2 = gb.product_id2.uos_id.factor_inv
				us_qty2 = qty_p2/cf2	

			kond = gb.condition_ids
			kond2 = gb.condition2_ids

			km_mtx = []#array penampung utk menghitung multiple/kelipatan
			km_mtx2 = []#array penampung utk menghitung multiple/kelipatan
			for sale2 in line :
				stot = sale2.gross_tot
				jml = sale2.qty_big * sale2.coeff + sale2.qty_small
				#yang di tambah disc hanya yang sesuai dengan di master disc saja
				ppr = sale2.product_id.id					
				#cek kodisi di master gift product
				for klp in kond:
					ppr2 = klp.product_id.id
					jm = klp.qty
					#jika di so line dan master sama
					if ppr == ppr2:
						#bilangan dibulatkan
						#qty di SO /min qty di master
						kl = int(jml / jm)
						km_mtx.append(kl)
				for klp2 in kond2:
					ppr2 = klp2.product_id.id
					jm2 = klp2.qty
					#jika di so line dan master sama
					if ppr == ppr2:
						#bilangan dibulatkan
						#qty di SO /min qty di master
						kl2 = int(jml / jm2)
						km_mtx2.append(kl2)
			km_so = sorted(km_mtx)
			if km_so == []:#pencegahan jika array kosong
				km_so = [0]
			km_so2 = sorted(km_mtx2)
			if km_so2 == []:#pencegahan jika array kosong
				km_so2 = [0]

			#import pdb;pdb.set_trace()
			if km_so != [0] and km_so2 == [0]:
				km_tot = sorted(km_so2)

			if km_so == [0] and km_so2 != [0]:
				km_tot = sorted(km_so)

			if km_so == [0] and km_so2 == [0]:
				km_tot = sorted(km_so)

			if km_so != [0] and km_so2 != [0]:
				#mencari jumlah product yang sesuai dan tdk ada duplikasi
				#z_tot = [(km_so) for x in km_so[:1] if x in km_so2 ][0] #[:1] membatasi looping cukup satu kali saja
				z_tot = set(km_so+km_so2)
				km_tot = sorted(z_tot)

			qty_pp = qty_p*km_so[0]	

			if gb.multi3:
				qty_pp2 = qty_p2*km_so2[0]	
			if not gb.multi3:
				qty_pp2 = qty_p2

			##############################list kondisi value atau qty product##########################		
			#jika menggunakan value/pot harga
			#jika tidak ada kondisi barang
			#import pdb;pdb.set_trace()
			if gb.condition_ids == [] and gb.condition2_ids ==[] :				
				if multi2:
					kond3 = gb.condition3_ids
					pr_prod	 = gb.per_product				

					for kond3_val in kond3:
						minv = kond3_val.min_value
						maxv = kond3_val.max_value
						value = kond3_val.value
						pres = kond3_val.presentase
						is_p = kond3_val.is_percent


						#cari kodisi tot yang sesuai dengan range yang mana
						if gr_tot >= minv and gr_tot <= maxv:
							# if gb.product_id.id :	
							# 	pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_p,'product_uom_qty':qty_p,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})

							if not pr_prod :				
								#looping ulang sale order line untuk tambah diskon
								for sale2 in line :
									dd = sale2.gross_tot
									jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small								
									qtty = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small	
									grr = sale2.price_unit
									gtot = sale2.gross_tot										
									
									if is_p :#percent true
										#isi discount % di tiap product (objek sale order line#)
										if type_disc == 'regular':
											xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
										elif type_disc == 'promo':
											xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
										elif type_disc == 'extra':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
										elif type_disc == 'cash':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
										elif type_disc == 'mix':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

									if not is_p :#percent false
										lt = len(km_tot)#hitung jumlah list sebagai pembagi jika pot harga
										p_price = value/lt
										#isi discount pot harga di tiap product (objek sale order line#)
										if type_disc == 'regular':
											xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
										elif type_disc == 'promo':
											xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
										elif type_disc == 'extra':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
										elif type_disc == 'cash':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
										elif type_disc == 'mix':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

							if pr_prod :				
								#looping ulang sale order line untuk tambah diskon
								for sale2 in line :
									dd = sale2.gross_tot
									jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small								
									qtty = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small	
									grr = sale2.price_unit
									gtot = sale2.gross_tot										
									#import pdb;pdb.set_trace()
									if is_p :#percent true
										#isi discount % di tiap product (objek sale order line#)
										if type_disc == 'regular':
											xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
										elif type_disc == 'promo':
											xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
										elif type_disc == 'extra':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
										elif type_disc == 'cash':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
										elif type_disc == 'mix':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

									if not is_p :#percent false
										#isi discount pot harga di tiap product (objek sale order line#)
										if type_disc == 'regular':
											xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
										elif type_disc == 'promo':
											xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
										elif type_disc == 'extra':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
										elif type_disc == 'cash':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
										elif type_disc == 'mix':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)			
				if not multi2:
					kond4 = gb.condition4_ids
					pr_prod	 = gb.per_product				

					for kond4_val in kond4:
						minq = kond4_val.min_qty
						maxq = kond4_val.max_qty
						value = kond4_val.value
						pres = kond4_val.presentase
						is_p = kond4_val.is_percent
						#import pdb;pdb.set_trace()
						#cari kodisi tot yang sesuai dengan range yang mana
						if qty_tot >= minq and qty_tot <= maxq:

							# if gb.product_id.id :	
							# 	pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_p,'product_uom_qty':qty_p,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})
		
							if not pr_prod :				
								#looping ulang sale order line untuk tambah diskon
								for sale2 in line :
									dd = sale2.gross_tot
									jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small								
									qtty = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small	
									grr = sale2.price_unit
									gtot = sale2.gross_tot										
									
									if is_p :#percent true
										#isi discount % di tiap product (objek sale order line#)
										if type_disc == 'regular':
											xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
										elif type_disc == 'promo':
											xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
										elif type_disc == 'extra':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
										elif type_disc == 'cash':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
										elif type_disc == 'mix':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

									if not is_p :#percent false
										lt = len(gr_tot_mx)#hitung jumlah list sebagai pembagi jika pot harga
										p_price = value/lt
										#isi discount pot harga di tiap product (objek sale order line#)
										if type_disc == 'regular':
											xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
										elif type_disc == 'promo':
											xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
										elif type_disc == 'extra':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
										elif type_disc == 'cash':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
										elif type_disc == 'mix':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)


							if pr_prod :				
								#looping ulang sale order line untuk tambah diskon
								for sale2 in line :
									dd = sale2.gross_tot
									jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small								
									qtty = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small	
									grr = sale2.price_unit
									gtot = sale2.gross_tot										
									#import pdb;pdb.set_trace()
									if is_p :#percent true
										#isi discount % di tiap product (objek sale order line#)
										if type_disc == 'regular':
											xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
										elif type_disc == 'promo':
											xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
										elif type_disc == 'extra':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
										elif type_disc == 'cash':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
										elif type_disc == 'mix':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
				
									if not is_p :#percent false
										#isi discount pot harga di tiap product (objek sale order line#)
										if type_disc == 'regular':
											xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
										elif type_disc == 'promo':
											xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
										elif type_disc == 'extra':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
										elif type_disc == 'cash':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
										elif type_disc == 'mix':
											xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)	

			################################List kondisi product nya#############################
			kond = gb.condition_ids
			kond5 = gb.condition5_ids
			kond2 = gb.condition2_ids
			min_qty = gb.min_qty_product
			
			#hitung jumlah kondisi barang di masternya sebagai perbandingan dg SO line
			if (kond != [] or kond5 != []) and kond2 == [] :

				
				liss_master = []
				liss = []
				p_per_tot = 0.00	

				if not is_categ :

					for kondis in kond :
						proo_id = kondis.product_id.id
						pro_qty = kondis.qty
						pro_uom = kondis.uom_id.id
						liss_master.append(proo_id)

						#import pdb;pdb.set_trace()
						#list perbandingan di SO yng sesuai dg di master		
						for lis in line :
							prod_id = lis.product_id.id
							prod_qty = round(lis.qty_big * lis.product_uos.factor_inv,3) + lis.qty_small
							prod_uom = lis.product_uom	
							#product jumlah list barang di SO harus sama dengan/lebih dari di master gift
							if prod_id == proo_id and prod_qty >= pro_qty :
								liss.append(prod_id)
								p_per = lis.price_subtotal
								p_per_tot += p_per

				if is_categ :

					for kondis in kond5 :
						#proo_id = kondis.product_id.id
						pro_categ = kondis.category_id.id
						pro_qty = kondis.qty
						pro_uom = kondis.uom_id.id
						liss_master.append(pro_categ)


						#list perbandingan di SO yng sesuai dg di master		
						for lis in line :
							prod_id = lis.product_id.id
							prod_categ = lis.product_id.categ_id.id
							prod_qty = round(lis.qty_big * lis.product_uos.factor_inv,3) + lis.qty_small
							prod_uom = lis.product_uom	
							#product jumlah list barang di SO harus sama dengan/lebih dari di master gift
							if pro_categ == prod_categ and prod_qty >= pro_qty :
								liss.append(prod_categ)
								p_per = lis.price_subtotal
								p_per_tot += p_per
		
				#agar bisa di bandingkan sorting dulu dari yang terkecil
				s_l = sorted(liss)
				s_lm = sorted(liss_master)
				#import pdb;pdb.set_trace()
				if s_l == s_lm and gb.min_qty_product <= 0.00:
					values = valu / len(s_l)
					
					#looping ulang sale order line untuk tambah diskon
					for sale2 in line :
						stot = sale2.gross_tot
						jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small
						dd = sale2.gross_tot
						qtty = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small
						grr = sale2.price_unit
						gtot = sale2.gross_tot	

						#yang di tambah disc hanya yang sesuai dengan di master disc saja
						ppr = sale2.product_id.id
						ppr_categ = sale2.product_id.categ_id.id

						#jika sesuai dg yang ada dlm matrix
						if not is_categ :
							if ppr in s_l :
								if not gb.multi:
									# if gb.product_id.id :	
									# 	pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_p,'product_uom_qty':qty_p,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})																																			

									#jika menggunakan value/pot harga
									if multi2:
										kond3 = gb.condition3_ids
										pr_prod	 = gb.per_product				

										for kond3_val in kond3:
											minv = kond3_val.min_value
											maxv = kond3_val.max_value
											value = kond3_val.value
											pres = kond3_val.presentase
											is_p = kond3_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if gr_tot >= minv and gr_tot <= maxv:	
												if not pr_prod :												
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = value/lt
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				

													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)																									

									if not multi2:
										kond4 = gb.condition4_ids
										pr_prod	 = gb.per_product				

										for kond4_val in kond4:
											minq = kond4_val.min_qty
											maxq = kond4_val.max_qty
											value = kond4_val.value
											pres = kond4_val.presentase
											is_p = kond4_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if qty_tot >= minq and qty_tot <= maxq:		
												if not pr_prod :												
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = value/lt
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				

													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)	


								if gb.multi :			

									#sudah dapat kelipatannya write di line SO line nya
									#jika menggunakan value/pot harga
									if multi2:
										kond3 = gb.condition3_ids
										pr_prod	 = gb.per_product				

										for kond3_val in kond3:
											minv = kond3_val.min_value
											maxv = kond3_val.max_value
											value = kond3_val.value
											vaval = value*km_so[0]
											pres = kond3_val.presentase
											is_p = kond3_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if gr_tot >= minv and gr_tot <= maxv:	
												if not pr_prod :													
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = (value/lt)*km_so[0]
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				

													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':vaval,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':vaval,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':vaval,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':vaval,'m_flat':flat},context=context)																									

									if not multi2:
										kond4 = gb.condition4_ids
										pr_prod	 = gb.per_product				

										for kond4_val in kond4:
											minq = kond4_val.min_qty
											maxq = kond4_val.max_qty
											value = kond4_val.value
											vaval = value*km_so[0]
											pres = kond4_val.presentase
											is_p = kond4_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if qty_tot >= minq and qty_tot <= maxq:
												disc = value		
												if not pr_prod :													
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = (value/lt)*km_so[0]
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				

													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':vaval,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':vaval,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':vaval,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':vaval,'m_flat':flat},context=context)	
						if is_categ :
							if ppr_categ in s_l :
								if not gb.multi:
									# if gb.product_id.id :	
									# 	pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_p,'product_uom_qty':qty_p,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})																																			

									#jika menggunakan value/pot harga
									if multi2:
										kond3 = gb.condition3_ids
										pr_prod	 = gb.per_product				

										for kond3_val in kond3:
											minv = kond3_val.min_value
											maxv = kond3_val.max_value
											value = kond3_val.value
											pres = kond3_val.presentase
											is_p = kond3_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if gr_tot >= minv and gr_tot <= maxv:	
												if not pr_prod :												
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = value/lt
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				

													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)																									

									if not multi2:
										kond4 = gb.condition4_ids
										pr_prod	 = gb.per_product				

										for kond4_val in kond4:
											minq = kond4_val.min_qty
											maxq = kond4_val.max_qty
											value = kond4_val.value
											pres = kond4_val.presentase
											is_p = kond4_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if qty_tot >= minq and qty_tot <= maxq:		
												if not pr_prod :												
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = value/lt
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				

													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)	


								if gb.multi :			

									#sudah dapat kelipatannya write di line SO line nya
									#jika menggunakan value/pot harga
									if multi2:
										kond3 = gb.condition3_ids
										pr_prod	 = gb.per_product				

										for kond3_val in kond3:
											minv = kond3_val.min_value
											maxv = kond3_val.max_value
											value = kond3_val.value
											vaval = value*km_so[0]
											pres = kond3_val.presentase
											is_p = kond3_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if gr_tot >= minv and gr_tot <= maxv:	
												if not pr_prod :													
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = (value/lt)*km_so[0]
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				

													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':vaval,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':vaval,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':vaval,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':vaval,'m_flat':flat},context=context)																									

									if not multi2:
										kond4 = gb.condition4_ids
										pr_prod	 = gb.per_product				

										for kond4_val in kond4:
											minq = kond4_val.min_qty
											maxq = kond4_val.max_qty
											value = kond4_val.value
											vaval = value*km_so[0]
											pres = kond4_val.presentase
											is_p = kond4_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if qty_tot >= minq and qty_tot <= maxq:
												disc = value		
												if not pr_prod :													
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = (value/lt)*km_so[0]
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				

													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':vaval,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':vaval,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':vaval,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':vaval,'m_flat':flat},context=context)	

					if gb.product_id.id :	
						pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_p,'product_uom_qty':qty_p,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})

				#import pdb;pdb.set_trace()
				if s_l != [] and s_lm != [] and gb.min_qty_product > 0.00:
					#mencari jumlah product yang sesuai antara di list PO dan di master
					#z = [(s_l) for x in s_l[:1] if x in s_lm ][0] #[:1] membatasi looping cukup satu kali saja
					y = set(s_l+s_lm)
					z = sorted(y)
					jml_z = len(z)

					if jml_z >= gb.min_qty_product:
						values = valu / len(s_l)

						#looping ulang sale order line untuk tambah diskon
						for sale2 in line :
							stot = sale2.gross_tot
							jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small
							dd = sale2.gross_tot
							qtty = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small
							grr = sale2.price_unit
							gtot = sale2.gross_tot								
							#yang di tambah disc hanya yang sesuai dengan di master disc saja
							ppr = sale2.product_id.id
							#jika sesuai dg yang ada dlm matrix
							if ppr in s_l :
								if not gb.multi:
									# if gb.product_id.id :	
									# 	pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_p,'product_uom_qty':qty_p,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})																																			

									#jika menggunakan value/pot harga
									if multi2:
										kond3 = gb.condition3_ids
										pr_prod	 = gb.per_product				

										for kond3_val in kond3:
											minv = kond3_val.min_value
											maxv = kond3_val.max_value
											value = kond3_val.value
											pres = kond3_val.presentase
											is_p = kond3_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if gr_tot >= minv and gr_tot <= maxv:	
												if not pr_prod :												
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(km_tot)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = value/lt
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)																									

									if not multi2:
										kond4 = gb.condition4_ids
										pr_prod	 = gb.per_product				

										for kond4_val in kond4:
											minq = kond4_val.min_qty
											maxq = kond4_val.max_qty
											value = kond4_val.value
											pres = kond4_val.presentase
											is_p = kond4_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if qty_tot >= minq and qty_tot <= maxq:		
												if not pr_prod :				
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(km_tot)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = value/lt
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)	


								if gb.multi :			

									#sudah dapat kelipatannya write di line SO line nya
									#jika menggunakan value/pot harga
									if multi2:
										kond3 = gb.condition3_ids
										pr_prod	 = gb.per_product				

										for kond3_val in kond3:
											minv = kond3_val.min_value
											maxv = kond3_val.max_value
											value = kond3_val.value
											vaval = value*km_so[0]
											pres = kond3_val.presentase
											is_p = kond3_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if gr_tot >= minv and gr_tot <= maxv:	
												if not pr_prod :										
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(km_tot)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = (value/lt)*km_so[0]
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':vaval,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':vaval,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':vaval,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':vaval,'m_flat':flat},context=context)																									

									if not multi2:
										kond4 = gb.condition4_ids
										pr_prod	 = gb.per_product				

										for kond4_val in kond4:
											minq = kond4_val.min_qty
											maxq = kond4_val.max_qty
											value = kond4_val.value
											vaval = value*km_so[0]
											pres = kond4_val.presentase
											is_p = kond4_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if qty_tot >= minq and qty_tot <= maxq:
												disc = value		
												if not pr_prod :													
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(km_tot)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = (value/lt)*km_so[0]
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':vaval,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':vaval,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':vaval,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':vaval,'m_flat':flat},context=context)	
						if not gb.multi:
							if gb.product_id.id :	
								pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_p,'product_uom_qty':qty_p,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})																																			

						if gb.multi:
							if gb.product_id.id :	
								pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_pp,'product_uom_qty':qty_pp,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})
						if gb.product_id2.id :	
							pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id2,'qty_small':qty_pp2,'product_uom_qty':qty_pp2,'product_uom':uo_id2,'order_id':vals[0],'name':nma+' '+p_name2,'product_uos_qty':us_qty2,'product_uos':us_id2})				

			#hitung jumlah kondisi barang di masternya sebagai perbandingan dg SO line
			# di master new product

			if kond != [] and kond2 != []:
				
				liss_master = []
				liss = []
				p_per_tot = 0.00				
				for kondis in kond :
					proo_id = kondis.product_id.id
					pro_qty = kondis.qty
					pro_uom = kondis.uom_id.id
					liss_master.append(proo_id)

					#list perbandingan di SO yng sesuai dg di master
					
					for lis in line :
						prod_id = lis.product_id.id
						prod_qty = round(lis.qty_big * lis.product_uos.factor_inv,3) + lis.qty_small
						prod_uom = lis.product_uom	
						#product jumlah list barang di SO harus sama dengan/lebih dari di master gift
						if prod_id == proo_id and prod_qty >= pro_qty :
							liss.append(prod_id)
							p_per = lis.gross_tot
							p_per_tot += p_per

				#kodisi product di condition2_ids
				liss_master2 =[]
				liss2 =[]
				p_per_tot2 = 0.00			
				for kondis2 in kond2 :
					proo_id = kondis2.product_id.id
					pro_qty = kondis2.qty
					pro_uom = kondis2.uom_id.id
					liss_master2.append(proo_id)							
					
					for lis in line :
						prod_id = lis.product_id.id
						prod_qty = round(lis.qty_big * lis.product_uos.factor_inv,3) + lis.qty_small
						prod_uom = lis.product_uom	
						#product jumlah list barang di SO harus sama dengan/lebih dari di master gift
						if prod_id == proo_id and prod_qty >= pro_qty :
							liss2.append(prod_id)
							p_per = lis.gross_tot
							p_per_tot2 += p_per
		
				#agar bisa di bandingkan sorting dulu dari yang terkecil
				s_l = sorted(liss)
				s_l2 = sorted(liss2)
				s_l3 = sorted(liss+liss2)

				s_lm = sorted(liss_master)
				s_lm2 = sorted(liss_master2)
				s_lm3 = sorted(liss_master+liss_master2)

				#import pdb;pdb.set_trace()

				if s_l3 == s_lm3 and gb.min_qty_product <= 0.00 and s_lm != []:
				
					values = valu / len(s_l)
					#looping ulang sale order line untuk tambah diskon
					for sale2 in line :
						stot = sale2.gross_tot
						jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small
						dd = sale2.gross_tot
						qtty = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small
						grr = sale2.price_unit
						gtot = sale2.gross_tot	

						#yang di tambah disc hanya yang sesuai dengan di master disc saja
						ppr = sale2.product_id.id
						#jika sesuai dg yang ada dlm matrix
						if ppr in s_lm3 :
							if not gb.multi:
								#jika menggunakan value/pot harga
								if multi2:
									kond3 = gb.condition3_ids
									pr_prod	 = gb.per_product				

									for kond3_val in kond3:
										minv = kond3_val.min_value
										maxv = kond3_val.max_value
										value = kond3_val.value
										pres = kond3_val.presentase
										is_p = kond3_val.is_percent

										#cari kodisi tot yang sesuai dengan range yang mana
										if gr_tot >= minv and gr_tot <= maxv:	
											if not pr_prod :												
													
												if is_p :#percent true
													#isi discount % di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

												if not is_p :#percent false
													lt = len(s_lm3)#hitung jumlah list sebagai pembagi jika pot harga
													p_price = value/lt
													#isi discount pot harga di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

											if pr_prod :				

												if is_p :#percent true
													#isi discount % di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

												if not is_p :#percent false
													#isi discount pot harga di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)																									

								if not multi2:
									kond4 = gb.condition4_ids
									pr_prod	 = gb.per_product				

									for kond4_val in kond4:
										minq = kond4_val.min_qty
										maxq = kond4_val.max_qty
										value = kond4_val.value
										pres = kond4_val.presentase
										is_p = kond4_val.is_percent

										#cari kodisi tot yang sesuai dengan range yang mana
										if qty_tot >= minq and qty_tot <= maxq:		
											if not pr_prod :												
													
												if is_p :#percent true
													#isi discount % di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

												if not is_p :#percent false
													lt = len(s_lm3)#hitung jumlah list sebagai pembagi jika pot harga
													p_price = value/lt
													#isi discount pot harga di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

											if pr_prod :				

												if is_p :#percent true
													#isi discount % di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
							
												if not is_p :#percent false
													#isi discount pot harga di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)	


							if gb.multi :			

								#sudah dapat kelipatannya write di line SO line nya
								#jika menggunakan value/pot harga
								if multi2:
									kond3 = gb.condition3_ids
									pr_prod	 = gb.per_product				

									for kond3_val in kond3:
										minv = kond3_val.min_value
										maxv = kond3_val.max_value
										value = kond3_val.value
										vaval = value*km_so[0]
										pres = kond3_val.presentase
										is_p = kond3_val.is_percent

										#cari kodisi tot yang sesuai dengan range yang mana
										if gr_tot >= minv and gr_tot <= maxv:	
											if not pr_prod :													
													
												if is_p :#percent true
													#isi discount % di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

												if not is_p :#percent false
													lt = len(s_lm3)#hitung jumlah list sebagai pembagi jika pot harga
													p_price = (value/lt)*km_so[0]
													#isi discount pot harga di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

											if pr_prod :				

												if is_p :#percent true
													#isi discount % di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

												if not is_p :#percent false
													#isi discount pot harga di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':vaval,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':vaval,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':vaval,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':vaval,'m_flat':flat},context=context)																									

								if not multi2:
									kond4 = gb.condition4_ids
									pr_prod	 = gb.per_product				

									for kond4_val in kond4:
										minq = kond4_val.min_qty
										maxq = kond4_val.max_qty
										value = kond4_val.value
										vaval = value*km_so[0]
										pres = kond4_val.presentase
										is_p = kond4_val.is_percent

										#cari kodisi tot yang sesuai dengan range yang mana
										if qty_tot >= minq and qty_tot <= maxq:
											disc = value		
											if not pr_prod :													
													
												if is_p :#percent true
													#isi discount % di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

												if not is_p :#percent false
													lt = len(s_lm3)#hitung jumlah list sebagai pembagi jika pot harga
													p_price = (value/lt)*km_so[0]
													#isi discount pot harga di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

											if pr_prod :				

												if is_p :#percent true
													#isi discount % di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
							
												if not is_p :#percent false
													#isi discount pot harga di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':vaval,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':vaval,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':vaval,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':vaval,'m_flat':flat},context=context)	

					if not gb.multi:
						if gb.product_id.id :	
							pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_p,'product_uom_qty':qty_p,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})																																			

					if gb.multi:
						if gb.product_id.id :	
							pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_pp,'product_uom_qty':qty_pp,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})
					if gb.product_id2.id :	
						pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id2,'qty_small':qty_pp2,'product_uom_qty':qty_pp2,'product_uom':uo_id2,'order_id':vals[0],'name':nma+' '+p_name2,'product_uos_qty':us_qty2,'product_uos':us_id2})				

				#import pdb;pdb.set_trace()
				if s_l3 == s_lm3 and gb.min_qty_product > 0.00 and s_lm != []:
				#if s_l != [] and s_lm != [] and gb.min_qty_product > 0.00:
					#mencari jumlah product yang sesuai antara di list PO dan di master
					#z = [(s_l3) for x in s_l3[:1] if x in s_lm3 ][0] #[:1] membatasi looping cukup satu kali saja
					y = set(s_l3+s_lm3)
					z = sorted(y)
					jml_z = len(z)

					if jml_z >= gb.min_qty_product:
						values = valu / len(s_l)

						#looping ulang sale order line untuk tambah diskon
						for sale2 in line :
							stot = sale2.gross_tot
							jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small
							dd = sale2.gross_tot
							qtty = round(sale2.qty_big * sale2.product_uos.factor_inv,3)
							grr = sale2.price_unit
							gtot = sale2.gross_tot								
							#yang di tambah disc hanya yang sesuai dengan di master disc saja
							ppr = sale2.product_id.id
							#jika sesuai dg yang ada dlm matrix
							if ppr in z :
								if not gb.multi:
									#jika menggunakan value/pot harga
									if multi2:
										kond3 = gb.condition3_ids
										pr_prod	 = gb.per_product				

										for kond3_val in kond3:
											minv = kond3_val.min_value
											maxv = kond3_val.max_value
											value = kond3_val.value
											pres = kond3_val.presentase
											is_p = kond3_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if gr_tot >= minv and gr_tot <= maxv:	
												if not pr_prod :												
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm3)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = value/lt
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)																									

									if not multi2:
										kond4 = gb.condition4_ids
										pr_prod	 = gb.per_product				

										for kond4_val in kond4:
											minq = kond4_val.min_qty
											maxq = kond4_val.max_qty
											value = kond4_val.value
											pres = kond4_val.presentase
											is_p = kond4_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if qty_tot >= minq and qty_tot <= maxq:		
												if not pr_prod :				
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm3)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = value/lt
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)										

								if gb.multi :			

									#sudah dapat kelipatannya write di line SO line nya
									#jika menggunakan value/pot harga
									if multi2:
										kond3 = gb.condition3_ids
										pr_prod	 = gb.per_product				

										for kond3_val in kond3:
											minv = kond3_val.min_value
											maxv = kond3_val.max_value
											value = kond3_val.value
											vaval = value*km_so[0]
											pres = kond3_val.presentase
											is_p = kond3_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if gr_tot >= minv and gr_tot <= maxv:	
												if not pr_prod :										
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm3)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = (value/lt)*km_so[0]
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':vaval,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':vaval,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':vaval,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':vaval,'m_flat':flat},context=context)																									

									if not multi2:
										kond4 = gb.condition4_ids
										pr_prod	 = gb.per_product				

										for kond4_val in kond4:
											minq = kond4_val.min_qty
											maxq = kond4_val.max_qty
											value = kond4_val.value
											vaval = value*km_so[0]
											pres = kond4_val.presentase
											is_p = kond4_val.is_percent

											#cari kodisi tot yang sesuai dengan range yang mana
											if qty_tot >= minq and qty_tot <= maxq:
												disc = value		
												if not pr_prod :													
														
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														lt = len(s_lm3)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = (value/lt)*km_so[0]
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				
													if is_p :#percent true
														#isi discount % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':vaval,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':vaval,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':vaval,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':vaval,'m_flat':flat},context=context)	
						if not gb.multi:
							if gb.product_id.id :	
								pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_p,'product_uom_qty':qty_p,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})																																			

						if gb.multi:
							if gb.product_id.id :	
								pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id,'qty_small':qty_pp,'product_uom_qty':qty_pp,'product_uom':uo_id,'order_id':vals[0],'name':nma+' '+p_name,'product_uos_qty':us_qty,'product_uos':us_id})
						if gb.product_id2.id :	
							pot_p = self.pool.get('sale.order.line').create(cr, uid,{'product_id':produc_id2,'qty_small':qty_pp2,'product_uom_qty':qty_pp2,'product_uom':uo_id2,'order_id':vals[0],'name':nma+' '+p_name2,'product_uos_qty':us_qty2,'product_uos':us_id2})				
								
		self.write(cr, uid, vals[0], {'state': 'sent'}, context=context)	

		return True	

	#reset semua discount ke nol dan hilangkan semua bonus productnya
	def reset_discount(self, cr, uid, ids, context=None):
		lin = self.browse(cr,uid,ids)[0]
		xx = self.pool.get("sale.order.line")
		unl = []
		for sett in lin.order_line:
			xx.write(cr, uid,sett.id, {
									'disc_value': 0.00,
									'discount': 0.00,
									'p_disc_value': 0.00,
									'p_disc_pre':0.00,
									'p_disc_value_x': 0.00,
									'p_disc_pre_x': 0.00,
									'p_disc_value_c': 0.00,
									'p_disc_pre_c': 0.00,
									'p_disc_value_m': 0.00,
									'p_disc_pre_m': 0.00,
									'r_flat':False,
									'p_flat':False,
									'x_flat':False,
									'c_flat':False,
									'm_flat':False,
									},context=context)
			
			if sett.product_id.bonus :
				#simpan semua bonus product
				unl.append(sett['id'])	
		#hapus semua product yang bertype bonus		
		xx.unlink(cr,uid,unl,context)
		#reset ulang nomor So agar tidak berubah
		nm = lin.name_bayangan
		#ubah state ke draft
		self.write(cr, uid, ids[0], {'state': 'draft','name':nm,}, context=context)

		return True

	def action_button_confirm(self, cr, uid, ids, context=None):
		assert len(ids) == 1, 'This option should only be used for a single id at a time.'
		wf_service = netsvc.LocalService('workflow')
		wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)

		# redisplay the record as a sales order
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
		view_id = view_ref and view_ref[1] or False,


		skrg = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
		lin = self.browse(cr,uid,ids)[0]

		####################################################################
		#Cek dulu qty product di gudang yang bersangkutan
		####################################################################
				
		loca = lin.location_id.id
		mv_obj = self.pool.get('stock.move')	
		for l in lin.order_line:
			prod = l.product_id.id
			prod_name = l.name
			qt = l.product_uom_qty	
			qt_m = l.product_uom.id
			qtu = l.product_uos_qty
			qtu_u = l.product_uos.id
			state = 'done'			
			
			# barang masuk
			cr.execute ('select sum(product_qty) from stock_move where location_id = %s and product_id = %s and state = %s',(loca,prod,state))
			oz = cr.fetchone()
			zoz = list(oz or 0)#karena dlm bentuk tuple di list kan dulu
			zozo = zoz[0]
			if zozo is None:
				zozo = 0.00   

			#barang keluar
			cr.execute ('select sum(product_qty) from stock_move where location_dest_id = %s and product_id = %s and state = %s',(loca,prod,state))
			uz = cr.fetchone()
			zuz = list(uz or 0)#karena dlm bentuk tuple di list kan dulu
			zuzu = zuz[0]
			if zuzu is None:
				zuzu = 0.00    

			qty_on_hand_in = zuzu
			qty_on_hand_out = zozo

			#onhand = barang masuk di kurangi barang keluar
			qty_on_hand = qty_on_hand_in - qty_on_hand_out


			res = qty_on_hand - qt
			if res < 0 :
				raise osv.except_osv(_('Error'), _('Qty untuk barang %s di gudang %s hanya tersedia %s %s') % (prod_name,lin.location_id.name,qty_on_hand,l.product_uom.name))
				return False	
			if res >= 0 :
				move = mv_obj.create(cr, uid,{'product_id':prod,
									'name':prod_name,
									'origin':lin.name,
									'location_id':loca,
									'location_dest_id':9,#customers
									'date_expacted':skrg,
									'product_uos':qtu_u,
									'product_uos_qty':qtu,														
									'product_qty':qt,
									'product_uom':qt_m,										
									'state':'done'										
									})			

		#cek ar di customer terkait
		ar = self.browse(cr,uid,ids)[0]
		cust_ar = ar.partner_id.credit
		lim_ar = ar.partner_id.credit_limit
		tot = ar.amount_total
		m_tot = cust_ar + tot

		obs = ar.partner_id.one_bill_sys

		#Cek jika menggunakan one bill system
		if obs :
			if cust_ar != 0.00 :
				raise osv.except_osv(_('One Bill System Warning!'),_('Jumlah Piutang Customer ini harus 0.00 !'))

		#jika jumlah piutang + SO yg di ajukan melebihi limit
		if m_tot > lim_ar:
			raise osv.except_osv(_('Warning!'),_('Jumlah Piutang Customer ini sudah melewati limit!'))

		#Set due date = date order+termin
		dt_o = lin.date_order
		trm = lin.property_payment_term.line_ids[0].days
		dd = datetime.datetime.strptime(dt_o,"%Y-%m-%d")	
		du = dd + datetime.timedelta(days=trm)	
		date_du = str(du)
		self.write(cr,uid,ids[0],{'due_date':date_du},context=context)

		return {
			'type': 'ir.actions.act_window',
			'name': _('Sales Order'),
			'res_model': 'sale.order',
			'res_id': ids[0],
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id,
			'target': 'current',
			'nodestroy': True,
		}					