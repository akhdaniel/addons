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

	#mengakali field readonly yang di beri nilai melalui event onchange
	def create(self, cr, uid, vals, context=None):
		prod_id = vals['product_id']
		prod_boj = self.pool.get('product.product').browse(cr,uid,prod_id,context=context)
		uos = prod_boj.uom_po_id.id
		uom = prod_boj.uom_id.id
		supp = prod_boj.principal_id.id
		#import pdb;pdb.set_trace()

		group =  self.pool.get('sale.order').browse(cr,uid,vals['order_id']).partner_id.category_id[0].id  		
		
		price = self.pool.get('master.harga.jual')

		#inisialisasi tanggal aktif(sekarang)
		skrg = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

		#cari  di tabel harga jual yang masih berlaku
		u_price = price.search(cr,uid,[('product_id','=',prod_id),('type_partner_id','=',group),('date_from','<=',skrg),('date_to','>=',skrg)])
		
		u_prc = u_price[0]
		list_prc = price.browse(cr,uid,u_prc)
		small_price = list_prc.small_price 

		uos_supp_price = {'product_uos':uos,'supplier_id':supp,'product_uom_qty':uom,'price_unit':small_price}
		vals = dict(vals.items()+uos_supp_price.items()) 
		return super(sale_order_line, self).create(cr, uid, vals, context=context)

	def _get_reg_disc_tot(self,cr,uid,ids,field,args,context=None):
		result = {}
		
		for res in self.browse(cr,uid,ids):
			r_disc= 0.00
			if res.disc_value != 0.00:
				r_disc = res.disc_value
			elif res.discount1 != 0.00:
				if res.r_flat:
					r_disc = res.gross_tot * res.discount1/100	
				elif not res.r_flat:
					r_disc = res.gross_tot * res.discount1/100		
			else:
				r_disc= 0.00
			result[res.id] = r_disc
			self.write(cr,uid,res.id,{'r_func':r_disc},context=context)
		return result

	def _get_pro_disc_tot(self,cr,uid,ids,field,args,context=None):
		result = {}
		for res in self.browse(cr,uid,ids):
			p_disc= 0.00
			if res.p_disc_value != 0.00:
				p_disc = res.p_disc_value
			elif res.p_disc_pre != 0.00:
				if res.p_flat:
					p_disc = res.gross_tot * res.p_disc_pre/100	
				elif not res.r_flat:
					p_disc = (res.gross_tot-res.r_func )* res.p_disc_pre/100			
			else:
				p_disc= 0.00
			result[res.id] = p_disc
			self.write(cr,uid,res.id,{'p_func':p_disc},context=context)
		return result

	def _get_ext_disc_tot(self,cr,uid,ids,field,args,context=None):
		result = {}
		for res in self.browse(cr,uid,ids):
			x_disc= 0.00
			if res.p_disc_value_x != 0.00:
				x_disc = res.p_disc_value_x
			elif res.p_disc_pre_x != 0.00:
				if res.x_flat:
					x_disc = res.gross_tot * res.p_disc_pre_x/100	
				elif not res.x_flat:
					x_disc = (res.gross_tot-res.r_func-res.p_func )* res.p_disc_pre_x/100			
			else:
				x_disc= 0.00
			result[res.id] = x_disc
			self.write(cr,uid,res.id,{'x_func':x_disc},context=context)
		return result

	def _get_cas_disc_tot(self,cr,uid,ids,field,args,context=None):
		result = {}
		for res in self.browse(cr,uid,ids):
			c_disc= 0.00
			if res.p_disc_value_c != 0.00:
				c_disc = res.p_disc_value_c
			elif res.p_disc_pre_c != 0.00:
				if res.c_flat:
					c_disc = res.gross_tot * res.p_disc_pre_c/100	
				elif not res.c_flat:
					c_disc = (res.gross_tot-res.r_func-res.p_func-res.x_func )* res.p_disc_pre_c/100			
			else:
				c_disc= 0.00
			result[res.id] = c_disc
			self.write(cr,uid,res.id,{'c_func':c_disc},context=context)
		return result

	def _get_mix_disc_tot(self,cr,uid,ids,field,args,context=None):
		result = {}
		for res in self.browse(cr,uid,ids):
			m_disc= 0.00
			if res.p_disc_value_m != 0.00:
				m_disc = res.p_disc_value_m
			elif res.p_disc_pre_m != 0.00:
				if res.m_flat:
					m_disc = res.gross_tot * res.p_disc_pre_m/100	
				elif not res.m_flat:
					m_disc = (res.gross_tot-res.r_func-res.p_func-res.c_func )* res.p_disc_pre_m/100			
			else:
				m_disc= 0.00
			result[res.id] = m_disc
			self.write(cr,uid,res.id,{'m_func':m_disc},context=context)
		return result		

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

			ratio =  line.product_id.uom_po_id.factor_inv#line.product_uos.factor_inv

			sm = line.qty_small
			
			uom = (sm)+ round(bg*ratio,3)
			#uom =  bg_uos + sm
			
			gro = line.price_unit * uom

			if uom == 0.00:
				uom = 1

			uos = sm_uom + bg			
			#harus di bagi uom qty dulu
			discv = line.r_calc /uom
			discv2 = line.p_calc/uom
			discv3 = line.x_calc/uom
			discv4 = line.c_calc/uom
			discv5 = line.m_calc/uom
			#import pdb;pdb.set_trace()				

			#reg discount
			pri = line.price_unit-discv #* (1 - (line.discount11 or 0.0) / 100.0))


			#promo discount
			pric = pri - discv2 #* (1 - (line.p_disc_pre or 0.0) / 100.0))
		

			#xtra discount
			pric2 = pric - discv3


			# #cash discount
			pric3 = pric2 - discv4


			# #mix discount
			price = pric3 - discv5

			gross = self.write(cr, uid,line.id, {'gross_tot': gro},context=context)	
			#import pdb;pdb.set_trace()				
			taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, uom, line.product_id, line.order_id.partner_id)
			cur = line.order_id.pricelist_id.currency_id
			res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
			self.write(cr,uid,line.id,{'tes':taxes['total']},context=context)
		return res


	_columns = {
		'supplier_id' : fields.many2one('res.partner','Principal',domain=[('supplier','=',True)]),
		'volume' : fields.float('Volume (m3)'),
		'volume2' : fields.related('product_id','volume',string ='Vlm'),
		'coeff' : fields.float('Ratio Uos'),
		'uos2' :fields.char('Satuan Besar'),
		'tax_id': fields.many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes'),		
		'gross_tot' : fields.float('Gross Total'),
		'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
		'partner_id' : fields.many2one('res.partner','Principle'),# field bayangan principle sesuai dg sale order
		#'product_id': fields.many2one('product.product', 'Product', domain="[('seller_ids[0].name.id','=',order_id)]", change_default=True),
		#regular disc	
		'r_func' : fields.float(string="Reg.Price"),
		'disc_value' : fields.float('R.Disc (Price)'),
		'discount1': fields.float('R.Disc (%)', digits_compute= dp.get_precision('discount')),	
		'r_flat' : fields.boolean('R.Flat'),
		'r_calc' : fields.function(_get_reg_disc_tot,type="float",string='R.Disc (Price)'),
		#promo discount1
		'p_func' : fields.float(string="Pro.Price"),
		'p_disc_value' : fields.float('P.Disc (Price)'),
		'p_disc_pre' : fields.float('P.Disc (%)',digits_compute= dp.get_precision('discount')),
		'p_flat' : fields.boolean('P.Flat'),
		'p_calc': fields.function(_get_pro_disc_tot,type="float",string='P.Disc (Price)'),
		#extra discount1
		'x_func' : fields.float(string="Ext.Price"),
		'p_disc_value_x' : fields.float('X.Disc (Price)'),
		'p_disc_pre_x' : fields.float('X.Disc (%)',digits_compute= dp.get_precision('discount')),
		'x_flat' : fields.boolean('X.Flat'),
		'x_calc': fields.function(_get_ext_disc_tot,type="float",string='X.Disc (Price)'),
		#cash discount1
		'c_func' : fields.float(string="Csh.Price"),
		'p_disc_value_c' : fields.float('C.Disc (Price)'),
		'p_disc_pre_c' : fields.float('C.Disc (%)',digits_compute= dp.get_precision('discount')),
		'c_flat' : fields.boolean('C.Flat'),
		'c_calc': fields.function(_get_cas_disc_tot,type="float",string='C.Disc (Price)'),
		#mix  discount1
		'm_func' : fields.float(string="Mx.Price"),
		'p_disc_value_m' : fields.float('M.Disc (Price)'),
		'p_disc_pre_m' : fields.float('M.Disc (%)',digits_compute= dp.get_precision('discount')),
		'm_flat' : fields.boolean('M.Flat'),
		'm_calc': fields.function(_get_mix_disc_tot,type="float",string='M.Disc (Price)'),	

		'qty_small':fields.float('Small Qty',digits_compute=dp.get_precision('Product Unit of Measure')),
		'qty_big':fields.float('Big Qty',digits_compute= dp.get_precision('Product UoS'),required=True),	

		'qty_awal' :fields.float('Qty Awal'),	

		'tes': fields.float('Tes'),	
		#'product_id': fields.many2one('product.product', 'Product', domain="[('sale_ok', '=', True),()]", change_default=True),		

	}

	_defaults = {
		'qty_awal': 0.0,
		}	

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
				'price_unit2' : pu2, 
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
				result['supplier_id'] = product_obj.principal_id.id or False
			else:
				result['product_uos'] = False
				result['product_uos_qty'] = qty
				result['supplier_id'] = product_obj.principal_id.id or False
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
			result['supplier_id'] = product_obj.principal_id.id or False
		elif uom: # whether uos is set or not
			default_uom = product_obj.uom_id and product_obj.uom_id.id
			q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
			if product_obj.uos_id:
				result['product_uos'] = product_obj.uos_id.id
				result['product_uos_qty'] = qty * product_obj.uos_coeff
				result['supplier_id'] = product_obj.principal_id.id or False
			else:
				result['product_uos'] = False
				result['product_uos_qty'] = qty
			result['th_weight'] = q * product_obj.weight        # Round the quantity up
			result['volume'] = q * product_obj.volume        # Round the quantity up
			result['coeff']= product_obj.uos_coeff
			result['uos2']= product_obj.uos_id.name
			result['supplier_id'] = product_obj.principal_id.id or False

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
		group = cust.category_id[0].id

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

	def _amount_line_tax(self, cr, uid, line, context=None):
		val = 0.0
		for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
			val += c.get('amount', 0.0)
		return val

	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		cur_obj = self.pool.get('res.currency')
		res = {}
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'amount_untaxed': 0.0,
				'amount_tax': 0.0,
				'amount_total': 0.0,
			}
			val = val1 = 0.0
			cur = order.pricelist_id.currency_id
			#import pdb;pdb.set_trace()
			for line in order.order_line:
				val1 += line.price_subtotal
				val += self._amount_line_tax(cr, uid, line, context=context)

			res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
			res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
			res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
		return res

	def amount(self, cr, uid, ids, arg, context=None):
		cur_obj = self.pool.get('res.currency')
		res = {}
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

		sol = self.pool.get('sale.order.line')

		if vivals :
			raise osv.except_osv(_('Error!'), _('Customer ini sudah ditandai sebagai customer yang bermasalah!'))
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
		
		for x in vals['order_line']:
			x1 = x[2]['qty_small']
			x2 = x[2]['qty_big']

			#uos ambil langsung di master product
			#id_uos = x[2]['product_uos']

			prod_id = x[2]['product_id']
			measure = self.pool.get('product.product').browse(cr,uid,prod_id,context=context)
			id_uos = measure.uom_po_id.id
			id_uom = measure.uom_id.id

			uos_fct = measure.uom_po_id.factor_inv

			qty_awal = x1+(x2*uos_fct)

			x[2]['qty_awal'] = qty_awal
 
		return super(sale_order, self).create(cr, uid, vals, context=context)

	#default shop sesuai cabang di master employee log in
	def _get_default_shop2(self, cr, uid, context=None):
		
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

	#default company per user
	def _default_company_user(self, cr, uid, context=None):
		user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		return user.company_id.partner_id.id

	#tambahkan gudang di invoice sesuai gudang di PO
	def _prepare_invoice(self, cr, uid, order, lines, context=None):
		#import pdb;pdb.set_trace()
		res=super(sale_order,self)._prepare_invoice(cr, uid, order, lines, context=context)
		# if order.warehouse_id :
		res['location_id']=order.location_id.id
		res['date_so']=order.date_order
		res['nik']=order.nik
		res['volume']=order.volume_tot
		res['weight']=order.tonase_tot
		#res2={'partner_id2':order.partner_id2.partner_id.id}
		result = dict(res.items())#+res2.items()) 
		return result
	

	#hitung kubikasi dan tonase per SO
	def _compute_volume(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		order = self.browse(cr, uid, ids, context=context)[0]
		res[order.id] = {
			'volume_tot': 0.0,
				}
		val =  0.0
		brt = 0.00
		for line in order.order_line:
			t_line = line.volume * line.product_uom_qty

			#tonase
			ton = line.product_id.weight * line.product_uom_qty

			val += t_line
			brt += ton

		#self.write(cr,uid,ids[0],{'tonase_tot':brt},context=context)

		res[order.id]['volume_tot'] = val
		res[order.id]['tonase_tot'] = brt
		return res

	def _get_order(self, cr, uid, ids, context=None):
		result = {}
		#import pdb;pdb.set_trace()
		for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
			result[line.order_id.id] = True
		return result.keys()


	_columns = {
		'partner_id2' : fields.many2one('limit.customer','Principal',domain="[('partner_id2','=',partner_id)]",required=False),
		'discount12' : fields.float('Promo',readonly=True),	
		'volume_tot' : fields.function(_compute_volume,string="Total Volume", type="float",multi="sums"),
		'tonase_tot' : fields.function(_compute_volume,string="Total Weight", type="float",multi="sums"),

		'date_order': fields.date('Date', required=True, readonly=True, select=True),
		'warehouse_id' : fields.many2one('stock.warehouse','Location',readonly=True),

		'credit' : fields.related('partner_id','credit',type="float",string="Total AR",readonly=True),
		'credit_limit' : fields.related('partner_id','credit_limit',type="float",string="Limit",readonly=True),

		'property_payment_term' : fields.related('partner_id','property_payment_term',type="many2one",relation="account.payment.term",string="Payment Term",readonly=True),
		'nik' :fields.char('Kode Sales',readonly=True),

		'partner_code':fields.related('partner_id','code',type="char",string=' ',readonly="True"),
		#'location_id' : fields.many2one('stock.location','Location',readonly=True),
		'location_id' : fields.many2one('sale.shop','Location',readonly=True),

		'loc_code': fields.char('Code',sixe=15,readonly=True),
		'name_bayangan': fields.char('Nm', readonly=True),

		'due_date' : fields.date('Due Date',readonly=True),
		#'company_id': fields.many2one('res.company', 'Company', required=True, select=True,),
		'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'sale.order.line': (_get_order, ['price_unit', 'tax_id','product_uom_qty'], 10),
			},
			multi='sums', help="The amount without tax.", track_visibility='always'),
		'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'sale.order.line': (_get_order, ['price_unit', 'tax_id','product_uom_qty'], 10),
			},
			multi='sums', help="The tax amount."),
		'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'sale.order.line': (_get_order, ['price_unit', 'tax_id','product_uom_qty'], 10),
			},
			multi='sums', help="The total amount."),
		'x_field':fields.boolean('x'),
		'street':fields.related('partner_id','street',type='char',string='Alamat',readonly=True),
		'street_onchange':fields.char('Alamat'),
		'top_onchange':fields.many2one('account.payment.term',string='ToP'),
			}

		

	_defaults ={
		'loc_code' : _get_default_lo,
		'location_id' : _get_default_shop2,
		'user_id': lambda obj, cr, uid, context: uid,
		'order_policy':'prepaid',
		'nik':_get_nik,

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
			'street_onchange' : part.street,
			'top_onchange': part.property_payment_term.id,
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

		#rombak######################################
		#prin = lin.partner_id2.partner_id.id
		##############################################
		channel = lin.partner_id.category_id[0].id
		
		loc = lin.location_id.id
		# ch = lin.partner_id.limit_ids
		# #cari cahnel sesuai supplier di customer tsb
		# for c in ch:
		# 	cp = c.partner_id.id
		# 	if cp == prin :
		# 		channel = c.type_partner_id.id			

		line = lin.order_line
		xx = self.pool.get('sale.order.line')

		skrg = time.strftime(DEFAULT_SERVER_DATE_FORMAT)	
				

		#####################################################################
		#mengakali penomoran SO
		#buat dari dua field, setelah di compute jadi satu field
		#
		#####################################################################
		cd = lin.loc_code
		nam = lin.name
		
		if not lin.x_field :
			self.write(cr, uid, vals[0], {'name_bayangan':nam,'name': cd+nam,'x_field':True}, context=context)


		##########################################################################################################

		#################################################
		#diskon all
		#################################################

	
		#looping sale order line yang aktif
		total_supp = []

		for x in line :
			#supllier perline so
			supp_line = x.supplier_id.id
			princ = x.product_id.seller_ids
			prima = x.product_id.id
			princ_p = x.product_id.name			
			if supp_line not in total_supp :
				#tampung semua supplier yg ada di so line, terus gruping per supplier id
				total_supp.append(supp_line)

			princ_p = x.product_id.name
			bns = x.product_id.bonus
			#jika ada product bonus harus di hapus dulu
			if bns :
				raise osv.except_osv(_('Error'), _('Product %s merupakan product bonus!')%(princ_p))

			#jika product tidak punya principal
			if not princ :
				raise osv.except_osv(_('Error'), _('Product %s tidak punya supplier!')%(princ_p))
			if princ :
				#yang di akui sbg supplier hanya array yang pertama saja
				princi = princ[0].name.id

		#import pdb;pdb.set_trace()

		disc_obj = self.pool.get("master.discount")

		for discount_per_supp in total_supp:
			prin = discount_per_supp

			#cari di master disc yang masih berlaku (group price ada nilainya)
			disc_search1 = disc_obj.search(cr,uid,[('partner_id','=',prin),
													('date_from','<=',skrg),
													('date_to','>=',skrg),
													('is_active','=',True),
													('group_price_ids','=',channel),
													('location_ids','in',loc)],
													context=context)
			# #cari di master disc yang masih berlaku (group price kosong/false)
			disc_search2 = disc_obj.search(cr,uid,[('partner_id','=',prin),
													('date_from','<=',skrg),
													('date_to','>=',skrg),
													('is_active','=',True),
													('group_price_ids','=',False),
													('location_ids','=',False)],		
																							
													context=context)	
			disc_search3 = disc_obj.search(cr,uid,[('partner_id','=',prin),
													('date_from','<=',skrg),
													('date_to','>=',skrg),
													('is_active','=',True),
													('group_price_ids','=',channel),
													('location_ids','=',False)],
													context=context)

			disc_search4 = disc_obj.search(cr,uid,[('partner_id','=',prin),
													('date_from','<=',skrg),
													('date_to','>=',skrg),
													('is_active','=',True),
													('group_price_ids','=',False),
													('location_ids','in',loc)],												
													context=context)
			disc_search = set(disc_search1 + disc_search2 + disc_search3 + disc_search4)

			#looping sale order line yang aktif dan gruping persupplier
			gr_tot = 0.00
			qty_tot = 0.00
			gr_tot_mx = []

			for x in line :

				if prin == x.supplier_id.id:
					#one2many principal/supplier pada product
					prima = x.product_id.id
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

			#disc yang sesuai
			disc_browse = disc_obj.browse(cr,uid,sorted(disc_search)) 		
			#looping semua disc yang ada/sesuai
			for gb in disc_browse :
				#import pdb;pdb.set_trace()
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
					# uo_id = gb.uom_id2.id		
					uo_id = gb.product_id.uom_id.id			
					cf = gb.product_id.uos_id.factor_inv
					us_qty = qty_p/cf	

				if gb.product_id2.id :
					produc_id2 = gb.product_id2.id
					p_name2 = gb.product_id2.name
					us_id2 = gb.product_id2.uos_id.id		
					#uo_id2 = gb.uom_id2.id	
					uo_id2 = gb.product_id2.uom_id.id				
					cf2 = gb.product_id2.uos_id.factor_inv
					us_qty2 = qty_p2/cf2	

				kond = gb.condition_ids
				kond2 = gb.condition2_ids
				kond5 = gb.condition5_ids

				km_mtx = []#array penampung utk menghitung multiple/kelipatan
				km_mtx2 = []#array penampung utk menghitung multiple/kelipatan
				for sale2 in line :
					if prin == sale2.supplier_id.id:
						stot = sale2.gross_tot
						#jml = sale2.qty_big * sale2.coeff + sale2.qty_small
						jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small
						#yang di tambah disc hanya yang sesuai dengan di master disc saja
						ppr = sale2.product_id.id	
						ppr_categ = sale2.product_id.categ_id.id				
						#cek kodisi di master gift product
						if not gb.is_category:
							for klp in kond:
								ppr2 = klp.product_id.id
								jm = klp.qty
								#jika di so line dan master sama
								if ppr == ppr2:
									if jm == 0:
										kl = 0
									else :
										#bilangan dibulatkan
										#qty di SO /min qty di master
										kl = int(jml / jm)
									km_mtx.append(kl)
						if gb.is_category:
							for klp in kond5:
								ppr2 = klp.category_id.id
								#jm = klp.qty
								jm = 1
								#jika di so line dan master sama
								if ppr_categ == ppr2 and jml >= jm:
									#bilangan dibulatkan
									#qty di SO /min qty di master
									kl = int(jml / jm)
									km_mtx.append(kl)							
						for klp2 in kond2:
							ppr2 = klp2.product_id.id
							jm2 = klp2.qty
							#jika di so line dan master sama
							if ppr == ppr2:
								if jm2 == 0:
									kl2 = 0
								else :
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
				if gb.condition_ids == [] and gb.condition5_ids== [] and gb.condition2_ids ==[] :	
					#import pdb;pdb.set_trace()	
					for sale2 in line :		
						if multi2 and prin == sale2.supplier_id.id:
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
											if prin == sale2.supplier_id.id:
												dd = sale2.gross_tot
												jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small								
												qtty = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small	
												grr = sale2.price_unit
												gtot = sale2.gross_tot										
												
												#percent true
												if is_p:
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

												if not is_p:#percent false
													lt = len(km_tot)#hitung jumlah list sebagai pembagi jika pot harga
													p_price = value/lt
													#isi discount1 pot harga di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
											if prin == sale2.supplier_id.id:
												dd = sale2.gross_tot
												jml = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small								
												qtty = round(sale2.qty_big * sale2.product_uos.factor_inv,3) + sale2.qty_small	
												grr = sale2.price_unit
												gtot = sale2.gross_tot										
												#import pdb;pdb.set_trace()
												if is_p:#percent true
													#isi discount1 % di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

												if not is_p:#percent false
													#isi discount1 pot harga di tiap product (objek sale order line#)
													if type_disc == 'regular':
														xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
													elif type_disc == 'promo':
														xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
													elif type_disc == 'extra':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
													elif type_disc == 'cash':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
													elif type_disc == 'mix':
														xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)			
						
						if not multi2 and prin == sale2.supplier_id.id:
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
											
											if is_p and prin == sale2.supplier_id.id:#percent true
												#isi discount1 % di tiap product (objek sale order line#)
												if type_disc == 'regular':
													xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
												elif type_disc == 'promo':
													xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
												elif type_disc == 'extra':
													xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
												elif type_disc == 'cash':
													xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
												elif type_disc == 'mix':
													xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

											if not is_p and prin == sale2.supplier_id.id:#percent false
												lt = len(gr_tot_mx)#hitung jumlah list sebagai pembagi jika pot harga
												p_price = value/lt
												#isi discount1 pot harga di tiap product (objek sale order line#)
												if type_disc == 'regular':
													xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
											if is_p  and prin == sale2.supplier_id.id:#percent true
												#isi discount1 % di tiap product (objek sale order line#)
												if type_disc == 'regular':
													xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
												elif type_disc == 'promo':
													xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
												elif type_disc == 'extra':
													xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
												elif type_disc == 'cash':
													xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
												elif type_disc == 'mix':
													xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
						
											if not is_p and prin == sale2.supplier_id.id:#percent false
												#isi discount1 pot harga di tiap product (objek sale order line#)
												if type_disc == 'regular':
													xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
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

					if not is_categ :
						p_per_tot = 0.00
						liss = []
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
								if prod_id == proo_id and prod_qty >= pro_qty:
									if prin == lis.supplier_id.id:
										liss.append(prod_id)
										p_per = lis.price_subtotal
										p_per_tot += p_per

					if is_categ :
						p_per_tot = 0.00
						liss = []
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
									if prin == lis.supplier_id.id:
										liss.append(prod_categ)
										p_per = lis.price_subtotal
										p_per_tot += p_per
			
					#agar bisa di bandingkan sorting dulu dari yang terkecil
					s_l = sorted(set(liss))
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
							ppr_categ = sale2.product_id.categ_id.id
							#yang di tambah disc hanya yang sesuai dengan di master disc saja
							if not is_categ:
								ppr = sale2.product_id.id
							if is_categ:
								ppr = sale2.product_id.categ_id.id

							#jika sesuai dg yang ada dlm matrix
							if not is_categ :
								if ppr in s_l :
									if not gb.multi and prin == sale2.supplier_id.id:
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
												if p_per_tot >= minv and p_per_tot <= maxv:	
													if not pr_prod :												
															
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = value/lt
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod :				

														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
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
															
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = value/lt
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod :				

														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
									
														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)	


									if gb.multi and prin == sale2.supplier_id.id:			

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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = (value/lt)*km_so[0]
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod :				

														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
															
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = (value/lt)*km_so[0]
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod :				

														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
									
														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
									if not gb.multi and prin == sale2.supplier_id.id:
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
															
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = value/lt
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod :				

														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
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
															
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = value/lt
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod :				

														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
									
														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)	


									if gb.multi and prin == sale2.supplier_id.id:			

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
															
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = (value/lt)*km_so[0]
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod :				

														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
															
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(s_lm)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = (value/lt)*km_so[0]
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod:				

														if is_p :#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
									
														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
					if s_l != [] and s_lm != [] and gb.min_qty_product > 0.00:
						#mencari jumlah product yang sesuai antara di list PO dan di master
						#z = [(s_l) for x in s_l[:1] if x in s_lm ][0] #[:1] membatasi looping cukup satu kali saja
						y = set(s_l+s_lm)
						z = sorted(y)
						jml_z = len(z)

						# if jml_z >= gb.min_qty_product:
						if len(liss) >= gb.min_qty_product:
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
								if not is_categ:
									ppr = sale2.product_id.id
								if is_categ:
									ppr = sale2.product_id.categ_id.id
								#jika sesuai dg yang ada dlm matrix
								if ppr in s_l :
									if not gb.multi and prin == sale2.supplier_id.id:
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
															
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(km_tot)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = value/lt
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod :				
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
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
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(km_tot)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = value/lt
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod :				
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
									
														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)	


									if gb.multi and prin == sale2.supplier_id.id:			

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
															
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(km_tot)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = (value/lt)*km_so[0]
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

													if pr_prod :				
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
															
														if is_p:#percent true
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p:#percent false
															lt = len(km_tot)#hitung jumlah list sebagai pembagi jika pot harga
															p_price = (value/lt)*km_so[0]
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
									
														if not is_p:#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
				#import pdb;pdb.set_trace()
				if is_categ == False and kond != [] and kond2 != []:
					
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
								if prin == lis.supplier_id.id:
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
								if prin == lis.supplier_id.id:
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
							if not is_categ:
								ppr = sale2.product_id.id
							if is_categ:
								ppr = sale2.product_id.categ_id.id
							#jika sesuai dg yang ada dlm matrix
							if ppr in s_lm3 :
								if not gb.multi:
									#jika menggunakan value/pot harga
									if multi2 and prin == sale2.supplier_id.id:
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
														
													if is_p:#percent true
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p:#percent false
														lt = len(s_lm3)#hitung jumlah list sebagai pembagi jika pot harga
														p_price = value/lt
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':p_price,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':p_price,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':p_price,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':p_price,'m_flat':flat},context=context)

												if pr_prod :				

													if is_p:#percent true
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p:#percent false
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)																									

									if not multi2 and prin == sale2.supplier_id.id:
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)	


								if gb.multi and prin == sale2.supplier_id.id:			

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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
								if not is_categ:
									ppr = sale2.product_id.id
								if is_categ:
									ppr = sale2.product_id.categ_id.id
								#jika sesuai dg yang ada dlm matrix
								if ppr in z :
									if not gb.multi and prin == sale2.supplier_id.id:
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p :#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
									
														if not is_p :#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)										

									if gb.multi and prin == sale2.supplier_id.id:			

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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p :#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
									
														if not is_p :#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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


				if is_categ == True and kond5 != [] and kond2 != []:
					
					liss_master = []
					liss = []
					p_per_tot = 0.00				
					for kondis in kond5 :
						proo_id = kondis.product_id.id
						pro_categ = kondis.category_id.id
						pro_qty = kondis.qty
						pro_uom = kondis.uom_id.id
						liss_master.append(proo_id)

						#list perbandingan di SO yng sesuai dg di master
						
						for lis in line :
							prod_id = lis.product_id.id
							prod_categ = kondis.product_id.category_id.id
							prod_qty = round(lis.qty_big * lis.product_uos.factor_inv,3) + lis.qty_small
							prod_uom = lis.product_uom	
							#product jumlah list barang di SO harus sama dengan/lebih dari di master gift
							if prod_id == proo_id and prod_qty >= pro_qty :
								if prin == sale2.supplier_id.id:
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
								if prin == sale2.supplier_id.id:
									liss2.append(prod_id)
									p_per = lis.gross_tot
									p_per_tot2 += p_per
			
					#agar bisa di bandingkan sorting dulu dari yang terkecil
					s_l = sorted(liss)
					s_l2 = sorted(liss2)
					s_l3 = sorted(set(liss+liss2))

					s_lm = sorted(liss_master)
					s_lm2 = sorted(liss_master2)
					s_lm3 = sorted(set(liss_master+liss_master2))

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
							if not is_categ:
								ppr = sale2.product_id.id
							if is_categ:
								ppr = sale2.product_id.categ_id.id
							#jika sesuai dg yang ada dlm matrix
							if ppr in s_lm3 :
								if not gb.multi and prin == sale2.supplier_id.id:
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)	


								if gb.multi and prin == sale2.supplier_id.id:			

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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

													if not is_p :#percent false
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
														#isi discount1 % di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
														elif type_disc == 'promo':
															xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
														elif type_disc == 'extra':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
														elif type_disc == 'cash':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
														elif type_disc == 'mix':
															xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
								
													if not is_p :#percent false
														#isi discount1 pot harga di tiap product (objek sale order line#)
														if type_disc == 'regular':
															xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
					if s_l3 == s_lm3 and s_lm != [] and gb.min_qty_product > 0.00 :
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
								if not is_categ:
									ppr = sale2.product_id.id
								if is_categ:
									ppr = sale2.product_id.categ_id.id
								#jika sesuai dg yang ada dlm matrix
								if ppr in z :
									if not gb.multi and prin == sale2.supplier_id.id:
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p :#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
									
														if not is_p :#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':value,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': 0.00,'p_disc_value':value,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': 0.00,'p_disc_value_x':value,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': 0.00,'p_disc_value_c':value,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': 0.00,'p_disc_value_m':value,'m_flat':flat},context=context)										

									if gb.multi and prin == sale2.supplier_id.id:			

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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)		

														if not is_p :#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
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
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':p_price,'r_flat':flat},context=context)
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
															#isi discount1 % di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': pres,'disc_value':0.00,'r_flat':flat},context=context)
															elif type_disc == 'promo':
																xx.write(cr, uid,sale2.id, {'p_disc_pre': pres,'p_disc_value':0.00,'p_flat':flat},context=context)
															elif type_disc == 'extra':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_x': pres,'p_disc_value_x':0.00,'x_flat':flat},context=context)
															elif type_disc == 'cash':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_c': pres,'p_disc_value_c':0.00,'c_flat':flat},context=context)
															elif type_disc == 'mix':
																xx.write(cr, uid,sale2.id, {'p_disc_pre_m': pres,'p_disc_value_m':0.00,'m_flat':flat},context=context)	
									
														if not is_p :#percent false
															#isi discount1 pot harga di tiap product (objek sale order line#)
															if type_disc == 'regular':
																xx.write(cr, uid,sale2.id, {'discount1': 0.00,'disc_value':vaval,'r_flat':flat},context=context)
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

	def recalculate(self,cr, uid, vals=None, context=None):
		order = self.browse(cr,uid,vals)[0]
		line = order.order_line
		for ln in line:
			#import pdb;pdb.set_trace()
			gross = ln.disc_value
			self.pool.get('sale.order.line').write(cr,uid,ln.id,{'price_unit':ln.price_unit,},context=context)

		return True

	#reset semua discount ke nol dan hilangkan semua bonus productnya
	def reset_discount(self, cr, uid, ids, context=None):
		lin = self.browse(cr,uid,ids)[0]
		xx = self.pool.get("sale.order.line")
		unl = []
		for sett in lin.order_line:
			xx.write(cr, uid,sett.id, {
									'disc_value': 0.00,
									'discount1': 0.00,
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
		self.write(cr, uid, ids[0], {'state': 'draft'}, context=context)

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
		sol_obj= self.pool.get('sale.order.line')

		####################################################################
		#Cek dulu qty product di gudang yang bersangkutan
		####################################################################
				
		loca = lin.location_id.warehouse_id.lot_stock_id.id
		mv_obj = self.pool.get('stock.move')
		sub_tot = 0.00	
		for l in lin.order_line:
			prod = l.product_id.id
			prod_name = l.name
			qt = l.product_uom_qty	
			qt_m = l.product_uom.id
			qtu = l.product_uos_qty
			qtu_u = l.product_uos.id
			state = 'done'	
			state2 = 'waiting'
			state3 = 'confirmed'	
			state4 = 'assigned'	
			sub_t = l.price_subtotal
			sub_tot += sub_t

			# barang masuk
			cr.execute ('SELECT sum(product_qty) FROM stock_move '\
				'WHERE location_id = %s '\
				'AND product_id = %s '\
				'AND (state = %s OR state = %s OR state = %s OR state = %s)',(loca,prod,state,state2,state3,state4))
			oz = cr.fetchone()
			zoz = list(oz or 0)#karena dlm bentuk tuple di list kan dulu
			zozo = zoz[0]
			if zozo is None:
				zozo = 0.00   

			#barang keluar
			cr.execute ('SELECT sum(product_qty) FROM stock_move '\
				'WHERE location_dest_id = %s '\
				'AND product_id = %s '\
				'AND (state = %s or state = %s OR state = %s or state = %s)',(loca,prod,state,state2,state3,state4))
			uz = cr.fetchone()
			zuz = list(uz or 0)#karena dlm bentuk tuple di list kan dulu
			zuzu = zuz[0]
			if zuzu is None:
				zuzu = 0.00    

			qty_future_in = zuzu
			qty_future_out = zozo

			#onfuture = barang masuk di kurangi barang keluar
			qty_future = qty_future_in - qty_future_out


			res = qty_future - qt
			if res < 0 :
				raise osv.except_osv(_('Error'), _('Qty untuk barang %s di gudang %s hanya tersedia %s %s') % (prod_name,lin.location_id.name,qty_future,l.product_uom.name))
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
									'state':'assigned'										
									})
		
		if round(sub_tot,2) != lin.amount_untaxed:
			raise osv.except_osv(_('Error!'),_('Total rupiah faktur tidak sama dengan total rupiah line faktur! \n '\
				'Klik "Recalculate"'))

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
			raise osv.except_osv(_('Warning!'),_('Jumlah piutang (global) customer ini sudah melewati limit!'))

		#####################################################################################################################
		#Protek limit piutang per supplier di disable, karena tidak ada supplier di form SO
		#####################################################################################################################
		#cek limit piutang persupplier 
		# cr.execute('SELECT payable_field,lc.limit FROM limit_customer lc '\
		# 	'WHERE partner_id2=%s AND partner_id=%s',(lin.partner_id.id,lin.partner_id2.partner_id.id))
		# dpt = cr.fetchall()
		# #import pdb;pdb.set_trace()
		# ttl = dpt[0][0]
		# lmt = dpt[0][1]
		# if lmt is None:
		# 	lmt = 0.00
		
		# ttlplus = ttl+lin.amount_total
		# slsh = ttlplus-lmt


		# if lmt >= 1.00 :
		# 	if ttlplus > lmt:
		# 		raise osv.except_osv(_('Warning!'),_('Jumlah piutang customer ini sudah melewati limit dari supplier %s !\n '\
		# 			'Limit = %s  \n '\
		# 			'Piutang saat ini = %s \n '\
		# 			'Selisih = %s' ) % (lin.partner_id2.partner_id.name,lmt,ttl,slsh))

		#Set due date = date order+termin
		tr = lin.property_payment_term.id
		if tr :
			trm = lin.property_payment_term.line_ids[0].days
			if trm:
				dt_o = lin.date_order		
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
