# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class res_partner_registration_wizard(models.TransientModel):
	_name = "res.partner.registration.wizard"

	def _get_tahun_akademik(self):
		year_obj          = self.env['academic.year']
		active_year       = year_obj.search([('is_active','=',True)])
		year = False
		if active_year:
			return active_year.id
		return year

	def _get_semester(self):
		smt_obj         = self.env['master.semester']
		smt     		= smt_obj.search([('name','=','1')])
		semester = False
		if smt:
			return smt.id
		return semester

	pas_foto			= fields.Binary('Pas Foto',required=True)
	partner_id 			= fields.Many2one('res.partner','Nama',readonly=True,)
	name 				= fields.Char('Nama Lengkap',required=True,size=128)
	no_reg				= fields.Char('No Pendaftaran',readonly=True)
	id_card 			= fields.Char('No. KTP/SIM',required=True)
	alamat_pendaftar	= fields.Text('Alamat Rumah',required=True)
	kota_pendaftar	  	= fields.Char('Kota',required=True)
	zip_pendaftar		= fields.Char('Kode Pos',required=True, size=8)
	telp_pendaftar		= fields.Char('Telepon',required=True, size=30)
	jenis_kelamin		= fields.Selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin',required=True)
	tempat_lahir		= fields.Char('Tempat Lahir',required=True, size=50)
	tanggal_lahir		= fields.Date('Tanggal Lahir',required=True)	
	jadwal_pagi			= fields.Boolean('Pagi')
	jadwal_siang		= fields.Boolean('Siang')
	jadwal_malam		= fields.Boolean('Malam')		
	agama				= fields.Selection([('islam','Islam'),('kristen','Kristen'),('hindu','Hindu'),('budha','Budha'),('kepercayaan','Kepercayaan')],'Agama',required=True)

	nama_ayah			= fields.Char('Nama Ayah',required=True, size=128)
	keadaan_ayah		= fields.Selection([('alm','Almarhum'),('ada','Masih Ada')],'Keadaan Ayah',required=True)
	alamat_ayah			= fields.Text('Alamat Rumah Ayah',required=True)
	telp_ayah			= fields.Char('Telepon Ayah',required=True, size=30)
	penghasilan_ayah 	= fields.Selection([('1','Dibawah Rp.1.000.000'),
												('2','Rp.1.000.000 - Rp.3.000.000'),
												('3','Rp.3.000.001 - Rp.6.000.000'),
												('4','Rp.6.000.001 - Rp.10.000.000'),
												('5','Diatas Rp.10.000.001')],
												'Penghasilan Ayah',required=True)
	pekerjaan_ayah		= fields.Selection([('pns','Pengawai Negeri Sipil'),
												('tni/polri','TNI/Polri'),
												('petani','Petani'),
												('peg_swasta', 'Pegawai Swasta'),
												('wiraswasta','Wiraswasta'),
												('none','Tidak Bekerja'),
												('lain','Lain-lain')],
												'Pekerjaan Ayah',required=True)

	nama_ibu			= fields.Char('Nama Ibu',required=True, size=128)
	keadaan_ibu			= fields.Selection([('alm','Almarhumah'),('ada','Masih Ada')],'Keadaan Ibu',required=True)
	alamat_ibu			= fields.Text('Alamat Rumah Ibu',required=True)
	telp_ibu			= fields.Char('Telepon Ibu',required=True, size=30)
	penghasilan_ibu 	= fields.Selection([('1','Dibawah Rp.1.000.000'),
												('2','Rp.1.000.000 - Rp.3.000.000'),
												('3','Rp.3.000.001 - Rp.6.000.000'),
												('4','Rp.6.000.001 - Rp.10.000.000'),
												('5','Diatas Rp.10.000.001')],
												'Penghasilan Ibu',required=True)
	pekerjaan_ibu		= fields.Selection([('pns','Pengawai Negeri Sipil'),
												('tni/polri','TNI/Polri'),
												('petani','Petani'),
												('peg_swasta', 'Pegawai Swasta'),
												('wiraswasta','Wiraswasta'),
												('none','Tidak Bekerja'),
												('lain','Lain-lain')],
												'Pekerjaan Ibu',required=True)


	nama_penanggung				= fields.Char('Nama',required=True, size=128)
	jenis_kelamin_penanggung	= fields.Selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin',required=True)
	alamat_penanggung			= fields.Text('Alamat Rumah',required=True)
	telp_penanggung				= fields.Char('Telepon ',required=True, size=30)
	penghasilan_penanggung 		= fields.Selection([('1','Dibawah Rp.1.000.000'),
												('2','Rp.1.000.000 - Rp.3.000.000'),
												('3','Rp.3.000.001 - Rp.6.000.000'),
												('4','Rp.6.000.001 - Rp.10.000.000'),
												('5','Diatas Rp.10.000.001')],
												'Penghasilan',required=True)
	pekerjaan_penanggung		= fields.Selection([('pns','Pengawai Negeri Sipil'),
												('tni/polri','TNI/Polri'),
												('petani','Petani'),
												('peg_swasta', 'Pegawai Swasta'),
												('wiraswasta','Wiraswasta'),
												('none','Tidak Bekerja'),
												('lain','Lain-lain')],
												'Pekerjaan',required=True)

	alamat_id					= fields.Many2one('master.alamat.kampus','Lokasi Kampus',required=True)
	tahun_ajaran_id				= fields.Many2one('academic.year',default=_get_tahun_akademik,string='Tahun Akademik',required=True)
	prodi_id					= fields.Many2one('master.prodi',string='Program Studi',domain="[('is_internal','=',True)]",required=True)
	type_pendaftaran			= fields.Selection([('ganjil','Ganjil'),('genap','Genap'),('pendek','Pendek')],'Type Pendaftaran',required=True)
	type_mhs_id					= fields.Many2one('master.type.mahasiswa','Type Mahasiswa',required=True)
	jenis_pendaftaran_id		= fields.Many2one('akademik.jenis_pendaftaran', 'Jenis Pendaftaran',required=True)

		#asal sekolah (SMA)
	nama_sekolah				= fields.Char('Nama Sekolah',required=True, size=128)
	alamat_sekolah				= fields.Text('Alamat Sekolah',required=True)
	website_sekolah				= fields.Char('website', size=30)
	jurusan_sekolah 			= fields.Char('Jurusan',required=True, size=30)

		#untuk mhs pindahan
	asal_univ_id 				= fields.Many2one('res.partner', 'Asal PT', domain=[('category_id','ilike','external')])
	asal_fakultas_id 			= fields.Many2one('master.fakultas', 'Asal Fakultas', domain="[('pt_id','=',asal_univ_id),('is_internal','=',False)]")
	asal_prodi_id 				= fields.Many2one('master.prodi', 'Asal Prodi', domain="[('fakultas_id','=',asal_fakultas_id),('is_internal','=',False)]")
	asal_npm					= fields.Char('NIM Asal')
	asal_sks_diakui		 		= fields.Integer('SKS Diakui')
	asal_jenjang_id 			= fields.Many2one('master.jenjang', 'Asal Jenjang')
	semester_id					= fields.Many2one('master.semester',default=_get_semester,string='Semester Awal Masuk',required=True)

	split_invoice 				= fields.Integer('Angsuran',help="jika di isi angka positif maka invoice yg digenerate dari KRS atas mahasiswa ini akan tersplit sesuai angka yang diisi")
		
	konsentrasi_id				= fields.Many2one('master.konsentrasi','Konsentrasi',default=1)
		
		#pemberi rekomendasi
	rekomendasi					= fields.Char('Perekomendasi',required=True)
	telp_rekomendasi 			= fields.Char('Telp. Perekomendasi',required=True)



	def confirm_registration(self, cr, uid, ids, context=None):
		partner_obj       = self.pool.get('res.partner')
		user_obj          = self.pool.get('res.users')
		reg_obj           = self.pool.get('partner.registration')

		usr 			= user_obj.search(cr, 1, [('id','=',uid)])
		exist_partner 	= user_obj.browse(cr, 1, usr[0]).partner_id

		for calon in self.browse(cr, uid, ids, context=context):
			
			if not calon.jadwal_pagi and not calon.jadwal_siang and not calon.jadwal_malam :
				raise except_orm(_('Data Tidak Lengkap !'), _("Waktu kuliah minimal dipilih satu pilihan ( Pagi / Siang / Malam )"))	

			if exist_partner.reg == "/" or exist_partner.reg == False:
				reg = self.pool.get('ir.sequence').get(cr, uid, 'res.partner') or '/'
			else:
				reg = exist_partner.reg 			

			kel_ayah = (0, 0, {'nama'					: calon.nama_ayah,
								'keadaan'				: calon.keadaan_ayah,
								'pekerjaan'				: calon.pekerjaan_ayah,
								'penghasilan'			: calon.penghasilan_ayah,
								'alamat'				: calon.alamat_ayah,
								'telepon'				: calon.telp_ayah,
								'jenis_kelamin'			: 'L',
								'hubungan_keluarga_id'	: 1,})

			kel_ibu = (0, 0, {'nama'					: calon.nama_ibu,
								'keadaan'				: calon.keadaan_ibu,
								'pekerjaan'				: calon.pekerjaan_ibu,
								'penghasilan'			: calon.penghasilan_ibu,
								'alamat'				: calon.alamat_ibu,
								'telepon'				: calon.telp_ibu,
								'jenis_kelamin'			: 'P',
								'hubungan_keluarga_id'	: 1,})

			kel_penanggung = (0, 0, {'nama'				: calon.nama_penanggung,
									'keadaan'			: 'ada',
									'pekerjaan'			: calon.pekerjaan_penanggung,
									'penghasilan'		: calon.penghasilan_penanggung,
									'alamat'			: calon.alamat_penanggung,
									'telepon'			: calon.telp_penanggung,
									'jenis_kelamin'		: calon.jenis_kelamin_penanggung,
									})

			keluarga_ids = [kel_ayah,kel_ibu,kel_penanggung]

			pendidikan_ids = [(0, 0, {'nama_sekolah'	: calon.nama_sekolah,
										'tingkat'		: 'SMA',
										'alamat'		: calon.alamat_sekolah,
										'website'		: calon.website_sekolah,
										'jurusan'		: calon.jurusan_sekolah})] 

			data = {
				'image'					: calon.pas_foto,
				'reg'					: reg,
				'name'					: calon.name,
				'id_card' 				: calon.id_card,
				'jenis_pendaftaran_id' 	: calon.jenis_pendaftaran_id.id,
				'alamat_id'				: calon.alamat_id.id,
				'type_pendaftaran'		: calon.type_pendaftaran,
				'type_mhs_id'			: calon.type_mhs_id.id,
				'street'		 		: calon.alamat_pendaftar,
				'city'					: calon.kota_pendaftar,
				'zip'					: calon.zip_pendaftar,
				'phone'					: calon.telp_pendaftar,
				'fakultas_id'			: calon.prodi_id.fakultas_id.id,
				'prodi_id'				: calon.prodi_id.id,
				'konsentrasi_id'		: calon.konsentrasi_id.id,
				'tahun_ajaran_id'		: calon.tahun_ajaran_id.id,
				'jenis_kelamin' 		: calon.jenis_kelamin,
				'agama'					: calon.agama,
				'tempat_lahir'			: calon.tempat_lahir,
				'tanggal_lahir'			: calon.tanggal_lahir,
				'is_company'			: False,
				'is_mahasiswa'			: True,
				'customer'				: True,
				'status_mahasiswa'		: 'calon',
				'no_ijazah_sma'			: '/',
				'biodata_keluarga_ids'	: keluarga_ids,
				'riwayat_pendidikan_ids': pendidikan_ids,
				'rekomendasi'			: calon.rekomendasi,
				'telp_rekomendasi'		: calon.telp_rekomendasi,
				'jadwal_pagi'			: calon.jadwal_pagi,
				'jadwal_siang'			: calon.jadwal_siang,
				'jadwal_malam'			: calon.jadwal_malam,
				'reg_online'			: True,
			}


			if calon.prodi_id.coa_hutang_id:
				data.update({'property_account_payable': calon.prodi_id.coa_hutang_id})
			if calon.prodi_id.coa_piutang_id:
				data.update({'property_account_receivable': calon.prodi_id.coa_piutang_id})
			#import pdb;pdb.set_trace()
			partner_obj.write(cr,1,exist_partner.id,data)

			reg_obj.write(cr,uid,context['active_id'],{'confirm':True,'no_reg':reg})
		return {'type': 'ir.actions.act_window_close'}