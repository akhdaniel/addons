# -*- coding: utf-8 -*-

######################################################################
#
#  Note: Program metadata is available in /__init__.py
#
######################################################################

from openerp.osv import fields, osv
import tools
import time
import openerp.addons.decimal_precision as dp

class vit_customer_card(osv.osv):
	_name = 'vit.customer.card'
	#_order = 'date'

	_columns = {
		'date': fields.date('Date'),
		'ref': fields.char('Reference', size=64),
		'nbr': fields.integer('Qty (Pcs)'),
		'debit': fields.integer('Debit (Rp)'),
		'credit': fields.integer('Credit (Rp)'),
		'balance': fields.integer('Balance (Rp)'),
		'quantity': fields.integer('Products Qty'),
		'description': fields.many2one('account.move','Transaction No.'),
		'narration' : fields.char('Description'),
		'customer_card_id': fields.many2one('vit.customer','Customer Card'),
		'note' : fields.char('Note'),
	}

vit_customer_card()


note0 = """
Post Penambah Piutang
"""
note1 = """
sales
Selisih Harga Kurang
Ongkos Kirim Kurang
Selisih Barang Jadi
"""
note2 = """
Post Pengurang Piutang
"""
note3 = """
Payment Cash & Bank
Sales Retur
Point Reward
Selisih Harga Lebih
Cash Back
Ongkos Kirim Lebih
Selisih Barang Kurang
"""

class vit_customer(osv.osv): 
	_name = 'vit.customer' 
	_rec_name = 'bayar'

	def _get_ending_balance(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		res = {}		
		for card in self.browse(cr,uid,ids,context=context):
			if card.customer_card_ids:
				total_debit = 0
				total_credit = 0
				total_qty = 0
				bayar = '-'
				for detail in card.customer_card_ids:
					total_debit += detail.debit
					total_credit += detail.credit
					total_qty += detail.quantity
				total_balance = detail.balance
				if total_balance > 0 :
					bayar = 'Lebih Bayar'
				elif total_balance < 0 :
					bayar = 'Kurang Bayar'	

				self.write(cr,uid,card.id,{'total_qty' : total_qty,
											'total_debit':total_debit,
											'total_credit':total_credit,
											'total_balance':total_balance,
											'bayar':bayar},context=context)	

			res[card.id] = True
		return res

	_columns = {
		'user_id'	 			: fields.many2one('res.users','User',readonly=True),
		'date_start' 			: fields.date('Date Start',required=True),
		'date_end'   			: fields.date('Date End',required=True),
		'partner_id' 			: fields.many2one('res.partner',string='Customer Name',required=True),
		'partner_code'			: fields.related('partner_id','code',type='char',string='Customer Code'),
		'street'				: fields.related('partner_id','street',type='char',string='Address'),
		'phone'					: fields.related('partner_id','phone',type='char',string='Phone'),
		'customer_card_ids'		: fields.one2many('vit.customer.card','customer_card_id','Card Details'),
		'note0' 				: fields.char('Note 0'),
		'note1' 				: fields.text('Note 1'),
		'note2' 				: fields.char('Note 2'),
		'note3' 				: fields.text('Note 3'),
		'insert_ending_balance' : fields.function(_get_ending_balance,type='boolean',string='Insert Ending Balance'),
		'total_qty'				: fields.integer('Total Qty'),
		'total_debit' 			: fields.integer('Total Debit'),
		'total_credit' 			: fields.integer('Total Credit'),
		'total_balance' 		: fields.float('Total Balance'),
		'bayar' 				: fields.char('Bayar'),
	}

	_defaults = {
		'note0' : note0,
		'note1' : note1,
		'note2' : note2,
		'note3' : note3,
	}


class account_invoice(osv.osv):
	_inherit = "account.invoice"

	def _get_tersebut(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		res = {}
		for inv in self.browse(cr,uid,ids,context=context):
			piutang = inv.partner_id.credit
			desc = '-'
			if piutang < 0 :
				desc = 'Lebih Bayar'
			elif piutang > 0 :
				desc = 'Kurang Bayar'

			res[inv.id] = desc
		return res

	_columns = {
		'credit' : fields.related('partner_id','credit',type='float',string='Piutang',readonly=True,digits_compute= dp.get_precision('Product Price')),
		'keterangan' : fields.function(_get_tersebut,type='char',string='Status Piutang'),
	}