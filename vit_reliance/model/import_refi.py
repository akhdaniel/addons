from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)

####################################################################
# partner data
# from refi-customer csv file
####################################################################
class import_refi(osv.osv): 
	_name 		= "reliance.import_refi"
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
	}

	def action_import_partner(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner(self, cr, uid, context=None):
		_logger.warning('running cron import_refi')
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=100, context=context)
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

		for import_refi in self.browse(cr, uid, ids, context=context):

			pemegang_data = {
				'name'				: import_refi.nama_pemegang,
				'policy_no'			: import_refi.policy_no,
				'is_company'		: True,
				'comment' 			: 'REFI'
			}
			
			########################## check exiting partner partner 
			pid = partner.search(cr, uid, [('policy_no','=',import_refi.policy_no)],context=context)
			if not pid:
				pid = partner.create(cr, uid, pemegang_data, context=context)	
				i = i + 1
			else:
				pid = pid[0]
				_logger.warning('Partner exist with policy_no %s' % import_refi.policy_no)
				ex = ex + 1

			pemegang_old = import_refi.nama_pemegang

			#commit per record
			cr.execute("update reliance_import_refi set is_imported='t' where id=%s" % import_refi.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )


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
	}


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
	}

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

	}

