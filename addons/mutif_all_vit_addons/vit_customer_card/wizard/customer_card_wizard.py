from osv import osv,fields
from openerp.tools.translate import _
import datetime 
import openerp.addons.decimal_precision as dp

class report_wizard(osv.TransientModel): 
	_name = 'vit_shortcut.report_wizard' 

	_columns = {
		'date_start' : fields.date('Date Start',required=True),
		'date_end'   : fields.date('Date End',required=True),
		'partner_id' : fields.many2one('res.partner',string='Customer',required=True),
		'starting_balance' : fields.float('Starting Balance'),
	}

	_defaults = {
		'date_start'  	: lambda *a : (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),	
		'date_end'		: fields.date.context_today,	
	}

	def _get_total_debit_credit(self, cr, uid, ids, l_state, m_state, date, partner_id, type, context):
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

	def _get_total_debit_credit_by_date(self, cr, uid, ids, l_state, m_state, date_start, date_end, partner_id, type, context):
		cr.execute('SELECT '\
                'sum(l.debit) as debit, '\
                'sum(l.credit) as credit '\
            'FROM '\
                'account_move_line l '\
                'left join account_account a on (l.account_id = a.id) '\
                'left join account_move am on (am.id=l.move_id) '\

            'WHERE l.state != %s '\
	            'AND am.state = %s '\
	            'AND am.date >= %s AND am.date <= %s '\
	            'AND l.partner_id = %s '\
	            'AND (l.debit != 0 or l.credit != 0) '\
	            'AND a.type = %s',(l_state, m_state, date_start, date_end, partner_id, type))		
		
		debit = 0
		credit = 0
		output = cr.fetchone()
		if output[0] != None :
			debit = output[0]
		if output[1] != None :
			credit = output[1]
		ending_balance = (debit,credit)

		return ending_balance

	def _ongkir_journal_manual(self, cr, uid, ids, l_state, m_state, date, partner_id, context):	
		cr.execute('SELECT '\
				'am.id as move_id, '\
                'sum(l.debit) as debit, '\
                'sum(l.credit) as credit '\
            'FROM '\
                'account_move_line l '\
                'left join account_account a on (l.account_id = a.id) '\
                'left join account_move am on (am.id=l.move_id) '\

            'WHERE l.state != %s '\
	            'AND am.state = %s '\
	            'AND am.date = %s '\
	            'AND l.partner_id = %s '\
	            'AND (l.debit != 0 or l.credit != 0) '\
	            'AND a.code = %s '\
	        'GROUP BY am.id' ,(l_state, m_state, date, partner_id,'2-500016'))	    	
		move_id = False
		debit = 0
		credit = 0
			
		outp = cr.fetchall()
		ongkirs = []
		if outp:
			for output in outp:
				if move_id != None :
					move_id = output[0]			
				if output[0] != None :
					debit = output[1]
				if output[1] != None :
					credit = output[2]
				ongkirs.append([move_id,debit,credit])
		return ongkirs

	def _point_reward_journal_manual(self, cr, uid, ids, l_state, m_state, date, partner_id, context):	
		cr.execute('SELECT '\
				'am.id as move_id, '\
                'sum(l.debit) as debit, '\
                'sum(l.credit) as credit '\
            'FROM '\
                'account_move_line l '\
                'left join account_account a on (l.account_id = a.id) '\
                'left join account_move am on (am.id=l.move_id) '\

            'WHERE l.state != %s '\
	            'AND am.state = %s '\
	            'AND am.date = %s '\
	            'AND l.partner_id = %s '\
	            'AND (l.debit != 0 or l.credit != 0) '\
	            'AND a.code = %s '\
	        'GROUP BY am.id' ,(l_state, m_state, date, partner_id,'2-800003'))	    	
		move_id = False
		debit = 0
		credit = 0
			
		outp = cr.fetchall()
		ongkirs = []
		if outp:
			for output in outp:
				if move_id != None :
					move_id = output[0]			
				if output[0] != None :
					debit = output[1]
				if output[1] != None :
					credit = output[2]
				ongkirs.append([move_id,debit,credit])
		return ongkirs

	def _cashback_journal_manual(self, cr, uid, ids, l_state, m_state, date, partner_id, context):	
		cr.execute('SELECT '\
				'am.id as move_id, '\
                'sum(l.debit) as debit, '\
                'sum(l.credit) as credit '\
            'FROM '\
                'account_move_line l '\
                'left join account_account a on (l.account_id = a.id) '\
                'left join account_move am on (am.id=l.move_id) '\

            'WHERE l.state != %s '\
	            'AND am.state = %s '\
	            'AND am.date = %s '\
	            'AND l.partner_id = %s '\
	            'AND (l.debit != 0 or l.credit != 0) '\
	            'AND a.code = %s '\
	        'GROUP BY am.id' ,(l_state, m_state, date, partner_id,'4-110012'))	    	
		move_id = False
		debit = 0
		credit = 0
			
		outp = cr.fetchall()
		cashback = []
		if outp:
			for output in outp:
				if move_id != None :
					move_id = output[0]			
				if output[0] != None :
					debit = output[1]
				if output[1] != None :
					credit = output[2]
				cashback.append([move_id,debit,credit])
		return cashback

	def _selisih_harga_journal_manual(self, cr, uid, ids, l_state, m_state, date, partner_id, context):	
		cr.execute('SELECT '\
				'am.id as move_id, '\
                'sum(l.debit) as debit, '\
                'sum(l.credit) as credit '\
            'FROM '\
                'account_move_line l '\
                'left join account_account a on (l.account_id = a.id) '\
                'left join account_move am on (am.id=l.move_id) '\

            'WHERE l.state != %s '\
	            'AND am.state = %s '\
	            'AND am.date = %s '\
	            'AND l.partner_id = %s '\
	            'AND (l.debit != 0 or l.credit != 0) '\
	            'AND a.code = %s '\
	        'GROUP BY am.id' ,(l_state, m_state, date, partner_id,'4-110011'))	    	
		move_id = False
		debit = 0
		credit = 0
			
		outp = cr.fetchall()
		cashback = []
		if outp:
			for output in outp:
				if move_id != None :
					move_id = output[0]			
				if output[0] != None :
					debit = output[1]
				if output[1] != None :
					credit = output[2]
				cashback.append([move_id,debit,credit])
		return cashback


	def hasil(self, cr, uid, desc, report, view_id, domain, context):
		return {
			'name' : _(desc),
			'view_type': 'form',
			'view_mode': 'form',			
			'res_model': 'vit.customer',
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
		
		sql = "delete from vit_customer where user_id = %s" % (uid)
		
		cr.execute(sql)

		l_state = 'draft'	
		am_state = 'posted'	
		a_type = 'receivable'

		customer_card_id = self.pool.get('vit.customer').create(cr,1,{'partner_id':wizard.partner_id.id,
																		'date_start': wizard.date_start,
																		'date_end': wizard.date_end,
																		'user_id':uid})

		#cari opening balance_get_total_balance dari hitungan atau input manual
		if wizard.starting_balance == 0 :
			opening = self._get_total_debit_credit(cr, 1, ids, l_state, am_state, wizard.date_start, wizard.partner_id.id, a_type, context=context)
			opening_balance = opening[1]-opening[0]
		else :
			opening_balance = wizard.starting_balance

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
	            'AND (a.type = %s '\
	            'OR a.code = %s OR a.code = %s OR a.code = %s OR a.code = %s) '\
	        'ORDER BY am.date,am.id ASC' ,(l_state,am_state,wizard.date_start, wizard.date_end,wizard.partner_id.id,a_type,'2-500016','2-800003','4-110012','4-110011'))

		hasil_query = cr.fetchall()
		
		if opening_balance < 0:
			note = 'Kurang Bayar'
		elif opening_balance > 0:
			note = 'Lebih Bayar'		
		else :
			note = '-'			
		self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
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

				hasil_ongkir = 0
				qty_ongkir = 0
				# Cari produck dengan kode ongkir ONGKOS001
				prod_obj =  self.pool.get('product.product')
				acc_i_obj = self.pool.get('account.invoice')
				inv_id = acc_i_obj.search(cr,uid,[('move_id','=',execute[1])])
				ongkir_product = prod_obj.search(cr,1,[('default_code','=','ONGKOS001')])
				#import pdb;pdb.set_trace()
				if inv_id :
					if ongkir_product :
						acc_i_line_obj = self.pool.get('account.invoice.line')
						ongkir = acc_i_line_obj.search(cr,1,[('invoice_id','=',inv_id[0]),('product_id','=',ongkir_product[0])])
						# jika ada ongkir di invoice line
						if ongkir :
							ongkir_browse = acc_i_line_obj.browse(cr,1,ongkir[0],context=context)
							hasil_ongkir = ongkir_browse.quantity*ongkir_browse.price_unit
							#balance += hasil_ongkir
							qty_ongkir = ongkir_browse.quantity
							# if balance < 0:
							# 	note = 'Kurang Bayar'
							# elif balance > 0:
							# 	note = 'Lebih Bayar'		
							# else :
							# 	note = '-'	
							# # Ongkir
							# self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
							# 													'date': execute[0] or False,
							# 													'description' : execute[1],
							# 													'narration' : 'Titipan ' +ongkir_browse.product_id.name+' '+ongkir_browse.invoice_id.number,
							# 													'quantity': 0,
							# 													'debit': 0,
							# 													'credit' : hasil_ongkir,
							# 													'balance' : balance,
							# 													'note':note})		
							
					if not ongkir_product :
						hasil = (execute[4]-hasil_ongkir) - execute[5]
						balance -= hasil
				if balance < 0:
					note = 'Kurang Bayar'
				elif balance > 0:
					note = 'Lebih Bayar'		
				else :
					note = '-'	

				quantity = 0 
				if execute[3] != None:
					quantity = execute[3]
				debit = 0 
				if execute[4] != None:
					debit = execute[4]

				#tambah type invoice,
				if inv_id :
					inv_type = acc_i_obj.browse(cr,1,inv_id[0]).type
					# jika refund masukan nominal ke credit
					if inv_type == 'out_refund':
						self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
																			'date': execute[0] or False,
																			'description' : execute[1],
																			'narration' : 'Retur Barang',
																			'quantity': -(quantity-qty_ongkir),
																			'debit': debit-hasil_ongkir,
																			'credit' : execute[5],
																			'balance' : balance,
																			'note':note})
					#  jika cust invoice masukan nominal ke debit						
					if inv_type == 'out_invoice':
						debt = acc_i_obj.browse(cr,1,inv_id[0]).amount_total
						#debt = debit-hasil_ongkir
						# handle jika ada invoice yang pricenya 0 / katalog
						if debt < 0 :
							debt = 0
							hasil_ongkir2 = hasil_ongkir*2
							balance -= hasil_ongkir2
						elif debt >= 0 :
							debt = debt-hasil_ongkir	
							balance -= debt
						if balance < 0:
							note = 'Kurang Bayar'
						elif balance > 0:
							note = 'Lebih Bayar'		
						else :
							note = '-'								
						self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
																			'date': execute[0] or False,
																			'description' : execute[1],
																			'narration' : 'Invoice',
																			'quantity': quantity-qty_ongkir,
																			'debit': debt,
																			'credit' : 0,
																			'balance' : balance,
																			'note':note})
								
				# cek ongkir manual yang pakai journal memorial	
				cek_ongkir_journal_manual = self._ongkir_journal_manual(cr, 1, ids, l_state, am_state, execute[0], wizard.partner_id.id, context)
				
				if len(cek_ongkir_journal_manual) >= 1:
					if loop_ongkir_date != execute[0]:
						
						for ongkir in cek_ongkir_journal_manual: 
							if ongkir[1] != 0: 	
								balance -= ongkir[1]
								if balance < 0:
									note = 'Kurang Bayar'
								elif balance > 0:
									note = 'Lebih Bayar'		
								else :
									note = '-'	
								ongkir_ref = acc_mv_obj.browse(cr,1,ongkir[0]).ref
								if not ongkir_ref:
									ongkir_ref = ''
								self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
																					'date': execute[0] or False,
																					'description' : ongkir[0],
																					'narration' : 'Realisasi Ongkos Kirim '+ongkir_ref,
																					'quantity': 0,
																					'debit': ongkir[1],
																					'credit' : 0,
																					'balance' : balance,
																					'note':note})
								# catat tanggalnya supaya pencarian tngggal journal memorial onkos kirim hanya 1 kali pertanggal
								loop_ongkir_date = execute[0]		
				# cek point reward manual yang pakai journal memorial	
				cek_pr_journal_manual = self._point_reward_journal_manual(cr, 1, ids, l_state, am_state, execute[0], wizard.partner_id.id, context)
				if len(cek_pr_journal_manual) >= 1:
					if loop_point_reward != execute[0]:
						for pr in cek_pr_journal_manual: 
							if pr[1] != 0:  	
								balance += pr[1]
								if balance < 0:
									note = 'Kurang Bayar'
								elif balance > 0:
									note = 'Lebih Bayar'		
								else :
									note = '-'							
								self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
																					'date': execute[0] or False,
																					'description' : pr[0],
																					'narration' : 'Bonus Point Reward',
																					'quantity': 0,
																					'debit': 0,
																					'credit' : pr[1],
																					'balance' : balance+pr[1],
																					'note':note})
								balance += pr[1]
								# catat tanggalnya supaya pencarian tngggal journal memorial pr hanya 1 kali pertanggal
								loop_point_reward = execute[0]
				# cek cash back manual yang pakai journal memorial	
				cek_cb_journal_manual = self._cashback_journal_manual(cr, 1, ids, l_state, am_state, execute[0], wizard.partner_id.id, context)				
				if len(cek_cb_journal_manual) >= 1:					
					if loop_cashback != execute[0]:
						for cb in cek_cb_journal_manual: 
							journal_entries_cb = acc_mv_obj.browse(cr,1,cb[0])
							
							ref_journal = ''
							if journal_entries_cb.ref != False:
								ref_journal = journal_entries_cb.ref

							#if execute[1] != cb[0]:
							if execute[1] != 0:									
								balance += cb[1]

							if balance < 0:
								note = 'Kurang Bayar'
							elif balance > 0:
								note = 'Lebih Bayar'		
							else :
								note = '-'							
							self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
																				'date': execute[0] or False,
																				'description' : cb[0],
																				'narration' : 'Cash Back '+ref_journal,
																				'quantity': 0,
																				'debit': 0,
																				'credit' : cb[1],
																				'balance' : balance,
																				'note':note})									
							# catat tanggalnya supaya pencarian tngggal journal memorial pr hanya 1 kali pertanggal
							loop_cashback = execute[0]	

				# cek selisih harga invoice manual yang pakai journal memorial/voucher
				cek_selisih_journal_manual = self._selisih_harga_journal_manual(cr, 1, ids, l_state, am_state, execute[0], wizard.partner_id.id, context)				
				if len(cek_selisih_journal_manual) >= 1:					
					if loop_selisih_harga != execute[0]:
						for selisih in cek_selisih_journal_manual: 
							journal_entries_selisih_brg = acc_mv_obj.browse(cr,1,selisih[0])
							ref_journal = ''
							if journal_entries_selisih_brg.ref != False:
								ref_journal = journal_entries_selisih_brg.ref
								
							if balance < 0:
								note = 'Kurang Bayar'
							elif balance > 0:
								note = 'Lebih Bayar'		
							else :
								note = '-'	
							if selisih[1] != 0 :

								text_selisih = 'Selisih Lebih Bayar '
								#if execute[1] != selisih[0]:															
								balance += selisih[1]
							if selisih[2] != 0 :
								text_selisih = 'Selisih Kurang Bayar '	
								#if execute[1] != selisih[0]:
								balance -= selisih[2]								
							self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
																				'date': execute[0] or False,
																				'description' : selisih[0],
																				'narration' : text_selisih+ref_journal,
																				'quantity': 0,
																				'debit': selisih[2],
																				'credit' : selisih[1],
																				'balance' : balance,
																				'note':note})																						
							# catat tanggalnya supaya pencarian tngggal journal memorial pr hanya 1 kali pertanggal
							loop_selisih_harga = execute[0]	

				# jika	payment	
				if not inv_id :
					# jika payment menggunakan Point Reward
					if journal_type in ('bank','cash') and journal_code == 'PR':
						balance += execute[5]
						#balance -= execute[5]
						self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
																			'date': execute[0] or False,
																			'description' : execute[1],
																			'narration' : 'Pencairan '+journal_name,
																			'quantity': 0,
																			'debit': debit-hasil_ongkir,
																			'credit' : execute[5],
																			'balance' : balance,
																			'note':note})
						continue
						
					if journal_type in ('bank','cash') and journal_code not in ('CB','SP','OK','PR','OK2','OK3'):
						
						move_id = execute[1]
						# cr.execute("""SELECT 
						# 			SUM(aml.debit) as debit
						# 			FROM account_move_line aml
						# 			LEFT JOIN account_move am ON am.id = aml.move_id
						# 			WHERE am.id = """+str(move_id)+"""
						# 			""")
						#import pdb;pdb.set_trace()
						cr.execute("""SELECT 
									aat.code as code,
									aml.debit as debit
									FROM account_move_line aml
									LEFT JOIN account_move am ON am.id = aml.move_id
									LEFT JOIN account_account aa ON aml.account_id = aa.id
									LEFT JOIN account_account_type aat ON aa.user_type = aat.id
									WHERE am.id = """+str(move_id)+"""
									""")

						debt = cr.fetchall()
						if debt :
							for de in debt :
								total_debt = de[1]
								if total_debt >=1 :
									if de[0] in ('bank','cash'):								
										balance += total_debt
										if balance < 0:
											note = 'Kurang Bayar'
										elif balance > 0:
											note = 'Lebih Bayar'		
										else :
											note = '-'											
										self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
																							'date': execute[0] or False,
																							'description' : execute[1],
																							'narration' : 'Payment '+journal_name,
																							'quantity': 0,
																							# 'debit': debit-hasil_ongkir,
																							'debit': 0,
																							'credit' : total_debt,
																							'balance' : balance,
																							'note':note})		
									else :								
										balance += total_debt
										if balance < 0:
											note = 'Kurang Bayar'
										elif balance > 0:
											note = 'Lebih Bayar'		
										else :
											note = '-'											
										self.pool.get('vit.customer.card').create(cr,1,{'customer_card_id' : customer_card_id,
																							'date': execute[0] or False,
																							'description' : execute[1],
																							'narration' : 'Payment '+'Deposit',
																							'quantity': 0,
																							# 'debit': debit-hasil_ongkir,
																							'debit': 0,
																							'credit' : total_debt,
																							'balance' : balance,
																							'note':note})

		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, 1, 'vit_customer_card', 'vit_customer_card_form')
		view_id = view_ref and view_ref[1] or False,	
		
		desc 	= 'Customer Card'
		domain 	= []
		context = {}

		return self.hasil(cr, uid, desc, customer_card_id, view_id, domain, context)