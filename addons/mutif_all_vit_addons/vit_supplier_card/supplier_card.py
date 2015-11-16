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

class vit_supplier_card(osv.osv):
	_name = 'vit.supplier.card'
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
		'supplier_card_id': fields.many2one('vit.supplier','Supplier Card'),
		'note' : fields.char('Note'),
	}

vit_supplier_card()



class vit_supplier(osv.osv): 
	_name = 'vit.supplier' 
	_rec_name = 'bayar'

	def _get_ending_balance(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		res = {}
		
		for card in self.browse(cr,uid,ids,context=context):
			if card.supplier_card_ids:
				total_debit = 0
				total_credit = 0
				total_qty = 0
				bayar = '-'
				for detail in card.supplier_card_ids:
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
		'partner_id' 			: fields.many2one('res.partner',string='Supplier Name',required=True),
		'partner_code'			: fields.related('partner_id','code',type='char',string='Supplier Code'),
		'street'				: fields.related('partner_id','street',type='char',string='Address'),
		'phone'					: fields.related('partner_id','phone',type='char',string='Phone'),
		'supplier_card_ids'		: fields.one2many('vit.supplier.card','supplier_card_id','Card Details'),
		'insert_ending_balance' : fields.function(_get_ending_balance,type='boolean',string='Insert Ending Balance'),
		'total_qty'				: fields.integer('Total Qty'),
		'total_debit' 			: fields.float('Total Debit'),
		'total_credit' 			: fields.float('Total Credit'),
		'total_balance' 		: fields.float('Tatal Balance'),
		'bayar' 				: fields.char('Bayar'),
	}