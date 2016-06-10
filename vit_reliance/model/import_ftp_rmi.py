from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
import zipfile,os.path
# import glob
import shutil
import ftp_utils as ftp

_logger = logging.getLogger(__name__)
DELIMITER=","
QUOTECHAR='"'

class import_ftp_rmi(osv.osv):
	_name 		= "reliance.import_ftp_rmi"
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
		_logger.warning('running FTP RMI cron_process')
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

		ftp_rmi_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_rmi_folder')
		ftp_utils.check_done_folder(ftp_rmi_folder)

		if context==None:
			context={}
		context.update({'date_start':time.strftime('%Y-%m-%d %H:%M:%S')})


		# search and extract ZIP and move zip to done folder
		# zip_files = glob.glob(ftp_rmi_folder + '/*.zip')
		zip_files = ftp_utils.insensitive_glob(ftp_rmi_folder + '/*.zip')

		for f in zip_files:
			if zipfile.is_zipfile(f):
				ftp_utils.unzip(f, ftp_rmi_folder)
				done = ftp_utils.done_filename(cr, uid, f, context=context)
				shutil.move(f, done)
			else:
				_logger.error('wrong zip file')

		# search CSV
		# csv_files = glob.glob(ftp_rmi_folder + '/*.csv')
		csv_files = ftp_utils.insensitive_glob(ftp_rmi_folder + '/*.csv')

		for csv_file in csv_files:
			if csv_file.upper().find('CUSTOMER') != -1:
				self.insert_rmi_customer(cr, uid, csv_file, context=context)

			elif csv_file.upper().find('HOLDING') != -1:
				self.insert_rmi_product_holding(cr, uid, csv_file, context=context)

		return 


	###########################################################
	# read the CSV into rmi partner
	###########################################################
	def insert_rmi_customer(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data insert_rmi_customer')
		ftp_utils = ftp.ftp_utils()
		import_rmi = self.pool.get('reliance.import_rmi')

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import RMI Partner")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import RMI Partner") )

		fields_map = [
			"no"						,
			"sid"						,
			"nama"						,
			"jenis_kelamin"				,
			"alamat_ktp"				,
			"no_ktp_siup"				,
			"propinsi"					,
			"kota"						,
			"kode_pos"					,
			"negara"					,
			"agama"						,
			"tempat_lahir"				,
			"tanggal_lahir"				,
			"nomor_tlp"					,
			"alamat_surat_menyurat"		,
			"propinsi_surat_menyurat"	,
			"kota_surat_menyurat"		,
			"kode_pos_surat_menyurat"	,
			"negara_surat_menyurat"		,
			"pendidikan_terakhir"		,
			"fax"						,
			"telpon"					,
			"email"						,
			"handphone"					,
			"ahli_waris"				,
			"hubungan_dengan_ahli_waris",
			"pekerjaan"					,
			"gaji_pertahun"				,
			"alasan_berinvestasi"		,
			"kewarganegaraan"			,
		]
		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_rmi, 
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
	# read the CSV into rmi cash
	###########################################################
	def insert_rmi_product_holding(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data import_rmi_product_holding')
		ftp_utils = ftp.ftp_utils()
		import_rmi_product_holding = self.pool.get('reliance.import_rmi_product_holding')

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import RMI Product Holding Partner")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import RMI Product Holding Partner") )

		fields_map = [
			"no"						,
			"sid"						,
			"nama_investor"				,
			"product_id"				,
			"product_name"				,
			"unit_penyertaan"			,
			"nab_saat_beli"				,
			"nab_sampai_hari_ini"		,
			"nominal_investasi_awal"	,
			"nominal_investasi_akhir"	,
			"profit_capital_loss"		,
		]

		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_rmi_product_holding, 
			delimiter=DELIMITER, quotechar=QUOTECHAR,
			cron_id=cron_id, cron_obj=cron_obj,
			context=context)
		
		if isinstance(i, dict):
			self.create(cr, uid, i, context=context )
			cr.commit()
			return
			
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



