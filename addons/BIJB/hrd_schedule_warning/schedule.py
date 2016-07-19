import time
import datetime
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from openerp.osv import fields, osv
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT


class schedeule_warning(osv.osv):
	_name = "schedule.warning"
	_description = " module untuk memberikan warning jika ada kontrak yang mau habis"

	_columns = {
		'name' : fields.selection([('kontrak','Kontrak')], 'Warning',required=True),
		'lama' : fields.integer("Warning/Hari"),
	}
schedeule_warning()

class contract(osv.osv):
	_inherit = "hr.contract"

	def cron_kontrak(self, cr, uid, ids=None,context=None):
		chat_obj        = self.pool.get('im_chat.message')
		conversation_obj= self.pool.get('im_chat.conversation_state')
		session_obj 	= self.pool.get('im_chat.session')

		date 			= fields.date.today()
		date_now 		= datetime.datetime.strptime(date,"%Y-%m-%d")

		obj = self.pool.get("schedule.warning")
		search = obj.search(cr,uid,[('name','=','kontrak')])
		day = obj.browse(cr,uid,search)[0].lama  
		days_warning 	= datetime.timedelta(days=day)
		
		contract_expired = self.search(cr,uid,[('date_end','<',str(date_now+days_warning)),('date_end','>',str(date_now))],context=context)
		contract_expired_3 = self.search(cr,uid,[('date_end','>',str(date_now+days_warning)),('date_end','>',str(date_now))],context=context)
		contract_expired_4 = self.search(cr,uid,[('date_end','=',False)],context=context)
		contract_expired_2 = contract_expired_3 + contract_expired_4

		x = 0
		data = []
		for no in self.browse(cr,uid,contract_expired) :
			for no_1 in self.browse(cr,uid,contract_expired_2) :
				if no.employee_id.id == no_1.employee_id.id :
					x = 1 
			if x != 1:
				data.append(no.id)		 
		
		names = 'Kontrak a/n'
		for name in self.browse(cr,uid,data) :
			names = names + " "+ name.name + ","

		obj = self.pool.get("res.users").search(cr,uid,[('name','=','info')])

		if contract_expired :

			#create sesi chat
			session_id 		= session_obj.create(cr,uid,{})

			#create chat yang di sign ke user warehouse dengan sesi yang di buat sebelumnya
			conversation_obj.create(cr,uid,{'state':'open',
											'session_id':session_id,
											'user_id':1})

			# create message
			if days_warning :
				chat_obj.create(cr,uid,{'create_date':fields.date.today(),
										'from_id':obj[0],
										'to_id':session_id,
										'type':'meta',
										'message':names + 'Sudah Masuk Masa Kaladuarsa'})

			chat_obj.create(cr,uid,{'create_date':fields.date.today(),
										'from_id':obj[0],
										'to_id':session_id,
										'type':'meta',
										'message':'Pemberitahuan ini dibuat oleh sistem, mohon tidak di balas. Terima kasih.'})				

		return True