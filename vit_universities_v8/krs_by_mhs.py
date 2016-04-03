from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import netsvc

class operasional_krs_mahasiswa (osv.osv):
	_name= 'operasional.krs.mahasiswa'

	def create(self, cr, uid, vals, context=None):
		if vals.get('name','/')=='/':
			user_obj = self.pool.get('res.users')
			nim = user_obj.browse(cr,uid,uid).partner_id.npm
			if nim == '/':
				raise osv.except_osv(_('Error!'), _('Data tidak bisa disimpan karena anda belum mempunyai NIM !'))
			smt = vals['semester_id']
			smt_name = self.pool.get('master.semester').browse(cr,uid,smt,context=context).name
			vals['name'] = nim +'-'+str(smt_name) or '/'

		return super(operasional_krs_mahasiswa, self).create(cr, uid, vals, context=context)		    

	def _get_default_partner(self, cr, uid, context=None):
		user_obj = self.pool.get('res.users')
		partner_id = user_obj.browse(cr,uid,uid).partner_id.id
		return partner_id
	
	_columns = {
		'name' : fields.char('Kode', 128, readonly=True),
		'state':fields.selection([('draft','Draft'),('confirm','Confirm')],'Status',readonly=True),
		'partner_id' : fields.many2one('res.partner','Mahasiswa', required=True, domain="[('status_mahasiswa','=','Mahasiswa')]",readonly=True),
		'nim' : fields.related('partner_id','npm',type='char', string='NIM',store=True,readonly=True),
		'fakultas_id':fields.related('partner_id','fakultas_id',type='many2one',relation='master.fakultas', string='Fakultas',store=True,readonly=True),         
		'konsentrasi_id':fields.related('partner_id','konsentrasi_id',type='many2one',relation='master.konsentrasi', string='Konsentrasi',store=True,readonly=True),          
		'prodi_id':fields.related('partner_id','prodi_id',type='many2one',relation='master.prodi', string='Prodi',store=True,readonly=True),
		'semester_id':fields.many2one('master.semester','Semester',domain="[('name','>',2)]",required = True),
		'tahun_ajaran_id': fields.related('partner_id','tahun_ajaran_id',type='many2one',relation='academic.year', string='Angkatan',store=True,readonly=True),
		'kelas_id':fields.related('partner_id','kelas_id',type='many2one',relation='master.kelas', string='Kelas',store=True,readonly=True),
		'krs_mhs_ids' : fields.one2many('operasional.krs_detail.mahasiswa','krs_mhs_id','Matakuliah'),
		#'view_ipk_ids' : fields.one2many('operasional.view_ipk','krs_id','Mata Kuliah'),
		'kurikulum_id':fields.many2one('master.kurikulum','Kurikulum'),
		#'ips':fields.function(_get_ips,type='float',string='Indeks Prestasi Kumulatif',),
		'ips_field':fields.float(string='Indeks Prestasi (field)',),
		'ips_field_persemester':fields.float(string='Indeks Prestasi Semester Ini',),
		'user_id':fields.many2one('res.users','User',readonly=True),
		'sks_tot' : fields.integer('Total SKS',readonly=True),
	}    
				 
	_defaults={
		'state' : 'draft', 
		'name': '/',
		'user_id': lambda obj, cr, uid, context: uid,
		'partner_id': _get_default_partner,
	}


	def onchange_semester(self, cr, uid, ids,semester_id, partner_id,context=None):
		results = {}
		if not semester_id:
			return results

		part_obj = self.pool.get('res.partner')	
		partner = part_obj.browse(cr,uid,partner_id)
		tahun_ajaran_id = partner.tahun_ajaran_id.id
		konsentrasi_id	= partner.konsentrasi_id.id
		prodi_id		= partner.prodi_id.id

		kur_obj = self.pool.get('master.kurikulum')
		kur_ids = kur_obj.search(cr, uid, [
			('tahun_ajaran_id','=',tahun_ajaran_id),
			('konsentrasi_id','=',konsentrasi_id),
			('prodi_id','=',prodi_id),
			('state','=','confirm'),
			('semester_id','=',semester_id)], context=context)
		if kur_ids == []:
			raise osv.except_osv(_('Error!'),
								_('Tidak ada kurikulum yang cocok untuk data ini!'))

		#cek partner dan semester yang sama
		krs_uniq = self.search(cr,uid,[('partner_id','=',partner_id),
										('semester_id','=',semester_id),
										('state','in',('draft','confirm'))])
		if krs_uniq != []:
			raise osv.except_osv(_('Error!'),
								_('Pengajuan KRS untuk semester ini sudah pernah dibuat!'))			
		
		kur_id = kur_obj.browse(cr,uid,kur_ids,context=context)[0].kurikulum_detail_ids
		kur_kode = kur_obj.browse(cr,uid,kur_ids,context=context)[0].id
		mk_kurikulum = []
		for kur in kur_id:
			mk_kurikulum.append(kur.id)
	
		#cari matakuliah apa saja yg sdh di tempuh di smt sebelumnya
		cr.execute("""SELECT okd.id, okd.mata_kuliah_id
						FROM operasional_krs_detail okd
						LEFT JOIN operasional_krs ok ON ok.id = okd.krs_id
						WHERE ok.partner_id = %s
						AND ok.state <> 'draft'"""%(partner_id))
		dpt = cr.fetchall()
		
		total_mk_ids = map(lambda x: x[1], dpt)
		#filter matakuliah yg benar-benar belum di tempuh
		mk_baru_ids =set(mk_kurikulum).difference(total_mk_ids)

		res = []
		for kur in mk_baru_ids:
			res.append([0,0,{'mata_kuliah_id': kur,'state':'draft'}])	
		results = {
			'value' : {
				'kurikulum_id': kur_kode,
				'krs_mhs_ids' : res,
			}
		}
		return results 

	def convert_to_krs(self,cr,uid,ids,context=None):
		krs_obj = self.pool.get('operasional.krs')
		kur_obj = self.pool.get('master.kurikulum')
		for pengajuan in self.browse(cr,uid,ids):
			kurikulum = kur_obj.search(cr,1,[('id','=',pengajuan.kurikulum_id.id)])
			max_sks = 0
			if kurikulum :
				max_sks = kur_obj.browse(cr,1,kurikulum[0]).max_sks
			mk_pengajuan = []
			total_sks = 0
			for mk_id in pengajuan.krs_mhs_ids:
				mk_pengajuan.append((0,0,{'mata_kuliah_id'	: mk_id.mata_kuliah_id.id, 'state': 'draft'}))
				self.pool.get('operasional.krs_detail.mahasiswa').write(cr,uid,mk_id.id,{'state':'confirm'})
				total_sks += int(mk_id.mata_kuliah_id.sks)
			if total_sks > max_sks: 
				raise osv.except_osv(_('Error!'), _('Total matakuliah (%s SKS) melebihi batas maximal SKS kurikulum (%s SKS) !')%(total_sks,max_sks))	
			krs_obj.create(cr,1,{'kode'					: str(pengajuan.partner_id.npm)+'-'+str(pengajuan.semester_id.name),
									'partner_id'		: pengajuan.partner_id.id,
									'tahun_ajaran_id'	: pengajuan.tahun_ajaran_id.id,
									'fakultas_id'		: pengajuan.fakultas_id.id,
									'prodi_id'			: pengajuan.prodi_id.id,
									'kurikulum_id'		: pengajuan.kurikulum_id.id,
									'semester_id'		: pengajuan.semester_id.id,
									'kelas_id'			: pengajuan.kelas_id.id or False,
									'user_id'			: uid,
									'konsentrasi_id'	: pengajuan.konsentrasi_id.id,
									#'state'			: 'draft',
									'krs_detail_ids'	: mk_pengajuan
									})	
			self.write(cr,uid,pengajuan.id,{'state':'confirm'})
		return True	

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(operasional_krs_mahasiswa, self).unlink(cr, uid, ids, context=context)

class krs_detail_mahasiswa (osv.osv):
	_name='operasional.krs_detail.mahasiswa'
	_rec_name='krs_mhs_id'
		
	_columns = {
		'krs_mhs_id'	:fields.many2one('operasional.krs.mahasiswa','Kode KRS',),
		'mata_kuliah_id':fields.many2one('master.matakuliah','Matakuliah',required=True),
		'sks'			:fields.related('mata_kuliah_id', 'sks',type='integer',relation='master.matakuliah', string='SKS',readonly=True,store=True),
		'jadwal_id'		:fields.many2one('master.jadwal','Jadwal'),
		'state'			:fields.selection([('draft','Draft'),('confirm','Confirm')],'Status',readonly=False),     
		'prodi_id'		:fields.many2one('master.prodi',string='Program Studi'),
		'semester_id'	:fields.many2one('master.semester','Semester'),
		'tahun_ajaran_id': fields.many2one('academic.year','Tahun Ajaran'),		
			}

	_defaults={
		'state' : 'draft', 
	}
	 
krs_detail_mahasiswa()