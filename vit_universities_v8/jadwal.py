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
		employee 	= vals['employee_id']
		
		hours_from 	= vals['hours_from']	
		hours_to 	= vals['hours_to']	
		kls_obj 	= self.pool.get('master.kelas')
		rg_obj 		= self.pool.get('master.ruangan')	
		jad_obj 	= self.pool.get('master.jadwal')

		alamat 		= rg_obj.browse(cr,uid,ruangan).alamat_id.id
		
		jad_ids		= jad_obj.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
			('fakultas_id','=',fakultas),
			('prodi_id','=',prodi),
			('semester_id','=',semester),
			('employee_id','=',employee),
			('ruangan_id','=',ruangan),	
			#('alamat_id','!=',alamat),	
			('hari','=',hari),
			('hours_from','>=',hours_from),
			('hours_to','<=',hours_to),
			('is_active','=',True),])

		if jad_ids :
			raise osv.except_osv(_('Error!'), _('Jadwal tersebut sudah ada!'))

		# pastikan satu dosen hanya mengajar di satu lokasi kampus perhari
		# jad2_ids		= jad_obj.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
		# 	('fakultas_id','=',fakultas),
		# 	('prodi_id','=',prodi),		
		# 	('hari','=',hari),	
		# 	('semester_id','=',semester),
		# 	('employee_id','=',employee),
		# 	('alamat_id','!=',alamat),	
		# 	('is_active','=',True),])

		# if jad2_ids :
		# 	raise osv.except_osv(_('Error!'), _('Satu dosen tidak boleh mengajar lebih dari satu lokasi kampus perhari !'))

		#import pdb;pdb.set_trace()
		# pastikan satu dosen tidak boleh over lap jam
		jad3_ids		= jad_obj.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
			('fakultas_id','=',fakultas),
			('prodi_id','=',prodi),		
			('hari','=',hari),	
			('semester_id','=',semester),
			('employee_id','=',employee),
			('hours_to','>=',hours_from-2),	
			('is_active','=',True),])

		if jad3_ids :
			raise osv.except_osv(_('Error!'), _('Jadwal bentrok kurang dari 2 jam !'))

		jad4_ids		= jad_obj.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
			('fakultas_id','=',fakultas),
			('prodi_id','=',prodi),		
			('hari','=',hari),	
			('semester_id','=',semester),
			('employee_id','=',employee),
			('hours_from','<=',hours_to),	
			('is_active','=',True),])

		if jad3_ids :
			raise osv.except_osv(_('Error!'), _('Jadwal Overlap jam !'))
			
		kapasitas_ruangan 	= rg_obj.browse(cr,uid,ruangan).kapasitas	
		hasil = 0 
		
		if 'kelas_id' in vals:
			kelas 		= vals['kelas_id']
			if kelas :
				sql = "select count(partner_id) from kelas_mahasiswa_rel where kelas_id = %s" % (kelas)
				cr.execute(sql)
				hasil = cr.fetchone()		
				if hasil and hasil[0] != None:
					hasil = hasil[0]
					if hasil > kapasitas_ruangan :
						raise osv.except_osv(_('Error!'), _('Peserta kelas (%s) melebihi kapasitas ruangan (%s) !')%(hasil,kapasitas_ruangan))
		return super(master_jadwal, self).create(cr, uid, vals, context=context)   

	# def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
	# 	if not args:
	# 		args = []
	# 	if context is None:
	# 		context = {}
	# 	ids = []
	# 	if name:
	# 		ids = self.search(cr, user, [('name','=',name)] + args, limit=limit, context=context)
	# 	if not ids:
	# 		ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
	# 	return self.name_get(cr, user, ids, context)

	def name_get(self, cr, uid, ids, context=None):
		
		if not ids:
			return []
		if isinstance(ids, (int, long)):
					ids = [ids]
		reads = self.read(cr, uid, ids, ['name', 'mata_kuliah_id','employee_id','ruangan_id','hari','hours_from','hours_to'], context=context)
		res = []
		for record in reads:
			kode 		= record['name']
			dosen 		= record['employee_id']
			ruangan 	= record['ruangan_id']
			hari 		= record['hari']
			hours_from 	= record['hours_from']
			hours_to 	= record['hours_to']
			name 		= kode+' | '+dosen[1]+' | '+ruangan[1]+' | '+hari+' | '+str(hours_from)+'-'+str(hours_to)
			res.append((record['id'], name))
		return res

	def _get_sisa_peserta(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}
		#import pdb;pdb.set_trace()
		booking_jadwal_obj = self.pool.get('operasional.krs_detail.mahasiswa')
		for jad in self.browse(cr,uid,ids,context=context):
			kapasitas = jad.ruangan_id.kapasitas
			booking_ids = booking_jadwal_obj.search(cr,1,[('jadwal_id','=',jad.id),('state','=','confirm')])
			if booking_ids :
				sisa = int(len(booking_ids))
				kapasitas = kapasitas - sisa
			result[jad.id] = kapasitas	
			self.write(cr,uid,jad.id,{'sisa_kapasitas_field':kapasitas})	
		return result 
		

	_columns = {
		'name'  : fields.char('Kode',size=30,required=True),
		'mata_kuliah_id' :fields.many2one('master.matakuliah',string='Mata Kuliah',required=True),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required=True,),
		'konsentrasi_id':fields.many2one('master.konsentrasi',string='Konsentrasi'),
		'semester_id':fields.many2one('master.semester',string='Semester',required=True),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',required=False,), 
		'ruangan_id' :fields.many2one('master.ruangan',string='Ruangan',required=True),
		'kapasitas' : fields.related('ruangan_id','kapasitas',string='Kapasitas'), 
		'sisa_kapasitas' : fields.function(_get_sisa_peserta,type='integer',string='Sisa Kapasitas (F)'),   
		'sisa_kapasitas_field' : fields.integer('Sisa Kapasitas'),            
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
		'user_id': fields.many2one('res.users','User'),
		'alamat_id'	: fields.related('ruangan_id','alamat_id',relation='master.alamat.kampus',store=True,type='many2one',string='Lokasi Kampus'),

			}
			
	_defaults= {
		'sesi':14,
		'is_active':True,
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'master.jadwal'), 
		'user_id': lambda obj, cr, uid, context: uid,
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode jadwal tidak boleh sama')]