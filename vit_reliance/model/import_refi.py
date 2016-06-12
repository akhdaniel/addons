from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)


PARTNER_MAPPING = {
	"no_debitur"			: "refi_no_debitur",
	"nama_depan"			: False,
	"nama_belakang"			: False,
	"nama_lengkap"			: "name",
	"nama_ibu"				: "perorangan_nama_gadis_ibu_kandung",
	"tipe_id"				: "refi_tipe_id",
	"no_id"					: "perorangan_nomor_ktp",
	"tgl_exp_id"			: "perorangan_masa_berlaku_ktp",
	"tempat_lahir"			: "perorangan_tempat_lahir",
	# "tgl_lahir"				: "perorangan_tanggal_lahir",
	"npwp"					: "perorangan_npwp",
	"legal_alamat"			: "street",
	"legal_kecamatan"		: "perorangan_kecamatan",
	"legal_kota"			: "city",
	"legal_propinsi"		: "state_id",
	"legal_kode_pos"		: "zip",
	"domisil_alamat"		: "perorangan_alamat_surat_menyurat",
	"domisili_kecamatan"	: "refi_domisili_kecamatan",
	"domisili_kota"			: "refi_domisili_kota",
	"domisili_propinsi"		: "refi_domisili_propinsi",
	"domisili_kode_pos"		: "refi_kode_pos",
	"wilayah"				: "refi_wilayah",
	"telepon_rumah"			: "phone",
	"no_hp"					: "mobile",
	"email"					: "email",
	# CUST 003
	# "jns_kelamin"			: "perorangan_jenis_kelamin",
	# "agama"					: "perorangan_agama",
	# "warga_negara"			: "perorangan_kewarganegaraan",
	"pendidikan"			: "perorangan_pendidikan_terakhir",
	"status_rumah"			: "refi_status_rumah",
	# "pekerjaan"				: "pekerjaan_nama",
	# "status_nikah"			: "perorangan_status_perkawinan",
	"profesi"				: "pekerjaan_profesi",
	"pisah_harta"			: "refi_pisah_harta",
	"jabatan"				: "pekerjaan_jabatan",
	"tanggungan"			: "refi_tanggunan",
	# "range_penghasilan"		: "pekerjaan_penghasilan_per_tahun",
}
####################################################################
# partner data
# from refi-customer csv file
####################################################################
class import_refi_partner(osv.osv): 
	_name 		= "reliance.import_refi_partner"
	_columns 	= {
		# CUST 001
		"no_debitur"			:	fields.char("No.Debitur"),
		"nama_depan"			:	fields.char("Nama Depan"),
		"nama_belakang"			:	fields.char("Nama Belakang"),
		"nama_lengkap"			:	fields.char("Nama Lengkap"),
		"nama_ibu"				:	fields.char("Nama Ibu"),
		"tipe_id"				:	fields.char("Tipe Id."),
		"no_id"					:	fields.char("No.Id."),
		"tgl_exp_id"			:	fields.char("Tgl.Exp.Id."),
		"tempat_lahir"			:	fields.char("Tempat Lahir"),
		"tgl_lahir"				:	fields.char("Tgl.Lahir"),
		"npwp"					:	fields.char("NPWP"),
		"legal_alamat"			:	fields.char("Legal Alamat"),
		"legal_kecamatan"		:	fields.char("Legal Kecamatan"),
		"legal_kota"			:	fields.char("Legal Kota"),
		"legal_propinsi"		:	fields.char("Legal Propinsi"),
		"legal_kode_pos"		:	fields.char("Legal Kode Pos"),
		"domisil_alamat"		:	fields.char("Domisil Alamat"),
		"domisili_kecamatan"	:	fields.char("Domisili Kecamatan"),
		"domisili_kota"			:	fields.char("Domisili Kota"),
		"domisili_propinsi"		:	fields.char("Domisili Propinsi"),
		"domisili_kode_pos"		:	fields.char("Domisili Kode Pos"),
		"wilayah"				:	fields.char("Wilayah"),
		"telepon_rumah"			:	fields.char("Telepon Rumah"),
		"no_hp"					:	fields.char("No.HP"),
		"email"					:	fields.char("Email"),
		# CUST 003
		"jns_kelamin"			:	fields.char("Jns.Kelamin"),
		"agama"					:	fields.char("Agama"),
		"warga_negara"			:	fields.char("Warga Negara"),
		"pendidikan"			:	fields.char("Pendidikan"),
		"status_rumah"			:	fields.char("Status Rumah"),
		"pekerjaan"				:	fields.char("Pekerjaan"),
		"status_nikah"			:	fields.char("Status Nikah"),
		"profesi"				:	fields.char("Profesi"),
		"pisah_harta"			:	fields.char("Pisah Harta"),
		"jabatan"				:	fields.char("Jabatan"),
		"tanggungan"			:	fields.char("Tanggungan"),
		"range_penghasilan"		:	fields.char("Range Penghasilan"),

		'is_imported' 		: 	fields.boolean("Imported to Partner?", select=1),
		"notes"				:	fields.char("Notes"),
		"source"			:	fields.char("Source"),	
	}

	def action_import_partner(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner(self, cr, uid, context=None):
		refi_import_partner_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'refi_import_partner_limit')
		_logger.warning('running cron refi_import_partner, limit=%s' % refi_import_partner_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(refi_import_partner_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')
		country = self.pool.get('res.country')
		master_agama = self.pool.get('reliance.agama')
		master_status_nikah = self.pool.get('reliance.status_nikah')
		master_warga_negara = self.pool.get('reliance.warga_negara')
		master_pekerjaan = self.pool.get('reliance.pekerjaan_refi')
		master_range_penghasilan = self.pool.get('reliance.range_penghasilan_refi')
		master_jenis_kelamin = self.pool.get('reliance.jenis_kelamin')
		states_mapping = self.pool.get('reliance.states_mapping')

		for import_refi in self.browse(cr, uid, ids, context=context):
			if not import_refi.no_debitur:
				ex = ex + 1
				self.write(cr, uid, import_refi.id ,  {'notes':'empty line'}, context=context)
				cr.commit()
				continue


			data = {}
			data2 = {}

			########################### default field mapping
			for k in PARTNER_MAPPING.keys():
				partner_fname = PARTNER_MAPPING[k]
				if partner_fname:
					import_refi_fname = "import_refi.%s" % k 
					data.update( {partner_fname : eval(import_refi_fname)})
			
			########################### date birth
			date_birth = False
			if import_refi.tgl_lahir:
				try: 
					date_birth = datetime.strptime(import_refi.tgl_lahir, "%d/%m/%Y")
				except ValueError:
					self.write(cr, uid, import_refi.id, {'notes':'date birth format error, use dd/mm/yyyy'}, context=context)
					ex = ex+1
					cr.commit()
					continue
			data2.update( {'perorangan_tanggal_lahir':date_birth})

			########################## lookup country and legal_propinsi
			country_id = country.search(cr, uid, [('name','ilike','indonesia')], context=context)
			data.update({'country_id': country_id[0]})

			# if import_refi.legal_propinsi:
			# state_id = country.find_or_create_state(cr,uid,import_refi.legal_propinsi, country_id[0], context=context)
			# data.update({'state_id': state_id})
			state_id = states_mapping.get(cr, uid, import_refi.legal_propinsi, context=context)
			data2.update({'state_id': state_id})
			data2.update({'initial_bu': 'REFI'})
			
			data.update({'comment': 'REFI'})
			
			########################### cek master agama
			agama_id = master_agama.get(cr, uid, 'refi', import_refi.agama, context=context)
			data2.update({'perorangan_agama': agama_id})
			
			########################### cek master status_nikah
			status_nikah_id = master_status_nikah.get(cr, uid, 'refi', import_refi.status_nikah, context=context)
			data2.update({'perorangan_status_perkawinan': status_nikah_id})
			
			########################### cek master warga_negara
			warga_negara_id = master_warga_negara.get(cr, uid, 'refi', import_refi.warga_negara, context=context)
			data2.update({'perorangan_kewarganegaraan': warga_negara_id})

			############################ cek master pekerjaan refi
			pekerjaan_id = master_pekerjaan.get(cr, uid, import_refi.pekerjaan, context=context)
			data2.update({'pekerjaan_nama': pekerjaan_id})
			
			############################ cek master range_penghasilan_refi
			range_penghasilan_id = master_range_penghasilan.get(cr, uid, import_refi.range_penghasilan, context=context)
			data2.update({'pekerjaan_penghasilan_per_tahun': range_penghasilan_id})

			############################ cek master jenis_kelamin refi
			jenis_kelamin_id = master_jenis_kelamin.get(cr, uid, 'refi', import_refi.jns_kelamin, context=context)
			data2.update({'perorangan_jenis_kelamin': jenis_kelamin_id})

			########################### check exiting partner partner 
			pid = partner.search(cr, uid, [('refi_no_debitur','=',import_refi.no_debitur)], context=context)
			if not pid:
				data.update(data2)
				pid = partner.create(cr, uid, data, context=context)	
				i = i + 1
			else:
				pid = pid[0]
				partner.write(cr, uid, pid, data2, context=context)	
				_logger.warning('Partner exist with refi_no_debitur %s' % import_refi.no_debitur)
				ex = ex + 1


			########################### commit per record
			cr.execute("update reliance_import_refi_partner set is_imported='t' where id=%s" % import_refi.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped/updated %s' % (i, ex) )

PERUSAHAAN_MAPPING = {
	"no_debitur"			: False,
	"nama_perusahaan"		: "name",
	"jenis_usaha"			: "perusahaan_bidang_usaha",
	"alamat"				: "street",
	"kecamatan"				: "perusahaan_kecamatan",
	"kota"					: "city",
	"provinsi"				: "state_id",
	"kode_pos"				: "zip",
	"telepon_1"				: "phone",
	"telepon_2"				: "mobile",
	"telex"					: False,
	"facsimile"				: "fax",
	"tanggal_masuk_kerja"	: False,
	"tanggal_bayar"			: False,
	"frek_bayar"			: False,
}

class import_refi_pekerjaan(osv.osv):
	_name = "reliance.import_refi_pekerjaan"
	_columns = {
		"no_debitur"			:	fields.char("No.Debitur"),
		"nama_perusahaan"		:	fields.char("Nama Perusahaan"),
		"jenis_usaha"			:	fields.char("Jenis Usaha"),
		"alamat"				:	fields.char("Alamat"),
		"kecamatan"				:	fields.char("Kecamatan"),
		"kota"					:	fields.char("Kota"),
		"provinsi"				:	fields.char("Provinsi"),
		"kode_pos"				:	fields.char("Kode Pos"),
		"telepon_1"				:	fields.char("Telepon-1"),
		"telepon_2"				:	fields.char("Telepon-2"),
		"telex"					:	fields.char("Telex"),
		"facsimile"				:	fields.char("Facsimile"),
		"tanggal_masuk_kerja"	:	fields.char("Tanggal Masuk Kerja"),
		"tanggal_bayar"			:	fields.char("Tanggal Bayar"),
		"frek_bayar"			:	fields.char("Frek Bayar"),

		'is_imported' 		: 	fields.boolean("Imported to Partner?", select=1),
		"notes"				:	fields.char("Notes"),
		"source"			:	fields.char("Source"),	
	}

	def action_import(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}
		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import(self, cr, uid, context=None):
		refi_import_pekerjaan_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'refi_import_pekerjaan_limit')
		_logger.warning('running cron refi_import_pekerjaan, limit=%s' % refi_import_pekerjaan_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(refi_import_pekerjaan_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')
		country = self.pool.get('res.country')
		states_mapping = self.pool.get('reliance.states_mapping')

		for import_refi in self.browse(cr, uid, ids, context=context):
			if not import_refi.no_debitur:
				ex = ex + 1
				self.write(cr, uid, import_refi.id ,  {'notes':'empty line'}, context=context)
				cr.commit()
				continue

			if not import_refi.nama_perusahaan or import_refi.nama_perusahaan == '.':
				ex = ex + 1
				self.write(cr, uid, import_refi.id ,  {'notes':'empty or dot nama perusahaan'}, context=context)
				cr.commit()
				continue

			data = {}
			data2 = {}
			for k in PERUSAHAAN_MAPPING.keys():
				partner_fname = PERUSAHAAN_MAPPING[k]
				if partner_fname:
					import_refi_fname = "import_refi.%s" % k 
					data.update( {partner_fname : eval(import_refi_fname)})
			
			
			########################## lookup country and legal_propinsi
			country_id = country.search(cr, uid, [('name','ilike','indonesia')], context=context)
			data.update({'country_id': country_id[0]})

			# if import_refi.provinsi:
			# 	state_id = country.find_or_create_state(cr,uid,import_refi.provinsi, country_id[0], context=context)
			# 	data.update({'state_id': state_id})
			state_id = states_mapping.get(cr, uid, import_refi.provinsi, context=context)
			data2.update({'state_id': state_id})
			data2.update({'initial_bu': 'REFI'})
			
			data.update({'is_company': True})			
			data.update({'comment': 'REFI'})
			
			########################## check exiting partner partner 
			pid = partner.search(cr, uid, [('name','=',import_refi.nama_perusahaan)], context=context)
			if not pid:
				data.update(data2)
				pid = partner.create(cr, uid, data, context=context)	
				i = i + 1
			else:
				pid = pid[0]
				partner.write(cr, uid,pid,  data2, context=context)	
				_logger.warning('Partner exist with name %s' % import_refi.nama_perusahaan)
				ex = ex + 1

			########################## update related no_debitur
			cust_id = partner.search(cr, uid, [('refi_no_debitur','=',import_refi.no_debitur)], context=context)
			if not cust_id:
				raise osv.except_osv(_('Error'),_("No REFI Partner with no_debitur=%s") % import_refi.no_debitur ) 

			partner.write(cr, uid, cust_id, 
				{'refi_parent_id':pid,
				'refi_tanggal_bayar': import_refi.tanggal_bayar,
				'refi_frek_bayar': import_refi.frek_bayar,
				'refi_tanggal_masuk_kerja': import_refi.tanggal_masuk_kerja,
				}, context=context)

			#commit per record
			cr.execute("update reliance_import_refi_pekerjaan set is_imported='t' where id=%s" % import_refi.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped/updated %s' % (i, ex) )


class import_refi_keluarga(osv.osv):
	_name = "reliance.import_refi_keluarga"
	_columns = {
		"no_debitur"		:	fields.char("No.Debitur"),
		"no_urut"			:	fields.char("No.Urut"),
		"nama"				:	fields.char("Nama"),
		"tgl_lahir"			:	fields.char("Tgl.Lahir"),
		"hubungan"			:	fields.char("Hubungan"),
		"jenis_kelamin"		:	fields.char("Jenis Kelamin"),
		"pendidikan"		:	fields.char("Pendidikan"),
		"profesi"			:	fields.char("Profesi"),	
		'is_imported' 		: 	fields.boolean("Imported to Partner Keluarga?", select=1),
		"notes"				:	fields.char("Notes"),
		"source"			:	fields.char("Source"),	
	}


	def action_import(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}
		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import(self, cr, uid, context=None):
		refi_import_keluarga_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'refi_import_keluarga_limit')
		_logger.warning('running cron refi_import_pekerjaan, limit=%s' % refi_import_keluarga_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(refi_import_keluarga_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')
		country = self.pool.get('res.country')

		for import_refi in self.browse(cr, uid, ids, context=context):

			if not import_refi.no_debitur:
				ex = ex + 1
				self.write(cr, uid, import_refi.id ,  {'notes':'empty line'}, context=context)
				cr.commit()
				continue


			pid = partner.search(cr, uid, [('refi_no_debitur','=',import_refi.no_debitur)], context=context)
			if not pid:
				ex=ex+1
				self.write(cr, uid, import_refi.id, {'notes':'NO DEBITUR NOT FOUND'}, context=context)
				cr.commit()
				continue


			data = {
				'partner_keluarga_ids' : [(0,0,{
					'nama'				: import_refi.nama,
					'hubungan_keluarga'	: import_refi.hubungan,
					'alamat'			: False,
					'nomor_telepon'		: False,
					# 'tgl_lahir'			: datetime.strptime(import_refi.tgl_lahir, "%d-%m-%Y"),
					'jenis_kelamin'		: import_refi.jenis_kelamin,
					'pendidikan'		: import_refi.pendidikan,
					'profesi'			: import_refi.profesi,
				})]
			}
			########################### date birth
			tgl_lahir = False
			if import_refi.tgl_lahir:
				try:
					tgl_lahir = datetime.strptime(import_refi.tgl_lahir, "%d/%m/%Y")
				except ValueError:
					self.write(cr, uid, import_refi.id, {'notes':'tgl_lahir format error, use dd/mm/yyyy'}, context=context)
					ex = ex+1
					cr.commit()
					continue
			data.update( {'perorangan_tanggal_lahir':tgl_lahir})

			partner.write(cr, uid, pid[0], data, context=context)

			#commit per record
			i = i + 1
			cr.execute("update reliance_import_refi_keluarga set is_imported='t' where id=%s" % import_refi.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s' % (i, ex) )


STATEMENT_MAPPING = {
	"bulan_tahun_survey"				:	"refi_bulan_tahun_survey",
	"time_deps_saving_account"			:	"refi_time_deps_saving_account",
	"vehicle"							:	"refi_vehicle",
	"jml_kendaraan"						:	"refi_jml_kendaraan",
	"properties"						:	"refi_properties",
	"jml_rumah"							:	"refi_jml_rumah",
	"others_aktiva_lainnya"				:	"refi_others_aktiva_lainnya",
	"mortagage_loan_inst"				:	"refi_mortagage_loan_inst",
	"mortgage_loan_inst_balance"		:	"refi_mortgage_loan_inst_balance",
	"renting"							:	"refi_renting",
	"car_credit"						:	"refi_car_credit",
	"car_credit_balance"				:	"refi_car_credit_balance",
	"credit_card"						:	"refi_credit_card",
	"credit_card_balance"				:	"refi_credit_card_balance",
	"credit_line"						:	"refi_credit_line",
	"credit_line_balance"				:	"refi_credit_line_balance",
	"monthly_expenditure"				:	"refi_monthly_expenditure",
	"monthly_expenditure_balance"		:	"refi_monthly_expenditure_balance",
	"mortgage_loan_int"					:	"refi_mortgage_loan_int",
	"mortgage_loan_int_balance_equity"	:	"refi_mortgage_loan_int_balance_equity",
	"other"								:	"refi_other",
	"other_balance_equity_net_income"	:	"refi_other_balance_equity_net_income",
	"spouse_income"						:	"refi_spouse_income",
	"other_income"						:	"refi_other_income",	
}

class import_refi_statement(osv.osv):
	_name = "reliance.import_refi_statement"
	_columns = {
		"no_debitur"						:	fields.char("No.Debitur"),
		"bulan_tahun_survey"				:	fields.char("Bulan/Tahun Survey"),
		"time_deps_saving_account"			:	fields.char("Time Deps/Saving account"),
		"vehicle"							:	fields.char("Vehicle"),
		"jml_kendaraan"						:	fields.char("Jml.Kendaraan"),
		"properties"						:	fields.char("Properties"),
		"jml_rumah"							:	fields.char("Jml.Rumah"),
		"others_aktiva_lainnya"				:	fields.char("Others (Aktiva Lainnya)"),
		"mortagage_loan_inst"				:	fields.char("Mortagage loan inst"),
		"mortgage_loan_inst_balance"		:	fields.char("Mortgage loan inst balance"),
		"renting"							:	fields.char("Renting"),
		"car_credit"						:	fields.char("Car credit"),
		"car_credit_balance"				:	fields.char("Car credit balance"),
		"credit_card"						:	fields.char("Credit Card"),
		"credit_card_balance"				:	fields.char("Credit Card balance"),
		"credit_line"						:	fields.char("Credit Line"),
		"credit_line_balance"				:	fields.char("Credit Line balance"),
		"monthly_expenditure"				:	fields.char("Monthly Expenditure"),
		"monthly_expenditure_balance"		:	fields.char("Monthly Expenditure balance"),
		"mortgage_loan_int"					:	fields.char("Mortgage loan int"),
		"mortgage_loan_int_balance_equity"	:	fields.char("Mortgage loan int balance (Equity)"),
		"other"								:	fields.char("Other"),
		"other_balance_equity_net_income"	:	fields.char("Other balance (Equity)Net Income"),
		"spouse_income"						:	fields.char("Spouse Income"),
		"other_income"						:	fields.char("Other Income"),

		'is_imported' 		: 	fields.boolean("Imported to Partner Statement?", select=1),
		"notes"				:	fields.char("Notes"),	
		"source"			:	fields.char("Source"),	
	}

	def action_import(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}
		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import(self, cr, uid, context=None):
		refi_import_statement_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'refi_import_statement_limit')
		_logger.warning('running cron refi_import_statement, limit=%s' % refi_import_statement_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(refi_import_statement_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')
		country = self.pool.get('res.country')

		for import_refi in self.browse(cr, uid, ids, context=context):
			if not import_refi.no_debitur:
				ex = ex + 1
				self.write(cr, uid, import_refi.id ,  {'notes':'empty line'}, context=context)
				cr.commit()
				continue

			data = {}
			for k in STATEMENT_MAPPING.keys():
				partner_fname = STATEMENT_MAPPING[k]
				if partner_fname:
					import_refi_fname = "import_refi.%s" % k 
					data.update( {partner_fname : eval(import_refi_fname)})

			cust_id = partner.search(cr, uid, [('refi_no_debitur','=',import_refi.no_debitur)], context=context)
			if not cust_id:
				raise osv.except_osv(_('Error'),_("No REFI Partner with no_debitur=%s") % import_refi.no_debitur ) 

			partner.write(cr, uid, cust_id, data , context=context)

			#commit per record
			i = i +1
			cr.execute("update reliance_import_refi_statement set is_imported='t' where id=%s" % import_refi.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done updating %s partner statement and skipped %s' % (i, ex) )


class import_refi_kontrak(osv.osv):
	_name = "reliance.import_refi_kontrak"
	_columns = {
		"contract_number"	:	fields.char("ContractNumber"),
		"customer_no"		:	fields.char("CustomerNo"),
		"customer_name"		:	fields.char("CustomerName"),
		"product"			:	fields.char("Product"),
		"asset_name"		:	fields.char("AssetName"),
		"outstanding"		:	fields.char("Outstanding"),
		"next_installment"	:	fields.char("NextInstallment"),
		"pass_due"			:	fields.char("PassDue"),
		"maturity_date"		:	fields.char("MaturityDate"),
		'is_imported' 		: 	fields.boolean("Imported to Partner Kontrak?", select=1),
		"notes"				:	fields.char("Notes"),	
		"source"			:	fields.char("Source"),	

	}


	def action_import(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}
		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import(self, cr, uid, context=None):
		refi_import_kontrak_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'refi_import_kontrak_limit')
		_logger.warning('running cron refi_import_kontrak, limit=%s' % refi_import_kontrak_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(refi_import_kontrak_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')
		country = self.pool.get('res.country')
		kontrak = self.pool.get('reliance.refi_kontrak')

		for import_refi in self.browse(cr, uid, ids, context=context):

			if not import_refi.contract_number:
				ex = ex + 1
				self.write(cr, uid, import_refi.id ,  {'notes':'empty line'}, context=context)
				cr.commit()
				continue
				
			data = {}

			cust_id = partner.search(cr, uid, [('refi_no_debitur','=',import_refi.customer_no)], context=context)
			if not cust_id:
				msg = _("PARTNER NOT FOUND")
				self.write(cr, uid, import_refi.id, {'notes':msg}, context=context)
				cr.commit()
				ex=ex+1
				continue

			########################### next_installment
			next_installment = False
			if import_refi.next_installment.strip():
				try: 
					next_installment = datetime.strptime(import_refi.next_installment.strip(), "%d-%m-%Y")
				except ValueError:
					self.write(cr, uid, import_refi.id, {'notes':'next_installment format error, use dd-mm-yyyy'}, context=context)
					ex = ex+1
					cr.commit()
					continue
			data.update( {'next_installment':next_installment})

			########################### maturity_date
			maturity_date = False
			if import_refi.maturity_date.strip():
				try: 
					maturity_date = datetime.strptime(import_refi.maturity_date.strip(), "%d-%m-%Y")
				except ValueError:
					self.write(cr, uid, import_refi.id, {'notes':'maturity_date format error, use dd-mm-yyyy'}, context=context)
					ex = ex+1
					cr.commit()
					continue
			data.update( {'maturity_date':maturity_date})
			
			data.update({
				"partner_id"		: 	cust_id[0],
				"contract_number"	:	import_refi.contract_number, 
				"customer_no"		:	import_refi.customer_no,	
				"customer_name"		:	import_refi.customer_name,	
				"product"			:	import_refi.product,	
				"asset_name"		:	import_refi.asset_name,	
				"outstanding"		:	import_refi.outstanding,	
				"pass_due"			:	import_refi.pass_due,	
			})

			# data = {
			# 	'refi_kontrak_ids'  : [(0,0,kontrak)]
			# }
			# partner.write(cr, uid, cust_id, data , context=context)
			kontrak_ids = kontrak.search(cr, uid, [
				('partner_id','=',cust_id[0]),
				('contract_number','=',import_refi.contract_number),
				('product','=',import_refi.product),
				('asset_name','=',import_refi.asset_name),
			], context=context)

			if not kontrak_ids:
				i = i +1
				kontrak.create(cr, uid, data, context=context)
			else:
				ex = ex +1
				_logger.warning('existing kontrak pid=%s, contract_number=%s, product=%s, asset_name=%s' % 
					(cust_id[0], import_refi.contract_number, import_refi.product, import_refi.asset_name))
				kontrak.write(cr, uid, kontrak_ids, data, context=context)

			#commit per record
			cr.execute("update reliance_import_refi_kontrak set is_imported='t' where id=%s" % import_refi.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner kontrak and skipped/updated %s' % (i, ex) )

