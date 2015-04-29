# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class account_invoice_line(osv.Model):
	_inherit = "account.invoice.line"

	def _amount_gross(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		for line in self.browse(cr, uid, ids):
			price 	= line.price_unit
			qty		= line.quantity
			gross 	= price*qty
			res[line.id] = gross
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
		'gross' : fields.function(_amount_gross, string='Gross Calculate',type='float',digits_compute= dp.get_precision('Account'),store=True),

	}