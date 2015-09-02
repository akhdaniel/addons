from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc


class sale_order(osv.osv):

	_name = 'sale.order'
	_inherit = "sale.order"

	_columns = {
		# 'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}),

	}



sale_order()

class sale_order_line(osv.osv):

	_name = 'sale.order.line'
	_inherit = "sale.order.line"
	
	_columns = {
		'qty_hand' :fields.char('Stock On Hand'),
		'outgoing' :fields.char('Booking'),
		'forecast' :fields.char('Forecasted Quantity'),
		'real_max_order': fields.float('Can Ordered'),
		'max_order' : fields.float('Max Order'),
		'price_max_order' : fields.float('Price Max Order')
	}

	def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
		# import pdb;pdb.set_trace()
		if product:
			product_pool = self.pool.get('product.product').browse(cr, uid, product)
			available = product_pool.qty_available
			out = product_pool.outgoing_qty
			forec = product_pool.virtual_available

			context = context or {}
	        lang = lang or context.get('lang',False)
	        if not  partner_id:
	            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
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

	        # import pdb;pdb.set_trace()
	        if not flag:
	            # result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
	            result['name'] = self.pool.get('product.product').browse(cr,uid,product_obj.id).name_template
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
	            domain = {'product_uom':
	                        [('category_id', '=', product_obj.uom_id.category_id.id)],
	                        'product_uos':
	                        [('category_id', '=', uos_category_id)]}
	        elif uos and not uom: # only happens if uom is False
	            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
	            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
	            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
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
	        if available == 0.0:
	        	result['qty_hand'] = 'Tidak Tersedia'
	        else:
	        	result['qty_hand'] = available

	        if out == 0.0:
	        	result['outgoing'] = 'Belum Keluar'
	        else:
	        	result['outgoing'] = out

	       	if forec == 0.0:
	        	result['forecast'] = 'Tidak ada Perkiraan/Terbooking'
	        else:
	        	result['forecast'] = forec

	        ##Cari Partner_id untuk mendapatkan nilai diskon
	        # import pdb;pdb.set_trace()
	        if partner_id: 
	        	partner_pool = partner_obj.browse(cr, uid, partner_id)
	        	discount = partner_pool.discount
	        	result['discount'] = discount

		return {'value': result, 'domain': domain, 'warning': warning}	
		# return {'value':{'qty_hand':available}}


sale_order_line()

