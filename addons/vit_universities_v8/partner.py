from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


SESSION_STATES = [('calon','Calon'),('Mahasiswa','Mahasiswa'),('alumni','Alumni'),('orang_tua','Orang Tua'),('cuti','Cuti Kuliah')]
class res_partner (osv.osv):
	_name = 'res.partner'
	_inherit= 'res.partner'
	
	#def create(self, cr, uid, vals, context=None):
		#jurusan = self.pool.get('master.jurusan').browse(cr, uid, vals['jurusan_id'], context)[0]
		#nim = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')
		#vals['npm'] = jurusan.fakultas_id.kode + jurusan.kode + nim 
		#return super(partner, self).create(cr, uid, vals, context=None)

	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
					ids = [ids]
		reads = self.read(cr, uid, ids, ['name', 'npm'], context=context)
		res = []
		for record in reads:
			name = record['name']
			if record['npm']:
				name = '['+record['npm'] +']'+ ' ' + name
			res.append((record['id'], name))
		return res

	def create(self, cr, uid, vals, context=None):
		#import pdb;pdb.set_trace()
		if 'status_mahasiswa' in vals :
			if vals['status_mahasiswa'] == 'calon':
				if vals.get('reg','/')=='/':
					vals['reg'] = self.pool.get('ir.sequence').get(cr, uid, 'res.partner') or '/'
			if vals['status_mahasiswa'] == 'Mahasiswa':
				if vals.get('npm','/')=='/':
					ta = vals['tahun_ajaran_id']
					t_idd = self.pool.get('academic.year').browse(cr,uid,ta,context=context).date_start				
					ta_tuple =  tuple(t_idd)
					ta_id = ta_tuple[2]+ta_tuple[3]#ambil 2 digit paling belakang dari tahun saja		

					fak = vals['fakultas_id']
					fak_id = self.pool.get('master.fakultas').browse(cr,uid,fak,context=context).kode

					pro = vals['prodi_id']
					pro_id = self.pool.get('master.prodi').browse(cr,uid,pro,context=context).kode

					sequence = self.pool.get('ir.sequence').get(cr, uid, 'seq.npm.partner') or '/'

					vals['npm'] = ta_id+fak_id+pro_id+sequence
			if vals['status_mahasiswa'] == 'alumni':
				raise osv.except_osv(_('Error!'), _('Data alumni harus dibuat dari data mahasiswa'))			
		return super(res_partner, self).create(cr, uid, vals, context=context)

	def _calc_age(self, cr, uid, ids, name, arg, context=None):
		''' Fungsi otomatis utk menghitung usia'''
		res = {}
		for mhs in self.browse(cr, uid, ids, context=context):
			start = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
			if mhs.tanggal_lahir:
				start = datetime.strptime(mhs.tanggal_lahir, DEFAULT_SERVER_DATE_FORMAT)
			end = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
			delta = end - start
			years = (delta.days / 365)
			res[mhs.id] = years
		return res		

		#jika penggambilan MK di KRS berdasarkan yang terbaru
	def get_ttl_mk_by_newest(self, cr, uid, ids, context=None):
		
		ops_obj = self.pool.get('operasional.krs')
		det_obj = self.pool.get('operasional.krs_detail')
	
		cr.execute("""SELECT okd.id AS id, okd.mata_kuliah_id AS mk, okd.nilai_angka AS nilai
						FROM operasional_krs ok
						LEFT JOIN operasional_krs_detail okd ON ok.id = okd.krs_id
						LEFT JOIN master_semester s ON s.id = ok.semester_id
						WHERE ok.state = 'done' AND ok.partner_id ="""+ str(ids[0]) +"""
						GROUP BY okd.id,s.name
						ORDER BY okd.mata_kuliah_id, s.name DESC""")		   
		mk = cr.fetchall()			

		if mk == []:
			mk=0
			return mk
		id_mk = []	#id khsdetail
		mk_ids = [] #Matakuliah khsdetail

		for m in mk:
			##################################
			# m[0] = operasional_krs_detail id
			# m[1] = matakuliah_id
			# m[2] = nilai angka
			##################################
			if m[1] not in mk_ids:
				if m[2] > 0 :
					id_mk.append(m[0])
					mk_ids.append(m[1])

		jml_id_mk = len(mk_ids)

		return {}#jml_id_mk

		#jika penggambilan MK di KRS berdasarkan yang terbaik
	def get_ttl_mk_by_better(self, cr, uid, ids, context=None):
		
		ops_obj = self.pool.get('operasional.krs')
		det_obj = self.pool.get('operasional.krs_detail')
	
		cr.execute("""SELECT okd.id AS id, okd.mata_kuliah_id AS mk,okd.nilai_angka AS nilai
						FROM operasional_krs ok
						LEFT JOIN operasional_krs_detail okd ON ok.id = okd.krs_id
						LEFT JOIN master_semester s ON s.id = ok.semester_id
						WHERE ok.state = 'done' AND ok.partner_id ="""+ str(ids[0]) +"""
						GROUP BY okd.id,s.name
						ORDER BY okd.mata_kuliah_id, okd.nilai_angka DESC""")		   
		mk = cr.fetchall()			

		if mk == []:
			mk = 0
			return mk
		id_mk = []	#id khsdetail
		mk_ids = [] #Matakuliah khsdetail

		for m in mk:
			##################################
			# m[0] = operasional_krs_detail id
			# m[1] = matakuliah_id
			# m[2] = nilai angka
			##################################
			if m[1] not in mk_ids:
				if m[2] > 0 :
					id_mk.append(m[0])
					mk_ids.append(m[1])

		jml_id_mk = len(mk_ids)

		return {}#jml_id_mk

	def _get_sidang_ready(self, cr, uid, ids, field_name, arg, context=None):
		results = {}

		for siap_sidang in  self.browse(cr, uid, ids, context=context):
			if siap_sidang.tahun_ajaran_id.id != False:
				tahun_ajaran = siap_sidang.tahun_ajaran_id.id
				fakultas 	= siap_sidang.fakultas_id.id
				prodi  		= siap_sidang.prodi_id.id
				# cari jumlah kurikulum untuk thn akademik ini sesuai dengan settingan master kurikulum
				kurikulum_obj = self.pool.get('master.kurikulum')
				th_kurikulum = kurikulum_obj.search(cr,uid,[('tahun_ajaran_id','=',tahun_ajaran),
															('fakultas_id','=',fakultas),
															('prodi_id','=',prodi),
															('state','=','confirm')])
				total_kurikulum = len(th_kurikulum)

				# hitung jumlah kurikulum untuk thn akademik dan mahasiswa yg bersangkutan, harus sama dg jumlah yg ada di kurikulum
				khs_obj = self.pool.get('operasional.krs')
				th_khs = khs_obj.search(cr,uid,[('partner_id','=',siap_sidang.id),('tahun_ajaran_id','=',tahun_ajaran),('state','=','done')])
				total_khs = len(th_khs)
				#import pdb;pdb.set_trace()
				results[siap_sidang.id] = False
				if total_khs >= total_kurikulum :
					#cek juga total mk di kurikulum harus sama dengan mk yg sudah ditempuh
					tahun_ajaran_id = self.browse(cr,uid,ids[0]).tahun_ajaran_id.id
					prodi_id = self.browse(cr,uid,ids[0]).prodi_id.id
					cr.execute("""SELECT kmr.matakuliah_id kmr
									FROM kurikulum_mahasiswa_rel kmr
									LEFT JOIN master_matakuliah mm ON mm.id = kmr.matakuliah_id
									LEFT JOIN master_kurikulum mk ON kmr.kurikulum_id = mk.id 
									WHERE mk.tahun_ajaran_id ="""+ str(tahun_ajaran_id) +""" 
									AND mk.prodi_id = """+ str(prodi_id) +"""
									AND mk.state = 'confirm'""")		   
					mk_klm = cr.fetchall()			
					if mk_klm != []:

						if self.browse(cr,uid,ids[0]).tahun_ajaran_id.mekanisme_nilai == 'terbaru' :
							mk = self.get_ttl_mk_by_newest(cr, uid, ids, context=None)
						elif self.browse(cr,uid,ids[0]).tahun_ajaran_id.mekanisme_nilai == 'terbaik' :
							mk = self.get_ttl_mk_by_better(cr, uid, ids, context=None)	

						if mk > 0 :										
							mk_ids = []
							for m in mk_klm:
								if m[0] not in mk_ids:
									mk_ids.append(m[0])		
							tot_kurikulum = len(mk_ids)
							
							toleransi_mk = self.browse(cr,uid,ids[0]).tahun_ajaran_id.max_mk
							#jika total mk yg telah ditempuh sama dengan / lebih dari yg ada di kurikulum
							if mk >= (tot_kurikulum-toleransi_mk):
								results[siap_sidang.id] = True

		return results

	_columns = {
		#Mahasiswa
		'npm' :fields.char(string='NIM',size=34),
		'reg': fields.char('No. Pendaftaran',readonly=True,size=34),
		# 'nama_tengah':fields.char('Nama Tengah',size=60),
		# 'nama_belakang':fields.char('Nama Tengah',size=60),
		'jenis_kelamin':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
		'tempat_lahir':fields.char('Tempat Lahir'),
		'tanggal_lahir':fields.date('Tanggal Lahir'),

		'status_mahasiswa':fields.selection(SESSION_STATES,'Status Mhs'),                  

		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas', domain=[('is_internal','=',True)]),
		# 'jurusan_id':fields.many2one('master.jurusan',string='Program Studi',domain="[('fakultas_id','=',fakultas_id)]"),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',domain="[('fakultas_id','=',fakultas_id),('is_internal','=',True)]"),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik'),
		'semester_id':fields.many2one('master.semester',string='Semester Awal Masuk'),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',readonly=True),                

		#'peserta_kelas_id':fields.many2one('master.peserta_kelas',string='Mahasiswa',),
		'ipk':fields.float('IPK',digits=(2,2),readonly=True),
		'judul':fields.text('Judul Tugas Akhir'),
		'wisuda':fields.date('Tanggal Wisuda'),
		'tgl_lulus':fields.date('Tanggal Lulus'),
		'no_formulir':fields.char('No Formulir Ujian'),
		'tgl_ujian':fields.date('Tanggal Ujian'),
		'nilai_ujian':fields.float('Nilai Ujian'),
		'nilai_ujian_asli':fields.float('Nilai Ujian Asli'),
		'batas_nilai':fields.float('Batas Nilai Kelulusan',readonly=True),
		'is_dosen':fields.boolean('Dosen ?'),
		'biodata_keluarga_ids':fields.one2many('master.biodata_keluarga','partner_id','Biodata Keluarga',),
		'riwayat_pendidikan_ids':fields.one2many('master.riwayat_pendidikan','partner_id','Riwayat Pendidikan',ondelete='cascade',),
		'pelanggaran_ids':fields.one2many('master.pelanggaran','partner_id','Pelanggaran',),
		'pekerjaan_ids':fields.one2many('master.history.pekerjaan','partner_id','History Pekerjaan',),
		#'jadwal_ids':fields.one2many('master.jadwal.kuliah','partner_id','Jadwal Mengajar',),
		'nidn':fields.char('NIDN'),
		'status_dosen':fields.selection([('tetap','Tetap'),('tidak_tetap','Tidak Tetap')],'Status Dosen'),
		#'state': fields.selection([('draft','Calon Mahasiswa'),('on_progress','Mahasiswa'),('done','Alumni')],'Status Mahasiswa'),
		'age':fields.function(_calc_age, method=True, required=True, string='Usia (Tahun)', readonly=True, type="integer"),
		'status_pernikahan':fields.selection([('belum','Belum Menikah'),('menikah','Menikah'),('janda','Janda'),('duda','Duda')],'Status Pernikahan'),
		'agama':fields.selection([('islam','Islam'),('kristen','Kristen'),('hindu','Hindu'),('budha','Budha'),('kepercayaan','Kepercayaan')],'Agama'),
		'lokasi_wisuda':fields.char('Tempat Wisuda',size=128,readonly=True),
		'tgl_daftar':fields.date('Tanggal Daftar',readonly=True),
		'siap_sidang' : fields.function(_get_sidang_ready,type='boolean',string='Siap Sidang',readonly=True),
		'is_mahasiswa' : fields.boolean('Is Mahasiswa/Calon ?'),
		'nilai_beasiswa':fields.float('Rata-Rata Nilai SMA/Sederajat'),
		'is_beasiswa' : fields.boolean('Penerima Beasiswa USM',readonly=True),
		'jadwal_usm_id': fields.many2one('jadwal.usm', 'Jadwal USM', required=True),
		'keluarga_alumni_id': fields.many2one('res.partner','Keluarga Alumni',domain=[('status_mahasiswa','=','alumni')]),
		'marketing_id': fields.many2one('master.marketing','Marketing'),
		'jenis_pendaftaran_id': fields.many2one('akademik.jenis_pendaftaran', 'Jenis Pendaftaran', required=True),

		'status_aktivitas': fields.selection([('A','A'),('N','N'),('K','K'),('L','L'),('C','C'),('D','D')],'Status Aktivitas',required=True),

		#untuk mhs pindahan
		'asal_univ_id' 		: fields.many2one('res.partner', 'Asal PT', domain=[('category_id','ilike','external')]),
		'asal_fakultas_id' 	: fields.many2one('master.fakultas', 'Asal Fakultas', domain="[('pt_id','=',asal_univ_id),('is_internal','=',False)]"),
		'asal_prodi_id' 	: fields.many2one('master.prodi', 'Asal Prodi', domain="[('fakultas_id','=',asal_fakultas_id),('is_internal','=',False)]"),
		'asal_npm'			: fields.char('Asal NIM'),
		'asal_sks_diakui' 	: fields.integer('SKS Diakui'),
		'asal_jenjang_id' 	: fields.many2one('master.jenjang', 'Asal Jenjang'),
		'semester_id'		:fields.many2one('master.semester','Semester'),

		#split invoice
		'split_invoice' : fields.integer('Otomatis Split',required=True,help="jika di isi angka positif maka invoice yg digenerate dari KRS atas mahasiswa ini akan tersplit sesuai angka yang diisi")

	}

	_sql_constraints = [('reg_uniq', 'unique(reg)','No. pendaftaran tidak boleh sama')]
	_sql_constraints = [('npm_uniq', 'unique(npm)','NPM tidak boleh sama')]

	def action_draft(self,cr,uid,ids,context=None):
			#set to "draft" state
		return self.write(cr,uid,ids,{'status_mahasiswa':SESSION_STATES[0][0]},context=context)
			
	def action_confirm(self,cr,uid,ids,jurusan_id,context=None):
		val = self.browse(cr,uid,ids)[0]
		kod = val.jurusan_id.kode
		val1 = val.jurusan_id.fakultas_id.kode
		val2= val.prodi_id.kode
		nem = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')        
		vals = val1+kod+val2+nem 
		return self.write(cr,uid,ids,{'status_mahasiswa':SESSION_STATES[1][0],'npm':vals},context=context)
			
	def action_done(self,cr,uid,ids,context=None):
			#set to "done" state
		return self.write(cr,uid,ids,{'status_mahasiswa':SESSION_STATES[2][0]},context=context)      

	_defaults = {
		#'is_dosen':False, #(domain = [('status_mahasiswa','=','calon')]),
		#'status_mahasiswa' : SESSION_STATES[3][0],
		#'angkatan': lambda*a : time.strftime('%Y'),
		'tgl_daftar' : fields.date.context_today,
		#'npm':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'res.partner'), 
		'npm' : '/',  
		'reg': '/',
		'is_mahasiswa': False,
		'split_invoice': 1,
	}



	def action_konversi(self,cr,uid,ids,context=None):
		konv_obj = self.pool.get('akademik.konversi')

		for mhs in self.browse(cr, uid, ids, context=context):
			exist = konv_obj.search(cr,uid,[('partner_id','=',mhs.id)],context=context)
			if exist:
				raise osv.except_osv(_('Error!'), _('Data konversi sudah pernah dibuat!'))
			data = {
				'partner_id' 		: mhs.id,
				'semester_id'		: mhs.semester_id.id,
				'asal_prodi_id'		: mhs.asal_prodi_id.id,
				'asal_fakultas_id'	: mhs.asal_fakultas_id.id,
				'asal_univ_id'		: mhs.asal_univ_id.id,
				'prodi_id'			: mhs.prodi_id.id,
				'fakultas_id'		: mhs.fakultas_id.id,
				'tahun_ajaran_id'	: mhs.tahun_ajaran_id.id,
				'state'				: 'draft',
				'notes' 			: '',
				'user_id'			: uid,
				'date'				: mhs.tgl_daftar,
				'krs_done'			: False,
			}
			konv_id = konv_obj.create(cr, uid, data, context=context)
		return konv_id

res_partner()