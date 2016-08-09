import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import netsvc
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval
import pprint


class tes_attendance(osv.osv):
	_name	= 'tes.attendance'
	_description = 'tes shift yang kosong'

	_columns = {
		'employee_id' : fields.many2one('hr.employee','Employee'),
		'date' : fields.datetime('datetime'),
	}


class hr_attendance(osv.osv):

	_name			= "hr.attendance"
	_inherit		= "hr.attendance"
	_description	= "attencance for Lucas Marin"

	def _fill_attendance(self, cr, uid, vals, context=None):
		em = self.pool.get('hr.employee')
		ff = em.search(cr, uid, [
			('fingerprint_code','=',int(vals['fingerprint_code'])),
			('no_mesin','=',int(vals['no_mesin'])),
			('work_location2','=',vals['lokasi_kerja'])], context=context)

		if ff == []:
			raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s tidak ada!") % (vals['fingerprint_code']) ))

		vals['employee_id']=ff[0]
		#import pdb;pdb.set_trace()
		#f= datetime.strptime(vals["name"],'%Y-%m-%d %H:%M:%S')+timedelta(hours=7)

		vals['name_date']=vals['name'][:10]
		if vals['binary_action'] == '1':
			vals['action']='sign_in'
		elif vals['binary_action'] == '0':
			vals['action']='sign_out'

		# elif vals['binary_action'] == 'action':
		# 	vals['action']='action'
		#import pdb;pdb.set_trace()

		# kurangi TZ WIB @@
		# vals['name']= str(datetime.strptime(vals["name"],'%Y-%m-%d %H:%M:%S')-timedelta(hours=7))
		return vals

	# add date 7 hours
	def _date(self, cr, uid, vals, context=None):
		vals['name'] = str(datetime.strptime(vals["name"],'%Y-%m-%d %H:%M:%S') )
		# vals['name'] = str(datetime.strptime(vals["name"],'%Y-%m-%d %H:%M:%S')+timedelta(hours=7))
		return vals

	# add date 7 hours
	def _date1(self, cr, uid, hr_from, hr_to, context=None):
		date_ov=[]
		hour_from = str(datetime.strptime(hr_from,'%Y-%m-%d %H:%M:%S') )[11:]
		hour_to = str(datetime.strptime(hr_to,'%Y-%m-%d %H:%M:%S') )[11:]
		# hour_from = str(datetime.strptime(hr_from,'%Y-%m-%d %H:%M:%S')+timedelta(hours=7))[11:]
		# hour_to = str(datetime.strptime(hr_to,'%Y-%m-%d %H:%M:%S')+timedelta(hours=7))[11:]
		date_ov = [hour_from] + [hour_to]
		return date_ov

	def isoweekday(self, cr, uid, vals, context=None):
		datas = datetime.strptime(vals["name"],'%Y-%m-%d %H:%M:%S')
		weekday = date.isoweekday(datas)
		return weekday

	def _altern_si_so(self, cr, uid, ids, context=None):
		return True

	def create(self, cr, uid, vals, context=None):
		# menghitung keterlambatan
		#if vals['binary_action'] == False :
		create_kurang 	= self.pool.get('hr.tampung.error')

		###########################################################################################
		##import tanpa ada tindakan login atau logout##
		###########################################################################################
		fing_id 		= vals['fingerprint_code']
		no_mesin 		= int(vals['no_mesin'])

		# tambahi TZ
		pal 			= vals['name']
		vals 			= self._date(cr, uid, vals, context=None)

		# import ipdb; ipdb.set_trace()

		###########################################################################################
		# cari data employee
		###########################################################################################
		search_emps = self.pool.get('hr.employee').search(cr,uid,[
			('fingerprint_code','=',fing_id),
			('no_mesin','=',no_mesin),
			('work_location2','=',vals['lokasi_kerja'])])
		if search_emps:
			search_emps = search_emps[0]

		else :
			return create_kurang.create(cr,uid,{
				'name':vals['fingerprint_code'],
				'message':'emp not found'})

		###########################################################################################
		# cari data kontrak
		###########################################################################################
		search_binary = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',search_emps)], context=context)
		if self.pool.get('hr.contract').browse(cr,uid,search_binary, context=context) == [] :
			return create_kurang.create(cr,uid,{'name':vals['fingerprint_code'], 'message':'contract not found'})

		for emps in self.pool.get('hr.contract').browse(cr,uid,search_binary, context=context):
			if emps.date_end == False or emps.date_end >= vals['name'][:10]:
				kon_id = emps.id
			else :
				return create_kurang.create(cr,uid,{
					'no_mesin':vals['no_mesin'],
					'lokasi':vals['lokasi_kerja'],
					'department_id':emps.department_id.id,
					'date':vals['name'],
					'name':vals['fingerprint_code'],
					'employee_id':emps.employee_id.id,
					'message':'tanggal kontrak berakhir'})
		shift_binary = 1

		###########################################################################################
		# jika karyawan shift, maka cari shift karyawan
		###########################################################################################
		if emps.shift_true == True :
			shift_binary = self.pool.get('hr.shift_karyawan').search(cr,uid,[
				('contract_id','=',kon_id),
				('date_from','<=',vals['name'][:10]),
				('date_to','>=',vals['name'][:10])], context=context)

		###########################################################################################
		# koding untuk cek karyawan yg tidak punya shift
		###########################################################################################
		if shift_binary == [] :
			x = 1
			values = {
				'employee_id':emps.employee_id.id,
				'date':vals['name']
				}

			emp_id = self.pool.get('tes.attendance').create(cr,uid,values)
			return create_kurang.create(cr,uid,{
				'no_mesin':vals['no_mesin'],
				'lokasi':vals['lokasi_kerja'],
				'department_id':emps.department_id.id,
				'date':vals['name'],
				'name':vals['fingerprint_code'],
				'employee_id':emps.employee_id.id,
				'message':'no shift'})

		###########################################################################################
		# yang punya shift dan jadwal
		###########################################################################################
		else :
			if emps.shift_true == True :
				for shf in self.pool.get('hr.shift_karyawan').browse(cr,uid,shift_binary):
					schedules = shf.schedule_id.id
			else :
				schedules = emps.working_hours.id

			if schedules == False :
				return create_kurang.create(cr,uid,{
					'no_mesin':vals['no_mesin'],
					'lokasi':vals['lokasi_kerja'],
					'department_id':emps.department_id.id,
					'date':vals['name'],
					'name':vals['fingerprint_code'],
					'employee_id':emps.employee_id.id,
					'message':'no schedule'})

			src_cal = self.pool.get('resource.calendar.attendance').search(cr,uid,[('calendar_id','=',schedules)], context=context)
			day = self.isoweekday(cr, uid, vals, context=None)
			x = 1
			daysto2 = 0
			daysto = 0
			hour_from = 1
			c = 0
			for shfatt in self.pool.get('resource.calendar.attendance').browse(cr,uid,src_cal) :
				if int(shfatt.dayofweek)+1 == day :
					daysto1 = shfatt
					if x == 1 :
						daysto = shfatt
					elif x == 2 :
						if emps.shift_true == True :
							if shf.schedule_id.shift_gt_hr == False :
								daysto2 = shfatt
					x = x+1
					c = 1
			cek = 0

			if c == 0 :
				######### cek lembur, jika dia absen di luar shift tapi ternyata dia lembur ########
				obj_ovr = self.pool.get('hr.overtime')
				src_ovr = obj_ovr.search(cr,uid,[
					('employee_id','=',emps.employee_id.id),
					('tanggal','=',vals['name'][:10])], context=context)
				if src_ovr == [] :
					return create_kurang.create(cr,uid,{
						'no_mesin':vals['no_mesin'],
						'lokasi':vals['lokasi_kerja'],
						'department_id':emps.department_id.id,
						'date':vals['name'],
						'name':vals['fingerprint_code'],
						'employee_id':emps.employee_id.id,
						'message':'masalah overtime diluar shift'})
				else :
					for ovr in obj_ovr.browse(cr,uid,src_ovr, context=context):
						hr_from = ovr.date_from
						hr_to = ovr.date_to
						ovrs = self._date1(cr, uid, hr_from, hr_to, context=None)
						hour_from = int(ovrs[0][:2])
						hour_to = int(ovrs[1][:2])
						cek = 1

			# ddd = jam masuk
			ddd = float(vals['name'][11]+vals['name'][12])
			if cek != 1	:
				if emps.shift_true == True :
					if shf.schedule_id.shift_gt_hr == True :
						hour_from    = daysto1.hour_from
					else :
						hour_from = daysto.hour_from
				else :
					hour_from = daysto.hour_from

				if daysto2 == 0 :
					hour_to = daysto.hour_to
				else :
					hour_to = daysto2.hour_to

				# toleransi jam masuk dan jam keluar
				if hour_from-4 <= ddd and  hour_from+2 >= ddd :
					vals['binary_action'] = '1'
				elif hour_to-4  <= ddd :
					vals['binary_action'] = '0'
				else :
					return create_kurang.create(cr,uid,{
						'no_mesin':vals['no_mesin'],
						'lokasi':vals['lokasi_kerja'],
						'department_id':emps.department_id.id,
						'date':vals['name'],
						'name':vals['fingerprint_code'],
						'employee_id':emps.employee_id.id,
						'message':'jam masuk - jam keluar diluar toleransi shift %s-%s' % (hour_from,hour_to)})
			else :
				if hour_from-4 <= ddd and  hour_from+1 > ddd :
					vals['binary_action'] = '1'
				elif hour_from+0.1 <= ddd :
					vals['binary_action'] = '0'
				else :
					return create_kurang.create(cr,uid,{
						'no_mesin':vals['no_mesin'],
						'lokasi':vals['lokasi_kerja'],
						'department_id':emps.department_id.id,
						'date':vals['name'],
						'name':vals['fingerprint_code'],
						'employee_id':emps.employee_id.id,
						'message':'masalah sign-in sign-out'})



			############################################################################################
			# persiapan inser attencance
			############################################################################################
			vals = self._fill_attendance(cr, uid, vals, context=None)

			############################################################################################
			# cari login lebih awal dan logout lebih akhir
			############################################################################################
			newestID = self.search(cr, uid, [
				('employee_id', '=', vals['employee_id']),
				('name_date', '=',vals['name_date']),
				('name', '>=',vals['name']),
				('action', '=', 'sign_in')], limit=1, order='name ASC', context=context)

			############################################################################################
			# menghindari dobel login karena old name < inputed name
			############################################################################################
			newerID = self.search(cr, uid, [
				('employee_id', '=', vals['employee_id']),
				('name_date', '=',vals['name_date']),
				('name', '<',vals['name']),
				('action', '=', 'sign_in')], limit=1, order='name ASC', context=context)

			############################################################################################
			#newID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '=',vals['name']), ('action', '=', 'sign_in')], limit=1, order='name ASC')
			############################################################################################
			latestID = self.search(cr, uid, [
				('employee_id', '=', vals['employee_id']),
				('name_date', '=',vals['name_date']),
				('name', '<=',vals['name']),
				('action', '=', 'sign_out')], limit=1, order='name DESC', context=context)

			############################################################################################
			# menghindari dobel logout karena old name > inputed name
			############################################################################################
			laterID = self.search(cr, uid, [
				('employee_id', '=', vals['employee_id']),
				('name_date', '=',vals['name_date']),
				('name', '>',vals['name']),
				('action', '=', 'sign_out')], limit=1, order='name DESC', context=context)

			############################################################################################
			# delete login awal and logout akhir
			############################################################################################
			if newerID and (vals['action'] =='sign_in'):
				old_date = self.browse(cr, uid, newerID, context=context)[0].name
				vals['name'] = str(datetime.strptime(old_date,'%Y-%m-%d %H:%M:%S') + timedelta(hours=7))
				cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(newerID),))

			if newestID and (vals['action'] =='sign_in'):
				cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(newestID),))

			if laterID and (vals['action'] =='sign_out'):
				vals ['name']= self.browse(cr, uid, laterID, context=None)[0].name
				cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(laterID),))

			if latestID and (vals['action'] =='sign_out'):
				cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(latestID),))

			############################################################################################
			# execute to overtime
			############################################################################################
			if (vals['action'] == 'sign_out') and laterID == []:

				# jika tidak ada record sign in pasangan
				# dan cek jika tidak ada sign_in: insertkan
				# sign in date = date out - jam kerja
				# sign in time = start hour sesuai schedule

				start_date = str(datetime.strptime(vals["name"],'%Y-%m-%d %H:%M:%S')-timedelta(hours=14) -timedelta(hours=7))
				sign_in_id = self.search(cr, uid, [
					('employee_id', '=', vals['employee_id']),
					('name', '>', start_date),
					('action', '=', 'sign_in')], limit=1, order='name DESC', context=context)

				if not sign_in_id:
					v = {}
					v = vals.copy()
					self._create_sign_in(cr, uid, v=v, hour_from=hour_from,  hour_to=hour_to, context=context)

				dates = vals['name']
				ye = datetime.strptime(dates,"%Y-%m-%d %H:%M:%S")
				date_now = ye.strftime("%Y-%m-%d")
				obj_over = self.pool.get('hr.overtime')
				obj_src = obj_over.search(cr,uid, [
                    ('employee_id','=',vals['employee_id']),
                    ('tanggal','=',date_now),('state','=','validate')] , context=context)
				for overtime in obj_over.browse(cr,uid,obj_src, context=context) :
					dates_to = datetime.strptime(overtime.date_to,"%Y-%m-%d %H:%M:%S")
					dates_from = datetime.strptime(overtime.date_from,"%Y-%m-%d %H:%M:%S")
					if ye >= dates_to :
						obj_over.write(cr, uid, [overtime.id], {'jam_lembur': overtime.number_of_hours_temp}, context=context)
					else :
						delta = ye - dates_from
						diff_day1 =float(delta.seconds) / 3600
						diff_day2 = int(delta.seconds) / 3600
						diff = diff_day1 - diff_day2
						diff1 = (diff*60)/100
						diff_day = diff_day2 + diff1
						obj_over.write(cr, uid, [overtime.id], {'jam_lembur': diff_day}, context=context)

			############################################################################################
			# jika diimport / no mesin exist
			############################################################################################
			emp 	= vals['employee_id']
			date 	= vals['name']
			action	= vals['binary_action']
			if action == '1' :
				contract_obj	= self.pool.get('hr.contract')
				contract_src	=contract_obj.search(cr, uid, [('employee_id','=', emp),('status','=',True)], context=context)
				keterlambatan1 = 100
				for contract in contract_obj.browse(cr,uid,contract_src, context=context) :
					if contract.shift_true == True :
						contract_id = contract.id
						shift_obj	= self.pool.get('hr.shift_karyawan')
						shift_src	= shift_obj.search(cr,uid, [
                            ('contract_id','=',contract.id),
                            ('date_from','<=',date),
                            ('date_to','>=',date)], context=context)
						for shift in shift_obj.browse(cr,uid,shift_src, context=context) :
							for schedule in shift.schedule_id.attendance_ids :
								if keterlambatan1 <= 100 :
									keterlambatan1 = 1+100
									hour 					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').hour
									minute					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').minute
									jum_date 				= hour + float('0.'+str(minute))
									keterlambatan			= jum_date - schedule.hour_from
									vals['keterlambatan']	= keterlambatan
									#schedule.hour_from -
					else:
						working = contract.working_hours.attendance_ids[0]
						#for schedule in working :
						hour 					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').hour
						minute					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').minute
						jum_date 				= hour + float('0.'+str(minute))
						keterlambatan			= jum_date - working.hour_from
						vals['keterlambatan']	= keterlambatan



			############################################################################################
			# insert akhirnya..
			############################################################################################
			try:
				if any('no_mesin' in att for att in vals) and vals['no_mesin'] <> '0':
					vals['name'] = str(datetime.strptime(vals["name"], '%Y-%m-%d %H:%M:%S') - timedelta(hours=7))
					new_id = super(hr_attendance,self).create(cr,uid,vals,context=context)
					return new_id
				else :
					return super(hr_attendance,self).create(cr,uid,vals,context=context)
			except Exception, e:
				return create_kurang.create(cr,uid,{
						'no_mesin':vals['no_mesin'],
						'lokasi':vals['lokasi_kerja'],
						'department_id':emps.department_id.id,
						'date':vals['name'],
						'name':vals['fingerprint_code'],
						'employee_id':emps.employee_id.id,
						'message': str(e)})

	def _create_sign_in(self, cr, uid, v=None, hour_from=0, hour_to=0, context=None):
		#kurangi jam shift
		sign_in_date = datetime.strptime(v["name"],'%Y-%m-%d %H:%M:%S')-timedelta(hours=8)
		date = sign_in_date.strftime("%Y-%m-%d")
		sign_in_date = datetime.strptime( date ,'%Y-%m-%d')+timedelta(hours=hour_from - 7)

		v['action'] = 'sign_in'
		v['binary_action'] = '1'
		v['name']=sign_in_date.strftime('%Y-%m-%d %H:%M:%S')
		v['name_date']=sign_in_date.strftime('%Y-%m-%d')
		new_id = super(hr_attendance, self).create(cr, uid, v, context=context)
		return new_id

	_columns = {
		'keterlambatan'	: fields.char("keterlambatan"),
		'employee_id'	: fields.many2one('hr.employee', "Employee"),
		"binary_action"	: fields.selection([('1','Sign In'),('0','Sign Out'),('2','Other')],'Kehadiran'),
	}

	_constraints = [(_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]


class tampung_eror_finger(osv.osv):
	_name = 'hr.tampung.error'
	_description = "untuk menampung eror fingerprint"

	_columns = {
		"name" : fields.integer('Fingerprint ID'),
		'employee_id' : fields.many2one('hr.employee','Karyawan'),
		'department_id' : fields.many2one('hr.department','Department'),
		'lokasi' : fields.char('Lokasi Kerja'),
		'no_mesin' : fields.integer('No Mesin'),
		'date' : fields.char("Date"),
		'message': fields.char("Message"),
	}
tampung_eror_finger()
