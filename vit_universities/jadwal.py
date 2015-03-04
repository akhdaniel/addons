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
		jurusan = vals['jurusan_id']
		prodi = vals['prodi_id']
		semester = vals['semester_id']
		ruangan = vals['ruangan_id']
		hari = vals['hari']
		sesi = vals['sesi']		
		jad_obj = self.pool.get('master.jadwal')
		jad_id = jad_obj.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
			('fakultas_id','=',fakultas),
			('jurusan_id','=',jurusan),
			('prodi_id','=',prodi),
			('semester_id','=',semester),
			('ruangan_id','=',ruangan),	
			('hari','=',hari),
			('sesi','=',sesi),
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
		'name'  : fields.char('Kode',size=30,required=True),
		'mata_kuliah_id' :fields.many2one('master.matakuliah',string='Mata Kuliah',required=True),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True),
		'jurusan_id':fields.many2one('master.jurusan',string='Jurusan',required=True),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required=True),
		'semester_id':fields.many2one('master.semester',string='Semester',required=True),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',required=True), 
		'ruangan_id' :fields.many2one('master.ruangan',string='Ruangan',required=True),                
		'employee_id' :fields.many2one('hr.employee','Dosen', domain="[('is_dosen','=',True)]",required=True),
		'sesi':fields.integer('Sesi/Jam ke-',required=True),
		'hari':fields.selection([('senin','Senin'),('selasa','Selasa'),('rabu','Rabu'),('kamis','Kamis'),('jumat','Jum\'at'),('sabtu','Sabtu'),('minggu','Minggu')],'Hari',required=True),
		'is_active':fields.boolean('Aktif'),
		
		'partner_id':fields.many2one('res.partner'),
		'kurikulum_id':fields.many2one('master.kurikulum'),

			}
			
	_defaults= {
		'sesi':1,
		'is_active':True,
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'master.jadwal'), 
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode jadwal tidak boleh sama')]

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in un active"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.is_active == True:
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus tidak aktif'))
		return super(master_jadwal, self).unlink(cr, uid, ids, context=context)

master_jadwal()