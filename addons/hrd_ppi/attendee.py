from openerp.osv import fields, osv

class hr_attendance(osv.osv):
	'''
	PPI Absensi
	'''

	_name = "hr.attendance"
	_inherit = "hr.attendance"
	_description = "attendance for PPI"


	_columns = {
		"jam_masuk" : fields.integer('Jam Masuk'),
		"jam_keluar" : fields.integer('jam Keluar'),
		'note' : fields.text('Catatan'),
	}
hr_attendance()