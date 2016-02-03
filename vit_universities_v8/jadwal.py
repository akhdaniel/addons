from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class master_jadwal (osv.osv):
	_name = 'master.jadwal'

	def create(self, cr, uid, vals, context=None):
		ajaran 		= vals['tahun_ajaran_id']
		fakultas 	= vals['fakultas_id']
		prodi 		= vals['prodi_id']
		semester 	= vals['semester_id']
		ruangan 	= vals['ruangan_id']
		hari 		= vals['hari']
		kelas 		= vals['kelas_id']
		hours_from 	= vals['hours_from']	
		hours_to 	= vals['hours_to']	
		kls_obj 	= self.pool.get('master.kelas')
		rg_obj 		= self.pool.get('master.ruangan')	
		jad_obj 	= self.pool.get('master.jadwal')
		jad_id 		= jad_obj.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
			('fakultas_id','=',fakultas),
			('prodi_id','=',prodi),
			('semester_id','=',semester),
			('ruangan_id','=',ruangan),	
			('hari','=',hari),
			('hours_from','>=',hours_from),
			('hours_to','<=',hours_to),
			('is_active','=',True),])

		if jad_id != [] :
			raise osv.except_osv(_('Error!'), _('Jadwal tersebut sudah ada!'))
		kapasitas_ruangan 	= rg_obj.browse(cr,uid,ruangan).kapasitas	
		hasil = 0 
		sql = "select count(partner_id) from kelas_mahasiswa_rel where kelas_id = %s" % (kelas)
		cr.execute(sql)
		hasil = cr.fetchone()		
		if hasil and hasil[0] != None:
			hasil = hasil[0]
			if hasil > kapasitas_ruangan :
				raise osv.except_osv(_('Error!'), _('Peserta kelas (%s) melebihi kapasitas ruangan (%s) !')%(hasil,kapasitas_ruangan))
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
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required=True,),
		'semester_id':fields.many2one('master.semester',string='Semester',required=True),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',required=True,), 
		'ruangan_id' :fields.many2one('master.ruangan',string='Ruangan',required=True),                
		'employee_id' :fields.many2one('hr.employee','Dosen Utama', domain="[('is_dosen','=',True)]",required=True),
		'sks' : fields.float('SKS'),
		'employee_id2' :fields.many2one('hr.employee','Dosen Pengganti 1', domain="[('is_dosen','=',True)]"),
		'sks2' : fields.float('SKS'),
		'employee_id3' :fields.many2one('hr.employee','Dosen Pengganti 2', domain="[('is_dosen','=',True)]"),
		'sks3' : fields.float('SKS'),
		'wali_id' :fields.many2one('hr.employee','Dosen Wali', domain="[('is_dosen','=',True)]",),
		'sesi':fields.integer('Total Sesi',required=True),
		'hari':fields.selection([('senin','Senin'),('selasa','Selasa'),('rabu','Rabu'),('kamis','Kamis'),('jumat','Jum\'at'),('sabtu','Sabtu'),('minggu','Minggu')],'Hari',required=True),
		'is_active':fields.boolean('Aktif'),
		
		'partner_id':fields.many2one('res.partner',"Partner"),
		'kurikulum_id':fields.many2one('master.kurikulum',"Kurikulum"),
		'hours_from' : fields.float('Jam Mulai'),
		'hours_to' : fields.float('Jam Selesai'),

			}
			
	_defaults= {
		'sesi':14,
		'is_active':True,
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'master.jadwal'), 
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode jadwal tidak boleh sama')]