from openerp.osv import fields, osv

class hr_employee (osv.Model):
	_inherit = 'hr.employee'
	_name = 'hr.employee'

	def _get_master_jadwal(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}
		emp_id = self.browse(cr,uid,ids[0],context=context).id
		#import pdb;pdb.set_trace()
		jad_obj = self.pool.get('master.jadwal')
		jad_ids = jad_obj.search(cr, uid, [
			('employee_id','=',emp_id),
			('is_active','=',True)], context=context)
		if jad_ids == []:
			return result		
		result[emp_id] = jad_ids
		return result

	_columns = {
		'is_dosen':fields.boolean('Dosen'),
		'master_jadwal_ids': fields.function(_get_master_jadwal, type='many2many', relation="master.jadwal", string="Jadwal Mengajar"),    		
	}

hr_employee()	