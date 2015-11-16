from osv import osv,fields
from openerp.tools.translate import _
import datetime 
import openerp.addons.decimal_precision as dp

class sc_report_wizard(osv.TransientModel): 
	_name = 'vit_sc.report_wizard' 

	_columns = {
		'date_start' : fields.date('Date Start',required=True),
		'date_end'   : fields.date('Date End',required=True),
		'partner_id' : fields.many2one('res.partner',string='Supplier',required=True),
	}

	_defaults = {
		'date_start'  	: lambda *a : (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),	
		'date_end'		: fields.date.context_today,	
	}

	def _get_total_debit_credit_supplier(self, cr, uid, ids, l_state, m_state, date, partner_id, type, context):
		cr.execute('SELECT '\
                'sum(l.debit) as debit, '\
                'sum(l.credit) as credit '\
            'FROM '\
                'account_move_line l '\
                'left join account_account a on (l.account_id = a.id) '\
                'left join account_move am on (am.id=l.move_id) '\

            'WHERE l.state != %s '\
	            'AND am.state = %s '\
	            'AND am.date < %s '\
	            'AND l.partner_id = %s '\
	            'AND (l.debit != 0 or l.credit != 0) '\
	            'AND a.type = %s',(l_state, m_state, date, partner_id, type))		
		
		debit = 0
		credit = 0
		output = cr.fetchone()
		if output[0] != None :
			debit = output[0]
		if output[1] != None :
			credit = output[1]
		opening_balance = (debit,credit)

		return opening_balance


	def hasil(self, cr, uid, desc, report, view_id, domain, context):
		return {
			'name' : _(desc),
			'view_type': 'form',
			'view_mode': 'form',			
			'res_model': 'vit.supplier',
			'res_id': report,
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			#'domain' : domain,
			#'context': context,
			'nodestroy': False,
			}


	def fill_table(self, cr, uid, ids, context=None):

		#UID diganti dengan id administrator agar full access id = 1

		wizard  = self.browse(cr, uid, ids[0], context=context) 
		
		sql = "delete from vit_supplier where user_id = %s" % (uid)
		
		cr.execute(sql)

		l_state = 'draft'	
		am_state = 'posted'	
		a_type = 'payable'

		supplier_card_id = self.pool.get('vit.supplier').create(cr,1,{'partner_id':wizard.partner_id.id,
																		'date_start': wizard.date_start,
																		'date_end': wizard.date_end,
																		'user_id':uid})

		#cari opening balance_get_total_balance
		opening = self._get_total_debit_credit_supplier(cr, 1, ids, l_state, am_state, wizard.date_start, wizard.partner_id.id, a_type, context=context)
		opening_balance = opening[1]-opening[0]

		cr.execute('SELECT '\
                'am.date as date, '\
                'am.id as description, '\
                'am.narration as narration, '\
                'ai.qty_total as quantity, '\
                'l.debit as debit, '\
                'l.credit as credit, '\
                'l.debit-l.credit as balance '\

            'FROM '\
                'account_move_line l '\
                'left join account_account a on (l.account_id = a.id) '\
                'left join account_move am on (am.id=l.move_id) '\
                'left join account_invoice ai on (ai.move_id=am.id) '\


            'WHERE l.state != %s '\
	            'AND am.state = %s '\
	            'AND am.date >= %s and am.date <= %s '\
	            'AND l.partner_id = %s '\
	            'AND (l.debit != 0 or l.credit != 0) '\
	            'AND a.type = %s '\
	        'ORDER BY am.date,am.id ASC' ,(l_state,am_state,wizard.date_start, wizard.date_end,wizard.partner_id.id,a_type))

		hasil_query = cr.fetchall()
		
		if opening_balance > 0:
			note = 'Kurang Bayar'
		elif opening_balance < 0:
			note = 'Lebih Bayar'		
		else :
			note = '-'			
		self.pool.get('vit.supplier.card').create(cr,1,{'supplier_card_id' : supplier_card_id,
															'narration' : 'Opening Balance',
															'balance' : opening_balance,
															'note':note})
		if hasil_query:
			am_execute = False
			loop_ongkir_date = False
			loop_point_reward = False
			loop_cashback = False
			loop_selisih_harga = False
			balance = opening_balance
			for execute in hasil_query:	
				if am_execute == execute[1]:
					continue
				am_execute = execute[1]
				acc_mv_obj = self.pool.get('account.move')
				journal_entries = acc_mv_obj.browse(cr,uid,execute[1])
				journal_type = journal_entries.journal_id.type
				journal_code = journal_entries.journal_id.code
				journal_name = journal_entries.journal_id.name

				prod_obj =  self.pool.get('product.product')
				acc_i_obj = self.pool.get('account.invoice')
				inv_id = acc_i_obj.search(cr,uid,[('move_id','=',execute[1])])
				#import pdb;pdb.set_trace()

				quantity = 0 
				if execute[3] != None:
					quantity = execute[3]
				debit = 0 
				if execute[4] != None:
					debit = execute[4]					
				credit = 0 
				if execute[5] != None:
					credit = execute[5]
				if inv_id :

					inv_type = acc_i_obj.browse(cr,1,inv_id[0]).type
					# jika refund masukan nominal ke credit
					if inv_type == 'in_refund':
						balance -= credit
						if balance > 0:
							note = 'Kurang Bayar'
						elif balance < 0:
							note = 'Lebih Bayar'		
						else :
							note = '-'						
						self.pool.get('vit.supplier.card').create(cr,1,{'supplier_card_id' : supplier_card_id,
																			'date': execute[0] or False,
																			'description' : execute[1],
																			'narration' : 'Retur Barang',
																			'quantity': -quantity,
																			'debit': credit,
																			'credit' : 0,
																			'balance' : balance,
																			'note':note})
					#  jika supp invoice masukan nominal ke debit						
					if inv_type == 'in_invoice':	
						balance += credit	
						if balance > 0:
							note = 'Kurang Bayar'
						elif balance < 0:
							note = 'Lebih Bayar'		
						else :
							note = '-'								
						self.pool.get('vit.supplier.card').create(cr,1,{'supplier_card_id' : supplier_card_id,
																			'date': execute[0] or False,
																			'description' : execute[1],
																			'narration' : 'Invoice',
																			'quantity': quantity,
																			'debit': 0,
																			'credit' : credit,
																			'balance' : balance,
																			'note':note})
								
				# jika	payment	
				if not inv_id :
					if journal_type in ('bank','cash'):
						balance -= debit
					if balance > 0:
						note = 'Kurang Bayar'
					elif balance < 0:
						note = 'Lebih Bayar'		
					else :
						note = '-'							
					self.pool.get('vit.supplier.card').create(cr,1,{'supplier_card_id' : supplier_card_id,
																		'date': execute[0] or False,
																		'description' : execute[1],
																		'narration' : 'Payment '+journal_name,
																		'quantity': 0,
																		'debit': debit,
																		'credit' : 0,
																		'balance' : balance,
																		'note':note})

		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, 1, 'vit_supplier_card', 'vit_supplier_card_form')
		view_id = view_ref and view_ref[1] or False,	
		
		desc 	= 'Supplier Card'
		domain 	= []
		context = {}

		return self.hasil(cr, uid, desc, supplier_card_id, view_id, domain, context)