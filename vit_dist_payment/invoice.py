from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
_logger = logging.getLogger(__name__)

class account_invoice(osv.osv):
	_inherit = "account.invoice"
	_name = "account.invoice"


	def create(self, cr, uid, vals, context=None):
		if 'is_claim' in vals:
			if vals['is_claim'] == True:
				jur_ids = self.pool.get('account.journal').search(cr,uid,[('type','=','sale_refund'),('is_claim','=',True)],context=context)
				if jur_ids != []:
					jur_id = jur_ids[0]
					jur_claim = {'journal_id': jur_id}
				vals = dict(vals.items()+jur_claim.items()) 
		elif 'is_claim' not in vals:
			#jika bukan dari SO
			if 'origin' not in vals:
				jur_ids = self.pool.get('account.journal').search(cr,uid,[('type','=','sale_refund'),('is_claim','=',False)],context=context)
				if jur_ids != []:
					jur_id = jur_ids[0]
					jur_claim = {'journal_id': jur_id}
				vals = dict(vals.items()+jur_claim.items()) 				
		return super(account_invoice, self).create(cr, uid, vals, context=context)

	def _get_journal(self, cr, uid, context=None):
		if context is None:
			context = {}
		#import pdb;pdb.set_trace()
		type_inv = context.get('type', 'out_invoice')
		user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		company_id = context.get('company_id', user.company_id.id)
		type2journal = {'out_invoice': 'sale', 'in_invoice': 'purchase', 'out_refund': 'sale_refund', 'in_refund': 'purchase_refund'}
		journal_obj = self.pool.get('account.journal')
		domain = [('company_id', '=', company_id)]
		if isinstance(type_inv, list):
			domain.append(('type', 'in', [type2journal.get(type) for type in type_inv if type2journal.get(type)]))

		#tambah kondisi is_claim jika menggunakan jurnal claim
		if 'default_is_claim' in context:
			if context['default_is_claim'] == True:
				domain.append(('is_claim','=',True))			
		else:
			domain.append(('type', '=', type2journal.get(type_inv, 'sale')))
			if 'default_is_claim' not in context:
				domain.append(('is_claim','=',False))
		res = journal_obj.search(cr, uid, domain, limit=1)

		return res and res[0] or False

	_columns = {
		'is_cn' : fields.related('journal_id','is_cn',type='boolean',relation='account.journal',string='CN Confirmation'),
		'is_draft_lph' : fields.boolean('Is Draft'),
		'is_claim' : fields.boolean('Is Claim'),
		'pay_estimates_date' : fields.date('Pay Estimates'),
			}

	# def action_number(self, cr, uid, ids, context=None):
	# 	#import pdb;pdb.set_trace()
	# 	if context is None:
	# 		context = {}
	# 	#TODO: not correct fix but required a frech values before reading it.
	# 	self.write(cr, uid, ids, {})

	# 	for obj_inv in self.browse(cr, uid, ids, context=context):
	# 		invtype = obj_inv.type
	# 		number = obj_inv.number
	# 		move_id = obj_inv.move_id and obj_inv.move_id.id or False
	# 		reference = obj_inv.reference or ''

	# 		self.write(cr, uid, ids, {'internal_number': number})

	# 		if invtype in ('in_invoice', 'in_refund'):
	# 			if not reference:
	# 				ref = self._convert_ref(cr, uid, number)
	# 			else:
	# 				ref = reference
	# 		else:
	# 			ref = self._convert_ref(cr, uid, number)

	# 		cr.execute('UPDATE account_move SET ref=%s ' \
	# 				'WHERE id=%s AND (ref is null OR ref = \'\')',
	# 				(ref, move_id))
	# 		cr.execute('UPDATE account_move_line SET ref=%s ' \
	# 				'WHERE move_id=%s AND (ref is null OR ref = \'\')',
	# 				(ref, move_id))
	# 		cr.execute('UPDATE account_analytic_line SET ref=%s ' \
	# 				'FROM account_move_line ' \
	# 				'WHERE account_move_line.move_id = %s ' \
	# 					'AND account_analytic_line.move_id = account_move_line.id',
	# 					(ref, move_id))
	# 	return True


account_invoice()