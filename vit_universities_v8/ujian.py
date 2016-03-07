from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class peserta_ujian (osv.osv):
	_name = 'peserta.ujian'

	def create(self, cr, uid, vals, context=None):
		ajaran 		= vals['tahun_ajaran_id']
		fakultas 	= vals['fakultas_id']
		prodi 		= vals['prodi_id']
		kelas 		= vals['kelas_id']
		jenis 		= vals['jenis_ujian']
		semester 	= vals['semester_id']
		kls_obj 	= self.pool.get('master.kelas')
		rg_obj 		= self.pool.get('master.ruangan')	
		jad_id 		= self.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
			('fakultas_id','=',fakultas),
			('prodi_id','=',prodi),
			('kelas_id','=',kelas),
			('jenis_ujian','=',jenis),
			('semester_id','=',semester)
			('is_active','=',True),])

		if jad_id != [] :
			raise osv.except_osv(_('Error!'), _('Jadwal tersebut sudah ada!'))
		return super(peserta_ujian, self).create(cr, uid, vals, context=context)   

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
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required=True,),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',required=True,), 
		'semester_id':fields.many2one('master.semester',string='Semester',required=True,),              
		'is_active':fields.boolean('Aktif'),
		'date_from' : fields.date('Tanggal Mulai'),
		'date_to' : fields.date('Tanggal Selesai'),
		'jenis_ujian' : fields.selection([('uts','UTS'),('uas','UAS')],'Jenis Ujian',required=True),
		'partner_ids':fields.many2many(
			'res.partner',   	# 'other.object.name' dengan siapa dia many2many
			'peserta_ujian_rel',          # 'relation object'
			'peserta_ujian_id',               # 'actual.object.id' in relation table
			'partner_id',           # 'other.object.id' in relation table
			'Mahasiswa',              # 'Field Name'
			domain="[('status_mahasiswa','=','Mahasiswa'), \
			('tahun_ajaran_id','=',tahun_ajaran_id),\
			('fakultas_id','=',fakultas_id),\
			('prodi_id','=',prodi_id),\
			('kelas_id','=',kelas_id)]",
			readonly=True),

			}
			
	_defaults= {
		'is_active':True,
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'peserta.ujian'), 
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode jadwal tidak boleh sama')]

	def get_peserta_ujian(self,cr,uid,ids,context=None):
		for my_form in self.browse(cr,uid,ids):
			angkatan 	= my_form.tahun_ajaran_id.id
			fakultas 	= my_form.fakultas_id.id
			prodi 		= my_form.prodi_id.id
			kelas 		= my_form.kelas_id.id
			jenis_ujian = my_form.jenis_ujian
			semester 	= my_form.semester_id.id

			par_obj = self.pool.get('res.partner')
			par_ids = par_obj.search(cr, uid, [
				('status_mahasiswa','=','Mahasiswa'),
				('tahun_ajaran_id','=',angkatan),
				('fakultas_id','=',fakultas),
				('prodi_id','=',prodi),
				('kelas_id','=',kelas),
				], context=context)			
			if jenis_ujian == 'uts' :
				peserta_kelas_ids = [(6,0,par_ids)]
			else :
				cr.execute("""SELECT rp.id
					FROM res_partner rp
					LEFT JOIN operasional_krs ok on ok.partner_id = rp.id
					LEFT JOIN account_invoice ai on ai.krs_id = ok.id 
					WHERE rp.status_mahasiswa = 'Mahasiswa'
					AND rp.kelas_id = """+ str(kelas) +"""
					AND ok.semester_id ="""+ str(semester) +"""
					AND ai.state is not null
					GROUP BY rp.id
					""")		   
				peserta = cr.fetchall()	
				peserta_kelas_punya_inv = map(lambda x: x[0], peserta)

				cr.execute("""SELECT rp.id
					FROM res_partner rp
					LEFT JOIN operasional_krs ok on ok.partner_id = rp.id
					LEFT JOIN account_invoice ai on ai.krs_id = ok.id 
					WHERE rp.status_mahasiswa = 'Mahasiswa'
					AND rp.kelas_id = """+ str(kelas) +"""
					AND ok.semester_id ="""+ str(semester) +"""
					AND ai.state not in ('paid','cancel')
					GROUP BY rp.id
					""")		   
				peserta = cr.fetchall()	
				peserta_kelas_inv_unpaid = map(lambda x: x[0], peserta)
				peserta_kelas = []
				#import pdb;pdb.set_trace()
				for mhs in peserta_kelas_punya_inv:
					if mhs not in peserta_kelas_inv_unpaid:
						peserta_kelas.append(mhs)

				peserta_kelas_ids = [(6,0,peserta_kelas)]
			self.write(cr,uid,my_form.id,{'partner_ids':peserta_kelas_ids,},context=context)

		return True

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.is_active :
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus non active'))
		return super(peserta_ujian, self).unlink(cr, uid, ids, context=context)	