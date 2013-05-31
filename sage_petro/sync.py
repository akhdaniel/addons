from datetime import datetime
from openerp.osv import osv, fields
import psycopg2

EXCH_HOST = "192.168.1.14"
EXCH_DB = "CARDDBLOCAL"
EXCH_USER = "postgres"
EXCH_PASS = "123456"

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


		# cari record yang p_date>p_date_exchange:
		# p_date = timestamp dari petro ketika dia update/create record
		# p_date_exchange = timestamp openerp ketika selesai proses record ini
		sql = """SELECT * FROM erpexchange."BONUSES" WHERE "P_DATE">"P_DATE_EXCHANGE" OR "P_DATE_EXCHANGE" IS NULL"""
		self.cur.execute(sql)

		rows = self.cur.fetchall()
		for row in rows:
			"""
			  "P_DATETIME" numeric(14,0),
			  "P_GUID" character varying(32),
			  "P_CLIENT_ID" character varying(12),
			  "P_CLIENT_TYPE" numeric,
			  "P_OPERATION_ID" numeric, -- Operation type (1,2,3,4,5)
			  "P_COMMENT" character varying(23), -- Comment to OPERATION_ID
			  "P_BONUS" numeric(14,2),
			  "P_POS_ID" numeric(12,0),
			  "P_POS_GROUP_ID" numeric(12,0),
			  "P_DATE" timestamp(0) without time zone,
			  "P_DATE_EXCHANGE" timestamp(0) without time zone			
			"""
			
			# create Journal Entries/ atau Invoice berdasarkan record transaksi 

			# selesai proses , set p_date_exchange = now
			sql = """UPDATE erpexchange."BONUSES" SET "P_DATE_EXCHANGE"='%s' WHERE "P_GUID"='%s'""" % (
				datetime.now(), row[1])

			self.cur.execute(sql)
			self.con.commit()
		return True

	_columns = {
        'card_no': fields.char('Card Number'),
		'at_limit': fields.integer('Alert Limit', translate=True),
		'nt_limit': fields.integer('Notification Limit', translate=True),
	}
