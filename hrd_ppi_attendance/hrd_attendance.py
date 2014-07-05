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
		if vals['binary_action'] == '1':
			vals['action']='sign_in'
		elif vals['binary_action'] == '0':
			vals['action']='sign_out'
		return vals
		
	def create(self, cr, uid, vals, context=None):
		vals = self._fill_attendance(cr, uid, vals, context=None)
		if any('no_mesin' in att for att in vals) and vals['no_mesin'] <> '0':
				new_id = super(hr_attendance,self).create(cr,uid,vals,context=context)
				return new_id
		else :
			return super(hr_attendance,self).create(cr,uid,vals,context=context)

	_columns = {
		"fingerprint_code" : fields.integer('Fingerprint ID', required=True),
		"binary_action": fields.selection([('1','Sign In'),('0','Sign Out')],'Cek In & Cek Out', required=True),
		"no_mesin" : fields.char('No Mesin',size=4),
	}

	_defaults = {
		'no_mesin':'0',
	}

	def _altern_si_so(self, cr, uid, ids, context=None):
		# TGL = vals['name'][:10]
		return super(hr_attendance,self)._altern_si_so(cr,uid,ids,context=context)

hr_attendance()