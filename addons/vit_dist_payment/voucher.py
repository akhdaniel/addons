from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from openerp.tools import float_compare
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
		if selisih > 0.00 :
			selisih = 0.00

		res2 = {
			'value' : {
				'w_amount' : selisih
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
		res_acc = res1['value']['account_id']

		total_hutang = context['default_amount']
		bayar = amount

		selisih = bayar-total_hutang
		if selisih > 0.00 :
			selisih = 0.00
		res2 = {
			'value' : {
				'w_amount' : selisih,
				'account_id' : res_acc
						}
				}
		#import pdb;pdb.set_trace()
		rs = dict(res1['value'].items()+res2['value'].items())
		res = {'value':rs}

		for key in res.keys():
			vals[key].update(res[key])

		return res


	_columns = {
		'writeoff_ids' : fields.one2many('writeoff','voucher_id','Write Off List'),
		'w_amount': fields.float('Difference Amount',),

	}


	def writeoff_move_line_get2(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
		'''
		Set a dict to be use to create the writeoff move line.

		:param voucher_id: Id of voucher what we are creating account_move.
		:param line_total: Amount remaining to be allocated on lines.
		:param move_id: Id of account move where this line will be added.
		:param name: Description of account move line.
		:param company_currency: id of currency of the company to which the voucher belong
		:param current_currency: id of currency of the voucher
		:return: mapping between fieldname and value of account move line to create
		:rtype: dict
		'''
		currency_obj = self.pool.get('res.currency')
		move_line = {}

		voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
		current_currency_obj = voucher.currency_id or voucher.journal_id.company_id.currency_id
		#import pdb;pdb.set_trace()
		#if currency_obj.is_zero(cr, uid, current_currency_obj, line_total):

			# for x in voucher.writeoff_ids:

			# 	move_l = {
			# 		'name': x.name,
			# 		'account_id': x.account_id.id,
			# 		'move_id': move_id,
			# 		'partner_id': voucher.partner_id.id,
			# 		'date': voucher.date,
			# 		'credit': x.amount > 0 and x.amount or 0.0,
			# 		'debit': x.amount < 0 and -x.amount or 0.0,
			# 		'amount_currency': company_currency <> current_currency and (sign * -1 * voucher.writeoff_amount) or False,
			# 		'currency_id': company_currency <> current_currency and current_currency or False,
			# 		'analytic_account_id': voucher.analytic_id and voucher.analytic_id.id or False,
			# 	}

			# 	move_line.update({x.id:move_l})
		move_line =voucher.writeoff_ids	
		return move_line

	def action_move_line_create(self, cr, uid, ids, context=None):
		'''
		Confirm the vouchers given in ids and create the journal entries for each of them
		'''
		if context is None:
			context = {}
		move_pool = self.pool.get('account.move')
		move_line_pool = self.pool.get('account.move.line')
		for voucher in self.browse(cr, uid, ids, context=context):
			if voucher.move_id:
				continue
			company_currency = self._get_company_currency(cr, uid, voucher.id, context)
			current_currency = self._get_current_currency(cr, uid, voucher.id, context)
			# we select the context to use accordingly if it's a multicurrency case or not
			context = self._sel_context(cr, uid, voucher.id, context)
			# But for the operations made by _convert_amount, we always need to give the date in the context
			ctx = context.copy()
			ctx.update({'date': voucher.date})
			# Create the account move record.
			move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
			# Get the name of the account_move just created
			name = move_pool.browse(cr, uid, move_id, context=context).name
			# Create the first line of the voucher
			move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, context), context)
			move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
			line_total = move_line_brw.debit - move_line_brw.credit
			rec_list_ids = []
			if voucher.type == 'sale':
				line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
			elif voucher.type == 'purchase':
				line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
			# Create one move line per voucher line where amount is not 0.0
			line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

			# Create the writeoff line if needed
			ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)

			ml_writeoff2 = self.writeoff_move_line_get2(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)	
			#import pdb;pdb.set_trace()
			if ml_writeoff2 == []:
				if ml_writeoff:
					move_line_pool.create(cr, uid, ml_writeoff, context)
			
			if ml_writeoff2 != []:
				m_line={}
				wo_amt = 0.0
				for x in ml_writeoff2:
					wo_amt += x.amount
					m_line = {
						'name':x.name,
						'credit': x.amount < 0 and -x.amount or 0.0,
						'debit': x.amount > 0 and x.amount or 0.0,
						'account_id':x.account_id.id,
						'date':ctx['date'],
						'journal_id':context['journal_id'],
						'period_id':context['period_id'],
						'move_id':move_id,
						'partner_id':move_line_brw.partner_id.id,
					}
					move_line_pool.create(cr, uid, m_line, context)	

				# We automatically reconcile the account move lines.
				reconcile = False
				# import pdb;pdb.set_trace()				
				# for rec_ids in rec_list_ids:
				# 	for rr in rec_ids:
				# 		r_id = self.pool.get('account.move.line').browse(cr,uid,rr)
				# 		r_debit = r_id.debit
				# 		if r_debit != 0.00:
				# 			new_debit = r_debit- wo_amt
				# 			self.pool.get('account.move.line').write(cr,uid,rr,{'debit':new_debit})
				# 	if len(rec_ids) >= 2:
				# 		reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)

			# We post the voucher.
			self.write(cr, uid, [voucher.id], {
				'move_id': move_id,
				'state': 'posted',
				'number': name,
			})
			if voucher.journal_id.entry_posted:
				move_pool.post(cr, uid, [move_id], context={})
			# We automatically reconcile the account move lines.
			reconcile = False

			for rec_ids in rec_list_ids:
				if len(rec_ids) >= 2:
					reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
		
		return True

	def button_proforma_voucher(self, cr, uid, ids, context=None):
		
		context = context or {}

		inv_id = context['invoice_id']
		def_amt = context['default_amount']

		vo_obj = self.pool.get('account.voucher')
		def_amount = vo_obj.browse(cr,uid,ids[0]).amount
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
		
		if not fet :
			raise osv.except_osv(_('Error!!'), _('Pembayaran harus dilakukan melalui menu LPH Payment!'))
		id_lph = fet[0]

		lph_obj = self.pool.get('vit_dist_payment.lph')
		lph_src = lph_obj.search(cr,uid,[('id','=',id_lph)])
		lph_brw = lph_obj.browse(cr,uid,lph_src)[0]
		
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
			 Sudah melewati nominal voucher: \n \
			 Rp. %s. \n \
			 Nominal yang bisa di input max: \n \
			 Rp. %s !') % (acum_paid,v_total,recom_paid))

		#jika write off pastikan amount yg di bayar+jml amount writeoff = total hutang
		v_id = vo_obj.browse(cr,uid,ids[0])
		if v_id.writeoff_ids != []:
			writeoff_total = 0.00
			for x in v_id.writeoff_ids:
				am = x.amount
				writeoff_total += am
			difference = def_amt-def_amount
			if difference != writeoff_total :
				return {'type': 'ir.actions.act_window_close'}
				raise osv.except_osv(_('Error!!'), _('Different amount tidak sama dengan total write off!'))

			elif difference == writeoff_total :
				mv_ac = self.browse(cr,uid,ids)[0].line_cr_ids
				for amo in mv_ac:
					if amo.amount != 0.00:
						balance = amo.amount_unreconciled

				# for wo in v_id.writeoff_ids:
				# 	nm = wo.name
				# 	rp = wo.amount
				# 	acc = wo.account_id.id
			#import pdb;pdb.set_trace()
			cr.execute('select id from account_voucher_line where '\
				'amount_unreconciled = '+str(def_amt)+' '\
				'and reconcile = False  '\
				'and voucher_id='+str(v_id.id)+'')	
			hsl = cr.fetchone()
			hsl_line = hsl[0]
			self.pool.get('account.voucher.line').write(cr,uid,hsl_line,{'amount':def_amt,'reconcile':True},context=context)

					
					
		elif v_id.writeoff_ids == [] :
			writeoff_total = 0.00
		#self.write(cr,uid,ids[0],{'amount':writeoff_total+def_amount},context=context)

		wf_service = netsvc.LocalService("workflow")
		for vid in ids:
			wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
			return {'type': 'ir.actions.act_window_close'}
	

class writeoff(osv.osv):
	_name = 'writeoff'

	_columns = {
		'voucher_id' : fields.many2one('account.voucher','Voucher ID'),
		'name' : fields.char('Description',required=True),
		'amount' : fields.float('Amount',required=True),
		'account_id' : fields.many2one('account.account','Counterpart Account',domain="[('type','=','other')]",required=True),
	}

writeoff()
