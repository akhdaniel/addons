from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools.translate import _

class employee(osv.osv):
	_name = "hr.employee"
	_inherit = 'hr.employee'

	_columns = {
		'fingerprint_code' : fields.integer('Fingerprint ID'),
		'no_mesin' : fields.integer('No Mesin'),
	}

	# _sql_constraints = [
	#     ('sequence_uniq', 'unique(fingerprint_code)','Fingerprint ID Tidak Boleh Sama')
	# ]
	
class hr_attendance(osv.osv):
	'''
	PPI Absensi
	'''
	_name = "hr.attendance"
	_inherit = "hr.attendance"
	_description = "Attendance for PPI"	

	def _fill_attendance(self, cr, uid, vals, context=None):
		em = self.pool.get('hr.employee')
		ff = em.search(cr, uid, [('fingerprint_code','=',int(vals['fingerprint_code'])),], context=context)
		if ff == []:
			raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s tidak ada!") % (vals['fingerprint_code']) ))
		vals['employee_id']=ff[0]
		vals['name_date']=vals['name'][:10]
		if vals['binary_action'] == '0':
			vals['action']='lieur'
		elif vals['binary_action'] == '1':
			vals['action']='mereun'
		# elif vals['binary_action'] == 'action':
		# 	vals['action']='action'
		return vals

	# def write(self, cr, uid, ids, vals, context=None):
	# 	import pdb;pdb.set_trace()
	# 	if vals['binary_action'] == True :
	# 		if vals['binary_action'] == "0" :
	# 			vals['action'] = "sign_in"
	# 		else :
	# 			vals['action'] = "sign_out"
	# 	return super(hr_attendance, self).write(cr, uid, ids,vals, context=context)
		
	def create(self, cr, uid, vals, context=None):
		vals = self._fill_attendance(cr, uid, vals, context=None)
		# cari login lebih awal dan logout lebih akhir
		newestID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '>=',vals['name']), ('action', '=', 'sign_in')], limit=1, order='name ASC')
			# menghindari dobel login karena old name < inputed name
		newerID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '<',vals['name']), ('action', '=', 'sign_in')], limit=1, order='name ASC')
		latestID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '<=',vals['name']), ('action', '=', 'sign_out')], limit=1, order='name DESC')
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
		if any('no_mesin' in att for att in vals) and vals['no_mesin'] <> '0':
			new_id = super(hr_attendance,self).create(cr,uid,vals,context=context)
			return new_id
		else :
			return super(hr_attendance,self).create(cr,uid,vals,context=context)

	def _get_single_sign(self, cr, uid, ids, field, arg, context=None):
		results = {}
		for absen in self.browse(cr, uid, ids, context=context) :
			employee_id = absen.employee_id.id
			#sign_before = self.search(cr,uid,[('employee_id','=',employee_id),('name','>',absen.name)])
			cr.execute("""Select id From hr_attendance WHERE employee_id = %s and name > %s ORDER BY name ASC""",(employee_id,absen.name,))            
			res = cr.fetchall()
			sign = False
			if res:
				if absen.action == 'sign_in':
					if self.browse(cr,uid,res[0]).action == 'sign_in':
						sign = True
				if absen.action == 'sign_out':
					if self.browse(cr,uid,res[0]).action == 'sign_out':
						sign = True

			results[absen.id] = sign
		return results

	def _onchange_action(self,cr,uid,ids,binary_action,context=None):
		if binary_action == '0' :
			ba = 'sign_in'
		else :
			ba = 'sign_out'
		return {'value':{
			'action' : ba,
		}}

	_columns = {
		"fingerprint_code" : fields.integer('Fingerprint ID', required=True, help="Fingerprint ID"),
		"binary_action": fields.selection([('1','Sign Out'),('0','Sign In'),('2','Other')],'Kehadiran', required=True),
		"no_mesin" : fields.char('No Mesin',size=4, help="Apakah dimport?", required=True),
		"name_date": fields.char('Date', readonly=True),
		'action_desc': fields.many2one("hr.action.reason", "Action Reason", help='Specifies the reason for Signing In/Signing Out in case of extra hours.'),
		'employee_id': fields.many2one('hr.employee', "Employee", required=False, select=True),
		'sign_red' : fields.function(_get_single_sign,'sign red'),	
	}

	_defaults = {
		'no_mesin':'0',
	}

hr_attendance()
