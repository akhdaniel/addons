from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class peserta_ujian (osv.osv):
	_name = 'peserta.ujian'

	# def create(self, cr, uid, vals, context=None):
	# 	ajaran 		= vals['tahun_ajaran_id']
	# 	fakultas 	= vals['fakultas_id']
	# 	matakuliah 	= vals['matakuliah_id']
	# 	prodi 		= vals['prodi_id']
	# 	kelas 		= vals['kelas_id']
	# 	jenis 		= vals['jenis_ujian']
	# 	semester 	= vals['semester_id']
	# 	ruangan 	= vals['ruangan_id']
	# 	kls_obj 	= self.pool.get('master.kelas')
	# 	rg_obj 		= self.pool.get('master.ruangan')	
	# 	jad_id 		= self.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
	# 		('fakultas_id','=',fakultas),
	# 		('prodi_id','=',prodi),
	# 		('kelas_id','=',kelas),
	# 		('jenis_ujian','=',jenis),
	# 		('semester_id','=',semester),
	# 		('matakuliah_id','=',matakuliah,),
	# 		('is_active','=',True)])

	# 	if jad_id != [] :
	# 		raise osv.except_osv(_('Error!'), _('Jadwal tersebut sudah ada!'))
	# 	return super(peserta_ujian, self).create(cr, uid, vals, context=context)   

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
		'name'  					: fields.char('Kode',size=30,required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'fakultas_id'				: fields.many2one('master.fakultas',string='Fakultas',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'tahun_ajaran_id'			: fields.many2one('academic.year',string='Tahun Akademik',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'prodi_id'					: fields.many2one('master.prodi',string='Program Studi',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'tahun_ajaran_id'			: fields.many2one('academic.year',string='Tahun Akademik',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'kelas_id'					: fields.many2one('master.kelas',string='Kelas',readonly=True, states={'draft': [('readonly', False)]}), 
		'semester_id'				: fields.many2one('master.semester',string='Semester',required=True,readonly=True, states={'draft': [('readonly', False)]}),  
		'matakuliah_id' 			: fields.many2one('master.matakuliah',string='Mata Kuliah',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'ruangan_id' 				: fields.many2one('master.ruangan',string='Ruangan',required=True,readonly=True, states={'draft': [('readonly', False)]}),                
		'employee_id' 				: fields.many2one('hr.employee','Dosen', domain="[('is_dosen','=',True)]",readonly=True, states={'draft': [('readonly', False)]}),		            
		'is_active'					: fields.boolean('Aktif',readonly=True, states={'draft': [('readonly', False)]}),
		'date'						: fields.date('Tanggal Ujian',readonly=True,states={'draft': [('readonly', False)]}),
		'date_from' 				: fields.date('Tanggal Awal Input Nilai Ujian',readonly=True, states={'draft': [('readonly', False)]}),
		'date_to' 					: fields.date('Tanggal Akhir Input Nilai Ujian',readonly=True, states={'draft': [('readonly', False)]}),
		'hours_from' 				: fields.float('Jam Mulai',readonly=True,states={'draft': [('readonly', False)]}),
		'hours_to' 					: fields.float('Jam Selesai',readonly=True, states={'draft': [('readonly', False)]}),
		'jenis_ujian' 				: fields.selection([('uts','UTS'),('uas','UAS')],'Jenis Ujian',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'state'  					: fields.selection([('draft','Draft'),('confirm','Confirmed'),('done','Done')],'Status'),
		'pengawas' 					: fields.char('Pengawas',size=128, readonly=True, states={'draft': [('readonly', False)]}),
		'peserta_ujian_detail_ids' 	: fields.one2many('peserta.ujian.detail','ujian_id','Mahasiswa'),
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
			('kelas_id','=',kelas_id)]"),

			}
			
	_defaults= {
		'is_active':True,
		'state':'draft',
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
			#import pdb;pdb.set_trace()
			par_obj = self.pool.get('res.partner')
			# par_ids = par_obj.search(cr, uid, [
			# 	('status_mahasiswa','=','Mahasiswa'),
			# 	('tahun_ajaran_id','=',angkatan),
			# 	('fakultas_id','=',fakultas),
			# 	('prodi_id','=',prodi),
			# 	('kelas_id','=',kelas),
			# 	], context=context)			
			# if jenis_ujian == 'uts' :
			# 	peserta_kelas_ids = [(6,0,par_ids)]
			# else :
			# cr.execute("""SELECT rp.id
			# 	FROM res_partner rp
			# 	LEFT JOIN operasional_krs ok on ok.partner_id = rp.id
			# 	LEFT JOIN account_invoice ai on ai.krs_id = ok.id 
			# 	WHERE rp.status_mahasiswa = 'Mahasiswa'
			# 	AND rp.kelas_id = """+ str(kelas) +"""
			# 	AND ok.semester_id ="""+ str(semester) +"""
			# 	AND ai.state is not null
			# 	GROUP BY rp.id
			# 	""")		   
			# peserta = cr.fetchall()	
			# peserta_kelas_punya_inv = map(lambda x: x[0], peserta)

			cr.execute("""SELECT rp.id,ai.state
				FROM res_partner rp
				LEFT JOIN operasional_krs ok on ok.partner_id = rp.id
				LEFT JOIN account_invoice ai on ai.krs_id = ok.id 
				WHERE rp.status_mahasiswa = 'Mahasiswa'
				AND rp.kelas_id = """+ str(kelas) +"""
				AND ok.semester_id ="""+ str(semester) +"""
				
				GROUP BY rp.id,ai.state
				""")	
				#AND ai.state not in ('paid','cancel','draft')	   
			peserta = cr.fetchall()	
			#peserta_kelas_inv = map(lambda x: x[0], peserta)
			# = []
			#import pdb;pdb.set_trace()
			no = 1
			partner = []
			peserta_obj = self.pool.get('peserta.ujian.detail')
			for mhs in peserta:
				if mhs[1] == 'open' :
					continue
				if mhs[0] not in partner:
					partner_exist = peserta_obj.search(cr,uid,[('partner_id','=',mhs[0]),('ujian_id','=',my_form.id)])
					if not partner_exist :
						peserta_obj.create(cr,uid,{'ujian_id' 	: my_form.id,
													'name'		: no,
													'partner_id': mhs[0],
													'state'		: 'draft'})
						#peserta_kelas.append([0,0,{'partner_id': mhs[0],'name':no,'state':'draft'}])
						no += 1
						partner.append(mhs[0])

			#peserta_kelas_ids = [peserta_kelas]
			#self.write(cr,uid,my_form.id,{'peserta_ujian_detail_ids':peserta_kelas_ids,},context=context)

		return True

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft' :
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(peserta_ujian, self).unlink(cr, uid, ids, context=context)	

	def confirm(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			if not ct.peserta_ujian_detail_ids :
				raise osv.except_osv(_('Error!'), _('Peserta kelas tidak boleh kosong !'))
			self.write(cr,uid,ct.id,{'state':'confirm'},context=context)
			for det in ct.peserta_ujian_detail_ids:
				self.pool.get('peserta.ujian.detail').write(cr,uid,det.id,{'state':'confirm'},context=context)
		return True	

	def done(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			if not ct.peserta_ujian_detail_ids :
				raise osv.except_osv(_('Error!'), _('Pesertakelas tidak boleh kosong !'))
			self.write(cr,uid,ct.id,{'state':'done'},context=context)
			for det in ct.peserta_ujian_detail_ids:
				self.pool.get('peserta.ujian.detail').write(cr,uid,det.id,{'state':'done'},context=context)
		return True

	def cancel(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'state':'draft'},context=context)
			for det in ct.peserta_ujian_detail_ids:
				self.pool.get('peserta.ujian.detail').write(cr,uid,det.id,{'state':'draft'},context=context)
		return True	


class peserta_ujian_detail(osv.osv):
	_name = 'peserta.ujian.detail'
	_order = 'name'

	_columns = {
		'ujian_id'		:fields.many2one('peserta.ujian','Ujian ID'),
		'name' 			:fields.integer('No Kursi'),
		'partner_id'	:fields.many2one('res.partner','Mahasiswa', domain="[('status_mahasiswa','=','Mahasiswa')]",required = True),              
		'absensi'		:fields.boolean('Absensi',),
		'state'			:fields.selection([('draft','Draft'),('confirm','Confirmed'),('done','Done')],'Status'),
		}

	_defaults= {
		'state':'draft',
	}

peserta_ujian_detail()


# select pud.id
# from peserta_ujian_detail pud
# left join peserta_ujian pu on pu.id=ujian_id
# where '2016-06-10' between '2016-06-11' and '2016-06-25'