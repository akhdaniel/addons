from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class master_jadwal (osv.Model):
	_name = 'master.jadwal'

	def create(self, cr, uid, vals, context=None):
		ajaran = vals['tahun_ajaran_id']
		fakultas = vals['fakultas_id']
		# jurusan = vals['jurusan_id']
		prodi = vals['prodi_id']
		semester = vals['semester_id']
		ruangan = vals['ruangan_id']
		hari = vals['hari']
		sesi = vals['sesi']		
		jad_obj = self.pool.get('master.jadwal')
		jad_id = jad_obj.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
			('fakultas_id','=',fakultas),
			# ('jurusan_id','=',jurusan),
			('prodi_id','=',prodi),
			('semester_id','=',semester),
			('ruangan_id','=',ruangan),	
			('hari','=',hari),
			#('sesi','=',sesi),
			('is_active','=',True),])

		if jad_id != [] :
			raise osv.except_osv(_('Error!'), _('Jadwal tersebut sudah ada!'))

		return super(master_jadwal, self).create(cr, uid, vals, context=context)   

	def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		if context is None:
			context = {}
		ids = []
		if name:
			ids = self.search(cr, user, [('name','=',name)] + args, limit=limit, context=context)
		if not ids:
			ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
		return self.name_get(cr, user, ids, context)

	_columns = {
		'name'  : fields.char('Kode',size=30,required=True,readonly=True, states={'open': [('readonly', False)]}),
		'mata_kuliah_id' :fields.many2one('master.matakuliah',string='Mata Kuliah',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'semester_id':fields.many2one('master.semester',string='Semester',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',required=True,readonly=True, states={'open': [('readonly', False)]}), 
		'ruangan_id' :fields.many2one('master.ruangan',string='Ruangan',required=True,readonly=True, states={'open': [('readonly', False)]}),                
		'employee_id' :fields.many2one('hr.employee','Dosen', domain="[('is_dosen','=',True)]",required=True,readonly=True, states={'open': [('readonly', False)]}),
		'wali_id' :fields.many2one('hr.employee','Dosen Wali', domain="[('is_dosen','=',True)]",readonly=True, states={'open': [('readonly', False)]}),
		'sesi':fields.integer('Total Sesi',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'hari':fields.selection([('senin','Senin'),('selasa','Selasa'),('rabu','Rabu'),('kamis','Kamis'),('jumat','Jum\'at'),('sabtu','Sabtu'),('minggu','Minggu')],'Hari',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'is_active':fields.boolean('Aktif'),
		
		'partner_id':fields.many2one('res.partner',"Partner",readonly=True, states={'open': [('readonly', False)]}),
		'kurikulum_id':fields.many2one('master.kurikulum',"Kurikulum",readonly=True, states={'open': [('readonly', False)]}),
		'hours_from' : fields.float('Jam Mulai',readonly=True, states={'open': [('readonly', False)]}),
		'hours_to' : fields.float('Jam Selesai',readonly=True, states={'open': [('readonly', False)]}),

			}
			
	_defaults= {
		'sesi':1,
		'is_active':True,
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'master.jadwal'), 
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode jadwal tidak boleh sama')]