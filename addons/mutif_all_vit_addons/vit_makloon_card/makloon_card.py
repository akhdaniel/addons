from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class makloon_card(osv.osv): 
	_name = 'makloon.card' 
	_rec_name = 'partner_code'

	# def _get_ending_balance(self, cr, uid, ids, field_name, arg, context=None):
	# 	if context is None:
	# 		context = {}
	# 	res = {}
		
	# 	for card in self.browse(cr,uid,ids,context=context):
	# 		if card.makloon_card_ids:
	# 			total_debit = 0
	# 			total_credit = 0
	# 			total_qty = 0
	# 			bayar = '-'
	# 			for detail in card.makloon_card_ids:
	# 				total_debit += detail.debit
	# 				total_credit += detail.credit
	# 				total_qty += detail.quantity
	# 			total_balance = detail.balance
	# 			if total_balance > 0 :
	# 				bayar = 'Lebih Bayar'
	# 			elif total_balance < 0 :
	# 				bayar = 'Kurang Bayar'

	# 			self.write(cr,uid,card.id,{'total_qty' : total_qty,
	# 										'total_debit':total_debit,
	# 										'total_credit':total_credit,
	# 										'total_balance':total_balance,
	# 										'bayar':bayar},context=context)	

	# 		res[card.id] = True
	# 	return res

	_columns = {
		'user_id'	 			: fields.many2one('res.users','User',readonly=True),
		'date_start' 			: fields.date('Date Start',required=True),
		'date_end'   			: fields.date('Date End',required=True),
		'partner_id' 			: fields.many2one('res.partner',string='Makloon Name',required=True),
		'partner_code'			: fields.related('partner_id','code',type='char',string='Makloon Code'),
		'street'				: fields.related('partner_id','street',type='char',string='Address'),
		'phone'					: fields.related('partner_id','phone',type='char',string='Phone'),
		'makloon_card_ids'		: fields.one2many('makloon.card.detail','makloon_card_id','Card Details'),

		#'insert_ending_balance' : fields.function(_get_ending_balance,type='boolean',string='Insert Ending Balance'),
		'total_order' 			: fields.integer('Total Qty Order'),
		'total_finish' 			: fields.integer('Total Qty Finish'),
		'total_hold' 			: fields.integer('Total Qty Dafect'),
		'total_qty'				: fields.integer('Total Qty Balance'),
		'total_balance' 		: fields.integer('Total Balance (Rp)'),
			}


class makloon_card_detail(osv.osv):
	_name 		= "makloon.card.detail"
	_description = 'Kartu Makloon Details'


	_columns 	= {
		'makloon_card_id'	: fields.many2one('makloon.card','Makloon Card'),
		'date_end'   		: fields.date('Date End'),
	
		'makloon_id' 		: fields.many2one('vit.makloon.order', 'No SPK Makloon'),
		'cutting_id'		: fields.related('makloon_id','origin',type='many2one',relation='vit.cutting.order',string='No SPK Cutting'),
		'model_type_id' 	: fields.many2one('vit.master.type','Model'),

		'size'				: fields.char('Size'),
		'total_mkl'			: fields.integer('Order (Qty)'),
		'total_finish'		: fields.integer('Finish (Qty)'),
		'total_hold'		: fields.integer('Defect (Qty)'),
		'qty_balance'		: fields.integer('Balance (Qty)'),
		'price_balance'		: fields.integer('Price (Rp)'),

	}