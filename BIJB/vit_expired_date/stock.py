import time
import datetime
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from openerp.osv import fields, osv
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT

class stock_production_lot(osv.osv):
	_inherit = 'stock.production.lot'

	def get_expired_days(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}

		for obj in self.browse(cr,uid,ids,context=context):
			alert_date = obj.alert_date
			res = 0
			if alert_date :
				date_now = fields.date.today()
				dt_now 	= datetime.datetime.strptime(date_now, '%Y-%m-%d')
				dt_end  = datetime.datetime.strptime(alert_date, '%Y-%m-%d')
				date  	= relativedelta(dt_now,dt_end)
				year 	= date.years
				month 	= date.months
				day 	= date.days

				res 	= -((year*365)+(month*30)+day)

			result[obj.id] = res
			self.write(cr,uid,obj.id,{'expired_days_field':res},context=context)
		return result   


	_columns = {
		'expired_days' : fields.function(get_expired_days,type='integer',string='Expired Date (days)'),
		'expired_days_field' : fields.integer('Expired Days',readonly=True),# diubah ke field biasa agar bisa di search
	}

	# cron utk warning ED injek langsung ke tabel im_chat.message
	def cron_expired_product(self, cr, uid, ids=None,context=None):
		chat_obj        = self.pool.get('im_chat.message')
		conversation_obj= self.pool.get('im_chat.conversation_state')
		session_obj 	= self.pool.get('im_chat.session')
		#import pdb;pdb.set_trace()

		date 			= fields.date.today()
		date_now 		= datetime.datetime.strptime(date,"%Y-%m-%d")

		tiga_bulan 		= datetime.timedelta(days=90)
		enam_bulan 		= datetime.timedelta(days=182)
		dualas_bulan 	= datetime.timedelta(days=365)

		product_expired_date_3_months = self.search(cr,uid,[('alert_date','=',str(date_now-tiga_bulan))],context=context)
		product_expired_date_6_months = self.search(cr,uid,[('alert_date','=',str(date_now-enam_bulan))],context=context)
		product_expired_date_12_months = self.search(cr,uid,[('alert_date','=',str(date_now-dualas_bulan))],context=context)

		if product_expired_date_3_months or product_expired_date_6_months or product_expired_date_12_months :
			# cari user id yang punya akses ke menu warehouse
			cr.execute("""SELECT rgul.uid FROM res_groups_users_rel rgul
							LEFT JOIN res_groups rg ON rg.id = rgul.gid
							LEFT JOIN ir_module_category imc ON imc.id = rg.category_id 
							WHERE imc.name ='Warehouse'
							GROUP BY rgul.uid
							""") 
									  
			user_ids        = cr.fetchall()

			for user_id in user_ids :
				warehouse_user = user_id[0]

				#create sesi chat
				session_id 		= session_obj.create(cr,uid,{})

				#create chat yang di sign ke user warehouse dengan sesi yang di buat sebelumnya
				conversation_obj.create(cr,uid,{'state':'open',
												'session_id':session_id,
												'user_id':warehouse_user})
				# create message
				if product_expired_date_3_months :
					chat_obj.create(cr,uid,{'create_date':fields.date.today(),
											'from_id':1,
											'to_id':session_id,
											'type':'meta',
											'message':str(len(product_expired_date_3_months))+' Batch Number 3 Bulan Lagi Kadaluarsa'})
				if product_expired_date_6_months :
					chat_obj.create(cr,uid,{'create_date':fields.date.today(),
											'from_id':1,
											'to_id':session_id,
											'type':'meta',
											'message':str(len(product_expired_date_6_months))+' Batch Number 6 Bulan Lagi Kadaluarsa'})
				if product_expired_date_12_months :
					chat_obj.create(cr,uid,{'create_date':fields.date.today(),
											'from_id':1,
											'to_id':session_id,
											'type':'meta',
											'message':str(len(product_expired_date_12_months))+' Batch Number 12 Bulan Lagi Kadaluarsa'})
				chat_obj.create(cr,uid,{'create_date':fields.date.today(),
										'from_id':1,
										'to_id':session_id,
										'type':'meta',
										'message':'Pemberitahuan ini dibuat oleh sistem, mohon tidak di balas. Terima kasih.'})														
		return True	