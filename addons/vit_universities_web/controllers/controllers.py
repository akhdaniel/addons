# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
import base64
import simplejson
import logging
_logger = logging.getLogger(__name__)
import time
from datetime import datetime

class Partner(http.Controller):

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
		tahun_ids = Tahun.search([])

		Semester  = http.request.env['master.semester']
		semester_ids = Semester.search([])

		Lokasi  = http.request.env['master.alamat.kampus']
		alamat_ids = Lokasi.search([])

		Type  = http.request.env['master.type.mahasiswa']
		type_mhs_ids = Type.search([])		
		
		Konsentrasi  = http.request.env['master.konsentrasi']
		konsentrasi_ids = Konsentrasi.search([])

		pekerjaans = [('psn','Pengawai Negeri Sipil'),('tni','TNI'),('petani','Petani'),('peg_swasta', 'Pegawai Swasta'),('wiraswasta','Wiraswasta'),('none','Tidak Bekerja'),('lain','Lain-lain')]
		jenis_kelamins = [('L','Laki-Laki'),('P','Perempuan')]
		agamas = [('islam','Islam'),('kristen','Kristen'),('hindu','Hindu'),('budha','Budha'),('kepercayaan','Kepercayaan')]
		type_pendaftarans = [('ganjil','Ganjil'),('Genap','Genap')]

		return http.request.render('vit_universities_web.registration',
		{
			'partner'		: partner,
			'target_title'	: 'Registration', 
			'prodi_ids'		: prodi_ids,
			'konsentrasi_ids': konsentrasi_ids,
			'tahun_ids'		: tahun_ids,
			'alamat_ids'    : alamat_ids,
			'type_mhs_ids'	: type_mhs_ids,
			'semester_ids'	: semester_ids,
			'pekerjaans'	: pekerjaans,
			'jenis_kelamins': jenis_kelamins,
			'agamas'		: agamas,
			'type_pendaftarans': type_pendaftarans,
			'partner'		: partner,
			'message_error'	: message_error,
			'message_success': message_success
		} )	


	######################################################################################
	# proses registration patient: 
	# print, email, save: insert transaksi Partner
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
		pekerjaan 		= kw.get('pekerjaan', '')	
		alamat_id 		= kw.get('alamat_id', '')
		type_mhs_id 	= kw.get('type_mhs_id', '')
		type_pendaftaran= kw.get('type_pendaftaran', '')

		#pribadi
		jenis_kelamin 	= kw.get('jenis_kelamin', '')
		tempat_lahir	= kw.get('tempat_lahir', '')		
		tanggal_lahir	= kw.get('tanggal_lahir', '')		
		jenis_kelamin	= kw.get('jenis_kelamin', '')		
		agama 			= kw.get('agama', '')		
		street 			= kw.get('street', '')		
		street2			= kw.get('street2', '')		
		city			= kw.get('city', '')		

		#orang tua
		nama_ayah		= kw.get('nama_ayah', '')		
		nama_ibu		= kw.get('nama_ibu', '')		
		telpon_ayah		= kw.get('telpon_ayah', '')		
		telpon_ibu		= kw.get('telpon_ibu', '')		

		#pendidiksn
		asal_sma		= kw.get('asal_sma', '')		
		asal_universitas= kw.get('asal_universitas', '')		
		nim_asal 		= kw.get('nim_asal', '')		
		
		#pekerjaan
		nama_instansi 	= kw.get('nama_instansi', '')		
		jabatan 		= kw.get('jabatan', '')		

		# email_template_obj = http.request.env['netpro.email_template']
		# email_template = email_template_obj.search([('name','=','Partner_email')])

		# Partner  = http.request.env['res.partner']
		Partner  = request.registry['res.partner']
		partner_data = {}

		jenis_pendaftaran_id 	= http.request.env['akademik.jenis_pendaftaran'].search([('name','=','Baru')])
		prodi 					= http.request.env['master.prodi'].browse( int(prodi_id) )
		jadwal_id 				= http.request.env['jadwal.usm'].search([('name','=','Gelombang 1')])
		tahun 					= http.request.env['academic.year'].browse( int(tahun_id) )
		alamat					= http.request.env['master.alamat.kampus'].browse( int(alamat_id) )
		type_mhs				= http.request.env['master.type.mahasiswa'].browse( int(type_mhs_id) )
		konsentrasi				= http.request.env['master.konsentrasi'].browse( int(konsentrasi_id) )

		# import pdb; pdb.set_trace()
		if partner.reg == "/" or partner.reg == False:
			reg = request.registry['ir.sequence'].get(cr, SUPERUSER_ID, 'res.partner') 
		else:
			reg = partner.reg 



		if kw.get('confirm') == '':
			##############################################################################
			# insert into netpro_Partner
			##############################################################################

			data = {
				'reg'			: reg,
				'name'			: name,
				'jenis_pendaftaran_id' : jenis_pendaftaran_id.id,
				'alamat_id'		: alamat.id,
				'type_pendaftaran': type_pendaftaran,
				'type_mhs_id'	: type_mhs.id,
				'street'		: street,
				'street2'		: street2,
				'city'			: city,
				'fakultas_id'	: prodi.fakultas_id.id,
				'prodi_id'		: prodi.id,
				'konsentrasi_id': konsentrasi.id,
				'tahun_ajaran_id': tahun.id,
				'jadwal_usm_id'	: jadwal_id.id,
				'jenis_kelamin' : jenis_kelamin,
				'agama'			: agama,
				'tempat_lahir'	: tempat_lahir,
				'tanggal_lahir'	: tanggal_lahir,
				'is_company'	: False,
				'is_mahasiswa'	: True,
				'status_mahasiswa': 'calon',

			}
			# partner_data = Partner.create( data )
			partner_data = Partner.write ( cr, SUPERUSER_ID, [partner.id],  data )
			message = "Registration Success!"

		return http.request.render('vit_universities_web.registration_process', {
			'partner'		: partner_data,
			'message'		: message
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

