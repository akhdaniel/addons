# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
import base64
import simplejson, json
import logging
_logger = logging.getLogger(__name__)
import time
from datetime import datetime

class Partner(http.Controller):


	@http.route('/cek_prodi', auth='user', website=False)
	def cek_prodi(self, **kw):
		cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
		
		prodi_id 			= int(kw.get('prodi_id', ''))
		prodi_ids 			= []
		if prodi_id :
			Konsentrasi  	= http.request.env['master.konsentrasi']
			konsentrasi_ids = Konsentrasi.search([('prodi_id','=',prodi_id)])
			if konsentrasi_ids :

				for kons in konsentrasi_ids:
					konsentrasi = [kons.id,kons.name]
					prodi_ids.append(konsentrasi)
		#import pdb;pdb.set_trace()	
		# return http.request.render('vit_universities_web.registration', {
		# 	'konsentrasi_ids': konsentrasi_ids
		# })


		print json.dumps(prodi_ids)		

	######################################################################################
	# halaman registration
	# muncul form registrasi, action ke registraion_process
	######################################################################################
	@http.route('/registration', auth='user', website=True)
	def registration(self, **kw):
		cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

		message_error = kw.get('message_error','')
		message_success = kw.get('message_success','')

		User = http.request.env['res.users']
		user = User.browse( uid )
		partner = user.partner_id

		Prodi  = http.request.env['master.prodi']
		prodi_ids = Prodi.search([('is_internal','=',True)])

		Tahun  = http.request.env['academic.year']
		tahun_ids = Tahun.search([('is_active','=',True)])

		Semester  = http.request.env['master.semester']
		semester_ids = Semester.search([])

		Lokasi  = http.request.env['master.alamat.kampus']
		alamat_ids = Lokasi.search([])

		Type  = http.request.env['master.type.mahasiswa']
		type_mhs_ids = Type.search([])		
		
		Konsentrasi  = http.request.env['master.konsentrasi']
		konsentrasi_ids = Konsentrasi.search([])

		Jenis_pendaftaran  = http.request.env['akademik.jenis_pendaftaran']
		jenis_pendaftaran_ids = Jenis_pendaftaran.search([])
		
		Jenjang  = http.request.env['master.jenjang']
		jenjangs = Jenjang.search([])

		penghasilans = [('1','Dibawah Rp.1.000.000'),('2','Rp.1.000.000 - Rp.3.000.000'),('3','Rp.3.000.001 - Rp.6.000.000'),('4','Rp.6.000.001 - Rp.10.000.000'),('5','Diatas Rp.10.000.001')]

		jadwal_ids = [('pagi','Pagi'),('siang','Siang'),('malam','Malam')]
		penghasilan_ayah = [('1','Dibawah Rp.1.000.000'),('2','Rp.1.000.000 - Rp.3.000.000'),('3','Rp.3.000.001 - Rp.6.000.000'),('4','Rp.6.000.001 - Rp.10.000.000'),('5','Diatas Rp.10.000.001')]
		pekerjaans = [('pns','Pengawai Negeri Sipil'),('tni/polri','TNI/Polri'),('petani','Petani'),('peg_swasta', 'Pegawai Swasta'),('wiraswasta','Wiraswasta'),('none','Tidak Bekerja'),('lain','Lain-lain')]
		jenis_kelamins = [('L','Laki-Laki'),('P','Perempuan')]
		keadaans = [('ada','Masih Ada'),('alm','Alm')]
		agamas = [('islam','Islam'),('kristen','Kristen'),('hindu','Hindu'),('budha','Budha'),('kepercayaan','Kepercayaan')]
		type_pendaftarans = [('ganjil','Ganjil'),('genap','Genap'),('pendek','Pendek')]
		jalur_masuks = [('perorangan','Perorangan'),('group','Group'),('prestasi','Jalur Prestasi')]
		hubungans = [('umum','Umum'),('ortu','Orang Tua Alumni ISTN'),('cikini','Lulusan SLTA Perguruan Cikini'),('karyawan','Karyawan Tetap (Masih Aktif) ISTN')]
		type_pembayarans = [('1','Tunai'),('6','6 x Angsuran')]
		
		Invoice = http.request.env['account.invoice']
		invoices = Invoice.search([('origin','ilike','pendaftaran'),('partner_id','=',partner.id),('state','!=','cancel')])
		invoice = []
		if invoices :
			invoice = invoices[0]

		Survey = http.request.env['survey.survey']
		survey = Survey.search([('title','ilike','tpa')])
		if not survey:
			message = "TPA not found! Please try again later.."
			return message


		page = ''
		if partner.reg == '/' and not partner.hubungan and not invoice:
			page = 'vit_universities_web.registration'
		elif partner.reg != '/' and not partner.hubungan and invoice and invoice.state == 'paid':
			page = 'vit_universities_web.registration_view'
		elif partner.reg != '/' and  partner.hubungan and invoice and invoice.state == 'paid':
			page = 'vit_universities_web.registration_view2'
		else :
			page = 'vit_universities_web.registration_just_view'

		return http.request.render(page,
		{
			'partner'		: partner,
			'target_title'	: 'Registration', 
			'prodi_ids'		: prodi_ids,
			'konsentrasi_ids': konsentrasi_ids,
			'tahun_ids'		: tahun_ids,
			'alamat_ids'    : alamat_ids,
			'jenis_pendaftaran_ids' : jenis_pendaftaran_ids,
			'type_mhs_ids'	: type_mhs_ids,
			'type_mhs_ids'	: type_mhs_ids,
			'semester_ids'	: semester_ids,
			'pekerjaans'	: pekerjaans,
			'pekerjaans2'	: pekerjaans,
			'pekerjaans3'	: pekerjaans,
			'penghasilan_ayah' : penghasilan_ayah,
			'penghasilan_ibu'  : penghasilan_ayah,
			'penghasilan_penanggung' : penghasilan_ayah,
			'keadaans'		: keadaans,
			'jenis_kelamins': jenis_kelamins,
			'agamas'		: agamas,
			'type_pendaftarans': type_pendaftarans,
			'jalur_masuks'	: jalur_masuks,
			'hubungans'		: hubungans,
			'type_pembayarans': type_pembayarans,
			'jadwal_ids'		: jadwal_ids,
			'jenjangs'		: jenjangs,
			'partner'		: partner,
			'message_error'	: message_error,
			'message_success': message_success
		} )	


	######################################################################################
	# proses update data mahasiswa
	# 
	######################################################################################
	@http.route('/registration_process/<model("res.partner"):partner>', auth='user', website=True)
	def registration_process(self, partner, **kw):
		cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

		message 		= kw.get('message','')

		#akademik
		tahun_id 		= kw.get('tahun_id', '')		
		semester_id 	= kw.get('semester_id', '')	
		name 			= kw.get('name', '')		
		prodi_id 		= kw.get('prodi_id', '')
		konsentrasi_id 	= kw.get('konsentrasi_id', '')		
			
		alamat_id 		= kw.get('alamat_id', '')
		jenis_pendaftaran_id = kw.get('jenis_pendaftaran_id', '')
		type_mhs_id 	= kw.get('type_mhs_id', '')
		type_pendaftaran= kw.get('type_pendaftaran', '')
		jadwal_ids 		= kw.get('jadwal_ids', '')

		jadwal_pagi 	= kw.get('jadwal_pagi', '')
		jadwal_siang 	= kw.get('jadwal_siang', '')
		jadwal_malam 	= kw.get('jadwal_malam', '')

		#pribadi
		id_card 		= kw.get('id_card', '')
		phone 			= kw.get('phone', '')
		mobile 			= kw.get('mobile', '')
		jenis_kelamin 	= kw.get('jenis_kelamin', '')
		tempat_lahir	= kw.get('tempat_lahir', '')		
		tanggal_lahir	= kw.get('tanggal_lahir', '')		
		jenis_kelamin	= kw.get('jenis_kelamin', '')		
		agama 			= kw.get('agama', '')		
		street 			= kw.get('street', '')		
		street2			= kw.get('street2', '')		
		city			= kw.get('city', '')
		zip_code 		= kw.get('zip', '') 		

		#orang tua
		nama_ayah		= kw.get('nama_ayah', '')
		alamat_ayah		= kw.get('alamat_ayah', '')
		keadaan_ayah	= kw.get('keadaan_ayah', '')
		pekerjaan 		= kw.get('pekerjaan', '')
		telpon_ayah		= kw.get('telpon_ayah', '')	
		penghasilan_ayah= kw.get('penghasilan_ayah', '')	
		nama_ibu		= kw.get('nama_ibu', '')
		keadaan_ibu		= kw.get('keadaan_ibu', '')
		alamat_ibu		= kw.get('alamat_ibu', '')		
		pekerjaan2 		= kw.get('pekerjaan2', '')		
		telpon_ibu		= kw.get('telpon_ibu', '')	
		penghasilan_ibu = kw.get('penghasilan_ibu', '')

		#penanggung biaya kuliah	
		nama_penanggung		= kw.get('nama_penanggung', '')
		jk_penanggung		= kw.get('jk_penanggung', '')
		alamat_penanggung	= kw.get('alamat_penanggung', '')		
		pekerjaan3 			= kw.get('pekerjaan3', '')		
		telpon_penanggung	= kw.get('telpon_penanggung', '')
		penghasilan_penanggung = kw.get('penghasilan_penanggung', '')
		keadaan_penanggung		= kw.get('keadaan_penanggung', '')

		#pendidikan
		asal_sma		= kw.get('asal_sma', '')
		asal_alamat_sma	= kw.get('asal_alamat_sma', '')
		asal_website_sma= kw.get('asal_website_sma', '')
		asal_jurusan_sma= kw.get('asal_jurusan_sma', '')

		asal_universitas= kw.get('asal_universitas', '')
		asal_alamat_univ= kw.get('asal_alamat_univ', '')
		asal_website_univ= kw.get('asal_website_univ', '')		
		nim_asal 		= kw.get('nim_asal', '')
		fakultas_asal_id 	= kw.get('fakultas_asal_id', '')
		prodi_asal_id 	= kw.get('prodi_asal_id', '')
		asal_jenjang_id 		= kw.get('jenjangs', '')	

		ref 		= kw.get('rekomendasi', '')	
		telp_ref 		= kw.get('telp_rekomendasi', '')	
		
		#pekerjaan
		nama_instansi 	= kw.get('telp_rekomendasi', '')		
		jabatan 		= kw.get('jabatan', '')		

		photo 			= kw.get('photo', '')	

		# email_template_obj = http.request.env['netpro.email_template']
		# email_template = email_template_obj.search([('name','=','Partner_email')])

		# Partner  = http.request.env['res.partner']
		Partner  = request.registry['res.partner']
		partner_data = {}

		
		jenis_pendaftaran_id 	= http.request.env['akademik.jenis_pendaftaran'].search([('id','=',int(jenis_pendaftaran_id))])
		prodi 					= http.request.env['master.prodi'].browse( int(prodi_id) )

		#jadwal_id 				= http.request.env['jadwal.usm'].search([('name','=','Gelombang 1')])
		today 					= datetime.now()
		print today 
		jadwal_id 				= http.request.env['jadwal.usm'].search([('date_start','<=',today),('date_end','>=',today)])
		print jadwal_id  
		if not jadwal_id:
			return "Tidak ada gelombang pendaftaran tanggal hari ini %s" % (today)


		tahun 					= http.request.env['academic.year'].browse( int(tahun_id) )
		alamat					= http.request.env['master.alamat.kampus'].browse( int(alamat_id) )
		type_mhs				= http.request.env['master.type.mahasiswa'].browse( int(type_mhs_id) )
		konsentrasi				= http.request.env['master.konsentrasi'].browse( int(konsentrasi_id) )
		#tanggal_lhr 		    = self.env["res.lang"].datetime_formatter(tanggal_lahir)
		#import pdb;pdb.set_trace()
		jadwal_id 				= http.request.env['jadwal.usm'].search([('date_start','<=',today),('date_end','>=',today),('tahun_ajaran_id','=',int(tahun_id))])
		print jadwal_id  
		if not jadwal_id:
			return "Tidak ada gelombang pendaftaran tanggal hari ini %s" % (today)

		hubungan_keluargas   	= http.request.env['master.hubungan_keluarga'].search([])
		hub_ayah				= hubungan_keluargas[0].id 
		hub_ibu					= hubungan_keluargas[1].id 
		hub_penganggung			= hubungan_keluargas[2].id 


		ortu_datas = [(0,0,{'nama' 			: nama_ayah,
							'keadaan'		: keadaan_ayah,
							'telepon' 		: telpon_ayah,
							'pekerjaan'		: pekerjaan,
							'alamat'		: alamat_ayah,
							'jenis_kelamin'	: 'L',
							'hubungan_keluarga_id' : hub_ayah,
							'penghasilan' 	: penghasilan_ayah}),
					(0,0,{'nama' 		: nama_ibu,
						'keadaan'		: keadaan_ibu,
						'telepon' 		: telpon_ibu,
						'pekerjaan'		: pekerjaan2,
						'alamat'		: alamat_ibu,
						'jenis_kelamin'	: 'P',
						'hubungan_keluarga_id' : hub_ibu,
						'penghasilan' 	: penghasilan_ibu}),
					(0,0,{'nama' 		: nama_penanggung,
						'keadaan'		: 'ada',
						'telepon' 		: telpon_penanggung,
						'pekerjaan'		: pekerjaan3,
						'alamat'		: alamat_penanggung,
						'jenis_kelamin'	: jk_penanggung,
						'hubungan_keluarga_id' : hub_penganggung,
						'penghasilan' 	: penghasilan_penanggung
						})]

		pend_datas = [(0,0,{'nama_sekolah'	: asal_sma,
							'tingkat'		: 'SMA',
							'jurusan'		: asal_jurusan_sma,
							'alamat' 		: asal_alamat_sma,
							'website'		: asal_website_sma})]				

		
		if partner.reg == "/" or partner.reg == False:
			reg = request.registry['ir.sequence'].get(cr, SUPERUSER_ID, 'res.partner') 
		else:
			reg = partner.reg 



		if kw.get('confirm') == '':
			##############################################################################
			# insert into calon mhs
			##############################################################################
			
			data = {
				'image'			: base64.encodestring(photo.read()),
				'reg'			: reg,
				'name'			: name,
				'id_card' 		: id_card,
				'jenis_pendaftaran_id' : jenis_pendaftaran_id.id,
				'alamat_id'		: alamat.id,
				'street'		: street,
				'type_pendaftaran': jadwal_id.type_pendaftaran,
				'type_mhs_id'	: type_mhs.id,
				'street'		: street,
				'street2'		: street2,
				'city'			: city,
				'zip'			: zip_code,
				'phone'			: phone,
				'mobile'		: mobile,
				'fakultas_id'	: prodi.fakultas_id.id,
				'prodi_id'		: prodi.id,
				'konsentrasi_id': konsentrasi.id,
				'tahun_ajaran_id'	: tahun.id,
				'jadwal_usm_id'	: jadwal_id.id,
				'jenis_kelamin' : jenis_kelamin,
				'agama'			: agama,
				'tempat_lahir'	: tempat_lahir,
				'tanggal_lahir'	: tanggal_lahir,
				'tgl_daftar'	: today,
				'is_company'	: False,
				'is_mahasiswa'	: True,
				'customer'		: True,
				'status_mahasiswa': 'calon',
				'no_ijazah_sma'	: '/',
				'biodata_keluarga_ids': ortu_datas,
				'riwayat_pendidikan_ids' : pend_datas,
				'rekomendasi'	: ref,
				'telp_rekomendasi'		: telp_ref,
				'jadwal_pagi'	: jadwal_pagi,
				'jadwal_siang'	: jadwal_siang,
				'jadwal_malam'	: jadwal_malam,

			}
			# jika coa ada di master prodi
			if prodi.coa_hutang_id:
				data.update({'property_account_payable': prodi.coa_hutang_id.id})
			if prodi.coa_piutang_id:
				data.update({'property_account_receivable': prodi.coa_piutang_id.id})

			
			# jika pindahan
			if jenis_pendaftaran_id.name != 'Baru':
				data.update({'asal_univ'			: asal_universitas,
							'asal_alamat_univ' 		: asal_alamat_univ,
							'asal_website_univ' 	: asal_website_univ,
							'asal_fakultas'			: fakultas_asal_id,
							'asal_prodi'			: prodi_asal_id,
							'asal_npm'				: nim_asal,
							'asal_jenjang_id'		: asal_jenjang_id,
							'semester_id'			: semester_id})

			# partner_data = Partner.create( data )
			partner_data = Partner.write ( cr, SUPERUSER_ID, [partner.id],  data )
			message = "Registration Success!"

		return http.request.render('vit_universities_web.registration_process', {
			'partner'		: partner_data,
			'message'		: message,
			'reg'			: reg
		})


	######################################################################################
	# proses update sebagian data mahasiswa 
	# registrasi ulang
	######################################################################################
	@http.route('/second_registration_process/<model("res.partner"):partner>', auth='user', website=True)
	def second_registration_process(self, partner, **kw):
		cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
		
		message 		= kw.get('message','')
		
		#jalur masuk
		jalur_masuk 	= kw.get('jalur_masuks', '')
		prestasi = False
		if jalur_masuk == 'prestasi' :
			prestasi = True
			prestasi_file 	= kw.get('prestasi_file', '')	
			smt1 			= kw.get('smt1', '')
			smt2 			= kw.get('smt2', '')
			smt3 			= kw.get('smt3', '')
			smt4 			= kw.get('smt4', '')
			smt5 			= kw.get('smt5', '')
			un 	 			= kw.get('un', '')

		#hubungan dengan istn
		hubungan 		= kw.get('hubungans', '')
		hub_istn_file 	= kw.get('hub_istn_file', '')		

		# transkrip
		transkrip_file 	= kw.get('transkrip_file', '')

		# pembayaran
		type_pembayaran = kw.get('type_pembayarans', '')	

		Partner  = request.registry['res.partner']
		partner_data = {}

		if kw.get('confirm_second_registration') == '':
			Attachments = request.registry['ir.attachment']
			##############################################################################
			# insert into calon mhs
			##############################################################################
			if prestasi :
				data = {
					'jalur_masuk'		: jalur_masuk,
					'semester1'			: float(smt1),
					'semester2'			: float(smt2),
					'semester3'			: float(smt3),
					'semester4'			: float(smt4),
					'semester5'			: float(smt5),
					'un'				: float(un),
					'split_invoice'		: int(type_pembayaran),
					'reg_online'		: True,
					'hubungan'			: hubungan,
				}
				###############################################################################
				# Create Attachment
				###############################################################################
				attachment_value1 = {
					'name'		: 'Jalur Prestasi',
					'type'		: 'binary',
					'datas'		: base64.encodestring(prestasi_file.read()),
					'res_model'	: 'res.partner',
					'res_name'	: partner.name,
					'res_id'	: int(partner.id),
					'partner_id': partner.id,
					'datas_fname': 'Jalur Prestasi',
				}	
				Attachments.create(request.cr, SUPERUSER_ID, attachment_value1, context=request.context)		
			else:
				data = {
					'jalur_masuk'		: jalur_masuk,
					'split_invoice'		: int(type_pembayaran),
					'reg_online'		: True,
					'hubungan'			: hubungan,
				}				

			partner_data = Partner.write ( cr, SUPERUSER_ID, [partner.id],  data )
			message = "Registrasi Ulang Sukses!"

			###############################################################################
			# Create Attachment
			###############################################################################
			attachment_value2 = {
				'name'		: str(hubungan),
				'type'		: 'binary',
				'datas'		: base64.encodestring(hub_istn_file.read()),
				'res_model'	: 'res.partner',
				'res_name'	: partner.name,
				'res_id'	: int(partner.id),
				'partner_id': partner.id,
				'datas_fname': str(hubungan),
				}
			Attachments.create(request.cr, SUPERUSER_ID, attachment_value2, context=request.context)

			if transkrip_file != '' :
				###############################################################################
				# Create Attachment jika transkrip, jika pindahan
				###############################################################################
				attachment_value3 = {
					'name'		: 'Transkrip Nilai',
					'type'		: 'binary',
					'datas'		: base64.encodestring(transkrip_file.read()),
					'res_model'	: 'res.partner',
					'res_name'	: partner.name,
					'res_id'	: int(partner.id),
					'partner_id': partner.id,
					'datas_fname': 'Transkrip Nilai',
					}
				Attachments.create(request.cr, SUPERUSER_ID, attachment_value3, context=request.context)

			#import pdb;pdb.set_trace()
			###############################################################################
			# create email notif ke user PMB
			groups = request.registry['res.groups']
			users  = groups.search(request.cr,SUPERUSER_ID,[('name','ilike','PMB')], context=request.context)
			if users :
				users_ids = groups.browse(request.cr,SUPERUSER_ID,users[0], context=request.context)
				if users_ids.users :
					mail = request.registry['mail.mail']
					for notif in users_ids.users :
						body = 'Hallo '+str(notif.partner_id.name)+', Calon Mahasiswa '+str(partner.name)+' dengan nomor pendaftaran '+str(partner.reg)+' butuh verifikasi anda silahkan cek di sistem !'
						mail_data = {'subject' 		: 'Verifikasi Registrasi Ulang Calon Mahasiswa ISTN '+str(partner.reg),
									'email_to' 		: notif.partner_id.email,
									'recipient_ids' : [(6, 0, [notif.partner_id.id])],
									'notification' 	: True,
									'auto_delete'	: False,
									'body_html'		: body}
						mail.create(request.cr, SUPERUSER_ID,mail_data,context=request.context)	
		return http.request.render('vit_universities_web.second_registration_process', {
			'partner'		: partner_data,
			'message'		: message,
			'reg'			: partner.reg
		})


	######################################################################################
	# halaman portal mahasiswa
	# muncul form portal mahasiswa
	######################################################################################
	@http.route('/mahasiswa', auth='user', website=True)
	def mahasiswa(self, **kw):
		cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

		message_error = kw.get('message_error','')
		message_success = kw.get('message_success','')

		User = http.request.env['res.users']
		user = User.browse( uid )
		partner = user.partner_id

		Prodi  = http.request.env['master.prodi']
		prodi_ids = Prodi.search([])

		Tahun  = http.request.env['academic.year']
		tahun_ids = Tahun.search([('is_active','=',True)])

		Semester  = http.request.env['master.semester']
		semester_ids = Semester.search([])

		Lokasi  = http.request.env['master.alamat.kampus']
		alamat_ids = Lokasi.search([])

		Type  = http.request.env['master.type.mahasiswa']
		type_mhs_ids = Type.search([])		
		
		Konsentrasi  = http.request.env['master.konsentrasi']
		konsentrasi_ids = Konsentrasi.search([])

		Jenis_pendaftaran  = http.request.env['akademik.jenis_pendaftaran']
		jenis_pendaftaran_ids = Jenis_pendaftaran.search([])

		penghasilans = [('1','Dibawah Rp.1.000.000'),('2','Rp.1.000.000 - Rp.3.000.000'),('3','Rp.3.000.001 - Rp.6.000.000'),('4','Rp.6.000.001 - Rp.10.000.000'),('5','Diatas Rp.10.000.001')]

		jadwal_ids = [('pagi','Pagi'),('siang','Siang'),('malam','Malam')]
		penghasilan_ayah = [('1','Dibawah Rp.1.000.000'),('2','Rp.1.000.000 - Rp.3.000.000'),('3','Rp.3.000.001 - Rp.6.000.000'),('4','Rp.6.000.001 - Rp.10.000.000'),('5','Diatas Rp.10.000.001')]
		pekerjaans = [('pns','Pengawai Negeri Sipil'),('tni/polri','TNI/Polri'),('petani','Petani'),('peg_swasta', 'Pegawai Swasta'),('wiraswasta','Wiraswasta'),('none','Tidak Bekerja'),('lain','Lain-lain')]
		jenis_kelamins = [('L','Laki-Laki'),('P','Perempuan')]
		keadaans = [('ada','Masih Ada'),('alm','Alm')]
		agamas = [('islam','Islam'),('kristen','Kristen'),('hindu','Hindu'),('budha','Budha'),('kepercayaan','Kepercayaan')]
		type_pendaftarans = [('ganjil','Ganjil'),('genap','Genap'),('pendek','Pendek')]
		jalur_masuks = [('perorangan','Perorangan'),('group','Group'),('prestasi','Jalur Prestasi')]
		hubungans = [('umum','Umum'),('ortu','Orang Tua Alumni ISTN'),('cikini','Lulusan SLTA Perguruan Cikini'),('karyawan','Karyawan Tetap (Masih Aktif) ISTN')]
		type_pembayarans = [('1','Tunai'),('6','6 x Angsuran')]
		
		page = ''
		if partner.status_mahasiswa == 'Mahasiswa':
			page = 'vit_universities_web.mahasiswa_view'
		else :
			page = 'vit_universities_web.mahasiswa_view_hidden'

		return http.request.render(page,
		{
			'partner'		: partner,
			'target_title'	: 'Mahasiswa', 
			'prodi_ids'		: prodi_ids,
			'konsentrasi_ids': konsentrasi_ids,
			'tahun_ids'		: tahun_ids,
			'alamat_ids'    : alamat_ids,
			'jenis_pendaftaran_ids' : jenis_pendaftaran_ids,
			'type_mhs_ids'	: type_mhs_ids,
			'type_mhs_ids'	: type_mhs_ids,
			'semester_ids'	: semester_ids,
			'pekerjaans'	: pekerjaans,
			'pekerjaans2'	: pekerjaans,
			'pekerjaans3'	: pekerjaans,
			'penghasilan_ayah' : penghasilan_ayah,
			'penghasilan_ibu'  : penghasilan_ayah,
			'penghasilan_penanggung' : penghasilan_ayah,
			'keadaans'		: keadaans,
			'jenis_kelamins': jenis_kelamins,
			'agamas'		: agamas,
			'type_pendaftarans': type_pendaftarans,
			'jalur_masuks'	: jalur_masuks,
			'hubungans'		: hubungans,
			'type_pembayarans': type_pembayarans,
			'jadwal_ids'		: jadwal_ids,
			'partner'		: partner,
			'message_error'	: message_error,
			'message_success': message_success
		} )	



	# # # # # # # # # # # # # # # # # # # # # 
	# 		REPLACE EMAIL GLOSSARY 			#
	# # # # # # # # # # # # # # # # # # # # # 
	def replaceString(self,content,Partner,plan):
		ret = ''
		benefits = ''
		for pl in plan.member_plan_detail_ids:
			benefits += pl.benefit_id.name + '			: '+ '{0:,.2f}'.format(int(pl.remaining)) + '\n'

		if content.find('[Partner_no]'):
			ret += content.replace('[Partner_no]', Partner.Partner_no)
		if content.find('[benefit]'):
			ret += content.replace('[benefit]', str(benefits))
		if content.find('[member_name]'):
			ret += content.replace('[member_name]', Partner.member_id.name)
		return content


	######################################################################################
	# convert kw string to array
	######################################################################################
	def string2array(self, name, kw):
		res = {}
		for k in kw.keys():
			if k.find('.') != -1:
				x = k.split('.')
				if x[0] == name:
					res[ int(x[1]) ] = kw.get(k)

		return res

	def collectDiagnosis(self, name, kw):
		res = {}

		for k in kw.keys():
			if k.startswith(name):
				data = http.request.env['netpro.diagnosis'].browse(int(kw.get(k)))
				res[int(kw.get(k))] = float(data.standard_fee)

		return res


	######################################################################################
	# action ke Partner list
	######################################################################################
	@http.route('/partner/partner_list', auth='user', website=True)
	def partner_list(self, **kw):
		message_error = kw.get('message_error','')
		message_success = kw.get('message_success','')

		if request.httprequest.method == 'POST':
			##############################################################################
			# cari dulu data member
			##############################################################################
			Member = http.request.env['netpro.member']
			member = Member.search([('card_no','=',kw.get('card_no','') )])
			if not member:
				message = "Member not found! Please try again."
				return request.redirect('/Partner/search?message_error=%s'% (message), code=301)

			##############################################################################
			# cari data Partner member tsb yang masih open
			##############################################################################
			Partner  = http.request.env['netpro.Partner']
			Partner_ids = Partner.search([('member_id','=',member.id) ])
			if not Partner_ids:
				message = "Partner Registration not found!"
				return request.redirect('/Partner/search?message_error=%s'% (message), code=301)

			# import pdb; pdb.set_trace()
			# Partners = Partner.browse(Partner_ids)

			return http.request.render('vit_universities_web.Partner_list',
				{'message_error'	: message_error,
				'message_success'	: message_success,
				'Partners' 			: Partner_ids,
				'member'			: member 
			} )	

