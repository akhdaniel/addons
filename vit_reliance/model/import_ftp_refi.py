from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
from openerp.tools.translate import _
import zipfile,os.path
import shutil
import ftp_utils as ftp
import logging
_logger = logging.getLogger(__name__)

DELIMITER=","
QUOTECHAR='"'

class import_ftp_refi(osv.osv):
	_name 		= "reliance.import_ftp_refi"
	_rec_name 	= "input_file"

	_columns 	= {
		'date_start'	: fields.datetime('Date Start'),
		'date_end'		: fields.datetime('Date End'),
		'user_id'		: fields.many2one('res.users', 'Users'),
		'input_file'	: fields.char('Input File'),
		'total_records'	: fields.integer('Total Records'),
		'notes'			: fields.char('Notes'),
	}

	_defaults = {
		'user_id'	: lambda obj, cr, uid, context: uid,
	}


	###########################################################
	# dipanggil dari cron job
	###########################################################
	def cron_process(self, cr, uid, context=None):
		_logger.warning('running FTP REFI cron_process')
		self.check_new_files(cr, uid, [], context=context)
		return True


	###########################################################
	#
	# is there new files on the ftp upload folder ?
	# called from cron job
	# if type=zip: unzip
	# process the extracted CSV 
	###########################################################
	def check_new_files(self, cr, uid, ids, context=None):
		ftp_utils = ftp.ftp_utils()

		ftp_refi_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_refi_folder')

		ftp_utils.check_done_folder(ftp_refi_folder)

		if context==None:
			context={}
		context.update({'date_start':time.strftime('%Y-%m-%d %H:%M:%S')})


		# search and extract ZIP and move zip to done folder
		# zip_files = glob.glob(ftp_refi_folder + '/*.zip')
		zip_files = ftp_utils.insensitive_glob(ftp_refi_folder + '/*.zip')

		for f in zip_files:
			if zipfile.is_zipfile(f):
				ftp_utils.unzip(f, ftp_refi_folder)
				done = ftp_utils.done_filename(cr, uid, f, context=context)
				shutil.move(f, done)
			else:
				_logger.error('wrong zip file')

		csv_files = ftp_utils.insensitive_glob(ftp_refi_folder + '/*.csv')


		for csv_file in csv_files:
			if csv_file.upper().find('PERSONAL') != -1:
				self.insert_refi_personal(cr, uid, csv_file, context=context)

			elif csv_file.upper().find('PEKERJAAN') != -1:
				self.insert_refi_pekerjaan(cr, uid, csv_file, context=context)

			elif csv_file.upper().find('KELUARGA') != -1:
				self.insert_refi_keluarga(cr, uid, csv_file, context=context)

			elif csv_file.upper().find('STATEMENT') != -1:
				self.insert_refi_statement(cr, uid, csv_file, context=context)

			elif csv_file.upper().find('KONTRAK') != -1:
				self.insert_refi_kontrak(cr, uid, csv_file, context=context)

		return 


	###########################################################
	# read the CSV into refi  personal
	###########################################################
	def insert_refi_personal(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data personal refi')
		ftp_utils = ftp.ftp_utils()
		import_refi_partner = self.pool.get('reliance.import_refi_partner')

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import REFI Partner")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import REFI Partner") )

		fields_map = [
			"no_debitur"			,
			"nama_depan"			,
			"nama_belakang"			,
			"nama_lengkap"			,
			"nama_ibu"				,
			"tipe_id"				,
			"no_id"					,
			"tgl_exp_id"			,
			"tempat_lahir"			,
			"tgl_lahir"				,
			"npwp"					,
			"legal_alamat"			,
			"legal_kecamatan"		,
			"legal_kota"			,
			"legal_propinsi"		,
			"legal_kode_pos"		,
			"domisil_alamat"		,
			"domisili_kecamatan"	,
			"domisili_kota"			,
			"domisili_propinsi"		,
			"domisili_kode_pos"		,
			"wilayah"				,
			"telepon_rumah"			,
			"no_hp"					,
			"email"					,
			# CUST 003
			"jns_kelamin"			,
			"agama"					,
			"warga_negara"			,
			"pendidikan"			,
			"status_rumah"			,
			"pekerjaan"				,
			"status_nikah"			,
			"profesi"				,
			"pisah_harta"			,
			"jabatan"				,
			"tanggungan"			,
			"range_penghasilan"		,
		]

		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_refi_partner, 
			delimiter=DELIMITER, quotechar=QUOTECHAR,
			cron_id=cron_id, cron_obj=cron_obj,
			context=context)
		
		if isinstance(i, dict):
			self.create(cr, uid, i, context=context )
			cr.commit()
			return

		# move csv_file to processed folder
		done = ftp_utils.done_filename(cr, uid, csv_file, context=context)
		shutil.move(csv_file, done)

		data = {
			'date_start' : context.get('date_start',False),
			'date_end' : time.strftime('%Y-%m-%d %H:%M:%S'),
			'input_file' : csv_file,
			'total_records' : i,
			'notes'	: '%s moved to %s' % (csv_file, done),
		}
		self.create(cr, uid, data, context=context )
		cr.commit()

		return 


	###########################################################
	# read the CSV into refi pekerjaan
	###########################################################
	def insert_refi_pekerjaan(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data pekerjaan refi')
		ftp_utils = ftp.ftp_utils()
		import_refi_pekerjaan = self.pool.get('reliance.import_refi_pekerjaan')

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import REFI Partner Pekerjaan")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import REFI Partner Pekerjaan") )

		fields_map = [
			"no_debitur"		,
			"nama_perusahaan"	,	
			"jenis_usaha"		,	
			"alamat"			,	
			"kecamatan"			,	
			"kota"				,	
			"provinsi"			,	
			"kode_pos"			,	
			"telepon_1"			,	
			"telepon_2"			,	
			"telex"				,	
			"facsimile"			,	
			"tanggal_masuk_kerja",	
			"tanggal_bayar"		,	
			"frek_bayar"		,	
		]

		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_refi_pekerjaan, 
			delimiter=DELIMITER, quotechar=QUOTECHAR,
			cron_id=cron_id, cron_obj=cron_obj,
			context=context)
		
		if isinstance(i, dict):
			self.create(cr, uid, i, context=context )
			cr.commit()
			return

		# move csv_file to processed folder
		done = ftp_utils.done_filename(cr, uid, csv_file, context=context)
		shutil.move(csv_file, done)

		data = {
			'date_start' : context.get('date_start',False),
			'date_end' : time.strftime('%Y-%m-%d %H:%M:%S'),
			'input_file' : csv_file,
			'total_records' : i,
			'notes'	: '%s moved to %s' % (csv_file, done),
		}
		self.create(cr, uid, data, context=context )
		cr.commit()

		return 



	###########################################################
	# read the CSV into refi keluarga
	###########################################################
	def insert_refi_keluarga(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data keluarga refi')
		ftp_utils = ftp.ftp_utils()
		import_refi_keluarga = self.pool.get('reliance.import_refi_keluarga')


		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import REFI Partner Keluarga")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import REFI Partner Keluarga") )

		fields_map = [
			"no_debitur"		,
			"no_urut"			,
			"nama"				,
			"tgl_lahir"			,
			"hubungan"			,
			"jenis_kelamin"		,
			"pendidikan"		,
			"profesi"			,
		]


		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_refi_keluarga, 
			delimiter=DELIMITER, quotechar=QUOTECHAR,
			cron_id=cron_id, cron_obj=cron_obj,
			context=context)
		
		if isinstance(i, dict):
			self.create(cr, uid, i, context=context )
			cr.commit()
			return


		# move csv_file to processed folder
		done = ftp_utils.done_filename(cr, uid, csv_file, context=context)
		shutil.move(csv_file, done)

		data = {
			'date_start' : context.get('date_start',False),
			'date_end' : time.strftime('%Y-%m-%d %H:%M:%S'),
			'input_file' : csv_file,
			'total_records' : i,
			'notes'	: '%s moved to %s' % (csv_file, done),
		}
		self.create(cr, uid, data, context=context )
		cr.commit()

		return 




	###########################################################
	# read the CSV into refi statement
	###########################################################
	def insert_refi_statement(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data statement refi')
		ftp_utils = ftp.ftp_utils()
		import_refi_statement = self.pool.get('reliance.import_refi_statement')

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import REFI Partner Statement")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import REFI Partner Statement") )

		fields_map = [
			"no_debitur"						,
			"bulan_tahun_survey"				,
			"time_deps_saving_account"			,
			"vehicle"							,
			"jml_kendaraan"						,
			"properties"						,
			"jml_rumah"							,
			"others_aktiva_lainnya"				,
			"mortagage_loan_inst"				,
			"mortgage_loan_inst_balance"		,
			"renting"							,
			"car_credit"						,
			"car_credit_balance"				,
			"credit_card"						,
			"credit_card_balance"				,
			"credit_line"						,
			"credit_line_balance"				,
			"monthly_expenditure"				,
			"monthly_expenditure_balance"		,
			"mortgage_loan_int"					,
			"mortgage_loan_int_balance_equity"	,
			"other"								,
			"other_balance_equity_net_income"	,
			"spouse_income"						,
			"other_income"						,
		]


		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_refi_statement, 
			delimiter=DELIMITER, quotechar=QUOTECHAR,
			cron_id=cron_id, cron_obj=cron_obj,
			context=context)
		
		if isinstance(i, dict):
			self.create(cr, uid, i, context=context )
			cr.commit()
			return

		# move csv_file to processed folder
		done = ftp_utils.done_filename(cr, uid, csv_file, context=context)
		shutil.move(csv_file, done)

		data = {
			'date_start' : context.get('date_start',False),
			'date_end' : time.strftime('%Y-%m-%d %H:%M:%S'),
			'input_file' : csv_file,
			'total_records' : i,
			'notes'	: '%s moved to %s' % (csv_file, done),
		}
		self.create(cr, uid, data, context=context )
		cr.commit()

		return 




	###########################################################
	# read the CSV into refi kontrak
	###########################################################
	def insert_refi_kontrak(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data kontrak refi')
		ftp_utils = ftp.ftp_utils()
		import_refi_kontrak = self.pool.get('reliance.import_refi_kontrak')

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import REFI Partner Kontrak")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import REFI Partner Kontrak") )

		fields_map = [
			"contract_number"	,
			"customer_no"		,
			"customer_name"		,
			"product"			,
			"asset_name"		,
			"outstanding"		,
			"next_installment"	,
			"pass_due"			,
			"maturity_date"		,
		]

		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_refi_kontrak, 
			delimiter=DELIMITER, quotechar=QUOTECHAR,
			cron_id=cron_id, cron_obj=cron_obj,
			context=context)
		
		if isinstance(i, dict):
			self.create(cr, uid, i, context=context )
			cr.commit()
			return

		# move csv_file to processed folder
		done = ftp_utils.done_filename(cr, uid, csv_file, context=context)
		shutil.move(csv_file, done)

		data = {
			'date_start' : context.get('date_start',False),
			'date_end' : time.strftime('%Y-%m-%d %H:%M:%S'),
			'input_file' : csv_file,
			'total_records' : i,
			'notes'	: '%s moved to %s' % (csv_file, done),
		}
		self.create(cr, uid, data, context=context )
		cr.commit()

		return 



