from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

from lxml import etree
import openerp.exceptions

from openerp import pooler

class account_invoice(osv.osv):
	_inherit = "account.invoice"
	_name = "account.invoice"

	# go from canceled state to draft state
	def action_cancel_draft_2(self, cr, uid, ids, *args):
		so_obj = self.pool.get('stock.move')
		va = self.browse(cr,uid,ids)[0]
		jut = va.journal_id.type
		ori = va.origin
		#import pdb;pdb.set_trace()
		if jut == 'sale' :
			sos = so_obj.search(cr,uid,[('origin','=',ori)])
			if sos != []:

				so = so_obj.browse(cr,uid,sos)[0]

				so_obj.write(cr,uid,so.id,{'state':'assigned'})
				
		self.write(cr, uid, ids, {'state':'draft'})
		wf_service = netsvc.LocalService("workflow")
		for inv_id in ids:
			wf_service.trg_delete(uid, 'account.invoice', inv_id, cr)
			wf_service.trg_create(uid, 'account.invoice', inv_id, cr)

		return True

	def action_cancel(self, cr, uid, ids, context=None):
		#import pdb;pdb.set_trace()
		if context is None:
			context = {}

		skrg = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
		jur = self.pool.get('account.journal')
		mv_obj = self.pool.get('stock.move')
		inv_line = self.pool.get('account.invoice.line')

		account_move_obj = self.pool.get('account.move')
		invoices = self.read(cr, uid, ids, ['move_id', 'payment_ids'])
		move_ids = [] # ones that we will need to remove
		for i in invoices:
			if i['move_id']:
				move_ids.append(i['move_id'][0])
			if i['payment_ids']:
				account_move_line_obj = self.pool.get('account.move.line')
				pay_ids = account_move_line_obj.browse(cr, uid, i['payment_ids'])
				for move_line in pay_ids:
					if move_line.reconcile_partial_id and move_line.reconcile_partial_id.line_partial_ids:
						raise osv.except_osv(_('Error!'), _('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))
		
		va = self.browse(cr,uid,ids)[0]
		ori = va.origin
		nm = va.name
		orinm = ori
		if ori != False and nm != False :
			orinm = ori+nm
		jut = va.journal_id.type
		loca = va.location_id2.warehouse_id.lot_stock_id.id

		so_obj = self.pool.get('stock.move')

		if jut == 'sale' :
			if ori :
				sos = so_obj.search(cr,uid,[('name','=',ori)])
				if sos != []:

					so = so_obj.browse(cr,uid,sos)[0]

					so_obj.write(cr,uid,so.id,{'state':'draft'},context=context)

		if jut == 'sale_refund' : # sales refund journal
			for x in va.invoice_line:
				prod = x.product_id.id
				prod_name = x.name
				uom_id = x.uom_id.id
				cf = x.uos_id.factor_inv
				uos_qty = x.quantity
				uos_id = x.uos_id.id

				mv_obj.create(cr, uid,{'product_id':prod,
									'name':prod_name,
									'origin':orinm,
									'location_id':9,#customer
									'location_dest_id':loca,
									'date_expacted':skrg,
									'product_uos':uos_id,
									'product_uos_qty':uos_qty/cf,														
									'product_qty':uos_qty,
									'product_uom':uom_id,										
									'state':'done',										
									})	
				#write qty supaya berbentik field(bukan field fungsi)
				inv_line.write(cr,uid,x.id,{'quantity3':uos_qty},context=context)

		mv = mv_obj.search(cr,uid,[('origin','=',ori)],context=context)
		if mv != [] :
			mv_id = mv_obj.browse(cr,uid,mv[0])
			#ubah stock move atas invoice ini ke draft
			if mv_id.id :
				mv_obj.write(cr,uid,mv_id.id,{'state':'draft'},context=context)

		for y in va.invoice_line:
			qty = y.quantity
			#write qty supaya berbentuk field(bukan field fungsi)
			inv_line.write(cr,uid,y.id,{'quantity3':qty},context=context)

		# First, set the invoices as cancelled and detach the move ids
		self.write(cr, uid, ids, {'state':'cancel', 'move_id':False})
		if move_ids:
			# second, invalidate the move(s)
			account_move_obj.button_cancel(cr, uid, move_ids, context=context)
			# delete the move this invoice was pointing to
			# Note that the corresponding move_lines and move_reconciles
			# will be automatically deleted too
			account_move_obj.unlink(cr, uid, move_ids, context=context)
		self._log_event(cr, uid, ids, -1.0, 'Cancel Invoice')
		return True

	def invoice_validate(self, cr, uid, ids, context=None):
		#import pdb;pdb.set_trace()
		jur = self.pool.get('account.journal')
		mv_obj = self.pool.get('stock.move')
		inv_line = self.pool.get('account.invoice.line')
		so_obj = self.pool.get('sale.order')

		skrg = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

		va = self.browse(cr,uid,ids)[0]
		jut = va.journal_id.type
		loca = va.location_id2.warehouse_id.lot_stock_id.id
		ori = va.origin or ''
		nama = va.name or ''


		if jut == 'sale' :
			if ori :
				sos = so_obj.search(cr,uid,[('name','=',ori)])
				if sos != []:

					so = so_obj.browse(cr,uid,sos)[0]

					so_obj.write(cr,uid,so.id,{'state':'done'},context=context)
		#import pdb;pdb.set_trace()
		if jut == 'sale_refund' : # sales refund journal
			for x in va.invoice_line:
				prod = x.product_id.id
				prod_name = x.name
				uom_id = x.uom_id.id
				cf = x.uos_id.factor_inv
				uos_qty = x.quantity
				uos_id = x.uos_id.id

				mv_obj.create(cr, uid,{'product_id':prod,
									'name':prod_name,
									'origin':ori+'-'+nama,
									'location_id':9,#customer
									'location_dest_id':loca,
									'date_expacted':skrg,
									'product_uos':uos_id,
									'product_uos_qty':uos_qty/cf,														
									'product_qty':uos_qty,#qty realnya disini krn sdh menjadi fieldfungsi
									'product_uom':uom_id,										
									'state':'done',										
									})	
				#write qty supaya berbentuk field(bukan field fungsi)
				inv_line.write(cr,uid,x.id,{'quantity3':uos_qty},context=context)

		for y in va.invoice_line:
			qty = y.quantity
			#write qty supaya berbentuk field(bukan field fungsi)
			inv_line.write(cr,uid,y.id,{'quantity3':qty},context=context)

		self.write(cr, uid, ids, {'state':'open'}, context=context)
		return True	

		#tambah nama gudang/cabang admin
	def _get_default_loc2(self, cr, uid, context=None):
		
		emplo = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		lo = self.pool.get('hr.employee').browse(cr,uid,emplo)[0]
		loc = lo.location_id.id

		return loc	

	def action_deliver(self,cr,uid,ids,context=None): 
		#import pdb;pdb.set_trace()
		mv_obj = self.pool.get('stock.move')

		inv = self.browse(cr,uid,ids)

		inv_ori = inv.origin

		mv = mv_obj.search(cr,uid,[('origin','=',inv_ori)],context=context)
		mv_id = mv_obj.browse(cr,uid,mv[0])

		if mv_id :
			mv_obj.write(cr,uid,mv_id,{'state':'done'},context=context)

		self.write(cr,uid,ids,{'state':'deliver'},context=context)

		return True

	def action_ttf(self,cr,uid,ids,context=None): 
		#import pdb;pdb.set_trace()
		return self.write(cr,uid,ids,{'note':'TTF'},context=context)	

	def action_not_ttf(self,cr,uid,ids,context=None): 
		#import pdb;pdb.set_trace()
		return self.write(cr,uid,ids,{'note':False},context=context)			

	def action_cn(self,cr,uid,ids,context=None): 
		#import pdb;pdb.set_trace()
		return self.write(cr,uid,ids,{'state':'cn_conf'},context=context)		

	def _get_nik(self, cr, uid, context=None):
		
		emplo = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		ni = self.pool.get('hr.employee').browse(cr,uid,emplo)[0]
		nik = ni.nik

		return nik

	_columns = {
		'warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
		'location_id' : fields.many2one('sale.shop','Location',readonly=True),
		'user_id2' :fields.many2one('res.users','User Admin',readonly=True),
		'location_id2' : fields.many2one('sale.shop','Location Admin',readonly=True),
		'credit' : fields.related('partner_id','credit',type="float",string="Total Receivable ",readonly="True"),
		'credit_limit' : fields.related('partner_id','credit_limit',type="float",string="Total Limit",readonly="True"),
		'partner_id2':fields.many2one('res.partner',string='Supplier',domain=[('supplier','=',True)],readonly=True, states={'draft':[('readonly',False)]}),
		'nik' :fields.char('Sales Code',readonly=True),

		'volume' : fields.float('Volume',readonly=True),
		'weight' : fields.float('Weight',readonly=True),

		'based_route_id': fields.related('partner_id','based_route_id',relation='master.based.route',type='many2one',string='Based Route',readonly=True, states={'draft':[('readonly',False)]}),

		'state': fields.selection([
			('draft','Draft'),
			('deliver','Deliver'),
			('proforma','Pro-forma'),
			('proforma2','Pro-forma'),
			('ttf','TTF'),
			('cn_conf','CN Confirmation'),
			('open','Open'),
			('paid','Paid'),
			('cancel','Cancelled'),
			],'Status', select=True, readonly=True, track_visibility='onchange',
			help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Invoice. \
			\n* The \'Pro-forma\' when invoice is in Pro-forma status,invoice does not have an invoice number. \
			\n* The \'Open\' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice. \
			\n* The \'Paid\' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
			\n* The \'Cancelled\' status is used when user cancel invoice.'),	
		'note' : fields.char('Note',readonly=True),	
		'button_hidden' : fields.boolean('Button Hidden'),	
		'date_invoice': fields.date('Confirm Date', readonly=True, states={'draft':[('readonly',False)]}, select=True, help="Keep empty to use the current date"),
		'date_so' : fields.date('Invoice Date', readonly=True, states={'draft':[('readonly',False)]}, select=True,),
		'description': fields.many2one('master.reason','Reason'),
		}


	_defaults ={
		'user_id2': lambda obj, cr, uid, context: uid,
		'location_id2' : _get_default_loc2,
		'location_id' : _get_default_loc2,
		'nik' :_get_nik,
		}		

	# go from canceled state to draft state
	def action_cancel_draft(self, cr, uid, ids, *args):
		st = self.browse(cr,uid,ids)[0].state

		if st != 'cancel':
			raise osv.except_osv(_('Error!'), _('Faktur tidak dapat dikembaliken ke status Draft'))
			return False

		self.write(cr, uid, ids, {'state':'draft'})
		wf_service = netsvc.LocalService("workflow")
		for inv_id in ids:
			wf_service.trg_delete(uid, 'account.invoice', inv_id, cr)
			wf_service.trg_create(uid, 'account.invoice', inv_id, cr)
		return True

	def action_move_create(self, cr, uid, ids, context=None):
		"""Creates invoice related analytics and financial move lines"""
		ait_obj = self.pool.get('account.invoice.tax')
		cur_obj = self.pool.get('res.currency')
		period_obj = self.pool.get('account.period')
		payment_term_obj = self.pool.get('account.payment.term')
		journal_obj = self.pool.get('account.journal')
		move_obj = self.pool.get('account.move')
		#import pdb;pdb.set_trace()
		if context is None:
			context = {}
		for inv in self.browse(cr, uid, ids, context=context):
			if not inv.journal_id.sequence_id:
				raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
			if not inv.invoice_line:
				raise osv.except_osv(_('No Invoice Lines!'), _('Please create some invoice lines.'))
			if inv.move_id:
				continue

			ctx = context.copy()
			ctx.update({'lang': inv.partner_id.lang})
			if not inv.date_invoice:
				self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
			company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
			# create the analytical lines
			# one move line per invoice line
			iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
			# check if taxes are all computed
			compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
			self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

			# I disabled the check_total feature
			group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
			group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
			if group_check_total and uid in [x.id for x in group_check_total.users]:
				if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0)):
					raise osv.except_osv(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

			if inv.payment_term:
				total_fixed = total_percent = 0
				for line in inv.payment_term.line_ids:
					if line.value == 'fixed':
						total_fixed += line.value_amount
					if line.value == 'procent':
						total_percent += line.value_amount
				total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
				if (total_fixed + total_percent) > 100:
					raise osv.except_osv(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

			# one move line per tax line
			iml += ait_obj.move_line_get(cr, uid, inv.id)

			entry_type = ''
			if inv.type in ('in_invoice', 'in_refund'):
				ref = inv.reference
				entry_type = 'journal_pur_voucher'
				if inv.type == 'in_refund':
					entry_type = 'cont_voucher'
			else:
				ref = self._convert_ref(cr, uid, inv.number)
				entry_type = 'journal_sale_vou'
				if inv.type == 'out_refund':
					entry_type = 'cont_voucher'

			diff_currency_p = inv.currency_id.id <> company_currency
			# create one move line for the total and possibly adjust the other lines amount
			total = 0
			total_currency = 0
			total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml, context=ctx)
			acc_id = inv.account_id.id

			name = inv['name'] or inv['supplier_invoice_number'] or '/'
			totlines = False
			if inv.payment_term:
				totlines = payment_term_obj.compute(cr,
						uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
			if totlines:
				res_amount_currency = total_currency
				i = 0
				ctx.update({'date': inv.date_invoice})
				for t in totlines:
					if inv.currency_id.id != company_currency:
						amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
					else:
						amount_currency = False

					# last line add the diff
					res_amount_currency -= amount_currency or 0
					i += 1
					if i == len(totlines):
						amount_currency += res_amount_currency

					iml.append({
						'type': 'dest',
						'name': name,
						'price': t[1],
						'account_id': acc_id,
						'date_maturity': t[0],
						'amount_currency': diff_currency_p \
								and amount_currency or False,
						'currency_id': diff_currency_p \
								and inv.currency_id.id or False,
						'ref': ref,
					})
			else:
				iml.append({
					'type': 'dest',
					'name': name,
					'price': total,
					'account_id': acc_id,
					'date_maturity': inv.date_due or False,
					'amount_currency': diff_currency_p \
							and total_currency or False,
					'currency_id': diff_currency_p \
							and inv.currency_id.id or False,
					'ref': ref
			})

			date = inv.date_invoice or time.strftime('%Y-%m-%d')

			part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

			line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)

			line = self.group_lines(cr, uid, iml, line, inv)

			journal_id = inv.journal_id.id
			journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
			if journal.centralisation:
				raise osv.except_osv(_('User Error!'),
						_('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

			line = self.finalize_invoice_move_lines(cr, uid, inv, line)
			#import pdb;pdb.set_trace()
			move = {
				'ref': inv.reference and inv.reference or inv.name,
				'line_id': line,
				'journal_id': journal_id,
				'date': date,
				'narration': inv.comment,
				'company_id': inv.company_id.id,
				'location_id' : inv.location_id.id
			}
			period_id = inv.period_id and inv.period_id.id or False
			ctx.update(company_id=inv.company_id.id,
					   account_period_prefer_normal=True)
			if not period_id:
				period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
				period_id = period_ids and period_ids[0] or False
			if period_id:
				move['period_id'] = period_id
				for i in line:
					i[2]['period_id'] = period_id

			ctx.update(invoice=inv)
			move_id = move_obj.create(cr, uid, move, context=ctx)
			new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
			# make the invoice point to that move
			self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
			# Pass invoice in context in method post: used if you want to get the same
			# account move reference when creating the same invoice after a cancelled one:
			move_obj.post(cr, uid, [move_id], context=ctx)
		self._log_event(cr, uid, ids)
		return True

class stock_location(osv.osv):
	_inherit = "stock.location"
	_name = "stock.location"

	_columns = {
		'code': fields.char('Code', size=13,required=True),

		}

class sale_shop(osv.osv):
	_inherit = "sale.shop"
	_name = "sale.shop"

	_columns = {
		'code': fields.char('Code', size=13,required=True),

		}

class account_invoice_line(osv.osv):
	_inherit = "account.invoice.line"
	_name = "account.invoice.line"

	def _get_uom_id(self, cr, uid, *args):
		try:
			proxy = self.pool.get('ir.model.data')
			result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
			return result[1]
		except Exception, ex:
			return False  

	def _get_tot_qty(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		#import pdb;pdb.set_trace()
		for line in self.browse(cr, uid, ids):
			t_qty = round((line.qty*line.uos_id.factor_inv) + (line.quantity2),3)
			res[line.id] = t_qty
		return res

	def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		#import pdb;pdb.set_trace()
		for line in self.browse(cr, uid, ids):
			#price = line.price_unit * (1-(line.discount or 0.0)/100.0)
			price = round(line.price_unit *line.quantity,3)
			# taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
			taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
			#res[line.id] = taxes['total']
			res[line.id] = price
			# if line.invoice_id:
			# 	cur = line.invoice_id.currency_id
			# 	res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
		return res

	_columns = {
		'quantity2': fields.float('Small Qty', digits_compute= dp.get_precision('Product Unit of Measure')),
		'uom_id' : fields.many2one('product.uom', 'Small UoM', ondelete='set null', select=True,required=True),
		'disc_tot': fields.float('Disc Total'),
		'price_subtotal': fields.function(_amount_line, string='Amount', type="float",
			digits_compute= dp.get_precision('Account'), store=True),
		'qty_func': fields.function(_get_tot_qty,string='Qty Tot'),
		'qty': fields.float('Qty', digits_compute= dp.get_precision('Product Unit of Measure')),
		'quantity': fields.function(_get_tot_qty,string='Quantity',type="float", digits_compute= dp.get_precision('Product Unit of Measure'), required=True),
		'price_unit2': fields.float('Price Unit 2'),
		'quantity3' : fields.float('Quantity PO'),

	}

	_defaults = {
		'uom_id' : _get_uom_id,
		} 

class account_invoice_refund(osv.osv_memory):
	_inherit = "account.invoice.refund"
	_name = "account.invoice.refund"

	_columns = {
	   #'description': fields.char('Reason', size=128, required=True),
		'description': fields.many2one('master.reason','Reason', required=True),
	}
	def _get_reason(self, cr, uid, context=None):
		res={}
		if context is None:
			context = {}
		elif context.get('active_id'):
			res = self.pool.get('account.invoice').browse(cr,uid,context.get('active_id',False)).description.id 
		return res

	_defaults = {
		'description': _get_reason,
	}

	
	def compute_refund(self, cr, uid, ids, mode='refund', context=None):

		inv_obj = self.pool.get('account.invoice')
		reconcile_obj = self.pool.get('account.move.reconcile')
		account_m_line_obj = self.pool.get('account.move.line')
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		wf_service = netsvc.LocalService('workflow')
		inv_tax_obj = self.pool.get('account.invoice.tax')
		inv_line_obj = self.pool.get('account.invoice.line')
		res_users_obj = self.pool.get('res.users')
		if context is None:
			context = {}

		for form in self.browse(cr, uid, ids, context=context):
			created_inv = []
			date = False
			period = False
			description = False
			numb=False
			company = res_users_obj.browse(cr, uid, uid, context=context).company_id
			journal_id = form.journal_id.id
			for inv in inv_obj.browse(cr, uid, context.get('active_ids'), context=context):
				if inv.state in ['draft', 'proforma2', 'cancel']:
					raise osv.except_osv(_('Error!'), _('Cannot %s draft/proforma/cancel invoice.') % (mode))
				if inv.reconciled and mode in ('cancel', 'modify'):
					raise osv.except_osv(_('Error!'), _('Cannot %s invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice.') % (mode))
				if form.period.id:
					period = form.period.id
				else:
					period = inv.period_id and inv.period_id.id or False

				if not journal_id:
					journal_id = inv.journal_id.id

				if form.date:
					date = form.date
					if not form.period.id:
							cr.execute("select name from ir_model_fields \
											where model = 'account.period' \
											and name = 'company_id'")
							result_query = cr.fetchone()
							if result_query:
								cr.execute("""select p.id from account_fiscalyear y, account_period p where y.id=p.fiscalyear_id \
									and date(%s) between p.date_start AND p.date_stop and y.company_id = %s limit 1""", (date, company.id,))
							else:
								cr.execute("""SELECT id
										from account_period where date(%s)
										between date_start AND  date_stop  \
										limit 1 """, (date,))
							res = cr.fetchone()
							if res:
								period = res[0]
				else:
					date = inv.date_invoice
				if inv.origin:
					numb = inv.origin
					description = inv.origin

				if not period:
					raise osv.except_osv(_('Insufficient Data!'), \
											_('No period found on the invoice.'))

				refund_id = inv_obj.refund(cr, uid, [inv.id], date, period, description, journal_id, context=context)
				refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
				inv_obj.write(cr, uid, [refund.id], {'date_due': date,
												'check_total': inv.check_total})
				inv_obj.button_compute(cr, uid, refund_id)
				#import pdb;pdb.set_trace()
				created_inv.append(refund_id[0])
				if mode in ('cancel', 'modify'):
					movelines = inv.move_id.line_id
					to_reconcile_ids = {}
					for line in movelines:
						if line.account_id.id == inv.account_id.id:
							to_reconcile_ids[line.account_id.id] = [line.id]
						if line.reconcile_id:
							line.reconcile_id.unlink()
					wf_service.trg_validate(uid, 'account.invoice', \
										refund.id, 'invoice_open', cr)
					refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
					for tmpline in  refund.move_id.line_id:
						if tmpline.account_id.id == inv.account_id.id:
							to_reconcile_ids[tmpline.account_id.id].append(tmpline.id)
					for account in to_reconcile_ids:
						account_m_line_obj.reconcile(cr, uid, to_reconcile_ids[account],
										writeoff_period_id=period,
										writeoff_journal_id = inv.journal_id.id,
										writeoff_acc_id=inv.account_id.id
										)

					if mode == 'modify':
						invoice = inv_obj.read(cr, uid, [inv.id],
									['name', 'type', 'number', 'reference',
									'comment', 'date_due', 'partner_id',
									'partner_insite', 'partner_contact',
									'partner_ref', 'payment_term', 'account_id',
									'currency_id', 'invoice_line', 'tax_line',
									'journal_id', 'period_id'], context=context)
						invoice = invoice[0]
						del invoice['id']
						invoice_lines = inv_line_obj.browse(cr, uid, invoice['invoice_line'], context=context)
						invoice_lines = inv_obj._refund_cleanup_lines(cr, uid, invoice_lines, context=context)
						tax_lines = inv_tax_obj.browse(cr, uid, invoice['tax_line'], context=context)
						tax_lines = inv_obj._refund_cleanup_lines(cr, uid, tax_lines, context=context)
						invoice.update({
							'type': inv.type,
							'date_invoice': date,
							'state': 'draft',
							'number': False,
							'invoice_line': invoice_lines,
							'tax_line': tax_lines,
							'period_id': period,
							'name': description,						
						})
						for field in ('partner_id', 'account_id', 'currency_id',
										 'payment_term', 'journal_id'):
								invoice[field] = invoice[field] and invoice[field][0]
						inv_id = inv_obj.create(cr, uid, invoice, {})
						if inv.payment_term.id:
							data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv.payment_term.id, date)
							if 'value' in data and data['value']:
								inv_obj.write(cr, uid, [inv_id], data['value'])
						created_inv.append(inv_id)
			xml_id = (inv.type == 'out_refund') and 'action_invoice_tree1' or \
					 (inv.type == 'in_refund') and 'action_invoice_tree2' or \
					 (inv.type == 'out_invoice') and 'action_invoice_tree3' or \
					 (inv.type == 'in_invoice') and 'action_invoice_tree4'
			result = mod_obj.get_object_reference(cr, uid, 'account', xml_id)
			id = result and result[1] or False
			result = act_obj.read(cr, uid, id, context=context)
			invoice_domain = eval(result['domain'])
			invoice_domain.append(('id', 'in', created_inv))
			result['domain'] = invoice_domain

			#inv_obj.write(cr,uid,refund.id,{'origin':numb},context=context)

			return result

	def invoice_refund(self, cr, uid, ids, context=None):
		#import pdb;pdb.set_trace()
		idd = context['active_id']
		data_refund = self.read(cr, uid, ids, ['filter_refund'],context=context)[0]['filter_refund']
		gr = self.pool.get('account.invoice')
		sr = gr.search(cr,uid,[('id','=',idd)])
		st = gr.browse(cr,uid,sr)[0].state
		nt = gr.browse(cr,uid,sr)[0].note

		if st not in ['open','paid'] or nt == 'CN Conf' :
			raise osv.except_osv(_('Error!'), _('CN Confirmation/Refund hanya dapat dilakukan jika status faktur dalam kondisi Open dan belum pernah CN Confirmation'))
			return False
		gr.write(cr,uid,idd,{'note':'CN Conf'})				

		return self.compute_refund(cr, uid, ids, data_refund, context=context)
	

class master_reason(osv.osv):
	_name = "master.reason"

	_columns = {
		'name' : fields.char('Reason',required=True),
		}    

class account_move(osv.osv):
	_inherit = "account.move"
	_name = "account.move"

	_columns = {
		'location_id': fields.many2one('sale.shop','Location',states={'posted': [('readonly', True)]}),
		#'xxx': fields.function(_get_location),
		}