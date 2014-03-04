from datetime import datetime
from openerp.osv import osv, fields
import psycopg2
from openerp import netsvc
import logging
_logger = logging.getLogger(__name__)
import openerp.tools
from openerp.tools.translate import _



class res_partner(osv.osv):
	EXCH_HOST 			= ""
	EXCH_DB 			= ""
	EXCH_USER 			= ""
	EXCH_PASS 			= ""
	LOYALTY_PRODUCT_ID 	= 0
	PAYMENT_PRODUCT_ID 	= 0

	_description 		= 'Partner'
	_name 				= "res.partner"
	_inherit 			= "res.partner"
	con 				= None
	cur 				= None
	payment_process 	= False 

	def connect_petro(self, cr, uid, context=None):
		self.EXCH_HOST 				= self.pool.get('ir.config_parameter').get_param(cr, uid, 'sage_petro.EXCH_HOST')
		self.EXCH_DB 				= self.pool.get('ir.config_parameter').get_param(cr, uid, 'sage_petro.EXCH_DB')
		self.EXCH_USER 				= self.pool.get('ir.config_parameter').get_param(cr, uid, 'sage_petro.EXCH_USER')
		self.EXCH_PASS 				= self.pool.get('ir.config_parameter').get_param(cr, uid, 'sage_petro.EXCH_PASS')
		self.LOYALTY_PRODUCT_ID 	= self.pool.get('ir.config_parameter').get_param(cr, uid, 'sage_petro.LOYALTY_PRODUCT_ID')
		self.PAYMENT_PRODUCT_ID 	= self.pool.get('ir.config_parameter').get_param(cr, uid, 'sage_petro.PAYMENT_PRODUCT_ID')

		conn_string2 = "host='"+self.EXCH_HOST+"' dbname='" + self.EXCH_DB + "' user='"+self.EXCH_USER+"' password='"+self.EXCH_PASS+"'"
		self.con = psycopg2.connect(conn_string2)
		self.cur = self.con.cursor()
		return True

	def update_client(self, cr, uid, partner, context=None):
		#check exists?
		sql = """SELECT * from erpexchange."SET_CLIENT_INFO" WHERE "P_CLIENT_ID"='%d'""" % (partner.id,) 
		self.cur.execute(sql)
		row = self.cur.fetchone()

		if not row:
			self.create_client(cr, uid, partner, context=context)
		else:
			sql = """UPDATE erpexchange."SET_CLIENT_INFO" SET 
				"P_CLIENT_TYPE"=%s,
				"P_CLIENT_NAME"='%s',
				"P_ADRES"='%s',
				"P_ADRES_FACT"='%s',
				"P_EMAIL"='%s',
				"P_NAME_FOR_REPORTS"='%s',
				"P_COMMENTS"='%s',
				"P_OPERATION"='%s',
				"P_CONTACT_PERSON"='%s',
				"P_DATE"='%s'
				where "P_CLIENT_ID"='%d'""" % (
				'3', 
				partner.name,
				partner.street,
				partner.street,
				partner.email,
				partner.name,
				partner.comment,
				'3',
				partner.name,
				datetime.now(),
				partner.id
				)

			self.cur.execute(sql)
			self.con.commit()
		return True

	def create_client(self, cr, uid, partner, context=None):
		sql = """INSERT INTO erpexchange."SET_CLIENT_INFO"
			("P_CLIENT_TYPE",
			"P_CLIENT_ID",
			"P_CLIENT_NAME",
			"P_ADRES",
			"P_ADRES_FACT",
			"P_EMAIL",
			"P_NAME_FOR_REPORTS",
			"P_COMMENTS",
			"P_OPERATION",
			"P_CONTACT_PERSON",
			"P_DATE",
			"P_GUID")
			VALUES (%d, '%d', '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '
				%d' ) """ % (
			3, 
			partner.id, 
			partner.name,
			partner.street,
			partner.street,
			partner.email,
			partner.name,
			partner.comment,
			1,
			partner.name,
			datetime.now(),
			partner.id
			)
		self.cur.execute(sql)
		self.con.commit()

		return True

	def update_client_account(self, cr, uid, partner, context=None):
		#check exists?
		sql = """SELECT * from erpexchange."SET_CLIENT_ACCOUNT" WHERE "P_CLIENT_ID"='%d'""" % (partner.id,) 
		self.cur.execute(sql)
		row = self.cur.fetchone()

		if not row:
			self.create_client_account(cr, uid, partner, context=context)
		else:
			sql = """UPDATE erpexchange."SET_CLIENT_ACCOUNT" SET 
				"P_CLIENT_TYPE"=%d,
				"P_SERVICE_ID"=%d,
				"P_OPERATION"=%d,
				"P_NOTIFICATION_LIMIT"=%d,
				"P_ALERT_LIMIT"=%d,
				"P_DATE"='%s'
				where "P_CLIENT_ID"='%d'""" % (
				3, 
				1,
				3,
				partner.nt_limit,
				partner.at_limit,
				datetime.now(),
				partner.id
				)

			self.cur.execute(sql)
			self.con.commit()

		return True

	def create_client_account(self, cr, uid, partner, context=None):
		sql = """INSERT INTO erpexchange."SET_CLIENT_ACCOUNT"
			("P_CLIENT_TYPE",
			"P_SERVICE_ID",
			"P_OPERATION",
			"P_CLIENT_ID",
			"P_NOTIFICATION_LIMIT",
			"P_ALERT_LIMIT",
			"P_DATE",
			"P_GUID")
			VALUES ('%d', '%d', '%d', '%d', '%d', '%d', '%s' , '%s') """ % (
			3, 
			1,
			1,
			partner.id,
			partner.nt_limit,
			partner.at_limit,
			datetime.now(),
			partner.id
			)
		self.cur.execute(sql)
		self.con.commit()

		return True


	######################################################################################
	#write partner => push to temp DB
	######################################################################################
	def write(self, cr, uid, ids, vals, context=None):
		if isinstance(ids, (int, long)):
			ids = [ids]
		result = super(res_partner,self).write(cr, uid, ids, vals, context=context)

		if not self.payment_process:
			self.connect_petro(cr, uid, context)
			for partner in self.browse(cr, uid, ids, context=context):
				self.update_client(cr, uid, partner)
				self.update_client_account(cr, uid, partner)

			if self.con:
				self.con.close()

		return result

	######################################################################################
	# read TRANSACTION raw data from temp DB, create invoices
	# according to OPERATION_ID, prepaid/postpaid trans
	######################################################################################
	def read_trans(self, cr, uid, context=None):
		_logger.info("reading TRANSACTION")
		self.connect_petro(cr, uid, context)

		##################################################################################
		# cari record yang p_date>p_date_exchange:
		# p_date = timestamp dari petro ketika dia update/create record
		# p_date_exchange = timestamp openerp ketika selesai proses record ini
		##################################################################################
		sql = """SELECT * FROM erpexchange."TRANSACTIONS" WHERE "P_DATE">"P_DATE_EXCHANGE" OR "P_DATE_EXCHANGE" IS NULL"""
		self.cur.execute(sql)


		##################################################################################
		# prepare common variable
		##################################################################################
		company_id 		= self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
		product_id 		= int(self.PAYMENT_PRODUCT_ID)
		product 		= self.pool.get('product.product').browse(cr, uid, product_id, context=context)
		journal_ids 	= self.pool.get('account.journal').search(cr, uid,[('type', '=', 'sale'), ('company_id', '=', company_id)],limit=1)
		if not journal_ids:
			raise osv.except_osv(_('Error!'),
				_('Please define sales journal for this company.')  )
		sale_journal_id = journal_ids[0]

		journal_ids 	= self.pool.get('account.journal').search(cr, uid,[('type', '=', 'purchase'), ('company_id', '=', company_id)],limit=1)
		if not journal_ids:
			raise osv.except_osv(_('Error!'),
				_('Please define purchase journal for this company.')  )
		purchase_journal_id = journal_ids[0]

		date_invoice 	= datetime.now().strftime('%Y-%m-%d')
		partner_id 		= 0
		omc_partner_id 	= 0
		ap_account_id 	= 0
		ar_account_id 	= 0		

		##################################################################################
		# loop every transaction records 
		##################################################################################
		rows = self.cur.fetchall()
		for row in rows:
			"""
			0 P_DATETIME
			1 P_CLIENT_ID
			2 P_POS_NUMBER
			3 P_CLIENT_TYPE
			4 P_SERVICE_ID
			5 P_AMOUNT
			6 P_TERMINAL_PRICE
			7 P_TOTAL_AMOUNT
			8 P_ACTUAL_PRICE
			9 P_TOTAL_AMOUNT_WITHOUT_DISC
			10 P_GUID
			11 P_OPERATION_ID
			12 P_COMMENT
			13 P_DATE
			14 P_DATE_EXCHANGE
			"""

			sale_inv_lines = []
			purchase_inv_lines = []

			#############################################################################
			# create Journal Entries/ atau Invoice berdasarkan record transaksi 
			#############################################################################
			P_DATETIME 						= row[0]
			P_CLIENT_ID						= row[1]
			P_POS_NUMBER					= row[2]
			P_CLIENT_TYPE					= row[3]
			P_SERVICE_ID					= row[4]
			P_AMOUNT						= row[5]
			P_TERMINAL_PRICE				= row[6]
			P_TOTAL_AMOUNT					= row[7]
			P_ACTUAL_PRICE					= row[8]
			P_TOTAL_AMOUNT_WITHOUT_DISC		= row[9]
			P_GUID							= row[10]
			P_OPERATION_ID					= row[11]
			P_COMMENT						= row[12]
			P_POS_NAME						= P_POS_NUMBER

			qty 							= P_AMOUNT


			#############################################################################
			#coming from each record's client_id (partner) and find the service_type
			#############################################################################
			prepaid 	= False
			postpaid 	= False  

			#############################################################################
			# look for OPERATION_ID = 1
			#############################################################################
			if P_OPERATION_ID == 1:

				#get partner for card User
				partner = self.find_partner_by_client_id(cr,uid,P_CLIENT_ID)
				if not partner:
					_logger.error(  'not found partner for card user.')
					return
				partner_id = partner.id
				ar_account_id = partner.property_account_receivable.id

				if partner.service_type == 'postpaid':
					postpaid = True 
				elif partner.service_type == 'prepaid':
					prepaid = True
				else:
					raise osv.except_osv(_('Error!'),
						">>> partner service type not postpaid nor prepaid, skipping %s...." % 
						(partner.name))
					continue

				########################################################################
				#get partner by pos_group_id : OMCs, temporary
				########################################################################
				omc_pos_group_id	= 4 
				omc_partner 		= self.find_partner_by_pos_group_id(cr,uid, omc_pos_group_id ) 
				if not omc_partner:
					raise osv.except_osv(_('Error!'),
						_('not found partner for OMC ')  )
					return
				omc_partner_id = omc_partner.id
				ap_account_id = omc_partner.property_account_payable.id

				########################################################################
				#setup inv_lines
				########################################################################
				sale_inv_lines.append(
					(0,0,{

						'name': "%s %s" % ( product.name , P_POS_NAME),
						'origin':  'interface records',
						'sequence':  '',
						'uos_id':  False,
						'product_id':  product_id,
						'account_id':  product.property_account_income.id, 
						#'price_unit':  product.list_price,
						'price_unit':  P_TOTAL_AMOUNT,
						'quantity':    qty , 
						#'price_subtotal': product.list_price * qty,  
						'price_subtotal': P_ACTUAL_PRICE,  
						'discount':  0,
						'company_id':  company_id,
						'partner_id':  partner_id
					})
				)			
				purchase_inv_lines.append(
					(0,0,{
						'name': "%s %s" % ( product.name , P_POS_NAME),
						'origin':  'interface records',
						'sequence':  '',
						'uos_id':  False,
						'product_id':  product_id,
						'account_id':  product.property_stock_account_input.id, 
						'price_unit':  product.standard_price,
						'quantity':  qty, 
						'price_subtotal': product.standard_price * qty,  
						'discount':  0,
						'company_id':  company_id,
						'partner_id':  omc_partner_id
					})
				)

				########################################################################
				#create customer invoice for this CLIENT_ID
				########################################################################
				if prepaid:
					print "prepaid processing..."

					####################################################################
					#create sales invoice to card user
					invoice_id = self.create_customer_invoice(cr, uid, date_invoice, 
						partner_id, ar_account_id, sale_inv_lines , sale_journal_id, 
						company_id, context)
					####################################################################

					####################################################################
					#confirm invoice
					####################################################################
					self.invoice_confirm(cr, uid, invoice_id, context)

					####################################################################
					#create payment from deposit, first cari jurnal deposit dulu
					####################################################################
					journal_ids = self.pool.get('account.journal').search(cr, uid,
						[('code', '=', 'DEP'), ('company_id', '=', company_id)],limit=1)
					if not journal_ids:
						raise osv.except_osv(_('Error!'),
							"Please define deposit journal  with code 'DEP' and type bank for this company." )

					dep_journal = self.pool.get('account.journal').browse(cr,uid, journal_ids[0])
					voucher_id = self.create_payment(cr, uid, invoice_id, partner_id, 
						qty*P_ACTUAL_PRICE, dep_journal, company_id, context)

					self.payment_process = True 
					self.payment_confirm( cr, uid, voucher_id, context)
					self.payment_process = False

					####################################################################
					#create purchase invoice to OMC
					####################################################################
					invoice_id=self.create_supplier_invoice(cr, uid, date_invoice, 
						omc_partner_id, ap_account_id, purchase_inv_lines , 
						purchase_journal_id, company_id, context)

					####################################################################
					#confirm invoice
					####################################################################
					self.invoice_confirm(cr, uid, invoice_id, context)

				elif postpaid:
					print "prepaid processing..."
					####################################################################
					#create sales invoice to card user
					####################################################################
					invoice_id = self.create_customer_invoice(cr, uid, date_invoice, partner_id, 
						ar_account_id, sale_inv_lines , sale_journal_id, 
						company_id, context)

					####################################################################
					#confirm invoice
					####################################################################
					self.invoice_confirm(cr, uid, invoice_id, context)


					####################################################################
					#create purchase invoice to OMC
					####################################################################
					invoice_id = self.create_supplier_invoice(cr, uid, date_invoice, omc_partner_id, 
						ap_account_id, purchase_inv_lines , purchase_journal_id, 
						company_id, context)
					
					####################################################################
					#confirm invoice
					####################################################################
					self.invoice_confirm(cr, uid, invoice_id, context)

			#############################################################################
			#end if operation id
			#############################################################################


			#############################################################################
			# selesai proses , set p_date_exchange = now
			#############################################################################
			sql = """UPDATE erpexchange."TRANSACTIONS" SET "P_DATE_EXCHANGE"='%s' WHERE "P_GUID"='%s'""" % (
				datetime.now(), P_GUID)
			self.cur.execute(sql)
			self.con.commit()

		if self.con:
			self.con.close()

		return True 

	####################################################################################
	#read BONUSES transaction from temp db, create invoices
	#according to OPERATION_ID
	####################################################################################
	def read_bonus(self, cr, uid, context=None):
		_logger.info("reading BONUSES")
		self.connect_petro(cr, uid, context)
		self.read_bonus_by_operation(cr, uid, "accum", context)
		self.read_bonus_by_operation(cr, uid, "remove", context)
		if self.con:
			self.con.close()		
		return True 

	####################################################################################
	#actual read BONUSES process
	####################################################################################
	def read_bonus_by_operation(self, cr, uid, operation, context=None):

		if operation == "accum":
			operation_ids = "1"
		elif operation == "remove":
			operation_ids = "3,4"

		# cari record yang p_date>p_date_exchange:
		# p_date = timestamp dari petro ketika dia update/create record
		# p_date_exchange = timestamp openerp ketika selesai proses record ini

		where = """WHERE ("P_DATE">"P_DATE_EXCHANGE" OR "P_DATE_EXCHANGE" IS NULL) 
				AND "P_POS_GROUP_ID" != 0
				AND "P_OPERATION_ID" IN (%s) """ % (operation_ids)

		sql = """SELECT "P_OPERATION_ID" , "P_POS_GROUP_ID", "P_POS_ID" , 
			SUM("P_BONUS") as P_BONUS 
			FROM erpexchange."BONUSES"
			%s
			group by "P_OPERATION_ID" , "P_POS_GROUP_ID", "P_POS_ID"
			order by "P_OPERATION_ID" , "P_POS_GROUP_ID", "P_POS_ID"
		""" % (where)

		self.cur.execute(sql)

		rows = self.cur.fetchall()

		old_pos_group_id = -1
		inv_lines 		= []
		company_id 		= self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id

		product_id 		= int(self.LOYALTY_PRODUCT_ID)
		product 		= self.pool.get('product.product').browse(cr, uid, product_id, context=context)
		if not product:
			raise osv.except_osv(_('Error!'),
				_('Cannot find product id:%s' % (product_id))  )

		journal_ids 	= self.pool.get('account.journal').search(cr, uid,[('type', '=', 'sale'), ('company_id', '=', company_id)],limit=1)
		if not journal_ids:
			raise osv.except_osv(_('Error!'),
				_('Please define sales journal for this company.')  )
		sale_journal_id = journal_ids[0]

		journal_ids = self.pool.get('account.journal').search(cr, uid,[('type', '=', 'purchase'), ('company_id', '=', company_id)],limit=1)
		if not journal_ids:
			raise osv.except_osv(_('Error!'),
				_('Please define purchase journal for this company.')  )
		purchase_journal_id = journal_ids[0]

		date_invoice 	= datetime.now().strftime('%Y-%m-%d')
		partner_id 		= 0
		ap_account_id 	= 0
		ar_account_id 	= 0
		
		i=0

		for row in rows:
			"""
			 query group by
			  0 "P_OPERATION_ID" numeric, -- Operation type (1,2,3,4,5)
			  1 "P_POS_GROUP_ID" numeric(12,0),
			  2 "P_POS_ID" numeric(12,0),
			  3 "P_BONUS" numeric(14,2),
			"""
			
			# create Journal Entries/ atau Invoice berdasarkan record transaksi 
			"""
			Types of transaksi berdasarkan P_OPERATION_ID: 

			1=> Accumulated Point => generate Customer Invoice
				Db	OMC AR	
				Cr		Sales-Loyalti Point

			Customer Invoice parameters:
				PartnerID = OMC's partner id
				Account   = OMC's account receivable
				Invoice Line: 
					Product ID = Loyalti Point Product Id 
					Qty        = P_BONUS

			3,4 => Claim from OMC => generate Supplier Invoice						
				Db	Expense-Loyalti Point	
				Cr		OMC AP

			Supplier Invoice Parameters:
				PartnerID = OMC's partner id
				Account   = OMC's account payable
				Invoice Line: 
					Product ID = Loyalti Point Product Id 
					Qty        = P_BONUS
			"""

			P_OPERATION_ID 	= row[0]
			P_POS_GROUP_ID 	= row[1]
			P_POS_ID 		= row[2]
			P_POS_NAME 		= row[2]
			P_BONUS 		= row[3]

			qty 			= P_BONUS

			#operation id accumulation
			if operation == "accum":
				if P_POS_GROUP_ID != old_pos_group_id and i!=0:
					print 'creating customer invoice ...'
					invoice_id = self.create_customer_invoice( cr, uid, date_invoice, partner_id, ar_account_id, inv_lines, sale_journal_id, company_id)
					self.invoice_confirm(cr, uid, invoice_id, context)
					inv_lines=[]

				inv_lines.append(
					(0,0,{
						'name'			:  "%s %s" % ( product.name , P_POS_NAME),
						'origin'		:  'interface records',
						'sequence'		:  '',
						'uos_id'		:  False,
						'product_id'	:  product_id,
						'account_id'	:  product.property_account_income.id, 
						'price_unit'	:  product.list_price,
						'quantity'		:  qty, 
						'price_subtotal':  product.list_price * qty,  
						'discount'		:  0,
						'company_id'	:  company_id,
						'partner_id'	:  partner_id
					})
				)

			#operation id removal
			elif operation=="remove":
				if P_POS_GROUP_ID != old_pos_group_id and i != 0:
					print 'creating supplier invoice ...'
					invoice_id = self.create_supplier_invoice( cr, uid, date_invoice, partner_id, ap_account_id, inv_lines, purchase_journal_id, company_id)
					self.invoice_confirm(cr, uid, invoice_id, context)
					inv_lines=[]

				inv_lines.append(
					(0,0,{
						'name'			:  "%s %s" % ( product.name , P_POS_NAME),
						'origin'		:  'interface records',
						'sequence'		:  '',
						'uos_id'		:  False,
						'product_id'	:  product_id,
						'account_id'	:  product.property_account_expense.id, 
						'price_unit'	:  product.standard_price,
						'quantity'		:  -1 * qty, 
						'price_subtotal':  -1 * product.standard_price * qty,  
						'discount'		:  0,
						'company_id'	:  company_id,
						'partner_id'	:  partner_id
					})
				)

			i = i + 1
			old_pos_group_id = P_POS_GROUP_ID

			#update partner 
			partner = self.find_partner_by_pos_group_id(cr,uid,P_POS_GROUP_ID)
			if not partner:
				print 'Please define POS Group ID for this partner.'
				return
			partner_id = partner.id
			ap_account_id = partner.property_account_payable.id
			ar_account_id = partner.property_account_receivable.id 

		if partner_id != 0 and ar_account_id !=0 and operation == "accum":
			print 'creating last customer invoice ...'
			invoice_id = self.create_customer_invoice( cr, uid, date_invoice, partner_id, ar_account_id, inv_lines, sale_journal_id, company_id)
			self.invoice_confirm(cr, uid, invoice_id, context)
			inv_lines=[]
		elif partner_id != 0 and ap_account_id !=0 and operation=="remove":
			print 'creating last supplier invoice ...'
			invoice_id = self.create_supplier_invoice( cr, uid, date_invoice, partner_id, ap_account_id, inv_lines, purchase_journal_id, company_id)
			self.invoice_confirm(cr, uid, invoice_id, context)
			inv_lines=[]				

		# selesai proses , set p_date_exchange = now
		sql = """UPDATE erpexchange."BONUSES" SET "P_DATE_EXCHANGE"='%s' 
			%s """ % (datetime.now(), where )		
		self.cur.execute(sql)
		self.con.commit()
		
		#psycopg2.close()
		return True

	####################################################################################
	#create customer invoice
	####################################################################################
	def create_customer_invoice(self, cr, uid, date_invoice, partner_id, account_id, lines , journal_id, company_id, context=None):
		invoice_id = self.pool.get('account.invoice').create(cr,uid,{
		    'date_invoice' : date_invoice,
		    'partner_id' : partner_id,
		    'account_id' : account_id,
		    'invoice_line': lines,
		    'type': 'out_invoice',
		    'journal_id': journal_id,
		    'company_id': company_id
		    })		
		print "created customer invoice id:%d" % (invoice_id)
		return invoice_id

	####################################################################################
	#create supplier invoice
	####################################################################################
	def create_supplier_invoice(self, cr, uid, date_invoice, partner_id, account_id, lines , journal_id, company_id, context=None ):
		invoice_id = self.pool.get('account.invoice').create(cr,uid,{
		    'date_invoice' : date_invoice,
		    'partner_id' : partner_id,
		    'account_id' : account_id,
		    'invoice_line': lines,
		    'type': 'in_invoice',
		    'journal_id': journal_id,
		    'company_id': company_id
		    })
		print "created supplier invoice id:%d" % (invoice_id)
		return invoice_id

	####################################################################################
	#create payment 
	#invoice_id: yang mau dibayar
	#journal_id: payment method
	####################################################################################
	def create_payment(self, cr, uid, invoice_id, partner_id, amount, journal, company_id, context=None):
		voucher_lines = []

		#cari invoice
		inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
		#import pdb; pdb.set_trace()

		#cari move_line yang move_id nya = invoice.move_id
		move_line_id = self.pool.get('account.move.line').search( cr, uid, [('move_id.id','=', inv.move_id.id)] );
		move_lines = self.pool.get('account.move.line').browse(cr, uid, move_line_id)
		move_line = move_lines[0] # yang AR saja

		voucher_lines.append((0,0,{
			'move_line_id': 		move_line.id,
			'account_id':			move_line.account_id.id,
			'amount_original':		move_line.debit,
			'amount_unreconciled':	move_line.debit,
			'reconcile':			True,
			'amount':				move_line.debit,
			'type':					'cr',
			'name':					move_line.name,
			'company_id':  			company_id
		}))
		

		voucher_id = self.pool.get('account.voucher').create(cr,uid,{
			'partner_id' 	: partner_id,
			'amount' 		: amount,
			'account_id'	: journal.default_debit_account_id.id,
			'journal_id'	: journal.id,
			'reference' 	: 'payment #',
			'name' 			: 'payment #',
			'company_id' 	: company_id,
			'type'			: 'receipt',
			'line_ids'		: voucher_lines
		    })
		print "created payment id:%d" % (voucher_id)
		return voucher_id

	####################################################################################
	#mencari partner berdasarkan POS_GROUP_ID, 
	#untuk partner OMC
	####################################################################################
	def find_partner_by_pos_group_id(self, cr, uid, pos_group_id, context=None ):
		partner_obj = self.pool.get('res.partner')
		partner_ids = partner_obj.search(cr, uid, [
			('pos_group_id','=', pos_group_id )
			], context=context)
		partner     = partner_obj.browse(cr,uid,partner_ids[0])
		print partner.name 
		if partner:
			return partner
		else:
			return False

	####################################################################################
	#mencari partner berdasarkan CLIENT_ID 
	#untuk partner retail cusomter postpaid/prepaid
	####################################################################################
	def find_partner_by_client_id(self, cr, uid, client_id, context=None ):
		partner_obj = self.pool.get('res.partner')
		partner_ids = partner_obj.search(cr, uid, [
			('id','=', client_id )
			], context=context)
		partner     = partner_obj.browse(cr,uid,partner_ids[0])
		print partner.name 
		if partner:
			return partner
		else:
			return False

	####################################################################################
	#set open/validate
	####################################################################################
	def invoice_confirm(self, cr, uid, id, context=None):
		wf_service = netsvc.LocalService('workflow')
		wf_service.trg_validate(uid, 'account.invoice', id , 'invoice_open', cr)
		return True

	####################################################################################
	#set done
	####################################################################################
	def payment_confirm(self, cr, uid, vid, context=None):
		wf_service = netsvc.LocalService('workflow')
		wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
		return True

	####################################################################################
	#additional columns 
	####################################################################################
	_columns = {
        'card_no'		: fields.char('Card Number'),
		'at_limit'		: fields.integer('Alert Limit', translate=True),
		'nt_limit'		: fields.integer('Notification Limit', translate=True),
		'pos_group_id' 	: fields.integer("POS Group ID"),
		'service_type'	: fields.selection([('none','None'),
							('loyalty', 'Loyalty'),
							('postpaid', 'Postpaid'),
							('prepaid', 'Prepaid')], string="Service Type")
	}
res_partner()

