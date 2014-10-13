from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc


class account_invoice(osv.osv):
	_inherit = "account.invoice"


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
		loca = va.location_id2.id

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
		loca = va.location_id2.id
		ori = va.origin

		if jut == 'sale' :
			if ori :
				sos = so_obj.search(cr,uid,[('name','=',ori)])
				so = so_obj.browse(cr,uid,sos)[0]

				so_obj.write(cr,uid,so.id,{'state':'done'},context=context)

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
									'origin':va.name,
									'location_id':9,#customer
									'location_dest_id':loca,
									'date_expacted':skrg,
									'product_uos':uos_id,
									'product_uos_qty':uos_qty/cf,														
									'product_qty':uos_qty,#qty reealnya disini krn sdh menjadi fieldfungsi
									'product_uom':uom_id,										
									'state':'done',										
									})	
				#write qty supaya berbentik field(bukan field fungsi)
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
		return self.write(cr,uid,ids,{'state':'ttf'},context=context)		

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
		'location_id' : fields.many2one('stock.location','Location',readonly=True),
		'user_id2' :fields.many2one('res.users','User Admin',readonly=True),
		'location_id2' : fields.many2one('stock.location','Location Admin',readonly=True),
		'credit' : fields.related('partner_id','credit',type="float",string="Total Receivable ",readonly="True"),
		'credit_limit' : fields.related('partner_id','credit_limit',type="float",string="Total Limit",readonly="True"),

		'nik' :fields.char('Sales Code',readonly=True),

		'volume' : fields.float('Volume',readonly=True),
		'weight' : fields.float('Weight',readonly=True),

		'based_route_id': fields.related('partner_id','based_route_id',relation='master.based.route',type='many2one',string='Based Route'),

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

class stock_location(osv.osv):
	_inherit = "stock.location"

	_columns = {
		'code': fields.char('Kode', size=13,required=True),

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
				if form.description:
					description = form.description.name
				else:
					description = inv.origin
				if inv.origin:
					numb = 	inv.origin

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
							'origin': numb,
							'comment': numb
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

			inv_obj.write(cr,uid,refund.id,{'origin':numb},context=context)

			return result

	def invoice_refund(self, cr, uid, ids, context=None):
		#import pdb;pdb.set_trace()
		idd = context['active_id']
		data_refund = self.read(cr, uid, ids, ['filter_refund'],context=context)[0]['filter_refund']
		gr = self.pool.get('account.invoice')
		sr = gr.search(cr,uid,[('id','=',idd)])
		st = gr.browse(cr,uid,sr)[0].state
		nt = gr.browse(cr,uid,sr)[0].note

		if st not in ['open','paid'] or nt == 'CN Confirmation' :
			raise osv.except_osv(_('Error!'), _('CN Confirmation/Refund hanya dapat dilakukan jika status faktur dalam kondisi Open dan belum pernah CN Confirmation'))
			return False
		gr.write(cr,uid,idd,{'note':'CN Confirmation'})				

		return self.compute_refund(cr, uid, ids, data_refund, context=context)
	

class master_reason(osv.osv):
	_name = "master.reason"

	_columns = {
		'name' : fields.char('Reason',required=True),
		}    
