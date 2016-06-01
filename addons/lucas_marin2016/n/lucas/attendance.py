from openerp.osv import fields, osv
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _

class hr_attendance(osv.osv):

	_name			= "hr.attendance"
	_inherit		= "hr.attendance"
	_description	= "attencance for Lucas Marin"

	def _fill_attendance(self, cr, uid, vals, context=None):
		em = self.pool.get('hr.employee')
		ff = em.search(cr, uid, [('fingerprint_code','=',int(vals['fingerprint_code'])),], context=context)
		if ff == []:
			raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s tidak ada!") % (vals['fingerprint_code']) ))
		vals['employee_id']=ff[0]
		#import pdb;pdb.set_trace()
		vals['name_date']=vals['name'][:10]
		if vals['binary_action'] == '1':
			vals['action']='sign_in'
		elif vals['binary_action'] == '0':
			vals['action']='sign_out'
		# elif vals['binary_action'] == 'action':
		# 	vals['action']='action'
		return vals

	def create(self, cr, uid, vals, context=None):
		# menghitung keterlambatan
		#if vals['binary_action'] == False :
		###########################################################################################
					##import tanpa ada tindakan login atau logout##
		fing_id =vals['fingerprint_code']
		search_emps = self.pool.get('hr.employee').search(cr,uid,[('fingerprint_code','=',fing_id)])[0]
		search_binary = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',search_emps)])
		for emps in self.pool.get('hr.contract').browse(cr,uid,search_binary):
			if emps.date_end == False or emps.date_end >= vals['name'][:10]:
				kon_id = emps.id
		shift_binary = self.pool.get('hr.shift_karyawan').search(cr,uid,[('contract_id','=',kon_id),('date_from','<=',vals['name'][:10]),('date_to','>=',vals['name'][:10])])
		for shf in self.pool.get('hr.shift_karyawan').browse(cr,uid,shift_binary):
			schedules = shf.schedule_id.id
		src_cal = self.pool.get('resource.calendar.attendance').search(cr,uid,[('calendar_id','=',schedules)])
		brw_cal = self.pool.get('resource.calendar.attendance').browse(cr,uid,src_cal)[0]
		hour_from = brw_cal.hour_from
		hour_to = brw_cal.hour_to
		#import pdb;pdb.set_trace()
		ddd = float(vals['name'][5]+vals['name'][12]) + 7
		if hour_from-4 <= ddd and  hour_from + 4 >= ddd :
			vals['binary_action'] = '1'
		if hour_to-4 <= ddd and hour_to+4 >= ddd :
			vals['binary_action'] = '0'
		############################################################################################		 
		
		vals = self._fill_attendance(cr, uid, vals, context=None)
		# cari login lebih awal dan logout lebih akhir
		newestID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '>',vals['name']), ('action', '=', 'sign_in')], limit=1, order='name ASC')
			# menghindari dobel login karena old name < inputed name
		newerID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '<',vals['name']), ('action', '=', 'sign_in')], limit=1, order='name ASC')
		latestID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '<',vals['name']), ('action', '=', 'sign_out')], limit=1, order='name DESC')
			# menghindari dobel logout karena old name > inputed name
		laterID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '>',vals['name']), ('action', '=', 'sign_out')], limit=1, order='name DESC')
		# delete login awal and logout akhir
		if newerID and (vals['action'] =='sign_in'):
			vals ['name'] = self.browse(cr, uid, newerID, context=None)[0].name
			# self.unlink(cr, uid, newerID, context=None)
			cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(newerID),))
		if newestID and (vals['action'] =='sign_in'):
			# self.unlink(cr, uid, newestID, context=None)
			cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(newestID),))
		if laterID and (vals['action'] =='sign_out'):
			vals ['name']= self.browse(cr, uid, laterID, context=None)[0].name
			# self.unlink(cr, uid, laterID, context=None)
			cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(laterID),))
		if latestID and (vals['action'] =='sign_out'):
			#execute to overtime disini
			# self.unlink(cr, uid, latestID, context=None)
			cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(latestID),))
		# execute to overtime
		if (vals['action'] == 'sign_out') and laterID == [] :
			dates = vals['name'] 
			ye = datetime.strptime(dates,"%Y-%m-%d %H:%M:%S")
			date_now = ye.strftime("%Y-%m-%d")
			obj_over = self.pool.get('hr.overtime')
			obj_src = obj_over.search(cr,uid, [('employee_id','=',vals['employee_id']),('tanggal','=',date_now),('state','=','validate')])
			for overtime in obj_over.browse(cr,uid,obj_src) :
				dates_to = datetime.strptime(overtime.date_to,"%Y-%m-%d %H:%M:%S")
				dates_from = datetime.strptime(overtime.date_from,"%Y-%m-%d %H:%M:%S")
				if ye >= dates_to :
					obj_over.write(cr, uid, [overtime.id], {'jam_lembur': overtime.number_of_hours_temp})					
				else :
					timedelta = ye - dates_from
					diff_day1 =float(timedelta.seconds) / 3600
					diff_day2 = int(timedelta.seconds) / 3600
					diff = diff_day1 - diff_day2
					diff1 = (diff*60)/100
					diff_day = diff_day2 + diff1
					obj_over.write(cr, uid, [overtime.id], {'jam_lembur': diff_day})
		# jika diimport / no mesin exist
		emp 	= vals['employee_id']
		date 	= vals['name']
		action	= vals['binary_action']
		if action == '1' :
			contract_obj	= self.pool.get('hr.contract')
			contract_src	=contract_obj.search(cr, uid, [('employee_id','=', emp),('status','=',True)])
			for contract in contract_obj.browse(cr,uid,contract_src) :
				if contract.shift_true == True :
					contract_id = contract.id
					shift_obj	= self.pool.get('hr.shift_karyawan')
					shift_src	= shift_obj.search(cr,uid, [('contract_id','=',contract.id),('date_from','<=',date),('date_to','>=',date)])
					for shift in shift_obj.browse(cr,uid,shift_src) :
						for schedule in shift.schedule_id.attendance_ids :
							hour 					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').hour
							minute					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').minute
							jum_date 				= hour + float('0.'+str(minute)) + 7
							keterlambatan			= jum_date - schedule.hour_from 
							vals['keterlambatan']	= keterlambatan
							#schedule.hour_from -
				else:
					working = contract.working_hours.attendance_ids[0]
					#for schedule in working :
					hour 					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').hour
					minute					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').minute
					jum_date 				= hour + float('0.'+str(minute)) + 7
					keterlambatan			= jum_date - working.hour_from 
					vals['keterlambatan']	= keterlambatan
					#day = datetime_day.strftime("%Y-%m-%d")
					#day_now = (date + timedelta(days=day))
					#day = date.isoweekday()
		if any('no_mesin' in att for att in vals) and vals['no_mesin'] <> '0':
			new_id = super(hr_attendance,self).create(cr,uid,vals,context=context)
			return new_id
		else :
			return super(hr_attendance,self).create(cr,uid,vals,context=context)

	_columns = {
		'keterlambatan'	: fields.char("keterlambatan"),
		'employee_id': fields.many2one('hr.employee', "Employee"),
		"binary_action": fields.selection([('1','Sign In'),('0','Sign Out'),('2','Other')],'Kehadiran'),
	}
