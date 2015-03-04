from osv import osv, fields
from openerp.tools.translate import _


class operasional_krs (osv.Model):
	_name= 'operasional.krs'
	_rec_name='kode'

	def create(self, cr, uid, vals, context=None):

		if not vals['krs_detail_ids']:
			raise osv.except_osv(_('Error!'), _('Matakuliah tidak boleh kosong !'))		
		if vals.get('kode','/')=='/':
			npm = vals['npm']
			if not npm :
				npm = '<<npm_kosong>> '
			smt = vals['semester_id']
			smt_name = self.pool.get('master.semester').browse(cr,uid,smt,context=context).name
			vals['kode'] = npm +'-'+str(smt_name) or '/'
		if vals['kurikulum_id']:
			kurikulum = vals['kurikulum_id']
			klm_brw = self.pool.get('master.kurikulum').browse(cr,uid,kurikulum)
			t_sks = klm_brw.max_sks
			sks_kurikulum = 0
			mk_ids_kurikulum = []
			for klm in klm_brw.kurikulum_detail_ids:
				mk_ids_kurikulum.append(klm.id)
				sks_kurikulum += int(klm.sks)

		#cek partner dan semester yang sama
		krs_uniq = self.search(cr,uid,[('partner_id','=',vals['partner_id']),('semester_id','=',vals['semester_id'])])
		if krs_uniq != []:
			raise osv.except_osv(_('Error!'),
								_('KRS untuk mahasiswa dengan semester ini sudah dibuat!'))	

		#cek krs_detail tdk boleh kosong
		if not vals['krs_detail_ids']:
			raise osv.except_osv(_('Error!'),
								_('Matakuliah harus di isi !'))	

		mk = vals['krs_detail_ids']
		mk_ids = []
		tot_mk = 0
		for m in mk:
			mk_id = m[2]['mata_kuliah_id']
			mk_ids.append(mk_id)
			sks = self.pool.get('master.matakuliah').browse(cr,uid,mk_id,context=context).sks
			tot_mk += int(sks)

		if tot_mk > t_sks :
			raise osv.except_osv(_('Error!'), _('Total matakuliah (%s SKS) melebihi batas maximal SKS (%s SKS) !')%(tot_mk,t_sks))	
		#import pdb;pdb.set_trace()
		#cek jika mengambil matakuliah lebih
		tambahan_mk = 0
		ids_tambahan_mk = []#ambil id matakuliah yang diinput lebih
		for tambahan in mk:
			if tambahan[2]['mata_kuliah_id'] not in mk_ids_kurikulum:
				mk_id = tambahan[2]['mata_kuliah_id']
				sks = self.pool.get('master.matakuliah').browse(cr,uid,mk_id,context=context).sks
				tambahan_mk += int(sks)
				ids_tambahan_mk.append(mk_id)
		selisih_tambahan_mk = t_sks - sks_kurikulum
		
		#pastikan matakuliah yang di tambah tidak lebih dari jatah yg bisa di inputkan
		if tambahan_mk > selisih_tambahan_mk:			
			raise osv.except_osv(_('Error!'), _('Total matakuliah (%s SKS) melebihi batas maximal SKS (%s SKS) !')%(tot_mk,t_sks))	

		#cek juga apa di setingan kurikulum mengijinkan tambah MK sesuai dengan minimal IP sementara
		if klm_brw.min_ip > 0 : #settingan IP di kurikulum harus di isi angka positif
			if len(mk_ids) > len(mk_ids_kurikulum) :
				#hitung IP sementara partner ini
				cr.execute("""SELECT okd.id, okd.mata_kuliah_id
								FROM operasional_krs_detail okd
								LEFT JOIN operasional_krs ok ON ok.id = okd.krs_id
								WHERE ok.partner_id = %s
								AND ok.state <> 'draft'"""%(vals['partner_id']))
				dpt = cr.fetchall()
				
				det_id = []
				total_mk_ids = []
				for x in dpt:
					x_id = x[0]
					det_id.append(x_id)
					total_mk_ids.append(x[1])

				#cek mk yang dinput lebih harus yang belum di tempuh pada semester sebelumnya
				mk_baru_ids = []
				if ids_tambahan_mk != []:
					for mk_krs in ids_tambahan_mk:	#mk yang baru di tambah
						if mk_krs not in total_mk_ids:#mk-mk yg telah ditempuh pd semester sebelumnya
							mk_baru_ids.append(mk_krs)

				det_sch = self.pool.get('operasional.krs_detail').browse(cr,uid,det_id,context=context)
				sks = 0
				bobot_total = 0.00
				total_mk_ids = []	
				for det in det_sch:
					sks += det.sks
					bobot_total += (det.nilai_angka*det.sks)			

				### ips = (total nilai angka*total sks) / total sks
				if sks == 0:
					ips = 0
				else :
					ips = round(bobot_total/sks,2)
			
				#jika ada mk bru yg di inputkan dan ip tidak memenuhi syarat
				if ips <= klm_brw.min_ip :
					if mk_baru_ids != []:
				 		raise osv.except_osv(_('Error!'), _('Indeks Prestasi Sementara (%s) kurang dari standar minimal untuk tambah matakuliah semester depan(%s) !')%(ips,klm_brw.min_ip))	

		#langsung create invoice nya
		byr_obj = self.pool.get('master.pembayaran')
		byr_sch = byr_obj.search(cr,uid,[('tahun_ajaran_id','=',vals['tahun_ajaran_id']),
			('fakultas_id','=',vals['fakultas_id']),
			('jurusan_id','=',vals['jurusan_id']),
			('prodi_id','=',vals['prodi_id']),
			('state','=','confirm'),
			])		
		if byr_sch != []:
			byr_brw = byr_obj.browse(cr,uid,byr_sch[0],context=context)
			list_pembayaran = byr_brw.detail_product_ids
			for bayar in list_pembayaran:
				
				#jika menemukan semester yang sama
				if vals['semester_id'] == bayar.semester_id.id:
					list_product = bayar.product_ids
					prod_id = []					
					for lp in list_product:
						prod_id.append((0,0,{'product_id': lp.id,'name':lp.name,'price_unit':lp.list_price}))

					prod_obj = self.pool.get('product.product')
					beban_sks_id = prod_obj.search(cr,uid,[('is_sks','=',True),('fakultas_id','=',vals['fakultas_id'])])

					if byr_brw.type == 'paket':
						if beban_sks_id != [] :
							prod_brw = prod_obj.browse(cr,uid,beban_sks_id[0],context=context)
							prod_id.append((0,0,{'product_id': beban_sks_id[0],'name':prod_brw.name,'quantity':tot_mk ,'price_unit':prod_brw.list_price}))

					elif byr_brw.type == 'flat':
						if beban_sks_id != [] and byr_brw.sks_plus == True:
							if tambahan_mk != 0:
								prod_brw = prod_obj.browse(cr,uid,beban_sks_id[0],context=context)
								prod_id.append((0,0,{'product_id': beban_sks_id[0],'name':prod_brw.name,'quantity':tambahan_mk ,'price_unit':prod_brw.list_price}))							

					inv_id = self.pool.get('account.invoice').create(cr,uid,{
							'partner_id':vals['partner_id'],
							'origin': str(self.pool.get('res.partner').browse(cr,uid,vals['partner_id']).npm) +'-'+ str(self.pool.get('master.semester').browse(cr,uid,vals['semester_id']).name),
							'type':'out_invoice',
							'account_id':self.pool.get('res.partner').browse(cr,uid,vals['partner_id']).property_account_receivable.id,
							'invoice_line': prod_id,
							},context=context)
					if inv_id :
						inv = {'invoice_id':inv_id}
						vals = dict(vals.items()+inv.items())						
					
							
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
		#import pdb;pdb.set_trace()	
		### ips = (total nilai angka*total sks) / total sks
		if sks == 0:
			ips = 0
		else :
			ips = round(bobot_total/sks,2)
		res[ids[0]] = ips
		return res
	
	_columns = {
		'kode' : fields.char('Kode', 128, readonly=True),
		'state':fields.selection([('draft','Draft'),('confirm','Confirm'),('done','Done')],'Status',readonly=True),
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
		'invoice_id' : fields.many2one('account.invoice','Invoice',domain=[('type', '=','out_invoice')],readonly=True),
			}    
				 
	_defaults={
		'state' : 'draft', 
		'kode': '/',
		'user_id': lambda obj, cr, uid, context: uid,
	}

	def confirm(self, cr, uid, ids, context=None):
		#import pdb;pdb.set_trace()
		form_id = self.browse(cr,uid,ids[0],context=context) 
		for x in form_id.krs_detail_ids:
			self.pool.get('operasional.krs_detail').write(cr,uid,x.id,{'state':'confirm'},context=context)
		#cek dahulu pembayaran atas KRS ini,
		if form_id.invoice_id.state != 'paid':
			raise osv.except_osv(_('Error!'), _('Pembayaran atas KRS ini harus dibayar lunas dahulu !'))	
		self.write(cr, uid, ids, {'state' : 'confirm'}, context=context)
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_universities', 'krs_tree_view')
		view_id = view_ref and view_ref[1] or False,		
		return {
			'name' : _('Temporary View'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'operasional.krs',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			'domain' : "[('state','=','draft')]",
			#'context': "{'default_state':'open'}",#
			'nodestroy': False,
			}

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

	def onchange_semester(self, cr, uid, ids, npm, tahun_ajaran_id, prodi_id, semester_id, partner_id, context=None):

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

		#cek partner dan semester yang sama
		krs_uniq = self.search(cr,uid,[('partner_id','=',partner_id),('semester_id','=',semester_id)])
		if krs_uniq != []:
			raise osv.except_osv(_('Error!'),
								_('KRS untuk mahasiswa dengan semester ini sudah dibuat!'))			
		
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
		
		total_mk_ids = []
		for x in dpt:
			total_mk_ids.append(x[1])
		#import pdb;pdb.set_trace()
		#filter matakuliah yg benar-benar belum di tempuh
		mk_baru_ids =set(mk_kurikulum).difference(total_mk_ids)

		res = []
		for kur in mk_baru_ids:
			res.append([0,0,{'mata_kuliah_id': kur,'state':'draft'}])	
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
		'state':fields.selection([('draft','Draft'),('confirm','Confirm'),('done','Done')],'Status',readonly=False),
			}

	_defaults={
		'state' : 'draft', 
	}
	 
krs_detail()

 
class operasional_transkrip(osv.Model):
	_name='operasional.transkrip'

	def create(self, cr, uid, vals, context=None):
		
		if 'partner_id' in vals:
			mhs = vals['partner_id']
			partner_brw = self.pool.get('res.partner').browse(cr,uid,mhs)
			prodi = partner_brw.prodi_id.id
			cek_mhs = self.search(cr,uid,[('partner_id','=',mhs),('prodi_id','=',prodi)])
			if cek_mhs != []:
				raise osv.except_osv(_('Error!'),
				('Mahasiswa ini sudah mempunyai transkrip dengan program studi dan jenjang yang sama!'))				

		return super(operasional_transkrip, self).create(cr, uid, vals, context=context)	 

		#jika penggambilan MK di KRS berdasarkan yang terbaru
	def get_mk_by_newest(self, cr, uid, ids, context=None):

		mhs_id = self.browse(cr,uid,ids[0],context=context).partner_id.id
		
		ops_obj = self.pool.get('operasional.krs')
		det_obj = self.pool.get('operasional.krs_detail')
	
		cr.execute("""SELECT okd.id AS id, okd.mata_kuliah_id AS mk,s.name AS smt,s2.name AS smt_kurikulum
						FROM operasional_krs ok
						LEFT JOIN operasional_krs_detail okd ON ok.id = okd.krs_id
						LEFT JOIN master_kurikulum mkk ON ok.kurikulum_id = mkk.id
						LEFT JOIN master_semester s ON s.id = ok.semester_id
						LEFT JOIN master_semester s2 ON s2.id = mkk.semester_id
						WHERE ok.state = 'done' AND ok.partner_id ="""+ str(mhs_id) +"""
						GROUP BY okd.id,s.name,s2.name
						ORDER BY s2.name,s.name DESC""")		   
		mk = cr.fetchall()			

		if mk == []:
			return mk
		id_mk = []	#id khsdetail
		mk_ids = [] #Matakuliah khsdetail

		for m in mk:
			#matakuliah
			if m[1] not in mk_ids:
				id_mk.append(m[0])
				mk_ids.append(m[1])

		return id_mk

		#jika penggambilan MK di KRS berdasarkan yang terbaik
	def get_mk_by_better(self, cr, uid, ids, context=None):

		mhs_id = self.browse(cr,uid,ids[0],context=context).partner_id.id
		
		ops_obj = self.pool.get('operasional.krs')
		det_obj = self.pool.get('operasional.krs_detail')
	
		cr.execute("""SELECT okd.id AS id, okd.mata_kuliah_id AS mk,okd.nilai_angka AS nilai,s2.name AS smt_kurikulum
						FROM operasional_krs ok
						LEFT JOIN operasional_krs_detail okd ON ok.id = okd.krs_id
						LEFT JOIN master_kurikulum mkk ON ok.kurikulum_id = mkk.id
						LEFT JOIN master_semester s ON s.id = ok.semester_id
						LEFT JOIN master_semester s2 ON s2.id = mkk.semester_id
						WHERE ok.state = 'done' AND ok.partner_id ="""+ str(mhs_id) +"""
						GROUP BY okd.id,s.name,s2.name
						ORDER BY s2.name, okd.nilai_angka DESC""")		   
		mk = cr.fetchall()			

		if mk == []:
			return mk
		id_mk = []	#id khsdetail
		mk_ids = [] #Matakuliah khsdetail

		for m in mk:
			#matakuliah
			if m[1] not in mk_ids:
				id_mk.append(m[0])
				mk_ids.append(m[1])

		return id_mk

	def get_total_khs(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}

		if self.browse(cr,uid,ids[0]).partner_id.tahun_ajaran_id.mekanisme_nilai == 'terbaru' :
			mk = self.get_mk_by_newest(cr, uid, ids, context=None)
		elif self.browse(cr,uid,ids[0]).partner_id.tahun_ajaran_id.mekanisme_nilai == 'terbaik' :
			mk = self.get_mk_by_better(cr, uid, ids, context=None)

		if mk == []:
			return result			

		result[ids[0]] = mk
		return result

	def _get_ipk(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}

		if self.browse(cr,uid,ids[0]).partner_id.tahun_ajaran_id.mekanisme_nilai == 'terbaru' :
			mk = self.get_mk_by_newest(cr, uid, ids, context=None)
		elif self.browse(cr,uid,ids[0]).partner_id.tahun_ajaran_id.mekanisme_nilai == 'terbaik' :
			mk = self.get_mk_by_better(cr, uid, ids, context=None)

		if mk == []:
			raise osv.except_osv(_('Error!'),
				('Untuk menggunakan fitur ini minimal harus selesai 1 semester!'))				
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
		'transkrip_detail_ids' : fields.function(get_total_khs, type='many2many', relation="operasional.krs_detail", string="Total Mata Kuliah"), 
		'ipk' : fields.function(_get_ipk,type='float',string='IPK',help="SKS = Total ( SKS * bobot nilai ) / Total SKS"),
		'yudisium' : fields.char('Yudisium',readonly=True),
		't_sks' : fields.integer('Total SKS',readonly=True),
		't_nilai' : fields.char('Total Nilai',readonly=True),
			}    

	_sql_constraints = [('name_uniq', 'unique(name)','Kode Transkrip tidak boleh sama')]

operasional_transkrip()