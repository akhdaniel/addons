from osv import osv
from osv import fields
import time
from tools.translate import _
import decimal_precision as dp
from array import *
from decimal import Decimal, ROUND_DOWN
import logging
_logger = logging.getLogger(__name__)


class res_company(osv.osv):
	_inherit = "res.company"
	# _description = "Journal"

	_columns = {
		'discount_account_id': fields.many2one('account.account', 'Discount Account', help="It acts as a Additional account for credit amount"),
	}
	

class account_invoice(osv.osv):
	_inherit = "account.invoice"

	################################################################################################
	# Pada Tombol Validate di account.invoice bila di eksekusi akan menjalan kan action_move_create 
	# Disini kita dapat menambahkan atau mengupdate account.move.line nya berdasarkan move_id yang
	# didapat
	###############################################################################################
	def action_move_create(self, cr, uid, ids, context=None):
		_logger.info("action_move_create")

		res = super(account_invoice, self).action_move_create(cr, uid, ids, context=None)
		self.update_saj_journal(cr, uid, ids, ids[0], context)
		return res

	def update_saj_journal(self, cr, uid, ids, invoice_id, context=None):
		_logger.info("Update SAJ journal voucher")
		move_obj = self.pool.get('account.move')

		#####################################################################
		#cari invoice SAJ
		#####################################################################
		invoice_browse = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
		if invoice_browse.journal_id.code != 'SAJ':
			return  
		
		#####################################################################
		# Cancel Dulu Post Di move_id yang sudah terbentuk
		#####################################################################
		move_id = invoice_browse.move_id.id
		move_obj.button_cancel(cr, uid, [move_id],context)

		account_move = move_obj.browse(cr,uid,move_id,context=context)
		account_move_line_obj = self.pool.get('account.move.line')

		#####################################################################
		# cari company id
		#####################################################################
		company_id = invoice_browse.company_id.id

		for invoice_line in invoice_browse.invoice_line:
			origins 	= invoice_browse.origin.split(":")
			order_obj 	= self.pool.get('sale.order')
			order_id 	= order_obj.search(cr, uid, [('name','=', origins[-1] )])[0]
			order 		= order_obj.browse(cr, uid, order_id, context)
			date_order 	= order.date_order	
			partner_id  = order.partner_id.id 

			####################################################################################################################
			# Update account.move.line, berdasarkan looping jika account_id di invoice == account_id di invoice account.move.line
			# dan Product di invoice == Product di invoice account.move.line, Lalu update nilai debit & kredit terbaru hasil dari
			# Quantity Barang tiap line invoice di kali dengan price unitnya
			####################################################################################################################
			for line in account_move.line_id:
				if (invoice_line.product_id.id == line.product_id.id) and (invoice_line.account_id.id == line.account_id.id):
					if (line.debit or line.credit)!=0:
						gross_subtotal = invoice_line.quantity * invoice_line.price_unit
						if line.debit !=0:
							aml_id = line.id
							account_move_line_obj.write(cr,uid,aml_id,{'debit': gross_subtotal},context=context)
						else:
							aml_id = line.id
							account_move_line_obj.write(cr,uid,aml_id,{'credit': gross_subtotal},context=context)
			
			#############################################################################
			# Update kan COA Diskon nya Nilai diskon nya
			#############################################################################
			gross_subtotal = invoice_line.quantity * invoice_line.price_unit
			disc_subtotal = gross_subtotal - ((invoice_line.quantity * invoice_line.price_unit) * (1-(invoice_line.discount or 0.0)/100.0))
			
			#####################################################################
			# Cari Discount Account
			#####################################################################
			company_obj = self.pool.get('res.company').browse(cr,uid,company_id,context)
			discount_account_id = company_obj.discount_account_id.id
			if not discount_account_id:
				raise osv.except_osv(_('Error !'), _('Sales Journal Belum ada  Discount Account. Set Up Melalui Setting - Companies - Configuration(Tab)') )
			

			#####################################################################
			# Update Account Move yang telah di peroleh account_move.id
			#####################################################################
			debit ={
					'date'		 : date_order,
					'name'       : 'Diskon'+' '+invoice_line.product_id.name,
					'ref'        : invoice_browse.number,
					'partner_id' : partner_id,
					'account_id' : discount_account_id,
					'debit'      : disc_subtotal,
					'credit'     : 0.0
					}
			lines = [(0,0,debit)]
			am_data = {
						'line_id'      : lines ,
						}

			move_obj.write(cr,uid,[account_move.id],am_data,context=context)

		#####################################################################
		# Posted Kembali account_move.id
		#####################################################################
		move_obj.button_validate(cr,uid, [account_move.id], context)
		_logger.info( "Journal Created & Posted" )
		return True

account_invoice()
