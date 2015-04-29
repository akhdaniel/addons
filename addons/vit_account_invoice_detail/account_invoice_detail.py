# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class account_invoice_line(osv.Model):
	_inherit = "account.invoice.line"

	def _amount_gross(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		for line in self.browse(cr, uid, ids):
			price 	= line.price_unit
			qty		= line.quantity
			gross 	= price*qty
			taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, gross, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
			res[line.id] = taxes['total']
			if line.invoice_id:
				cur = line.invoice_id.currency_id
				res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
		return res		

	_columns = {
		#'partner_id': fields.related('invoice_id','partner_id',type='many2one',relation='res.partner',string='Partner',store=True)
		'type': fields.related('invoice_id','type',type='selection',string='Type'),
		'state': fields.related('invoice_id','state',type='selection',string='State',store=True),
		'user_id':fields.related('invoice_id','user_id',type='many2one',relation='res.users',string='Responsible',store=True),
		'journal_id': fields.related('invoice_id','journal_id',type='many2one',relation='account.journal',string='Journal',store=True),
		'period_id': fields.related('invoice_id','period_id',type='many2one',relation='account.period',string='Period',store=True),
		'date_invoice': fields.related('invoice_id','date_invoice',type='date',string='Invoice date',store=True),
		'date_due': fields.related('invoice_id','date_due',type='date',string='Due Date',store=True),
		'move_id': fields.related('invoice_id','move_id',type='many2one',relation='account.move',string='Journal Entry',store=True),
		'gross' : fields.function(_amount_gross, string='Gross',type='float',digits_compute= dp.get_precision('Account'),store=True),

	}