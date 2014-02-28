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

class account_invoice(osv.osv):
	_inherit = "account.invoice"


	#######################################################################################
	# menyisipkan fn create_npa_journal setelah invoice di validate
	# supaya dapat refenrece nomor invoice di move
	#######################################################################################
	def invoice_validate(self, cr, uid, ids, context=None):
		_logger.info("validating invoice")
		res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=None)
		self.create_npa_journal(cr, uid, ids, ids[0], context)
		return res

	#######################################################################################
	# menyisipkan fn cancel_npa_journal sebelum invoice di cancel
	# supaya masih dapat nomor invoice utk reference di move 
	#######################################################################################
	def action_cancel(self, cr, uid, ids, context=None):
		_logger.info("canceling invoice")
		self.cancel_npa_journal(cr, uid, ids, context)
		res = super(account_invoice, self).action_cancel(cr, uid, ids, context=None)
		return res

	#######################################################################################
	# create NPA journal waktu invoice validate
	# move line nya sesuai dengan produk di sales order,
	# satu produk menghasilkan 2 journal : NPA dan Defferential
	# posisi debit dan credit tergantung dari berapa besar selisih harga jual dengan 
	# core price (harga produksi)
	#######################################################################################
	def create_npa_journal(self, cr, uid, ids, invoice_id, context=None):
		_logger.info("creating NPA journal voucher")

		move_lines = []

		#####################################################################
		#cari invoice
		#####################################################################
		invoice_browse = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
		if invoice_browse.journal_id.code != 'EXREF':
			return  

		
		#####################################################################
		# cari company id
		#####################################################################
		company_id = invoice_browse.company_id.id

		#####################################################################
		# cari currency
		#####################################################################
		company_currency = invoice_browse.company_id.currency_id.id
		diff_currency_p = invoice_browse.currency_id.id <> company_currency
		currency_id = invoice_browse.currency_id.id
		cur_obj = self.pool.get('res.currency')

		#####################################################################
		# period
		#####################################################################
		period_id = invoice_browse.period_id.id

		#####################################################################
		# cari npa partner
		#####################################################################
		partner_obj = self.pool.get('res.partner')
		npa_partner_id = partner_obj.search(cr, uid, [('name','=', 'National Petroleum Authority')])[0]
		if not npa_partner_id:
			raise osv.except_osv(_('Error !'), _('No Partner with name National Petroleum Authority. Please set it up through Partner data') )


		#####################################################################
		# cari NPA journal , default db and cr account
		#####################################################################
		journal_id 		= self.pool.get('account.journal').search(cr,uid,[('name','=','NPA Journal'),('company_id','=', company_id)])[0]
		journal 		= self.pool.get('account.journal').browse(cr,uid,journal_id,context)
		default_credit_account_id = journal.default_credit_account_id.id
		if not default_credit_account_id:
			raise osv.except_osv(_('Error !'), _('NPA Journal does not have Default Credit Account. Please set it up through Accounting - Configuration - Journals ') )
		default_debit_account_id = journal.default_debit_account_id.id
		if not default_debit_account_id:
			raise osv.except_osv(_('Error !'), _('NPA Journal does not have Default Debit Account. Please set it up through Accounting - Configuration - Journals ') )



		#####################################################################
		# find the sales order originating the invoice
		#####################################################################
		origins 	= invoice_browse.origin.split(":")
		order_obj 	= self.pool.get('sale.order')
		order_id 	= order_obj.search(cr, uid, [('name','=', origins[-1] )])[0]
		order 		= order_obj.browse(cr, uid, order_id, context)

		#####################################################################
		# cari price list sales order
		#####################################################################
		pricelist 	= order.pricelist_id.id
		date_order 	= order.date_order	
		partner_id  = order.partner_id.id 

		#####################################################################
		# loop setiap item di sales order
		# generate NPA journal
		# kumpulkan ke move_lines
		# createa account.move dengan move_lines tsb
		#####################################################################
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
			
			_logger.error("pricelist id")
			_logger.error(pricelist)

			#mencari harga product dari pricelist pada suatu tanggal 
			product_pricelist = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
				product_id,  qty, partner_id, {
					'uom' : uom,
					'date': date_order,
			})
			_logger.error("product_pricelist")
			_logger.error(product_pricelist)

			#value NPA = core_price - price_unit 
			#:: harga subsidi - harga jual 
			val_currency = (product_pricelist['core_price'] - price_unit ) * qty
			
			_logger.error("val_currency")
			_logger.error(val_currency)

			# hitung val dengan currency 
			val = cur_obj.compute(cr, uid, 
				currency_id, 
				company_currency, val_currency, context={'date': date_order}) 

			_logger.error("val")
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
					'period_id'		: period_id,
					'company_id' 	: company_id,
					'partner_id':npa_partner_id,
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
					'partner_id':npa_partner_id,
					'period_id':period_id,
					'company_id' 	: company_id,
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
					'period_id'		: period_id,
					'company_id' 	: company_id,
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
					'period_id'		: period_id,
					'company_id' 	: company_id,
					'product_id':product_id,
				}))      

		_logger.warning(move_lines )
		move_obj 	= self.pool.get('account.move')
		move_id 	= move_obj.create(cr,uid,{
			'journal_id'	: journal.id,
			'ref' 			: invoice_browse.number ,
			'internal_sequence_number' : invoice_browse.number ,
			'company_id' 	: company_id,
			'period_id'		: period_id,
			'line_id'		: move_lines
		})
		move_obj.button_validate(cr,uid, [move_id], context)

		_logger.info( "created journal item" )
		return move_id


	#######################################################################################
	# cancel NPA journal waktu cancel validate
	# hapus semua move dan move line yang memiliki ref = nomor invoice yang 
	# di-cancel
	#######################################################################################
	def cancel_npa_journal(self, cr, uid, ids, context=None):
		_logger.info("deleting move and move_lines for NPA journal")
		invoice_id = ids[0]

		#####################################################################
		#cari invoice object
		#####################################################################
		invoice_browse = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
		_logger.info(invoice_browse)
		_logger.info(invoice_browse.number)
		company_id = invoice_browse.company_id.id
		
		#####################################################################
		#cari account move yang ref nya = invoice number
		#####################################################################
		account_move_obj = self.pool.get('account.move')
		move_ids = account_move_obj.search(cr,uid, [('ref','=',invoice_browse.number),('company_id','=',company_id)])

		#####################################################################
		# jika ditemukan ada id move, jalankan button_cancel dan 
		# delete /unlink
		#####################################################################
		_logger.info(move_ids)
		if move_ids:
			account_move_obj.button_cancel(cr, uid, move_ids, context=context)
			account_move_obj.unlink(cr, uid, move_ids, context=context)

		return True

account_invoice()

class prettyFloat(float):
	def __repr__(self):
		return "%0.4f" % self