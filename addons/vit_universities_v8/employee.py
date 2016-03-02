from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class hr_employee (osv.Model):
	_inherit = 'hr.employee'
	_name = 'hr.employee'

	def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		ids = []
		if name:
			ids = self.search(cr, user, ['|','|',('name', operator, name),('otherid', operator, name)] + args, limit=limit)
		else:
			ids = self.search(cr, user, args, context=context, limit=limit)
		return self.name_get(cr, user, ids, context=context)


	# def name_get(self, cr, uid, ids, context=None):
	# 	if not ids:
	# 		return []
	# 	if isinstance(ids, (int, long)):
	# 				ids = [ids]
	# 	reads = self.read(cr, uid, ids, ['name', 'kode'], context=context)
	# 	res = []
	# 	for record in reads:
	# 		name = record['name']
	# 		if record['kode']:
	# 			name = record['kode'] + ' ' + name
	# 		res.append((record['id'], name))
	# 	return res	

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
		'nip': fields.char('NIP'),
		'nidn': fields.char('NIDN'),
		'master_jadwal_ids': fields.function(_get_master_jadwal, type='many2many', relation="master.jadwal", string="Jadwal Mengajar"),    		
	}

hr_employee()	