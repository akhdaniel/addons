from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime,date
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big
from openerp import netsvc
from openerp.addons.base.ir.ir_mail_server import MailDeliveryException
from openerp import tools, api
import locale
from openerp.addons.vit_universities_spc_bni import bni


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
		###import pdb;pdb.set_trace()
		if not ids:
			return []
		if isinstance(ids, (int, long)):
					ids = [ids]
		reads = self.read(cr, uid, ids, ['name', 'npm','reg','is_mahasiswa'], context=context)
		res = []
		for record in reads:
			name = record['name']
			if record['is_mahasiswa'] :
				if record['npm'] != '/':
					name = '['+record['npm'] +']'+ ' ' + name
				elif record ['npm'] == '/' :
					name = '['+record['reg'] +']'+ ' ' + name
				res.append((record['id'], name))
			else:
				res.append((record['id'], name))
		return res

	def create(self, cr, uid, vals, context=None):
		#import pdb;pdb.set_trace()
		if 'status_mahasiswa' in vals :
			if 'is_import' not in vals:
				if vals['status_mahasiswa'] == 'calon':
					if vals.get('reg','/')=='/':
						vals['reg'] = self.pool.get('ir.sequence').get(cr, uid, 'res.partner') or '/'
					partner = super(res_partner, self).create(cr, uid, vals, context=context)
					byr_obj = self.pool.get('master.pembayaran.pendaftaran')
					byr_sch = byr_obj.search(cr,uid,[('tahun_ajaran_id','=',vals['tahun_ajaran_id']),
						('fakultas_id','=',vals['fakultas_id']),
						('prodi_id','=',vals['prodi_id']),
						('state','=','confirm'),
						])		
					if byr_sch != []:
						inv_obj = self.pool.get('account.invoice')
						origin = str(self.pool.get('res.partner').browse(cr,uid,partner).reg)
						inv_exist = inv_obj.search(cr,uid,[('origin','=',origin)])
						if not inv_exist :
							byr_brw = byr_obj.browse(cr,uid,byr_sch[0],context=context)
							list_pembayaran = byr_brw.detail_product_ids
							prod_id = []
							for bayar in list_pembayaran:
							
								product = self.pool.get('product.product').browse(cr,uid,bayar.product_id.id)
								coa_line = product.property_account_income.id
								if not coa_line:
									coa_line = product.categ_id.property_account_income_categ.id
								prod_id.append((0,0,{'product_id'	: bayar.product_id.id,
													 'name'			: bayar.product_id.name,
													 'price_unit'	: bayar.public_price,
													 'account_id'	: coa_line}))
							inv = inv_obj.create(cr,uid,{
								'partner_id':partner,
								'origin': 'Pendaftaran '+origin,
								'type':'out_invoice',
								'fakultas_id': vals['fakultas_id'],
								'prod_id': vals['prodi_id'],
								'account_id':self.pool.get('res.partner').browse(cr,uid,partner).property_account_receivable.id,
								'invoice_line': prod_id,
								},context=context)
							#wf_service = netsvc.LocalService('workflow')
							from openerp import workflow
							workflow.trg_validate(uid, 'account.invoice', inv, 'invoice_open', cr)						
							self.write(cr,uid,partner,{'invoice_id':inv})


			elif vals['status_mahasiswa'] == 'Mahasiswa':
				if 'is_import' not in vals:
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
						partner = super(res_partner, self).create(cr, uid, vals, context=context)
				else :
					partner = super(res_partner, self).create(cr, uid, vals, context=context)	
			elif vals['status_mahasiswa'] == 'alumni':
				if 'is_import' not in vals:
					raise osv.except_osv(_('Error!'), _('Data alumni harus dibuat dari data mahasiswa'))
				partner = super(res_partner, self).create(cr, uid, vals, context=context)		
			else:
				partner = super(res_partner, self).create(cr, uid, vals, context=context)
		else:
			partner = super(res_partner, self).create(cr, uid, vals, context=context)		
		return partner

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
			if not siap_sidang.is_import :
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
					
					results[siap_sidang.id] = False
					if total_khs >= total_kurikulum :
						#cek juga total mk di kurikulum harus sama dengan mk yg sudah ditempuh
						tahun_ajaran_id = self.browse(cr,uid,ids[0]).tahun_ajaran_id.id
						prodi_id = self.browse(cr,uid,ids[0]).prodi_id.id
						if tahun_ajaran_id and prodi_id:
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
			else : 							
				results[siap_sidang.id] = True
		return results

	_columns = {
		#Mahasiswa
		'npm' :fields.char(string='NIM',size=34),
		'reg': fields.char('No. Pendaftaran',readonly=True,size=34),
		'no_alumni': fields.char('No. Alumni', size=34),
		'street':fields.text('Alamat Rumah'),
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
		'is_import': fields.boolean('Import'),
		'ipk':fields.float('IPK',digits=(2,2)),
		'judul':fields.text('Judul Tugas Akhir'),
		'wisuda':fields.date('Tanggal Wisuda'),
		'lokasi_wisuda':fields.char('Tempat Wisuda',size=128,readonly=True),
		'tgl_lulus':fields.date('Tanggal Lulus'),
		'siap_sidang' : fields.function(_get_sidang_ready,type='boolean',string='Siap Sidang',readonly=True),
		'tgl_sidang':fields.date('Tanggal Sidang'),
		'nilai_sidang_huruf':fields.char('Nilai Sidang (Huruf)',size=3),
		'nilai_sidang_angka':fields.float('Nilai Sidang (Angka)',digits=(2,2)),
		'jml_praktikum': fields.float('Jumlah Praktikum'),
		'jml_mk_pilihan': fields.float('Jumlah MK Pilihan'),
		'jml_nilai_d': fields.float('Jumlah Nilai D (%)'),
		'jml_sks_komultif': fields.float('Jumlah SKS Komulatif'),

		'no_formulir':fields.char('No Formulir Ujian'),
		'tgl_ujian':fields.date('Tanggal Ujian'),
		'nilai_ujian':fields.float('Nilai Ujian'),
		'nilai_ujian_asli':fields.float('Nilai Ujian Asli'),
		'batas_nilai':fields.float('Batas Nilai Kelulusan',readonly=True),
		'is_dosen':fields.boolean('Dosen ?'),
		'biodata_keluarga_ids':fields.one2many('master.biodata_keluarga','partner_id','Biodata Keluarga', ondelete='cascade',),
		'riwayat_pendidikan_ids':fields.one2many('master.riwayat_pendidikan','partner_id','Riwayat Pendidikan',ondelete='cascade',),
		'pelanggaran_ids':fields.one2many('master.pelanggaran','partner_id','Pelanggaran', ondelete='cascade',),
		'pekerjaan_ids':fields.one2many('master.history.pekerjaan','partner_id','History Pekerjaan', ondelete='cascade',),
		#'jadwal_ids':fields.one2many('master.jadwal.kuliah','partner_id','Jadwal Mengajar',),
		'nidn':fields.char('NIDN'),
		'status_dosen':fields.selection([('tetap','Tetap'),('tidak_tetap','Tidak Tetap')],'Status Dosen'),
		#'state': fields.selection([('draft','Calon Mahasiswa'),('on_progress','Mahasiswa'),('done','Alumni')],'Status Mahasiswa'),
		'age':fields.function(_calc_age, method=True, required=True, string='Usia (Tahun)', readonly=True, type="integer"),
		'status_pernikahan':fields.selection([('belum','Belum Menikah'),('menikah','Menikah'),('janda','Janda'),('duda','Duda')],'Status Pernikahan'),
		'agama':fields.selection([('islam','Islam'),('kristen','Kristen'),('hindu','Hindu'),('budha','Budha'),('kepercayaan','Kepercayaan')],'Agama'),
		'tgl_daftar':fields.date('Tanggal Daftar',),

		'is_mahasiswa' : fields.boolean('Is Mahasiswa'),
		'nilai_beasiswa':fields.float('Rata-Rata Nilai SMA/Sederajat'),
		'is_beasiswa' : fields.boolean('Penerima Beasiswa USM',readonly=True),
		'jadwal_usm_id': fields.many2one('jadwal.usm', 'Jadwal USM'),
		'keluarga_alumni_id': fields.many2one('res.partner','Keluarga Alumni',domain=[('status_mahasiswa','=','alumni')]),
		'marketing_id': fields.many2one('master.marketing','Marketing'),
		'jenis_pendaftaran_id': fields.many2one('akademik.jenis_pendaftaran', 'Jenis Pendaftaran'),
		'no_ijazah_sma'		: fields.char('No. Ijazah SMA/Sederajat'),
		'status_aktivitas': fields.selection([('A','A'),('N','N'),('K','K'),('L','L'),('C','C'),('D','D')],'Status Aktivitas',required=True),

		#untuk mhs pindahan
		'asal_univ_id' 		: fields.many2one('res.partner', 'Asal PT', domain=[('category_id','ilike','external')]),
		'asal_univ'			: fields.char('Asal PT',readonly=True),
		'asal_fakultas_id' 	: fields.many2one('master.fakultas', 'Asal Fakultas', domain="[('pt_id','=',asal_univ_id),('is_internal','=',False)]"),
		'asal_fakultas'		: fields.char('Asal Fakultas',readonly=True),
		'asal_prodi_id' 	: fields.many2one('master.prodi', 'Asal Prodi', domain="[('fakultas_id','=',asal_fakultas_id),('is_internal','=',False)]"),
		'asal_prodi'		: fields.char('Asal Prodi',readonly=True),
		'asal_alamat_univ' 	: fields.char('Asal Alamat PT',readonly=True),
		'asal_website_univ'	: fields.char('Asal Website PT',readonly=True),
		'asal_npm'			: fields.char('Asal NIM'),
		'asal_sks_diakui' 	: fields.integer('SKS Diakui'),
		'asal_jenjang_id' 	: fields.many2one('master.jenjang', 'Asal Jenjang'),
		'semester_id'		: fields.many2one('master.semester','Semester '),

		# flag jika pernah kuliah di kampus yg sama (alumni)
		'is_alumni'			: fields.boolean('Alumni'),

		# split invoice
		'split_invoice' : fields.integer('Angsuran',help="jika di isi angka positif maka invoice yg digenerate dari KRS atas mahasiswa ini akan tersplit sesuai angka yang diisi", size=1),
		'alamat_id'	: fields.many2one('master.alamat.kampus','Lokasi Kampus'),
		'type_pendaftaran': fields.selection([('ganjil','Ganjil'),('genap','Genap'),('pendek','Pendek')],'Type Pendaftaran'),

		'invoice_id' : fields.many2one('account.invoice','Uang Pendaftaran'),
		'invoice_state' : fields.related('invoice_id','state',type='char',relation='account.invoice',string='Pembayaran Pendaftaran',readonly=True),
		'invoice_bangunan_id' : fields.many2one('account.invoice','Uang Pengembangan',readonly=True),
		'invoice_bangunan_state' : fields.related('invoice_bangunan_id','state',type='char',relation='account.invoice',string='Pembayaran UP'),

		'karyawan_id'	: fields.many2one('hr.employee','Karyawan'),
		'type_mhs_id'	: fields.many2one('master.type.mahasiswa','Type Mahasiswa'),
		'konsentrasi_id': fields.many2one('master.konsentrasi','Konsentrasi'),
		'no_ijazah'		: fields.char('No. Ijazah'),
		'tgl_sk_dekan' 	: fields.date('Tgl. SK Dekan'),
		'no_sk_dekan'	: fields.char('No. SK Dekan'),
		'no_transkrip'	: fields.char('No. Transkrip'),
		'yudisium_id' 	: fields.many2one('master.yudisium','Yudisium'),
		'id_card'		: fields.char('No. KTP/SIM'),
		'jadwal_pagi'	: fields.boolean('Pagi'),
		'jadwal_siang'	: fields.boolean('Siang'),
		'jadwal_malam'	: fields.boolean('Malam'),
		'jalur_masuk'	: fields.selection([('perorangan','Perorangan'),('group','Group'),('prestasi','Jalur Prestasi')],'Jalur Masuk'),

		# pemberi rekomendasi
		'rekomendasi'	: fields.char('Rekomendasi'),
		'telp_rekomendasi' : fields.char('Telp. Rekomendasi'),

		# flag her registration online
		'reg_online'	: fields.boolean('Registrasi Ulang'),

		#flag pembeda user
		'partner_type'	: fields.selection([('mahasiswa','mahasiswa'),
											('ortu','Orang Tua'),
											('dosen','Dosen'),
											('sales','Sales'),
											('pegawai','Pegawai')],string='Type Partner'),
		# beasiswa dari front_end
		'semester1'		: fields.float('Semester 1'),
		'semester2'		: fields.float('Semester 2'),
		'semester3'		: fields.float('Semester 3'),
		'semester4'		: fields.float('Semester 4'),
		'semester5'		: fields.float('Semester 5'),
		'un'			: fields.float('UN'),
		'hubungan' 		: fields.selection([('umum','Umum'),('ortu','Orang Tua Alumni ISTN'),('cikini','Lulusan SLTA Perguruan Cikini'),('karyawan','Karyawan Tetap (Masih Aktif) ISTN')],'Hubungan Dengan ISTN'),
		'ranking'		: fields.integer('Ranking'),

		}

	_sql_constraints = [('reg_uniq', 'unique(reg)','No. pendaftaran tidak boleh sama')]
	_sql_constraints = [('npm_uniq', 'unique(npm)','NPM tidak boleh sama')]


	def add_discount_sequence_bangunan(self, cr, uid, ids ,disc,inv_line,bea_line_obj,partner,jml_inv,inv_ids, context=None):
		disc_ids = map(lambda x: x[0], disc)
		for bea_line in bea_line_obj.browse(cr,uid,disc_ids):
			disc_code 	= bea_line.code
			disc_id 	= bea_line.product_id.id
			disc_name 	= bea_line.name
			disc_nilai 	= bea_line.limit_nilai
			disc_nilai_max 	= bea_line.limit_nilai_max
			disc_amount	= bea_line.amount/int(jml_inv)
			disc_coa  	= bea_line.product_id.property_account_income.id
			#import pdb;pdb.set_trace()
			if not disc_coa:
				disc_coa = bea_line.product_id.categ_id.property_account_income_categ.id	
			if bea_line.uang_bangunan:
				if disc_code == '0':
					if partner.nilai_beasiswa >= disc_nilai: 
						for inv in inv_ids:	
							inv_line.create(cr,uid,{'invoice_id': inv,
													'product_id': disc_id,
													'name'		: disc_name,
													'quantity'	: 1 ,
													'price_unit': disc_amount,
													'account_id': disc_coa},context=context)
						break															  						
				elif disc_code == '1':
					if partner.keluarga_alumni_id: 
						for inv in inv_ids:	
							inv_line.create(cr,uid,{'invoice_id': inv,
													'product_id': disc_id,
													'name'		: disc_name,
													'quantity'	: 1 ,
													'price_unit': disc_amount,
													'account_id': disc_coa},context=context)
						break						
				elif disc_code == '2':
					for inv in inv_ids:	
						inv_line.create(cr,uid,{'invoice_id': inv,
												'product_id': disc_id,
												'name'		: disc_name,
												'quantity'	: 1 ,
												'price_unit': disc_amount,
												'account_id': disc_coa},context=context)
					break	
				elif disc_code == '3':
					if partner.karyawan_id: 
						for inv in inv_ids:	
							inv_line.create(cr,uid,{'invoice_id': inv,
													'product_id': disc_id,
													'name'		: disc_name,
													'quantity'	: 1 ,
													'price_unit': disc_amount,
													'account_id': disc_coa},context=context)
						break	
				# 		
				# elif disc_code == '4':
				# 	krs_sebelumnya = self.search(cr,uid,[('partner_id','=',partner.id),('semester_id','=',semester.id-1)])
				# 	if krs_sebelumnya:
				# 		if self.browse(cr,uid,krs_sebelumnya[0]).ips_field_persemester >= disc_nilai :
				# 			for inv in inv_ids:	
				# 				inv_line.create(cr,uid,{'invoice_id': inv,
				# 										'product_id': disc_id,
				# 										'name'		: disc_name,
				# 										'quantity'	: 1 ,
				# 										'price_unit': disc_amount,
				# 										'account_id': disc_coa},context=context)

				elif disc_code == '5':
					if partner.riwayat_pendidikan_ids:
						ranking = 0
						for pend in partner.riwayat_pendidikan_ids:
							if pend.satu_yayasan :
								ranking = pend.ranking
								break
						if ranking > 0 :		
							if ranking >= disc_nilai and ranking <= disc_nilai_max:
								for inv in inv_ids:	
									inv_line.create(cr,uid,{'invoice_id': inv,
															'product_id': disc_id,
															'name'		: disc_name,
															'quantity'	: 1 ,
															'price_unit': disc_amount,
															'account_id': disc_coa},context=context)
								break
		return True

	def add_discount_bangunan(self, cr, uid, ids ,partner, inv_id, context=None):
		tahun_ajaran 	= partner.tahun_ajaran_id
		fakultas 		= partner.fakultas_id
		prodi 			= partner.prodi_id 
		jml_inv 		= partner.split_invoice
		bea_obj 		= self.pool.get('beasiswa.prodi')
		data_bea 		= bea_obj.search(cr,uid,[('is_active','=',True),
											('tahun_ajaran_id','=',tahun_ajaran.id),
											('fakultas_id','=',fakultas.id),
											('prodi_id','=',prodi.id),],context=context)
		if data_bea :
			inv_line = self.pool.get('account.invoice.line')
			bea_line_obj = self.pool.get('beasiswa.prodi.detail')	

			#########################################################
			# cari dan hitung disc yg memerlukan sequence
			#########################################################
			cr.execute("""SELECT id
							FROM beasiswa_prodi_detail
							WHERE sequence >= 0
							AND beasiswa_prodi_id = %s
							AND uang_bangunan = True
							ORDER BY sequence ASC """%(data_bea[0]))
			disc_seq = cr.fetchall()
			if disc_seq :				
				self.add_discount_sequence_bangunan(cr, uid, ids ,disc_seq,inv_line,bea_line_obj,partner,jml_inv,inv_id, context=context)


			#########################################################
			# cari dan hitung disc yg tidak memerlukan sequence
			#########################################################
			cr.execute("""SELECT id
							FROM beasiswa_prodi_detail
							WHERE sequence < 0
							AND beasiswa_prodi_id = %s
							AND uang_bangunan = True
							ORDER BY sequence ASC """%(data_bea[0]))
			disc_non_seq = cr.fetchall()
			if disc_non_seq :
				self.add_discount_sequence_bangunan(cr, uid, ids ,disc_non_seq,inv_line,bea_line_obj,partner,jml_inv,inv_id, context=context)

		return True


	def create_inv_pendaftaran(self,cr,uid,ids,context=None):
		byr_obj = self.pool.get('master.pembayaran.pendaftaran')
		for partner in self.browse(cr,uid,ids):
			byr_sch = byr_obj.search(cr,uid,[('tahun_ajaran_id','=',partner.tahun_ajaran_id.id),
				('fakultas_id','=',partner.fakultas_id.id),
				('prodi_id','=',partner.prodi_id.id),
				('state','=','confirm'),
				('type_mhs_id','=',partner.type_mhs_id.id),
				])	
			if not byr_sch:
				byr_sch = byr_obj.search(cr,uid,[('tahun_ajaran_id','=',partner.tahun_ajaran_id.id),
					('fakultas_id','=',partner.fakultas_id.id),
					('prodi_id','=',partner.prodi_id.id),
					('state','=','confirm'),
					])						
			if byr_sch :
				byr_brw = byr_obj.browse(cr,uid,byr_sch[0],context=context)
				list_pembayaran = byr_brw.detail_product_ids
				prod_id = []
				for bayar in list_pembayaran:
					#import pdb;pdb.set_trace()
					product = self.pool.get('product.product').browse(cr,uid,bayar.product_id.id)
					coa_line = product.property_account_income.id
					if not coa_line:
						coa_line = product.categ_id.property_account_income_categ.id

					prod_id.append((0,0,{'product_id'	: bayar.product_id.id,
										 'name'			: bayar.product_id.name,
										 'price_unit'	: bayar.public_price,
										 'account_id'	: coa_line}))
				inv = self.pool.get('account.invoice').create(cr,uid,{
					'partner_id':partner.id,
					'origin': 'Pendaftaran '+str(partner.reg),
					'type':'out_invoice',
					'fakultas_id': partner.fakultas_id.id,
					'prod_id': partner.prodi_id.id,
					'account_id':partner.property_account_receivable.id,
					'invoice_line': prod_id,
					},context=context)

				
				#wf_service = netsvc.LocalService('workflow')
				from openerp import workflow
				workflow.trg_validate(uid, 'account.invoice', inv, 'invoice_open', cr)
				self.pool.get('account.invoice').invoice_validate(cr, uid, [inv], context=context)			
				self.write(cr,uid,partner.id,{'invoice_id':inv})
				


		return True		


	def verifikasi_daftar_ulang(self,cr,uid,ids,context=None):
		
		byr_obj = self.pool.get('master.pembayaran')
		usm_obj = self.pool.get('jadwal.usm')
		smt_obj = self.pool.get('master.semester')
		
		for partner in self.browse(cr,uid,ids):
			byr_sch = byr_obj.search(cr,uid,[('tahun_ajaran_id','=',partner.tahun_ajaran_id.id),
				('fakultas_id','=',partner.fakultas_id.id),
				('prodi_id','=',partner.prodi_id.id),
				('state','=','confirm'),
				('type_pendaftaran','=',partner.type_pendaftaran)
				])

			if byr_sch :
				smt_exist = smt_obj.search(cr,uid,[('name','=',1)])
				if not smt_exist :
					raise osv.except_osv(_("Warning"),_("Tidak ada Semester 1 di master semester !"))
				smt_1 = smt_obj.browse(cr,uid,smt_exist[0])
				byr_brw = byr_obj.browse(cr,uid,byr_sch[0],context=context)
				list_pembayaran = byr_brw.detail_product_ids
				prod_id = []
				discount = 0
				for bayar in list_pembayaran[:1]:
					if bayar.semester_id.id == smt_1.id :
						up_uk = bayar.total
						
						product = self.pool.get('product.product').browse(cr,uid,bayar.product_ids[0].id)
						coa_line = product.property_account_income.id
						if not coa_line:
							coa_line = product.categ_id.property_account_income_categ.id
						# if not coa_line :
						# 	raise osv.except_osv(_("Warning"),_("CoA untuk tahun akademik dan prodi ini belum di set di master uang kuliah !"))
						total_potongan = 0
						#cari potongan
						pot_usm_exist = usm_obj.search(cr,uid,[('date_start','<=',partner.tgl_daftar),('date_end','>=',partner.tgl_daftar)])
						if pot_usm_exist :
							pot = usm_obj.browse(cr,uid,pot_usm_exist[0])
							disc_usm 		= pot.discount
							disc_tunai 		= pot.discount_tunai
							disc_alumni  	= pot.discount_alumni
							disc_lembaga	= pot.discount_lembaga
							disc_karyawan	= pot.discount_karyawan
							disc_rank1		= pot.discount_ranking1
							disc_rank2		= pot.discount_ranking2
							disc_rank3		= pot.discount_ranking3
							disc_non_rank	= pot.discount_non_ranking

							discount = disc_usm+disc_lembaga
							# jika calon merupakan alumni satu yayasan
							if partner.hubungan == 'cikini':	
								if partner.ranking == 1 :	
									up 		= byr_brw.uang_semester
									up_disc = (up*disc_rank1)/100
									new_up 	= up-up_disc
								elif partner.ranking == 2 :	
									up 		= byr_brw.uang_semester
									up_disc = (up*disc_rank2)/100
									new_up 	= up-up_disc
								elif partner.ranking == 3 :
									up 		= byr_brw.uang_semester
									up_disc = (up*disc_rank3)/100
									new_up 	= up-up_disc
								else : 
									up 		= byr_brw.uang_semester
									up_disc = (up*disc_non_rank)/100
									new_up 	= up-up_disc			
								up_uk = new_up
								# diskon di 0 kan karena tidak boleh akumulasi
								discount = 0
							elif partner.hubungan == 'ortu' :
								if partner.keluarga_alumni_id :
									discount += disc_alumni
							elif partner.hubungan == 'karyawan' :
								if partner.karyawan_id :
									discount += disc_karyawan	

							####################################################################
							# tambah logic special price (ignore semua potongan)
							####################################################################
							if byr_brw.is_special_price :
								discount = 0
								up_uk = byr_brw.uang_semester
								prod_id.append((0,0,{'product_id'	: bayar.product_ids[0].id,
													 'name'			: bayar.product_ids[0].name,
													 'price_unit'	: up_uk,
													 'discount'		: discount,
													 'account_id'	: coa_line}))
								inv = self.pool.get('account.invoice').create(cr,uid,{
									'partner_id':partner.id,
									'origin': 'UP dan UK '+str(partner.reg),
									'type':'out_invoice',
									'fakultas_id': partner.fakultas_id.id,
									'prod_id': partner.prodi_id.id,
									'date_due':bayar.date1,
									'account_id':partner.property_account_receivable.id,
									'invoice_line': prod_id,
									},context=context)

								#wf_service = netsvc.LocalService('workflow')
								from openerp import workflow
								workflow.trg_validate(uid, 'account.invoice', inv, 'invoice_open', cr)
								#self.pool.get('account.invoice').invoice_validate(cr, uid, [inv], context=context)				
								self.write(cr,uid,partner.id,{'invoice_bangunan_id':inv})

								# create notifikasi ke email
								template_pool = self.pool.get('email.template')
								template_id = template_pool.search(cr,uid,[('name','=ilike','Uang Pengembangan dan Uang Kuliah ISTN')])
								if template_id:
									self.pool.get('email.template').send_mail(cr, uid, template_id[0], inv)
									
								break
							##################################################################################
							##################################################################################		

							if partner.split_invoice == 1 :									
								# create 1 invoice
								discount += disc_tunai
								prod_id.append((0,0,{'product_id'	: bayar.product_ids[0].id,
													 'name'			: bayar.product_ids[0].name,
													 'price_unit'	: up_uk,
													 'discount'		: discount,
													 'account_id'	: coa_line}))
								inv = self.pool.get('account.invoice').create(cr,uid,{
									'partner_id':partner.id,
									'origin': 'UP dan UK '+str(partner.reg),
									'type':'out_invoice',
									'fakultas_id': partner.fakultas_id.id,
									'prod_id': partner.prodi_id.id,
									'date_due':bayar.date1,
									'account_id':partner.property_account_receivable.id,
									'invoice_line': prod_id,
									},context=context)

								#wf_service = netsvc.LocalService('workflow')
								from openerp import workflow
								workflow.trg_validate(uid, 'account.invoice', inv, 'invoice_open', cr)
								#self.pool.get('account.invoice').invoice_validate(cr, uid, [inv], context=context)				
								self.write(cr,uid,partner.id,{'invoice_bangunan_id':inv})

								# create notifikasi ke email
								template_pool = self.pool.get('email.template')
								template_id = template_pool.search(cr,uid,[('name','=ilike','Uang Pengembangan dan Uang Kuliah ISTN')])
								if template_id:
									self.pool.get('email.template').send_mail(cr, uid, template_id[0], inv)

							elif partner.split_invoice > 1 :
								cicil_up_uk = 0
								if discount > 0 :
									cicil_up_uk = ((up_uk*discount)/100) /partner.split_invoice
								angske = 1
								# create invoice (looping sesuai jumlah angsuran)
								# import pdb;pdb.set_trace()
								for angs in range(0,partner.split_invoice):
									upuk = 'UP dan UK '
									if angske == 1 :
										price_unit = round(bayar.angsuran1-cicil_up_uk,0)
										due_date = bayar.date1
										date_invoice = False
									elif angske == 2 :
										price_unit = round(bayar.angsuran2-cicil_up_uk,0)
										due_date = bayar.date2
										date_invoice = bayar.date1
									elif angske == 3 :
										price_unit = round(bayar.angsuran3-cicil_up_uk,0)
										due_date = bayar.date3
										date_invoice = bayar.date2
									elif angske == 4 :
										price_unit = round(bayar.angsuran4-cicil_up_uk,0)
										due_date = bayar.date4
										date_invoice = bayar.date3
									elif angske == 5 :
										price_unit = round(bayar.angsuran5-cicil_up_uk,0)
										due_date = bayar.date5
										date_invoice = bayar.date4
									elif angske == 6 :
										price_unit = round(bayar.angsuran6-cicil_up_uk,0)		
										due_date = bayar.date6
										date_invoice = bayar.date5
									else :
										break
									inv = self.pool.get('account.invoice').create(cr,uid,{
											'partner_id':partner.id,
											'origin': upuk+str(partner.reg)+' - '+str(angske),
											'type':'out_invoice',
											'fakultas_id': partner.fakultas_id.id,
											'prod_id': partner.prodi_id.id,
											'account_id':partner.property_account_receivable.id,
											'date_invoice' : date_invoice,
											'date_due' : due_date,
											'invoice_line': [((0,0,{'product_id'	: bayar.product_ids[0].id,
																	 'name'			: bayar.product_ids[0].name,
																	 'price_unit'	: price_unit,
																	 'discount'		: 0,
																	 'account_id'	: coa_line}))],
											},context=context)
									if angske == 1 :
										#wf_service = netsvc.LocalService('workflow')
										from openerp import workflow
										workflow.trg_validate(uid, 'account.invoice', inv, 'invoice_open', cr)
										#self.pool.get('account.invoice').invoice_validate(cr, uid, [inv], context=context)				
										self.write(cr,uid,partner.id,{'invoice_bangunan_id':inv})

										# create notifikasi ke email
										template_pool = self.pool.get('email.template')
										template_id = template_pool.search(cr,uid,[('name','=ilike','Uang Pengembangan dan Uang Kuliah ISTN')])
										if template_id:
											self.pool.get('email.template').send_mail(cr, uid, template_id[0], inv)

									angske += 1
							

		return True	


	def create_krs_smt_1_dan_2(self,cr,uid,ids,context=None):
		calon_obj = self.pool.get('res.partner.calon.mhs')
		bea_obj = self.pool.get('beasiswa.prodi')
		kurikulum_obj = self.pool.get('master.kurikulum')
		krs_obj = self.pool.get('operasional.krs')
		smt_obj = self.pool.get('master.semester')
		#import pdb; pdb.set_trace()
		for partner in self.browse(cr,uid,ids):
			t_id = partner.tahun_ajaran_id.date_start
			t_tuple =  tuple(t_id)
			t_id_final = t_tuple[2]+t_tuple[3]#ambil 2 digit paling belakang dari tahun saja
			f_id = partner.fakultas_id.kode	
			p_id = partner.prodi_id.kode
			lokasi = partner.alamat_id.kode
			t_pend = partner.type_pendaftaran

			smt1_exist = smt_obj.search(cr,uid,[('name','=',1)])
			smt1_id = smt_obj.browse(cr,uid,smt1_exist[0]).id

			smt2_exist = smt_obj.search(cr,uid,[('name','=',2)])
			smt2_id = smt_obj.browse(cr,uid,smt2_exist[0]).id

			if t_pend == 'ganjil' :
				pend = '1'
			else:
				pend = '2'

			if p_id.find(".") != -1:
				j = p_id.split(".")
				p_id = j[1]					
			#batas nilai penerima beasiswa
			limit_bea = 1000 # default nilai besar supaya tidak ada yg lolos
			data_bea = bea_obj.search(cr,uid,[('is_active','=',True),
												('tahun_ajaran_id','=',partner.tahun_ajaran_id.id),
												('fakultas_id','=',partner.fakultas_id.id),
												('prodi_id','=',partner.prodi_id.id),],context=context)			
			if data_bea:
				bea_browse=bea_obj.browse(cr,uid,data_bea[0])
				if bea_browse.product_id1:
					limit_bea = bea_browse.limit_nilai_sma

			is_bea = False
			if partner.nilai_beasiswa >= limit_bea:
				is_bea = True
			st = partner.status_mahasiswa
			nilai_sma = partner.nilai_beasiswa
			jp_id = partner.jenis_pendaftaran_id.code

			se = self.pool.get('ir.sequence').get(cr, uid, 'seq.npm.partner') or '/'

			# sql = "select count(*) from res_partner where jenis_pendaftaran_id=%s and jurusan_id=%s and tahun_ajaran_id=%s" % (
			sql = "select count(*) from res_partner where jenis_pendaftaran_id=%s and prodi_id=%s and tahun_ajaran_id=%s and status_mahasiswa='Mahasiswa' " % (
				partner.jenis_pendaftaran_id.id, 
				partner.prodi_id.id, 
				partner.tahun_ajaran_id.id)
			cr.execute(sql)
			
			hasil = cr.fetchone()
			if hasil and hasil[0] != None:
				se = "%04d" % (hasil[0] + 1)
			else:
				se = "0001"

			nim = t_id_final +pend+ f_id+p_id +lokasi+ jp_id + se
			self.write(cr,uid,partner.id,{
										'status_mahasiswa':'Mahasiswa',
										'npm':nim,
										'user_id':uid,
										'is_beasiswa':is_bea},
										context=context)

			#create data calon yang lulus tersebut ke tabel res.partner.calon.mhs agar ada history terpisah
			calon_obj.create(cr,uid,{'reg'				:partner.reg,
									'name'				:partner.name,
									'jenis_kelamin'		:partner.jenis_kelamin or False,
									'tempat_lahir'		:partner.tempat_lahir or False,
									'tanggal_lahir'		:partner.tanggal_lahir or False,                  
									'fakultas_id'		:partner.fakultas_id.id,
									'prodi_id'			:partner.prodi_id.id,
									'tahun_ajaran_id'	:partner.tahun_ajaran_id.id,                
									'tgl_lulus'			:partner.tgl_lulus or False,
									'no_formulir'		:partner.no_formulir or False,
									'tgl_ujian'			:partner.tgl_ujian or False,
									'nilai_ujian'		:partner.nilai_ujian or False,
									'batas_nilai'		:0,
									'status_pernikahan'	:partner.status_pernikahan or False,
									'agama'				:partner.agama or False,
									'tgl_daftar'		:partner.tgl_daftar or False,
									'nilai_beasiswa'	:nilai_sma or False,
									'is_beasiswa' 		:is_bea,
									'state'				:'lulus',
									'date_move'			:time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
									'user_id'			:uid},									
									context=context)
			kur_sch_smt_1 = kurikulum_obj.search(cr,uid,[('tahun_ajaran_id','=',partner.tahun_ajaran_id.id),
				('fakultas_id','=',partner.fakultas_id.id),
				('prodi_id','=',partner.prodi_id.id),
				('state','=','confirm'),
				('semester_id','=',smt1_id),
				])
			if kur_sch_smt_1 :
				#kur_id   = kurikulum_obj.browse(cr,uid,kur_sch_smt_1,context=context)[0].kurikulum_detail_ids
				kur_id   = kurikulum_obj.browse(cr,uid,kur_sch_smt_1,context=context)[0].mk_kurikulum_detail_ids
				mk_kurikulum = []
				for kur in kur_id:
					#mk_kurikulum.append(kur.id)
					mk_kurikulum.append((0,0,{'mata_kuliah_id'	: kur.matakuliah_id.id,'sks':kur.sks, 'state': 'draft'}))	
				krs_obj.create(cr,uid,{'kode'					: nim+'-1',
											'partner_id'		: partner.id,
											'tahun_ajaran_id'	: partner.tahun_ajaran_id.id,
											'fakultas_id'		: partner.fakultas_id.id,
											'prodi_id'			: partner.prodi_id.id,
											'kurikulum_id'		: kur_sch_smt_1[0],
											'semester_id'		: smt1_id,
											'kelas_id'			: partner.kelas_id.id or False,
											'user_id'			: uid,
											'konsentrasi_id'	: partner.konsentrasi_id.id,
											'state'				: 'confirm',
											'krs_detail_ids'	: mk_kurikulum
											})	

			kur_sch_smt_2 = kurikulum_obj.search(cr,uid,[('tahun_ajaran_id','=',partner.tahun_ajaran_id.id),
				('fakultas_id','=',partner.fakultas_id.id),
				('prodi_id','=',partner.prodi_id.id),
				('state','=','confirm'),
				('semester_id','=',smt2_id),
				])			
			if kur_sch_smt_2 :
				#kur_id   = kurikulum_obj.browse(cr,uid,kur_sch_smt_2,context=context)[0].kurikulum_detail_ids
				kur_id   = kurikulum_obj.browse(cr,uid,kur_sch_smt_2,context=context)[0].mk_kurikulum_detail_ids
				mk_kurikulum = []
				for kur in kur_id:
					mk_kurikulum.append((0,0,{'mata_kuliah_id'	: kur.matakuliah_id.id,'sks':kur.sks, 'state': 'draft'}))
				krs_obj.create(cr,uid,{'kode'				: nim+'-2',
										'partner_id'		: partner.id,
										'tahun_ajaran_id'	: partner.tahun_ajaran_id.id,
										'fakultas_id'		: partner.fakultas_id.id,
										'prodi_id'			: partner.prodi_id.id,
										'kurikulum_id'		: kur_sch_smt_2[0],
										'semester_id'		: smt2_id,
										'kelas_id'			: partner.kelas_id.id or False,
										'user_id'			: uid,
										'konsentrasi_id'	: partner.konsentrasi_id.id,
										#'state'			: 'draft',
										'krs_detail_ids'	: mk_kurikulum
										})


	@api.multi
	def write(self, vals):
		# res.partner must only allow to set the company_id of a partner if it
		# is the same as the company of all users that inherit from this partner
		# (this is to allow the code from res_users to write to the partner!) or
		# if setting the company_id to False (this is compatible with any user
		# company)
		#
		if vals.get('website'):
			vals['website'] = self._clean_website(vals['website'])
		if vals.get('company_id'):
			company = self.env['res.company'].browse(vals['company_id'])
			for partner in self:
				if partner.user_ids:
					companies = set(user.company_id for user in partner.user_ids)
					if len(companies) > 1 or company not in companies:
						raise osv.except_osv(_("Warning"),_("You can not change the company as the partner/user has multiple user linked with different companies."))
		result = super(res_partner, self).write(vals)
		# tambah logic jika update data calon mahasiswa dari web, create inv pendaftaran
		inv = False
		if vals.get('status_mahasiswa') :
			if vals.get('status_mahasiswa') == 'calon' :
				prodi_obj = self.env['master.prodi']
				coa_prodi = prodi_obj.search([('id','=',vals.get('prodi_id'))]).coa_piutang_id.id,

				byr_obj = self.env['master.pembayaran.pendaftaran']
				for partner in self:
					inv_obj = self.env['account.invoice']
					# search dulu apa inv pendaftaran untuk partner ini pernah dibuat ?
					inv_pendf_exist = inv_obj.search([('partner_id','=',partner.id),('origin','ilike','Pendaftaran')])
					if inv_pendf_exist :
						break
					byr_sch = byr_obj.search([('tahun_ajaran_id','=',vals.get('tahun_ajaran_id')),
						('prodi_id','=',vals.get('prodi_id')),
						('state','=','confirm'),
						('type_mhs_id','=',vals.get('type_mhs_id')),
						('lokasi_kampus_id','=',vals.get('alamat_id')),
						])	
					if not byr_sch:
						byr_sch = byr_obj.search([('tahun_ajaran_id','=',vals.get('tahun_ajaran_id')),
							('prodi_id','=',vals.get('prodi_id')),
							('state','=','confirm'),
							('lokasi_kampus_id','=',vals.get('alamat_id')),
							])	

					if byr_sch :
						prod_id = []
						for bayar in byr_sch[0].detail_product_ids:
							product = bayar.product_id
							coa_line = product.property_account_income.id
							if not coa_line:
								coa_line = product.categ_id.property_account_income_categ.id

							prod_id.append((0,0,{'product_id'	: self.env['product.product'].search([('product_tmpl_id','=',product.id)]).id,
												 'name'			: product.name,
												 'price_unit'	: bayar.public_price,
												 'account_id'	: coa_line}))
						inv = self.env['account.invoice'].create({
							'partner_id':partner.id,
							'origin': 'Pendaftaran: '+str(partner.reg),
							'type':'out_invoice',					
							'fakultas_id':  vals.get('fakultas_id'),
							'prod_id': vals.get('prodi_id'),
							'account_id':coa_prodi,
							'invoice_line': prod_id,
							})
						#self._cr.commit()
						#wf_service = netsvc.LocalService('workflow')
						#import pdb;pdb.set_trace()
						from openerp import workflow
						workflow.trg_validate(self._uid, 'account.invoice', inv.id, 'invoice_open', self._cr)
						vals.update({'invoice_id':inv.id})
						result = super(res_partner, self).write(vals)
						
		for partner in self:
			self._fields_sync(partner, vals)
		return result


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
		'status_mahasiswa' : SESSION_STATES[3][0],
		#'angkatan': lambda*a : time.strftime('%Y'),
		'tgl_daftar' : fields.date.context_today,
		#'npm':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'res.partner'), 
		'npm' : '/',  
		'reg': '/',
		'no_ijazah_sma':'/',
		'is_mahasiswa': False,
		'split_invoice': 1,
		'is_import' : False,
	}



	def action_konversi(self,cr,uid,ids,context=None):
		konv_obj = self.pool.get('akademik.konversi')

		for mhs in self.browse(cr, uid, ids, context=context):
			exist = konv_obj.search(cr,uid,[('partner_id','=',mhs.id)],context=context)
			# if exist:
			# 	raise osv.except_osv(_('Error!'), _('Data konversi sudah pernah dibuat!'))
			if not exist :
				data = {
					'partner_id' 		: mhs.id,
					'semester_id'		: mhs.semester_id.id,
					'asal_prodi_id'		: mhs.asal_prodi_id.id,
					'asal_fakultas_id'	: mhs.asal_fakultas_id.id,
					'asal_univ_id'		: mhs.asal_univ_id.id,
					'prodi_id'			: mhs.prodi_id.id,
					'fakultas_id'		: mhs.fakultas_id.id,
					'tahun_ajaran_id'	: mhs.tahun_ajaran_id.id,
					'konsentrasi_id'	: mhs.konsentrasi_id.id,
					'status'			: 'draft',
					'state'				: 'draft',
					'notes' 			: mhs.jenis_pendaftaran_id.name,
					'user_id'			: uid,
					'date'				: mhs.tgl_daftar,
					'create_date'		: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
					'krs_done'			: False,
				}
				konv_id = konv_obj.create(cr, uid, data, context=context)

				# create email notif ke user prodi (doc. konversi)
				groups_obj = self.pool.get('res.groups')
				users  = groups_obj.search(cr,uid,[('name','ilike','Staff Prodi')], context=context)
				if users :
					users_ids = groups_obj.browse(cr,uid,users[0])
					if users_ids.users :
						for usr in users_ids.users :					
							konv_obj.convertion_notification(cr, uid, [konv_id], usr)
		return True


	####################################################################################################
	# Cron Job untuk reminder tagihan pendaftaran
	####################################################################################################
	def cron_reminder_tagihan_pendaftaran(self, cr, uid, ids=None,context=None):
		partner_obj 	= self.pool.get('res.partner')
		account_obj 	= self.pool.get('account.invoice')
		#import pdb;pdb.set_trace()
		tagihan_pendaftaran = account_obj.search(cr,uid,[('state','=','open'),('origin','ilike','pendaftaran')])
		if tagihan_pendaftaran :
			# create notifikasi ke email
			template_pool = self.pool.get('email.template')
			template_id = template_pool.search(cr,uid,[('name','=ilike','[REMINDER] Pendaftaran Mahasiswa Baru ISTN')])
			if template_id :
				for tag in account_obj.browse(cr,uid,tagihan_pendaftaran):
					template_pool.send_mail(cr, uid, template_id[0], tag.id)
		return True

res_partner()				