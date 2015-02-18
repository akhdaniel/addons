from osv import osv, fields
from openerp.tools.translate import _


class operasional_krs (osv.Model):
	_name= 'operasional.krs'
	_rec_name='kode'

	def create(self, cr, uid, vals, context=None):
		#import pdb;pdb.set_trace() 
		if vals.get('kode','/')=='/':
			npm = vals['npm']
			if not npm :
				npm = '<<npm_kosong>> '
			smt = vals['semester_id']
			vals['kode'] = npm +'-'+str(smt) or '/'
		return super(operasional_krs, self).create(cr, uid, vals, context=context)	    
	
	def _get_ips(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		res = {}
		
		krs_id = self.browse(cr,uid,ids[0],context=context)
		partner = krs_id.partner_id.id

		cr.execute("""SELECT okd.id
						FROM operasional_krs_detail okd
						LEFT JOIN operasional_krs ok ON ok.id = okd.krs_id
						WHERE ok.partner_id = %s
						AND ok.state <> 'draft'"""%(partner))
		dpt = cr.fetchall()
		
		det_id = []
		for x in dpt:
			x_id = x[0]
			det_id.append(x_id)
		#import pdb;pdb.set_trace()
		det_sch = self.pool.get('operasional.krs_detail').browse(cr,uid,det_id,context=context)
		sks = 0
		bobot_total = 0.00
		
		for det in det_sch:
			sks += det.sks
			bobot_total += (det.nilai_angka*det.sks)

		self.write(cr,uid,ids[0],{'sks_tot':sks},context=context)

		### ips = (total nilai angka*total sks) / total sks
		if sks == 0:
			ips = 0
		else :
			ips = round(bobot_total/sks,2)
		res[ids[0]] = ips
		return res
	
	_columns = {
		'kode' : fields.char('Kode', 128, readonly=True),
		'state':fields.selection([('draft','Draft'),('confirm','Konfirmasi'),('done','Selesai')],'Status',readonly=True),
		'partner_id' : fields.many2one('res.partner','Mahasiswa', required=True, domain="[('status_mahasiswa','=','Mahasiswa')]"),
		#'employee_id' : fields.many2one('hr.employee','Dosen Wali'),
		#'npm':fields.related('partner_id', 'npm', type='char', relation='res.partner',size=128, string='NPM',readonly=True),
		'npm' : fields.char('NPM',size=28,),
		'fakultas_id':fields.many2one('master.fakultas','Fakultas',required = True),         
		'jurusan_id':fields.many2one('master.jurusan',string='Jurusan',required = True),           
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required = True),
		'max_smt': fields.integer("Max Semester",),
		'semester_id':fields.many2one('master.semester','Semester',domain="[('name','<=',max_smt)]",required = True),
		'tahun_ajaran_id': fields.many2one('academic.year','Tahun Ajaran',required = True),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',required=True), 
		'krs_detail_ids' : fields.one2many('operasional.krs_detail','krs_id','Mata Kuliah'),
		'view_ipk_ids' : fields.one2many('operasional.view_ipk','krs_id','Mata Kuliah'),
		'kurikulum_id':fields.many2one('master.kurikulum','Kurikulum',required = True),
		'ips':fields.function(_get_ips,type='float',string='Indeks Prestasi',),
		'user_id':fields.many2one('res.users','User',readonly=True),
		'sks_tot' : fields.integer('Total SKS',readonly=True),
			}    
				 
	_defaults={
		'state' : 'draft', 
		'kode': '/',
		'user_id': lambda obj, cr, uid, context: uid,
	}

	def confirm(self, cr, uid, ids, context=None):
		#import pdb;pdb.set_trace()  
		for x in self.browse(cr,uid,ids[0],context=context).krs_detail_ids:
			self.pool.get('operasional.krs_detail').write(cr,uid,x.id,{'state':'confirm'},context=context)
		self.write(cr, uid, ids, {'state' : 'confirm'}, context=context)
		return True

	def cancel(self,cr,uid,ids,context=None):   

		for x in self.browse(cr,uid,ids[0],context=context).krs_detail_ids:
			self.pool.get('operasional.krs_detail').write(cr,uid,x.id,{'state':'draft'},context=context)
		self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
		return True

	def done(self,cr,uid,ids,context=None):   

		for x in self.browse(cr,uid,ids[0],context=context).krs_detail_ids:
			self.pool.get('operasional.krs_detail').write(cr,uid,x.id,{'state':'done'},context=context)
		self.write(cr, uid, ids, {'state' : 'done'}, context=context)
		return True

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(operasional_krs, self).unlink(cr, uid, ids, context=context)


	def onchange_partner(self, cr, uid, ids, tahun_ajaran_id, fakultas_id, jurusan_id, prodi_id, kelas_id, partner_id, npm, context=None):

		results = {}
		if not partner_id:
			return results

		par_obj = self.pool.get('res.partner')
		par_ids = par_obj.search(cr, uid, [('id','=',partner_id)], context=context)

		#import pdb;pdb.set_trace()
		par_id = par_obj.browse(cr,uid,par_ids,context=context)[0]
		npm =par_id.npm
		kelas_id = par_id.kelas_id.id
		tahun_ajaran_id = par_id.tahun_ajaran_id.id
		fakultas_id = par_id.fakultas_id.id
		jurusan_id = par_id.jurusan_id.id
		prodi_id = par_id.prodi_id.id
		max_smt = par_id.prodi_id.semester_id.name

		results = {
			'value' : {
				'npm' : npm,
				'kelas_id': kelas_id,
				'tahun_ajaran_id' : tahun_ajaran_id,
				'fakultas_id' : fakultas_id,
				'jurusan_id' : jurusan_id,
				'prodi_id' : prodi_id,
				'max_smt': max_smt,
			}
		}
		return results 

	def onchange_semester(self, cr, uid, ids, npm, tahun_ajaran_id, prodi_id, semester_id,context=None):

		results = {}
		if not semester_id:
			return results

		kur_obj = self.pool.get('master.kurikulum')
		kur_ids = kur_obj.search(cr, uid, [
			('tahun_ajaran_id','=',tahun_ajaran_id),
			('prodi_id','=',prodi_id),
			('state','=','confirm'),
			('semester_id','=',semester_id)], context=context)
		if kur_ids == []:
			raise osv.except_osv(_('Error!'),
								_('Tidak ada kurikulum yang cocok untuk data ini!'))
		
		kur_id = kur_obj.browse(cr,uid,kur_ids,context=context)[0].kurikulum_detail_ids
		kur_kode = kur_obj.browse(cr,uid,kur_ids,context=context)[0].id
		res = []
		for kur in kur_id:
			det = kur.id
			res.append([0,0,{'mata_kuliah_id': det,'state':'draft'}])
		#import pdb;pdb.set_trace()

		results = {
			'value' : {
				'kurikulum_id': kur_kode,
				'krs_detail_ids' : res,
			}
		}
		return results 
			
operasional_krs()

class krs_detail (osv.Model):
	_name='operasional.krs_detail'
	_rec_name='krs_id'


	def _get_nilai_akhir(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		
		nil_obj = self.pool.get('master.nilai')
		
		#import pdb;pdb.set_trace()
		result = {}
		for nil in self.browse(cr,uid,ids,context=context):
			tugas = nil.tugas
			ulangan = nil.ulangan
			uts = nil.uts
			uas = nil.uas
			tot = (tugas+ulangan+uts+uas)/4
			nil_src = nil_obj.search(cr,uid,[('min','<=',tot),('max','>=',tot)],context=context)
			if nil_src == []:
				return result

			nil_par = nil_obj.browse(cr,uid,nil_src,context=context)[0]
			huruf = nil_par.name
			angka = nil_par.bobot
			self.write(cr,uid,nil.id,{'nilai_angka':angka},context=context)
			result[nil.id] = huruf
		return result
		
	_columns = {
		'krs_id':fields.many2one('operasional.krs','Kode KRS',),
		'mata_kuliah_id':fields.many2one('master.matakuliah','Mata Kuliah',required=True,ondelete="cascade"),
		'sks':fields.related('mata_kuliah_id', 'sks',type='integer',relation='master.matakuliah', string='SKS',readonly=True,store=True),
		'tugas' : fields.float('Tugas'),
		'ulangan' : fields.float('Ulangan'),
		'uts':fields.float('UTS'),
		'uas':fields.float('UAS'),
		'nilai_huruf':fields.function(_get_nilai_akhir,type='char',string='Nilai Akhir'),
		'nilai_angka':fields.float('Nilai Angka'),
		'transkrip_id':fields.many2one('operasional.transkrip','Transkrip'),
		'state':fields.selection([('draft','Draft'),('confirm','Konfirmasi'),('done','Selesai')],'Status',readonly=False),
			}

	_defaults={
		'state' : 'draft', 
	}
	 
krs_detail()

 
class operasional_transkrip(osv.Model):
	_name='operasional.transkrip'

	def create(self, cr, uid, vals, context=None):
		#import pdb;pdb.set_trace() 
		if 'partner_id' in vals:
			mhs = vals['partner_id']
			partner_brw = self.pool.get('res.partner').browse(cr,uid,mhs)
			prodi = partner_brw.prodi_id.id
			cek_mhs = self.search(cr,uid,[('partner_id','=',mhs),('prodi_id','=',prodi)])
			if cek_mhs != []:
				raise osv.except_osv(_('Error!'),
				('Mahasiswa ini sudah mempunyai transkrip dengan program studi dan jenjang yang sama!'))				

		return super(operasional_transkrip, self).create(cr, uid, vals, context=context)	 

	def get_mk(self, cr, uid, ids, context=None):

		mhs_id = self.browse(cr,uid,ids[0],context=context).partner_id.id
		
		ops_obj = self.pool.get('operasional.krs')
		det_obj = self.pool.get('operasional.krs_detail')
		cr.execute("""SELECT okd.id
						FROM operasional_krs ok 
						LEFT JOIN operasional_krs_detail okd ON ok.id = okd.krs_id
						WHERE okd.state = 'done'
						AND ok.partner_id ="""+ str(mhs_id))
					   
		mk = cr.fetchall()	

		if mk == []:
			return mk		
		mk_ids = []
		for m in mk:
			mk_ids.append(m[0])
	
		return mk_ids


	def _get_total_khs(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}

		mk = self.get_mk(cr, uid, ids, context=None)

		if mk == []:
			return result			
	
		result[ids[0]] = mk
		return result

	def _get_ipk(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}

		mk = self.get_mk(cr, uid, ids, context=None)
		if mk == []:
			return result

		det_obj = self.pool.get('operasional.krs_detail')			
		tot_nil = 0.0
		tot_sks = 0.0
		for m in mk:
			det_id = det_obj.browse(cr,uid,m,context=context)
			sks = det_id.sks
			nil = det_id.nilai_angka
			nil_jml = nil*sks

			tot_sks += sks
			tot_nil += nil_jml

		ipk = tot_nil/tot_sks
		result[ids[0]] = ipk

		#update nilai IPK di di objek mahasiswa bersangkutan
		nama_mahasiswa = self.browse(cr,uid,ids[0]).partner_id.id
		partner_obj = self.pool.get('res.partner')
		partner_obj.write(cr,uid,nama_mahasiswa,{'ipk':ipk},context=context)

		#get yudisium
		yud_obj = self.pool.get('master.yudisium')
		yud_src = yud_obj.search(cr,uid,[('min','<=',ipk),('max','>=',ipk)],context=context)
		if yud_src != [] :
			yud = yud_src[0]
			yudisium = yud_obj.browse(cr,uid,yud,context=context).name
			self.write(cr,uid,ids[0],{'yudisium':yudisium},context=context)
		self.write(cr,uid,ids[0],{'t_sks':tot_sks,'t_nilai':tot_nil},context=context)

		return result

	_columns={
		'name' : fields.char('Kode',size=28,required=True),
		'partner_id' : fields.many2one('res.partner','Nama Mahasiswa', required=True, domain="[('status_mahasiswa','=','Mahasiswa')]"),
		'npm':fields.related('partner_id','npm',type='char',relation='res.partner',string='NPM'),
		'tempat_lahir':fields.related('partner_id','tempat_lahir',type='char',relation='res.partner',string='Tempat Lahir',readonly=True),
		'tanggal_lahir':fields.related('partner_id','tanggal_lahir',type='date',relation='res.partner',string='Tanggal Lahir',readonly=True),
		'tahun_ajaran_id':fields.related('partner_id', 'tahun_ajaran_id', type='many2one', relation='academic.year',string='Angkatan',readonly=True),
		'fakultas_id':fields.related('partner_id', 'fakultas_id', type='many2one',relation='master.fakultas', string='Fakultas',readonly=True),
		'jurusan_id':fields.related('partner_id', 'jurusan_id', type='many2one',relation='master.jurusan', string='Jurusan',readonly=True),
		'prodi_id':fields.related('partner_id', 'prodi_id', type='many2one',relation='master.prodi', string='Program Studi',readonly=True),
		'transkrip_detail_ids' : fields.function(_get_total_khs, type='many2many', relation="operasional.krs_detail", string="Total Mata Kuliah"), 
		'ipk' : fields.function(_get_ipk,type='float',string='IPK'),
		'yudisium' : fields.char('Yudisium',readonly=True),
		't_sks' : fields.integer('Total SKS',readonly=True),
		't_nilai' : fields.char('Total Nilai',readonly=True),
			}    

	_sql_constraints = [('name_uniq', 'unique(name)','Kode Transkrip tidak boleh sama')]

operasional_transkrip()