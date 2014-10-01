from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import time
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
	_inherit = "account.invoice"


	def invoice_validate(self, cr, uid, ids, context=None):
		#import pdb;pdb.set_trace()
		jur = self.pool.get('account.journal')
		mv_obj = self.pool.get('stock.move')

		skrg = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

		va = self.browse(cr,uid,ids)[0]
		ju = va.journal_id.id
		loca = va.location_id2.id
		if ju == 4 : # sales refund journal
			for x in va.invoice_line:
				prod = x.product_id.id
				prod_name = x.name
				uom_id = x.uom_id.id
				cf = x.uos_id.factor_inv
				uos_qty = x.quantity
				uos_id = x.uos_id.id

				mv_obj.create(cr, uid,{'product_id':prod,
									'name':prod_name,
									'origin':va.name,
									'location_id':9,#customer
									'location_dest_id':loca,
									'date_expacted':skrg,
									'product_uos':uos_id,
									'product_uos_qty':uos_qty/cf,														
									'product_qty':uos_qty,
									'product_uom':uom_id,										
									'state':'done',										
									})	

		self.write(cr, uid, ids, {'state':'open'}, context=context)
		return True	

		#tambah nama gudang/cabang admin
	def _get_default_loc2(self, cr, uid, context=None):
		
		emplo = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		lo = self.pool.get('hr.employee').browse(cr,uid,emplo)[0]
		loc = lo.location_id.id

		return loc	

	def action_deliver(self,cr,uid,ids,context=None): 
		#import pdb;pdb.set_trace()
		return self.write(cr,uid,ids,{'state':'deliver'},context=context)

	def action_cn(self,cr,uid,ids,context=None): 
		#import pdb;pdb.set_trace()
		return self.write(cr,uid,ids,{'state':'cn_conf'},context=context)		

	def _get_nik(self, cr, uid, context=None):
		
		emplo = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		ni = self.pool.get('hr.employee').browse(cr,uid,emplo)[0]
		nik = ni.nik

		return nik

	_columns = {
		'warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
		'location_id' : fields.many2one('stock.location','Location',readonly=True),
		'user_id2' :fields.many2one('res.users','User Admin',readonly=True),
		'location_id2' : fields.many2one('stock.location','Location Admin',readonly=True),
		'credit' : fields.related('partner_id','credit',type="float",string="Total Receivable ",readonly="True"),
		'credit_limit' : fields.related('partner_id','credit_limit',type="float",string="Total Limit",readonly="True"),

		'nik' :fields.char('Sales Code',readonly=True),

		'volume' : fields.float('Volume',readonly=True),
		'weight' : fields.float('Weight',readonly=True),

		'based_route_id': fields.related('partner_id','based_route_id',relation='master.based.route',type='many2one',string='Based Route'),

		'state': fields.selection([
			('draft','Draft'),
			('deliver','Deliver'),
			('proforma','Pro-forma'),
			('proforma2','Pro-forma'),
			('cn_conf','CN Confirmation'),
			('open','Open'),
			('paid','Paid'),
			('cancel','Cancelled'),
			],'Status', select=True, readonly=True, track_visibility='onchange',
			help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Invoice. \
			\n* The \'Pro-forma\' when invoice is in Pro-forma status,invoice does not have an invoice number. \
			\n* The \'Open\' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice. \
			\n* The \'Paid\' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
			\n* The \'Cancelled\' status is used when user cancel invoice.'),		
		}


	_defaults ={
		'user_id2': lambda obj, cr, uid, context: uid,
		'location_id2' : _get_default_loc2,
		'location_id' : _get_default_loc2,
		'nik' :_get_nik,
		}		

class stock_location(osv.osv):
	_inherit = "stock.location"

	_columns = {
		'code': fields.char('Kode', size=13,required=True),

		}


class account_invoice_line(osv.osv):
	_inherit = "account.invoice.line"
	_name = "account.invoice.line"

	def _get_uom_id(self, cr, uid, *args):
		try:
			proxy = self.pool.get('ir.model.data')
			result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
			return result[1]
		except Exception, ex:
			return False  

	def _get_tot_qty(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		#import pdb;pdb.set_trace()
		for line in self.browse(cr, uid, ids):
			t_qty = round((line.qty*line.uos_id.factor_inv) + (line.quantity2*line.uom_id.factor_inv),3)
			res[line.id] = t_qty
		return res

	def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		#import pdb;pdb.set_trace()
		for line in self.browse(cr, uid, ids):
			#price = line.price_unit * (1-(line.discount or 0.0)/100.0)
			price = round(line.price_unit *line.quantity,3)
			# taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
			taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
			#res[line.id] = taxes['total']
			res[line.id] = price
			# if line.invoice_id:
			# 	cur = line.invoice_id.currency_id
			# 	res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
		return res

	_columns = {
		'quantity2': fields.float('Small Qty', digits_compute= dp.get_precision('Product Unit of Measure')),
		'uom_id' : fields.many2one('product.uom', 'Small UoM', ondelete='set null', select=True,required=True),
		'disc_tot': fields.float('Disc Total'),
		'price_subtotal': fields.function(_amount_line, string='Amount', type="float",
			digits_compute= dp.get_precision('Account'), store=True),
		'qty_func': fields.function(_get_tot_qty,string='Qty Tot'),
		'qty': fields.float('Qty', digits_compute= dp.get_precision('Product Unit of Measure')),
		'quantity': fields.function(_get_tot_qty,string='Quantity',type="float", digits_compute= dp.get_precision('Product Unit of Measure'), required=True),

	}

	_defaults = {
		'uom_id' : _get_uom_id,
	} 