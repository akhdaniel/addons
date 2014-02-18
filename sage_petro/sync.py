from datetime import datetime
from openerp.osv import osv, fields
import psycopg2

EXCH_HOST = "127.0.0.1"
EXCH_DB = "card"
EXCH_USER = "postgres"
EXCH_PASS = "123456"
LOYALTY_PRODUCT_ID = 3

class res_partner(osv.osv):
	_description = 'Partner'
	_name = "res.partner"
	_inherit = "res.partner"
	con = None
	cur = None

	def connect_petro(self, cr, uid, context=None):
		conn_string2 = "host='"+EXCH_HOST+"' dbname='" + EXCH_DB + "' user='"+EXCH_USER+"' password='"+EXCH_PASS+"'"
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

	def write(self, cr, uid, ids, vals, context=None):
		if isinstance(ids, (int, long)):
			ids = [ids]
		result = super(res_partner,self).write(cr, uid, ids, vals, context=context)

		self.connect_petro(cr, uid, context)
		for partner in self.browse(cr, uid, ids, context=context):
			self.update_client(cr, uid, partner)
			self.update_client_account(cr, uid, partner)

		if self.con:
			self.con.close()

		return result

	def read_trans(self, cr, uid, context=None):
		self.connect_petro(cr, uid, context)


		# cari record yang p_date>p_date_exchange:
		# p_date = timestamp dari petro ketika dia update/create record
		# p_date_exchange = timestamp openerp ketika selesai proses record ini
		sql = """SELECT * FROM erpexchange."TRANSACTIONS" WHERE "P_DATE">"P_DATE_EXCHANGE" OR "P_DATE_EXCHANGE" IS NULL"""
		self.cur.execute(sql)

		rows = self.cur.fetchall()
		for row in rows:
			"""
			P_DATETIME
			P_CLIENT_ID
			P_POS_NUMBER
			P_CLIENT_TYPE
			P_SERVICE_ID
			P_AMOUNT
			P_TERMINAL_PRICE
			P_TOTAL_AMOUNT
			P_ACTUAL_PRICE
			P_TOTAL_AMOUNT_WITHOUT_DISC
			P_GUID
			P_OPERATION_ID
			P_COMMENT
			P_DATE
			P_DATE_EXCHANGE
			"""

			# create Journal Entries/ atau Invoice berdasarkan record transaksi 

			# selesai proses , set p_date_exchange = now
			sql = """UPDATE erpexchange."TRANSACTIONS" SET "P_DATE_EXCHANGE"='%s' WHERE "P_GUID"='%s'""" % (
				datetime.now(), row[10])

			self.cur.execute(sql)
			self.con.commit()

		if self.con:
			self.con.close()

		return True 

	def read_bonus(self, cr, uid, context=None):
		self.connect_petro(cr, uid, context)
		self.read_bonus_by_operation(cr, uid, "accum", context)
		self.read_bonus_by_operation(cr, uid, "remove", context)
		return True 

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
		inv_lines = []
		company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
		product_id 		= LOYALTY_PRODUCT_ID
		product 		= self.pool.get('product.product').browse(cr, uid, product_id, context=context)
		journal_ids = self.pool.get('account.journal').search(cr, uid,[('type', '=', 'sale'), ('company_id', '=', company_id)],limit=1)
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
		partner_id = 0
		ap_account_id = 0
		ar_account_id = 0
		
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
					self.create_customer_invoice( cr, uid, date_invoice, partner_id, ar_account_id, inv_lines, sale_journal_id)
					inv_lines=[]

				inv_lines.append(
					(0,0,{
						'name': "%s %s" % ( product.name , P_POS_NAME),
						'origin':  'interface records',
						'sequence':  '',
						'uos_id':  False,
						'product_id':  product_id,
						'account_id':  product.property_account_income.id, 
						'price_unit':  product.list_price,
						'quantity':  qty, 
						'price_subtotal': product.list_price * qty,  
						'discount':  0,
						'company_id':  company_id,
						'partner_id':  partner_id
					})
				)
			#operation id removal
			elif operation=="remove":
				if P_POS_GROUP_ID != old_pos_group_id and i != 0:
					print 'creating supplier invoice ...'
					self.create_supplier_invoice( cr, uid, date_invoice, partner_id, ap_account_id, inv_lines, purchase_journal_id)
					inv_lines=[]

				inv_lines.append(
					(0,0,{
						'name': "%s %s" % ( product.name , P_POS_NAME),
						'origin':  'interface records',
						'sequence':  '',
						'uos_id':  False,
						'product_id':  product_id,
						'account_id':  product.property_account_expense.id, 
						'price_unit':  product.standard_price,
						'quantity':  -1 * qty, 
						'price_subtotal': -1 * product.standard_price * qty,  
						'discount':  0,
						'company_id':  company_id,
						'partner_id':  partner_id
					})
				)

			i = i + 1
			old_pos_group_id = P_POS_GROUP_ID

			#update partner 
			partner = self.find_partner_by_pos_group(cr,uid,P_POS_GROUP_ID)
			if not partner:
				print 'Please define POS Group ID for this partner.'
				return
			partner_id = partner.id
			ap_account_id = partner.property_account_payable.id
			ar_account_id = partner.property_account_receivable.id 

		if partner_id != 0 and ar_account_id !=0 and operation == "accum":
			print 'creating last customer invoice ...'
			self.create_customer_invoice( cr, uid, date_invoice, partner_id, ar_account_id, inv_lines, sale_journal_id)
			inv_lines=[]
		elif partner_id != 0 and ap_account_id !=0 and operation=="remove":
			print 'creating last supplier invoice ...'
			self.create_supplier_invoice( cr, uid, date_invoice, partner_id, ap_account_id, inv_lines, purchase_journal_id)
			inv_lines=[]				

		# selesai proses , set p_date_exchange = now
		sql = """UPDATE erpexchange."BONUSES" SET "P_DATE_EXCHANGE"='%s' 
			%s """ % (datetime.now(), where )		
		self.cur.execute(sql)
		self.con.commit()
		
		#psycopg2.close()
		return True

	def create_customer_invoice(self, cr, uid, date_invoice, partner_id, account_id, lines , journal_id, context=None):
		invoice_id = self.pool.get('account.invoice').create(cr,uid,{
		    'date_invoice' : date_invoice,
		    'partner_id' : partner_id,
		    'account_id' : account_id,
		    'invoice_line': lines,
		    'type': 'out_invoice',
		    'journal_id': journal_id
		    })		
		print "created customer invoice id:%d" % (invoice_id)
		return True

	def create_supplier_invoice(self, cr, uid, date_invoice, partner_id, account_id, lines , journal_id, context=None ):
		invoice_id = self.pool.get('account.invoice').create(cr,uid,{
		    'date_invoice' : date_invoice,
		    'partner_id' : partner_id,
		    'account_id' : account_id,
		    'invoice_line': lines,
		    'type': 'in_invoice',
		    'journal_id': journal_id		    
		    })
		print "created supplier invoice id:%d" % (invoice_id)
		return True

	def find_partner_by_pos_group(self, cr, uid, pos_group_id, context=None ):
		print pos_group_id
		partner_obj = self.pool.get('res.partner')
		partner_ids = partner_obj.search(cr, uid, [
			('pos_group_id.name','=', pos_group_id )
			], context=context)
		partner     = partner_obj.browse(cr,uid,partner_ids[0])
		print partner.name 
		if partner:
			return partner
		else:
			return False

	_columns = {
        'card_no': fields.char('Card Number'),
		'at_limit': fields.integer('Alert Limit', translate=True),
		'nt_limit': fields.integer('Notification Limit', translate=True),
		'pos_group_id' : fields.many2one("sage_petro.pos_group", "POS Group")
	}
res_partner()

class pos_group(osv.osv):
	_name = "sage_petro.pos_group"
	_columns = {
		'name': fields.integer("Number"),
	}
pos_group()