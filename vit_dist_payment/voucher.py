from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from openerp import netsvc


_logger = logging.getLogger(__name__)

class voucher(osv.osv):
	_name 		= "vit_dist_payment.voucher"
	_order = 'name desc'

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
		#'received_from' : fields.char('Received From'),
		'received_from' : fields.many2one('res.users','Received From',required=True),
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

class account_voucher(osv.osv):
	_inherit = "account.voucher"
	_name = "account.voucher"

	def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
		
		if context is None:
			context = {}
		ctx = context.copy()
		ctx.update({'date': date})
		#read the voucher rate with the right date in the context
		currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
		voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
		ctx.update({
			'voucher_special_currency': payment_rate_currency_id,
			'voucher_special_currency_rate': rate * voucher_rate})
		res1 = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
		vals = self.onchange_rate(cr, uid, ids, rate, amount, currency_id, payment_rate_currency_id, company_id, context=ctx)
		for key in vals.keys():
			res1[key].update(vals[key])

		#import pdb;pdb.set_trace()
		total_hutang = context['default_amount']
		bayar = amount

		selisih = bayar-total_hutang
		res2 = {
			'value' : {
				'writeoff_amount' : selisih
						}
				}

		rs = dict(res2['value'].items()+res1['value'].items())
		res = {'value':rs}

		return res

	def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
		if context is None:
			context = {}
		if not journal_id:
			return False
		journal_pool = self.pool.get('account.journal')
		journal = journal_pool.browse(cr, uid, journal_id, context=context)
		account_id = journal.default_credit_account_id or journal.default_debit_account_id
		tax_id = False
		if account_id and account_id.tax_ids:
			tax_id = account_id.tax_ids[0].id

		vals = {'value':{} }
		if ttype in ('sale', 'purchase'):
			vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
			vals['value'].update({'tax_id':tax_id,'amount': amount})
		currency_id = False
		if journal.currency:
			currency_id = journal.currency.id
		else:
			currency_id = journal.company_id.currency_id.id
		vals['value'].update({'currency_id': currency_id})
		#in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal 
		#without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
		#this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
		
		if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
			vals['value']['amount'] = 0
			amount = 0
		res1 = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)

		total_hutang = context['default_amount']
		bayar = amount

		selisih = bayar-total_hutang
		res2 = {
			'value' : {
				'writeoff_amount' : selisih
						}
				}
		#import pdb;pdb.set_trace()
		rs = dict(res1['value'].items()+res2['value'].items())
		res = {'value':rs}

		for key in res.keys():
			vals[key].update(res[key])
		return res

	def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
		#import pdb;pdb.set_trace()
		if not ids: return {}
		currency_obj = self.pool.get('res.currency')
		res = {}
		debit = credit = 0.0
		for voucher in self.browse(cr, uid, ids, context=context):
			sign = voucher.type == 'payment' and -1 or 1
			for l in voucher.line_dr_ids:
				debit += l.amount
			for l in voucher.line_cr_ids:
				credit += l.amount
			currency = voucher.currency_id or voucher.company_id.currency_id
			res[voucher.id] =  currency_obj.round(cr, uid, currency, voucher.amount - sign * (credit - debit))
		return res

	def _compute_writeoff_amount1(self, cr, uid, line_dr_ids, line_cr_ids, amount, type):
		
		debit = credit = 0.0
		sign = type == 'payment' and -1 or 1
		for l in line_dr_ids:
			debit += l['amount']
		for l in line_cr_ids:
			credit += l['amount']
		
		val = amount
		return val

	def _compute_writeoff_amount2(self, cr, uid, line_dr_ids, line_cr_ids, amount, type):
		
		debit = credit = 0.0
		sign = type == 'payment' and -1 or 1
		for l in line_dr_ids:
			debit += l['amount']
		for l in line_cr_ids:
			credit += l['amount']
		
		val = credit
		return val

	def _compute_writeoff_amount3(self, cr, uid, line_dr_ids, line_cr_ids, amount, type):
		
		debit = credit = 0.0
		sign = type == 'payment' and -1 or 1
		for l in line_dr_ids:
			debit += l['amount']
		for l in line_cr_ids:
			credit += l['amount']
		
		val =debit
		return val		

	def onchange_line_ids(self, cr, uid, ids, line_dr_ids, line_cr_ids, amount, voucher_currency, type, context=None):
		#import pdb;pdb.set_trace()
		context = context or {}
		if not line_dr_ids and not line_cr_ids:
			return {'value':{'writeoff_amount': 0.0}}
		line_osv = self.pool.get("account.voucher.line")
		line_dr_ids = resolve_o2m_operations(cr, uid, line_osv, line_dr_ids, ['amount'], context)
		line_cr_ids = resolve_o2m_operations(cr, uid, line_osv, line_cr_ids, ['amount'], context)
		#compute the field is_multi_currency that is used to hide/display options linked to secondary currency on the voucher
		is_multi_currency = False
		#loop on the voucher lines to see if one of these has a secondary currency. If yes, we need to see the options
		for voucher_line in line_dr_ids+line_cr_ids:
			line_id = voucher_line.get('id') and self.pool.get('account.voucher.line').browse(cr, uid, voucher_line['id'], context=context).move_line_id.id or voucher_line.get('move_line_id')
			if line_id and self.pool.get('account.move.line').browse(cr, uid, line_id, context=context).currency_id:
				is_multi_currency = True
				break
		return {'value': {
			'writeoff_amount': self._compute_writeoff_amount(cr, uid, line_dr_ids, line_cr_ids, amount, type), 
			#'w_amount': self._compute_writeoff_amount1(cr, uid, line_dr_ids, line_cr_ids, amount, type), 
			'w_amount2': self._compute_writeoff_amount2(cr, uid, line_dr_ids, line_cr_ids, amount, type), 
			'w_amount3': self._compute_writeoff_amount3(cr, uid, line_dr_ids, line_cr_ids, amount, type), 
			'is_multi_currency': is_multi_currency}}


	_columns = {
		'writeoff_ids' : fields.one2many('writeoff','voucher_id','Write Off List'),
		'writeoff_amount': fields.float('Difference Amount',readonly=True, help="Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines."),
		'w_amount': fields.float('Diff Amount',),
		#'w_amount': fields.function(_get_writeoff_amount, string='Diff Amount', type='float'),
		#'w_amount2': fields.function(_get_writeoff_amount, string='Diff Amount 2', type='float'),
		#'w_amount3': fields.function(_get_writeoff_amount, string='Diff Amount 3', type='float'),
	}

	def button_proforma_voucher(self, cr, uid, ids, context=None):
		
		context = context or {}
		wf_service = netsvc.LocalService("workflow")

		inv_id = context['invoice_id']
		#def_amount = context['default_amount']

		def_amount = self.pool.get('account.voucher').browse(cr,uid,ids[0]).amount
		st = "'open'"
		# inv_obj = self.pool.get('account.invoice')
		# inv_src = inv_obj.search(cr,uid,[('id','=',inv_id)])[0]
		# inv_br = inv_obj.browse(cr,uid,inv_src)

		#cr.execute('select lph_id from lph_invoice where invoice_id ='+str(inv_id))
		cr.execute('select lph_id from lph_invoice lphi '\
			'left join vit_dist_payment_lph vlph on vlph.id = lphi.lph_id '\
			'where lphi.invoice_id ='+str(inv_id)+' '\
			'and vlph.state = '+st)		
		fet = cr.fetchone()
		id_lph = fet[0]

		lph_obj = self.pool.get('vit_dist_payment.lph')
		lph_src = lph_obj.search(cr,uid,[('id','=',id_lph)])
		lph_brw = lph_obj.browse(cr,uid,lph_src)[0]
		#import pdb;pdb.set_trace()
		if lph_brw.voucher_id.id :
			v_total = lph_brw.voucher_id.total
		else :
			v_total = 0.0
		
		t_paid = lph_brw.total_paid
		acum_paid = t_paid + def_amount
		recom_paid = v_total - t_paid

		if acum_paid > v_total :
			raise osv.except_osv(_('Error!!'), _('Total pembayaran atas faktur ini:\n \
			 Rp. %s \n \
			 sudah melewati nominal voucher: \n \
			 Rp. %s. \n \
			 Nominal yang bisa di input max: \n \
			 Rp. %s !') % (acum_paid,v_total,recom_paid))					

		for vid in ids:
			wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
		return {'type': 'ir.actions.act_window_close'}

	# def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
	# 	'''
	# 	Set a dict to be use to create the writeoff move line.

	# 	:param voucher_id: Id of voucher what we are creating account_move.
	# 	:param line_total: Amount remaining to be allocated on lines.
	# 	:param move_id: Id of account move where this line will be added.
	# 	:param name: Description of account move line.
	# 	:param company_currency: id of currency of the company to which the voucher belong
	# 	:param current_currency: id of currency of the voucher
	# 	:return: mapping between fieldname and value of account move line to create
	# 	:rtype: dict
	# 	'''
	# 	currency_obj = self.pool.get('res.currency')
	# 	move_line = {}

	# 	voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
	# 	current_currency_obj = voucher.currency_id or voucher.journal_id.company_id.currency_id

	# 	if not currency_obj.is_zero(cr, uid, current_currency_obj, line_total):
	# 		import pdb;pdb.set_trace()
	# 		diff = line_total
	# 		account_id = False
	# 		write_off_name = ''
	# 		if voucher.payment_option == 'with_writeoff':
	# 			account_id = voucher.writeoff_acc_id.id
	# 			write_off_name = voucher.comment
	# 		elif voucher.type in ('sale', 'receipt'):
	# 			account_id = voucher.partner_id.property_account_receivable.id
	# 		else:
	# 			account_id = voucher.partner_id.property_account_payable.id
	# 		sign = voucher.type == 'payment' and -1 or 1


	# 		for ml in voucher.writeoff_ids :
	# 			move_line = {
	# 				'name': ml.name or name, #write_off_name or name,
	# 				'account_id': ml.account_id.id,#account_id,
	# 				'move_id': move_id,
	# 				'partner_id': voucher.partner_id.id,
	# 				'date': voucher.date,
	# 				'credit': diff > 0 and diff or 0.0,
	# 				'debit': diff < 0 and -diff or 0.0,
	# 				'amount_currency': company_currency <> current_currency and (sign * -1 * voucher.writeoff_amount) or False,
	# 				'currency_id': company_currency <> current_currency and current_currency or False,
	# 				'analytic_account_id': voucher.analytic_id and voucher.analytic_id.id or False,
	# 			}

	# 	return move_line		

class writeoff(osv.osv):
	_name = 'writeoff'

	_columns = {
		'voucher_id' : fields.many2one('account.voucher','Voucher ID'),
		'name' : fields.char('Description',required=True),
		'amount' : fields.float('Amount',required=True),
		'account_id' : fields.many2one('account.account','Counterpart Account',domain="[('type','=','other')]",required=True),
	}

writeoff()

def resolve_o2m_operations(cr, uid, target_osv, operations, fields, context):
	results = []
	for operation in operations:
		result = None
		if not isinstance(operation, (list, tuple)):
			result = target_osv.read(cr, uid, operation, fields, context=context)
		elif operation[0] == 0:
			# may be necessary to check if all the fields are here and get the default values?
			result = operation[2]
		elif operation[0] == 1:
			result = target_osv.read(cr, uid, operation[1], fields, context=context)
			if not result: result = {}
			result.update(operation[2])
		elif operation[0] == 4:
			result = target_osv.read(cr, uid, operation[1], fields, context=context)
		if result != None:
			results.append(result)
	return results