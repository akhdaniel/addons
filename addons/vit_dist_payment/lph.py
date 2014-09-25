from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.product.product
import openerp.addons.decimal_precision as dp
import time
from openerp.tools.translate import _

class lph(osv.osv):
	_name 		= "vit_dist_payment.lph"

	def hitung_total(self,lph_line_ids):
		total = 0.0
		for lphl in lph_line_ids:
			total = total + lphl.amount_total 
		return total 

	def hitung_balance(self,lph_line_ids):
		total = 0.0
		for lphl in lph_line_ids:
			total = total + lphl.residual 
		return total 

	def hitung_paid(self,lph_line_ids):
		total = 0.0
		for lphl in lph_line_ids:
			total = total + ( lphl.amount_total - lphl.residual )
		return total 

	def _calc_total(self, cr, uid, ids, field, arg, context=None):
		results = {}
		lphs = self.browse(cr, uid, ids, context=context) 
		for lph in lphs:
			results[lph.id] = self.hitung_total(lph.lph_line_ids)
		return results

	def _calc_balance(self, cr, uid, ids, field, arg, context=None):
		results = {}
		lphs = self.browse(cr, uid, ids, context=context)
		for lph in lphs:
			results[lph.id] = self.hitung_balance(lph.lph_line_ids)
		return results

	def _calc_paid(self, cr, uid, ids, field, arg, context=None):
		results = {}
		lphs = self.browse(cr, uid, ids, context=context)
		for lph in lphs:
			results[lph.id] = self.hitung_paid(lph.lph_line_ids)
		return results

	_columns 	= {
		'name'			  : fields.char('Number'),
		'date'			  : fields.date('Date'),
        'user_id'		  : fields.many2one('res.users', 'Salesman', select=True, ),
        'based_route_id'  : fields.many2one('master.based.route','Route'),		
        'lph_line_ids'    : fields.many2many(
			'account.invoice',   	# 'other.object.name' dengan siapa dia many2many
			'lph_invoice',          # 'relation object'
			'lph_id',               # 'actual.object.id' in relation table
			'invoice_id',           # 'other.object.id' in relation table
			'Invoice',              # 'Field Name'
			domain="[('state','=','open')]",
			required=True),
        'total'           : fields.function(_calc_total, type="float", string="Total"),
        'balance'         : fields.function(_calc_balance, type="float", string="Balance"),
        'total_paid'      : fields.function(_calc_paid, type="float", string="Total Paid"),
        'state'           : fields.selection([
            ('draft', 'Draft'),
            ('open', 'On Progress'),
            ('done', 'Done'),
            ], 'Status', readonly=True, 
            help="Gives the status of the quotation or sales order.", 
            select=True),
       	'voucher_id'	  : fields.many2one('vit_dist_payment.voucher', 'Voucher'),
       	'voucher_total'	  : fields.related('voucher_id', 'total' , type="float", 
       		relation="vit_dist_payment.voucher", string="Voucher Total", store=True)
	}

	def create(self, cr, uid, vals, context=None):
		ctx = None
		new_name= self.pool.get('ir.sequence').get(cr, uid, 'lph', context=ctx) or '/'
		vals.update({'name' : new_name}) 
		return super(lph, self).create(cr, uid, vals, context=context)

	_defaults = {
		'state' : 'draft',
		'date'  : lambda *a : time.strftime("%Y-%m-%d") ,
	}

	def onchange_based_route(self, cr, uid, ids, date, user_id, based_route_id, context=None):

		results = {}
		if not based_route_id:
			return results

		##############################################################################
		# 
		##############################################################################
		inv_obj = self.pool.get('account.invoice')
		inv_ids = inv_obj.search(cr, uid, [
			('state','=','open'),
			('based_route_id','=',based_route_id) ], context=context)

		#insert many2many records
		lph_line_ids = [(6,0,inv_ids)]
		results = {
			'value' : {
				'lph_line_ids' : lph_line_ids
			}
		}
		return results

	def action_confirm(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'open'},context=context)

	def action_done(self,cr,uid,ids,context=None):
		lph = self.browse(cr, uid, ids[0], context=context )
		if lph.voucher_total != lph.total_paid:
			raise osv.except_osv(_('Validate Error'),_("Amount Voucher is not equal to LPH Total Paid ") ) 

		return self.write(cr,uid,ids,{'state':'done'},context=context)

	def action_draft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'},context=context)

