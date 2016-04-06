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
		type_pendaftarans = [('ganjil','Ganjil'),('Genap','Genap'),('pendek','Pendek')]
		

		page = ''
		if partner.reg != '/':
			page = 'vit_universities_web.registration_view'
		else:
			page = 'vit_universities_web.registration'
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
			'jadwal_ids'		: jadwal_ids,
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
		prodi_asal_id 	= kw.get('prodi_asal_id', '')	

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

		
		jenis_pendaftaran_id 	= http.request.env['akademik.jenis_pendaftaran'].search([('name','=','Baru')])
		prodi 					= http.request.env['master.prodi'].browse( int(prodi_id) )

		#jadwal_id 				= http.request.env['jadwal.usm'].search([('name','=','Gelombang 1')])
		today 					= datetime.now()
		print today 
		jadwal_id 				= http.request.env['jadwal.usm'].search([('date_start','<=',today),('date_end','>=',today)])
		print jadwal_id  
		if not jadwal_id:
			return "tidak ada gelombang pendaftaran tanggal hari ini %s" % (today)


		tahun 					= http.request.env['academic.year'].browse( int(tahun_id) )
		alamat					= http.request.env['master.alamat.kampus'].browse( int(alamat_id) )
		type_mhs				= http.request.env['master.type.mahasiswa'].browse( int(type_mhs_id) )
		konsentrasi				= http.request.env['master.konsentrasi'].browse( int(konsentrasi_id) )
		#tanggal_lhr 		    = self.env["res.lang"].datetime_formatter(tanggal_lahir)

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
						'keadaan'		: keadaan_penanggung,
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
				'type_pendaftaran': type_pendaftaran,
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
			if prodi.coa_hutang_id:
				data.update({'property_account_payable': prodi.coa_hutang_id.id})
			if prodi.coa_piutang_id:
				data.update({'property_account_receivable': prodi.coa_piutang_id.id})
			# partner_data = Partner.create( data )
			partner_data = Partner.write ( cr, SUPERUSER_ID, [partner.id],  data )
			message = "Registration Success!"

		return http.request.render('vit_universities_web.registration_process', {
			'partner'		: partner_data,
			'message'		: message,
			'reg'			: reg
		})


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

