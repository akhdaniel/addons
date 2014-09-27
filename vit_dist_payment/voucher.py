from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class voucher(osv.osv):
	_name 		= "vit_dist_payment.voucher"

	def hitung_total(self,voucher_line_ids):
		total = 0.0
		for vl in voucher_line_ids:
			total = total + vl.amount 
		return total 

	def _calc_total(self, cr, uid, ids, field, arg, context=None):
		results = {}
		vouchers = self.browse(cr, uid, ids, context=context)
		for v in vouchers:
			results[v.id] = self.hitung_total(v.voucher_line_ids)
		return results

	def _has_lph(self, cr, uid, ids, field, arg, context=None):
		results = {}
		vouchers = self.browse(cr, uid, ids, context=context)
		for v in vouchers:
			results[v.id] = False 
			if v.lph_ids:
				results[v.id] = True
		return results

	_columns 	= {
		'received_from' : fields.char('Received From'),
		'date'          : fields.date('Date'),
		'name'          : fields.char('Number'),
		'voucher_line_ids': fields.one2many('vit_dist_payment.voucher_line', 'voucher_id', 
			'Voucher Lines', ondelete="cascade"),
        'state'           : fields.selection([
            ('draft', 'Draft'),
            ('open', 'On Progress'),
            ('done', 'Done'),
            ], 'Status', readonly=True, 
            help="Gives the status of the quotation or sales order.", 
            select=True),
       	'total'         : fields.function(_calc_total, type="float", string="Total" , store=True ),
		'lph_ids'       : fields.one2many('vit_dist_payment.lph', 'voucher_id', 'LPH Lines'),
       	'has_lph'		: fields.function(_has_lph, type='boolean', string='Has LPH'),
	}

	def create(self, cr, uid, vals, context=None):
		ctx = None
		new_name= self.pool.get('ir.sequence').get(cr, uid, 'voucher', context=ctx) or '/'
		vals.update({'name' : new_name}) 
		return super(voucher, self).create(cr, uid, vals, context=context)

	_defaults = {
		'state' : 'draft',
		'date'  : lambda *a : time.strftime("%Y-%m-%d") ,
	}
	
	def action_confirm(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'open'},context=context)

	def action_done(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'done'},context=context)

	def action_draft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'},context=context)


class voucher_line(osv.osv):
	_name 		= "vit_dist_payment.voucher_line"
	_columns 	= {
		'voucher_id'  : fields.many2one('vit_dist_payment.voucher', string="Voucher"),
		'account_id'  : fields.many2one('account.account', 'Account'),
		'description' : fields.char('Description'),
		'amount'      : fields.float('Amount')
	}