from osv import osv
from osv import fields
#from _common import rounding
import time
from tools.translate import _
import decimal_precision as dp
from array import *
from decimal import Decimal, ROUND_DOWN
import logging
_logger = logging.getLogger(__name__)

class sale_order(osv.osv):
	_inherit = "sale.order"

	def action_invoice_create(self, cr, uid, ids, context=None):
		_logger.info("creating manual invoice")
		invoice_id = super(sale_order, self).action_invoice_create(cr, uid, ids, context=None)

		### create NPA journal
		# kalau mau dicreate waktu create invoice draft
		self.create_npa_journal(cr, uid, ids, invoice_id, context)

		return invoice_id 



	def create_npa_journal(self, cr, uid, ids, invoice_id, context=None):
		_logger.info("creating NPA journal voucher")

		move_lines = []

		#cari invoice
		invoice_browse = self.pool.get('account.invoice').browse(cr, uid, invoice_id)

		#company id, currency
		company_id = invoice_browse.company_id.id
		#currency
		company_currency = invoice_browse.company_id.currency_id.id
		diff_currency_p = invoice_browse.currency_id.id <> company_currency
		currency_id = invoice_browse.currency_id.id
		cur_obj = self.pool.get('res.currency')
		#period
		period_id = invoice_browse.period_id.id

		#npa partner
		partner_obj = self.pool.get('res.partner')
		npa_partner_id = partner_obj.search(cr, uid, [('name','=', 'National Petroleum Authority')])[0]
		if not npa_partner_id:
			raise osv.except_osv(_('Error !'), _('No Partner with name National Petroleum Authority. Please set it up through Partner data') )


		#EXREF journal , default db and cr account
		journal = invoice_browse.journal_id
		default_credit_account_id = invoice_browse.journal_id.default_credit_account_id.id
		if not default_credit_account_id:
			raise osv.except_osv(_('Error !'), _('Ex Journal does not have Default Credit Account. Please set it up through Accounting - Configuration - Journals ') )
		default_debit_account_id = invoice_browse.journal_id.default_debit_account_id.id
		if not default_debit_account_id:
			raise osv.except_osv(_('Error !'), _('Ex Journal does not have Default Debit Account. Please set it up through Accounting - Configuration - Journals ') )

		#cari sales order, masukkan ke voucher line 
		order 		= self.pool.get('sale.order').browse(cr, uid, ids[0] )
		pricelist 	= order.pricelist_id.id
		date_order 	= order.date_order	
		partner_id  = order.partner_id.id 

		for so_line in order.order_line:
			_logger.info("creating move_lines")
			product 				= so_line.product_id
			product_name			= product.name 
			product_xref_account 	= product.property_account_exref.id

			#core - sale price
			product_id 	= so_line.product_id.id 
			qty 		= so_line.product_uom_qty
			price_unit	= so_line.price_unit
			uom 		= so_line.product_uos.id
			cur_obj = self.pool.get('res.currency')
			

			core_price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
				product_id,  qty, partner_id, {
					'uom': uom,
					'date': date_order,
			})

			val_currency = (core_price['core_price'] - price_unit ) * qty
			_logger.error(val_currency)
			val = cur_obj.compute(cr, uid, 
				currency_id, 
				company_currency, val_currency, context={'date': date_order}) 
			_logger.error(val)

			
			#core > sale price
			if val > 0:
				"""
				diff journal 
				"""
				move_lines.append((0,0,{
					'name': 'Differential ' + product_name,
					'credit': prettyFloat(val),
					'account_id': product_xref_account,
					'date_maturity': date_order,
					'amount_currency': diff_currency_p \
						and -1*val_currency or False,
					'currency_id': diff_currency_p \
						and currency_id or False,
					'ref': 'core price > exref price',
					'period_id': period_id,
					#'partner_id':partner_id,                           
					'product_id':product_id,
				}))
				"""
				NPA journal
				"""         
				move_lines.append((0,0,{
					'name': 'NPA receivable',
					'debit' : prettyFloat(val),
					'account_id': default_debit_account_id ,
					'date_maturity': date_order,
					'amount_currency': diff_currency_p \
						and val_currency or False,
					'currency_id': diff_currency_p \
						and currency_id or False,
					'ref': 'core price > exref price',
					'period_id':period_id,
					'partner_id':npa_partner_id,
					'product_id':product_id,
				}))             
			else:
				"""
				differential journal, core price < exref price
				NPA payable
				"""   
				val = val *-1
				val_currency = val_currency * -1
				move_lines.append((0,0,{
					'name': 'NPA payable',
					'credit': prettyFloat(val),
					'account_id': default_credit_account_id ,
					'date_maturity': date_order ,
					'amount_currency': diff_currency_p \
						and -1*val_currency or False,
					'currency_id': diff_currency_p \
						and currency_id or False,
					'ref': 'core price < exref price',
					'period_id': period_id,
					'partner_id':npa_partner_id,                           
					'product_id':product_id,
				}))
				"""
				NPA journal
				"""         
				move_lines.append((0,0,{
					'type': 'dest',
					'name': 'Differential ' + product_name,
					'debit' : prettyFloat(val),
					'price': prettyFloat(val),
					'account_id': product_xref_account ,
					'date_maturity': date_order ,
					'amount_currency': diff_currency_p \
						and val_currency or False,
					'currency_id': diff_currency_p \
						and currency_id or False,
					'ref': 'core price < exref price',
					'period_id':period_id,
					#'partner_id':partner_id,
					'product_id':product_id,
				}))      

		move_id = self.pool.get('account.move').create(cr,uid,{
			'journal_id'	: journal.id,
			'ref' 			: order.name ,
			'company_id' 	: company_id,
			'line_id'		: move_lines
		})
		_logger.info( "created journal item" )
		return move_id

sale_order()

class prettyFloat(float):
    def __repr__(self):
        return "%0.4f" % self
