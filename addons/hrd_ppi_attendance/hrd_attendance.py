from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools.translate import _

class employee(osv.osv):
	_name = "hr.employee"
	_inherit = 'hr.employee'

	_columns = {
		'fingerprint_code' : fields.integer('Fingerprint ID', required=True),
	}

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
			raise osv.except_osv(_('Fingerprint Error!'), _("Kode Fingerprint tidak ada!"))
		vals['employee_id']=ff[0]
		vals['name_date']=vals['name'][:10]
		if vals['binary_action'] == '1':
			vals['action']='sign_in'
		elif vals['binary_action'] == '0':
			vals['action']='sign_out'
		elif vals['binary_action'] == 'action':
			vals['action']='action'
		return vals
		
	def create(self, cr, uid, vals, context=None):
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
			# self.unlink(cr, uid, latestID, context=None)
			cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(latestID),))
		# jika diimport / no mesin exist
		if any('no_mesin' in att for att in vals) and vals['no_mesin'] <> '0':
			new_id = super(hr_attendance,self).create(cr,uid,vals,context=context)
			return new_id
		else :
			return super(hr_attendance,self).create(cr,uid,vals,context=context)

	#Sudah embed di hrd_ppi_payroll
	# def _altern_si_so(self, cr, uid, ids, context=None):
	# 	""" Alternance sign_in/sign_out check.
	# 		PPI: All data added, restriction removed
	# 	"""
	# 	return super(hr_attendance,self)._altern_si_so(cr,uid,ids,context=context)

	_columns = {
		"fingerprint_code" : fields.integer('Fingerprint ID', required=True, help="Fingerprint ID"),
		"binary_action": fields.selection([('1','Sign In'),('0','Sign Out'), ('action','Action')],'Cek In & Cek Out', required=True),
		"no_mesin" : fields.char('No Mesin',size=4, help="Apakah dimport?", required=True, readonly=True),
		"name_date": fields.char('Date', readonly=True),
	}

	_defaults = {
		'no_mesin':'0',
	}

hr_attendance()