from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class res_partner(osv.osv):
	_inherit 	= "res.partner"
	_name 		= "res.partner"
	_columns 	= {
		'reliance_id' 							: fields.char('Reliance ID', select=1),
        'city'									: fields.char('City', select=1),
        'initial_bu'							: fields.char('Initial BU', length=4, select=1),

        # related partners
        'related_partner_id'					: fields.many2one('res.partner', 'Related Partner Parent'),
        'related_partner_ids'					: fields.one2many('res.partner', 'related_partner_id','Related Partners', ondelete="cascade"),

		'nomor_nasabah' 						: fields.char('Nomor Nasabah', select=1),
		'agent_id' 								: fields.char('Agent', select=1),

		'perusahaan_npwp' 						: fields.char('NPWP'),
		'perusahaan_bidang_usaha' 				: fields.char('Bidang Usaha'),
		'perusahaan_siup' 						: fields.char('SIUP'),
		'perusahaan_tdp' 						: fields.char('TDP'),
		'perusahaan_akte_pendirian' 			: fields.char('Akte Pendirian'),
		'perusahaan_nomor_ijin_usaha' 			: fields.char('Nomor Ijin Usaha'),
		'perusahaan_nama_direktur' 				: fields.char('Nama Direktur'),
		'perusahaan_sumber_dana' 				: fields.char('Sumber dana'),
		'perusahaan_tujuan_asuransi_investasi' 	: fields.char('Tujuan Asuransi/Investasi'),
		'perusahaan_bentuk_badan_usaha' 		: fields.char('Bentuk Badan Usaha'),
		'perusahaan_nama_direksi' 				: fields.char('Nama Direksi'),
		'perusahaan_domisili_perusahaan' 		: fields.char('Domisili Perusahaan'),
		'perusahaan_kecamatan' 					: fields.char('Kecamatan Perusahaan'),
		'perusahaan_tanggal_kedaluarsa_siup' 	: fields.date('Tanggal Kedaluarsa SIUP'),
		'perusahaan_kode_nasabah' 				: fields.char('Kode Nasabah'),
		'perusahaan_karakteristik_perusahaan' 	: fields.char('Karakteristik Perusahaan'),
		'perusahaan_status_domisili_kantor' 	: fields.char('Status Domisili Kantor'),
		'perusahaan_persentase_kepemilikan_saham' 	: fields.char('Persentase Kepemilikan saham'),
		'perusahaan_tanggal_kedaluarsa_tdp' 	: fields.date('Tanggal Kedaluarsa TDP'),
		'perusahaan_nomor_single_investor_id' 	: fields.char('Nomor Single Investor ID'),
		'perusahaan_nama_bank_nomor_rekening' 	: fields.char('Nama bank & nomor rekening'),
		'perusahaan_nomor_formulir' 			: fields.char('Nomor Formulir'),
		'perusahaan_nama_equity_sales' 			: fields.char('Nama Equity Sales'),
		'perusahaan_kode_equity_sales' 			: fields.char('Kode Equity Sales'),
		'perusahaan_kantor_perwakilan_galery' 	: fields.char('Kantor Perwakilan/Galery'),
		'perusahaan_nomor_sub_rekening_efek' 	: fields.char('Nomor Sub Rekening Efek'),
		'perusahaan_nama_komisaris' 			: fields.char('Nama Komisaris'),
		'perusahaan_jabatan' 					: fields.char('Jabatan '),
		'perusahaan_diterbitkan_di' 			: fields.char('Diterbitkan di'),
		'perusahaan_nomor_ijin_pma' 			: fields.char('Nomor Ijin PMA'),
		'perusahaan_tanggal_kedaluarsa_pma' 	: fields.date('Tanggal Kedaluarsa PMA'),
		'perusahaan_diterbitkan_di' 			: fields.char('Diterbitkan di'),
		'perusahaan_tahun_berdiri_perusahaan' 	: fields.char('Tahun berdiri perusahaan'),
		'perusahaan_jumlah_karyawan' 			: fields.char('Jumlah karyawan'),
		'perusahaan_jumlah_karyawan_yang_diikutsertakan' : fields.char('Jumlah Karyw. yg Diikutkan'),
		'perusahaan_polis_lain_yang_dimiliki' 	: fields.char('Polis lain yang dimiliki'),
		'perusahaan_tujuan_menutup_asuransi' 	: fields.char('Tujuan menutup Asuransi'),
		'perusahaan_modal_disetor' 				: fields.char('Modal disetor'),
		'perusahaan_total_asset' 				: fields.char('Total Asset'),
		'perusahaan_total_kewajiban' 			: fields.char('Total Kewajiban'),
		'perusahaan_laba_bersih' 				: fields.char('Laba bersih'),
		'perusahaan_pendapatan_operasional' 	: fields.char('Pendapatan Oper.'),
		'perusahaan_pendapatan_non_operasional' : fields.char('Pendapatan non Oper.'),
		
		'perorangan_tempat_lahir' 				: fields.char('Tempat Lahir'),
		'perorangan_tanggal_lahir' 				: fields.date('Tanggal Lahir'),
		'perorangan_nomor_ktp' 					: fields.char('Nomor KTP'),
		
		# 'perorangan_kewarganegaraan' 			: fields.char('Kewarganegaraan'),
		'perorangan_kewarganegaraan' 			: fields.many2one('reliance.warga_negara', 'Kewarganegaraan'),
		'perorangan_npwp' 						: fields.char('NPWP'),
		
		# 'perorangan_status_perkawinan' 			: fields.char('Status Perkawinan'),
		'perorangan_status_perkawinan' 			: fields.many2one('reliance.status_nikah', 'Status Perkawinan'),
		
		'perorangan_alamat_surat_menyurat' 		: fields.char('Alamat surat menyurat'),
		'perorangan_kecamatan' 					: fields.char('Kecamatan'),
		
		# 'perorangan_jenis_kelamin' 				: fields.char('Jenis Kelamin'),
		'perorangan_jenis_kelamin' 				: fields.many2one('reliance.jenis_kelamin', 'Jenis Kelamin'),
		
		'perorangan_nama_istri_suami' 			: fields.char('Nama istri/ suami'),
		'perorangan_alamat_email' 				: fields.char('Email (Perorangan)'),
		'perorangan_pendidikan_terakhir' 		: fields.char('Pendidikan Terakhir'),
		'perorangan_masa_berlaku_ktp' 			: fields.char('Masa berlaku KTP'),
		# 'perorangan_agama' 						: fields.char('Agama'),
		'perorangan_agama' 						: fields.many2one('reliance.agama', 'Agama'),
		'perorangan_tujuan_investasi' 			: fields.char('Tujuan Investasi'),
		'perorangan_kitas' 						: fields.char('Kitas'),
		'perorangan_masa_berlaku_kitas' 		: fields.char('Masa berlaku Kitas'),
		'perorangan_paspor' 					: fields.char('Paspor'),
		'perorangan_masa_berlaku_paspor' 		: fields.char('Masa berlaku Paspor'),
		'perorangan_nama_gadis_ibu_kandung' 				: fields.char('Nama gadis ibu kandung'),
		'perorangan_sumber_dana_yg_akan_diinvestasikan' 	: fields.char('Sumber dana yg diinvest.'),
		'perorangan_alamat_tempat_tinggal_saat_ini' 		: fields.char('Alamat Saat Ini'),
		'perorangan_periode_asuransi' 			: fields.char('Periode Asuransi'),
		'perorangan_lokasi_resiko' 				: fields.char('Lokasi Resiko'),
		'perorangan_harga_pertanggungan' 		: fields.char('Harga Pertanggungan'),
		'perorangan_kondisi_bangunan' 			: fields.char('Kondisi Bangunan'),
		'perorangan_penggunaan_bangunan_kendaraan' 	: fields.char('Penggunaan Bangunan/Kend.'),
		'perorangan_wilayah_kendaraan' 			: fields.char('Wilayah Kendaraan'),
		'perorangan_obyek_pertanggungan' 		: fields.char('Obyek Pertanggungan'),
		'perorangan_jenis_pertanggungan' 		: fields.char('Jenis Pertanggungan'),
		'perorangan_jenis_perluasan' 			: fields.char('Jenis Perluasan'),
		'perorangan_pengalaman_klaim' 			: fields.char('Pengalaman Klaim'),
		'perorangan_status_nasabah' 			: fields.char('Status Nasabah'),
		'perorangan_kegiatan_berorganisasi' 	: fields.char('Kegiatan berorganisasi'),
		'perorangan_nama_organisasi' 			: fields.char('Nama organisasi'),
		'perorangan_jabatan' 					: fields.char('Jabatan'),

		# 'pekerjaan_nama' 						: fields.char('Pekerjaan'),
		'pekerjaan_nama' 						: fields.many2one('reliance.pekerjaan', 'Pekerjaan'),

		'pekerjaan_profesi' 					: fields.char('Profesi'),
		'pekerjaan_nama_perusahaan' 			: fields.char('Nama perusahaan'),
		'pekerjaan_alamat_perusahaan' 			: fields.char('Alamat Perusahaan'),
		'pekerjaan_bidang_usaha' 				: fields.char('Bidang Usaha'),
		
		# 'pekerjaan_penghasilan_per_tahun' 		: fields.char('Penghasilan per tahun'),
		'pekerjaan_penghasilan_per_tahun' 		: fields.many2one('reliance.range_penghasilan', 'Penghasilan per tahun'),

		'pekerjaan_jabatan' 					: fields.char('Jabatan'),
		'pekerjaan_penghasilan_per_bulan' 		: fields.char('Penghasilan per bulan'),
		'pekerjaan_nomor_npwp' 					: fields.char('Nomor NPWP'),
		'pekerjaan_nomor_telepon' 				: fields.char('Nomor Telepon'),
		'pekerjaan_alamat_email' 				: fields.char('Alamat Email (Pekerjaan)'),
		'pekerjaan_masa_kerja' 					: fields.char('Masa Kerja'),
		'pekerjaan_nama_direktur' 				: fields.char('Nama Direktur'),
		'pekerjaan_nomor_extension' 			: fields.char('Nomor Extension'),
		'pekerjaan_nomor_faksimile' 			: fields.char('Nomor Faksimile'),

		'partner_account_ids' 					: fields.one2many('reliance.partner_account','partner_id','Accounts', ondelete="cascade", select=1),
		'partner_ahli_waris_ids' 				: fields.one2many('reliance.ahli_waris','partner_id','Ahli Waris', ondelete="cascade", select=1),
		'partner_keluarga_ids' 					: fields.one2many('reliance.keluarga','partner_id','Keluarga', ondelete="cascade", select=1),
		'calendar_last_notif_ack': fields.datetime('Last Notif. from Cal.'),
		'notify_email': fields.selection([
		    ('none', 'Never'),
		    ('always', 'All Messages'),
		    ], 'Recv. Inbox Not. by Email', required=True,
		    oldname='notification_email_send',
		    help="Policy to receive emails for new messages pushed to your personal Inbox:\n"
		            "- Never: no emails are sent\n"
		            "- All Messages: for every notification you receive in your Inbox"),

		'hobby_ids'								: fields.many2many(
					'reliance.hobby',    # 'other.object.name' dengan siapa dia many2many
					'partner_hobby',     # 'relation object'
					'partner_id',        # 'actual.object.id' in relation table
					'hobby_id',          # 'other.object.id' in relation table
					'Hobby',             # 'Field Name'
					required=False),
		'risk_profile'							: fields.char('Risk Profile'),
	}
	_sql_constraints = [('unique_reliance_id', 'unique(reliance_id)',
                         'Reliance ID Must be Unique!')]


	#############################################################
	# search partner_id apakah berada dalam salah satu campaing
	# if yes: return the campaign records (array)
	#############################################################
	def button_in_campaign(self, cr, uid, ids, context=None):
		partner = self.browse(cr, uid, ids[0], context=context)
		reliance_id = partner.reliance_id
		campaigns = self.in_campaign(cr, uid, reliance_id, context=context)
		
		names = []
		for cam in campaigns:
			names.append(cam['name'])
		raise osv.except_osv(_('campaign names:'), names ) 


	#############################################################
	# cek in_campaign by reliance_id
	#############################################################
	def in_campaign(self, cr, uid, reliance_id, context=None):

		if not reliance_id:
			raise osv.except_osv(_('error'),_("Please specify Reliance ID") ) 

		##### cek partner.id 
		pid = self.search(cr, uid, [('reliance_id','=',reliance_id)], context=context)
		if not pid:
			raise osv.except_osv(_('Error'),_("No Partner with Reliance ID=%s")  % reliance_id ) 

		campaigns =  self.in_campaign_by_id(cr, uid, pid[0], context=context)

		return campaigns

	#############################################################
	# cek in_campaign by id 
	#############################################################
	def in_campaign_by_id(self, cr, uid, pid, context=None):

		campaigns = []


		##### cari filters utk model res.partner
		ir_filter = self.pool.get('ir.filters')
		ir_filter_ids = ir_filter.search(cr, uid, [('model_id','=','res.partner')], context=context)

		##### cek apakah pid berada di salah satu filter  

		for filter_id in ir_filter.browse(cr, uid, ir_filter_ids, context=context):
			if filter_id.domain != '[]':
				criteria = eval(filter_id.domain)
				criteria[:0] = ['&',('id','=',pid)]
				pids = self.search(cr, uid, criteria, context=context)
				if pids:
					campaigns.append({'id':filter_id.id,'name' : filter_id.name} )

		return campaigns


	def in_campaign_old(self, cr, uid, reliance_id, context=None):
		campaigns = []

		pid = self.search(cr, uid, [('reliance_id','=',reliance_id)], context=context)
		if not pid:
			raise osv.except_osv(_('Error'),_("No Partner with Reliance ID=%s")  % reliance_id ) 

		sql = "select campaign_id from reliance_campaign_partner where campaign_id is not null and partner_id=%s" % pid[0]
		cr.execute(sql)
		result = cr.fetchall()

		if result != (None,) : 
			for r in result :
				res=map(lambda x:x[0],result)
				fields = ('name','date_start','date_end','state','user_id')
		campaigns = self.pool.get('reliance.campaign').search_read(cr, uid, [('id','in',res)], fields, context=context)
		print campaigns
		return campaigns

	def button_merge(self, cr, uid, ids, context=None):
		# test merge to SAGUNG 
		self.merge(cr, uid, ids[0], 42260, context=context)

	def merge(self, cr, uid, partner_id1, partner_id2, context=None):
		p1 = self.read(cr, uid, partner_id1, context=context) # src
		if not p1:
			raise osv.except_osv(_('error'),_("partner_id1 not found") ) 

		p2 = self.read(cr, uid, partner_id2, context=context) # dest
		if not p2:
			raise osv.except_osv(_('error'),_("partner_id2 not found") ) 

		

		p2_data = {}

		############################################################
		#for partner fields:
		#fill p2 empty fields from p1
		############################################################
		for kol in self._columns.keys():

			if isinstance(self._columns[kol], fields.one2many):
				continue
			if isinstance(self._columns[kol], fields.many2one):
				continue

			# only update if p1 field is not empty and p2 field is empty
			p1_field = p1[kol]
			p2_field = p2[kol]

			if p1_field and not p2_field:
				p2_data.update({
					kol : p1_field,
				})

		############################################################
		# ARG details
		# many2one:
		# one2many: pindahkan partner_polis_ids punya p1 ke p2
		############################################################
		if p1['partner_polis_ids']:
			cr.execute('update reliance_arg_partner_polis set partner_id=%s where partner_id=%s' %(partner_id2, partner_id1) )

		############################################################
		# AJRI details
		# many2one: pindahkan ajri_parent_id punya p1 ke p2
		############################################################
		if p1['ajri_parent_id']:
			p2_data['ajri_parent_id'] = p1['ajri_parent_id'][0]

		############################################################
		# one2many: pindahkan partner_ajri_products punya p1 ke p2
		############################################################
		if p1['partner_ajri_product_ids']:
			cr.execute('update reliance_partner_ajri_product set partner_id=%s where partner_id=%s' %(partner_id2, partner_id1) )
		

		############################################################
		# LS details
		# one2many: partner_cash
		############################################################
		if p1['partner_cash_ids']:
			cr.execute('update reliance_partner_cash set partner_id=%s where partner_id=%s' %(partner_id2, partner_id1) )

		############################################################
		# one2many: partner_stock
		############################################################
		if p1['partner_stock_ids']:
			cr.execute('update reliance_partner_stock set partner_id=%s where partner_id=%s' %(partner_id2, partner_id1) )

		############################################################
		# HEALTH details
		# many2one: polis holder
		############################################################
		if p1['health_parent_id']:
			p2_data['health_parent_id'] = p1['health_parent_id'][0]

		############################################################
		# one2many: health_limit
		############################################################
		if p1['health_limit_ids']:
			cr.execute('update reliance_partner_health_limit set partner_id=%s where partner_id=%s' %(partner_id2, partner_id1) )
		
		############################################################
		# REFI details
		# many2one: pindahkan ajri_parent_id punya p1 ke p2
		############################################################
		if p1['refi_parent_id']:
			p2_data['refi_parent_id'] = p1['refi_parent_id'][0]

		############################################################
		# pindahkan refi_kontrak punya p1 ke p2
		############################################################
		if p1['refi_kontrak_ids']:
			cr.execute('update reliance_refi_kontrak set partner_id=%s where partner_id=%s' %(partner_id2, partner_id1) )
		
		############################################################
		# pindahkan partner_keluarga_ids punya p1 ke p2
		############################################################
		if p1['partner_keluarga_ids']:
			cr.execute('update reliance_keluarga set partner_id=%s where partner_id=%s' %(partner_id2, partner_id1) )
				
		############################################################
		# pindahkan partner_ahli_waris_ids punya p1 ke p2
		############################################################
		if p1['partner_ahli_waris_ids']:
			cr.execute('update reliance_ahli_waris set partner_id=%s where partner_id=%s' %(partner_id2, partner_id1) )
		
		############################################################
		# RMI details
		# many2one
		# one2many
		############################################################

		############################################################
		# save p2
		############################################################
		print p2_data

		if p2_data:
			self.write(cr, uid, partner_id2, p2_data, context=context)


		############################################################
		# write logs
		############################################################

		src_partners = self.browse(cr, uid, [partner_id1], context=context)
		dst_partner = self.browse(cr, uid, partner_id2, context=context)

		dst= "%s<%s>(ID %s)" % (dst_partner.name, dst_partner.email or 'n/a', dst_partner.id)
		dst_partner.message_post(body= '%s %s %s' % ( dst, _("merged with the following partners:"), ", ".join('%s<%s>(ID %s)' % (p.name, p.email or 'n/a', p.id) for p in src_partners)))

		############################################################
		#delete p1 
		############################################################
		# self.unlink(cr, uid, [partner_id1], context=context)
		self.write(cr, uid, [partner_id1], {'active':False }, context=context)
        
		############################################################
		# return p2 lengkap
		############################################################
		return self.read(cr, uid, partner_id2, context=context)


class ahli_waris(osv.osv):
	_name = "reliance.ahli_waris"
	_columns 	= {
		'partner_id' 		: fields.many2one('res.partner', 'Partner'),
		'nama' 				: fields.char('Nama'),
		'nomor_telepon' 	: fields.char('Nomor Telepon'),
		'hubungan_keluarga' : fields.char('Hubungan keluarga'),
		'alamat' 			: fields.char('Alamat'),
		'pendidikan_terakhir' : fields.char('Pendidikan terakhir'),
	}


class keluarga(osv.osv):
	_name = "reliance.keluarga"
	_columns 	= {
		'partner_id' 		: fields.many2one('res.partner', 'Partner'),
		'nama' 				: fields.char('Nama'),
		'nomor_telepon' 	: fields.char('Nomor Telepon'),
		'hubungan_keluarga' : fields.char('Hubungan keluarga'),
		'alamat' 			: fields.char('Alamat'),
		'tgl_lahir'			: fields.date('Tanggal Lahir'),
		'jenis_kelamin'		: fields.char('Jenis Kelamin'),
		'pendidikan'		: fields.char('Pendidikan'),
		'profesi'			: fields.char('Profesi'),
		
	}


class partner_account(osv.osv):
	_name = "reliance.partner_account"
	_columns 	= {
		'partner_id' : fields.many2one('res.partner', 'Partner'),
		'product_id' : fields.many2one('product.product', 'Product')
	}

