from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
import zipfile,os.path
# import glob
# import csv
import shutil
import ftp_utils as ftp

_logger = logging.getLogger(__name__)
DELIMITER="\t"
QUOTECHAR='"'

class import_ftp_ls(osv.osv):
	_name 		= "reliance.import_ftp_ls"
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
		_logger.warning('running FTP LS cron_process')
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

		ftp_ls_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_ls_folder')
		ftp_utils.check_done_folder(ftp_ls_folder)

		if context==None:
			context={}
		context.update({'date_start':time.strftime('%Y-%m-%d %H:%M:%S')})


		# search and extract ZIP and move zip to done folder
		# zip_files = glob.glob(ftp_ls_folder + '/*.zip')
		zip_files = ftp_utils.insensitive_glob(ftp_ls_folder + '/*.zip')

		for f in zip_files:
			if zipfile.is_zipfile(f):
				ftp_utils.unzip(f, ftp_ls_folder)
				done = ftp_utils.done_filename(cr, uid, f, context=context)
				shutil.move(f, done)
			else:
				_logger.error('wrong zip file')

		# search CSV
		# csv_files = glob.glob(ftp_ls_folder + '/*.csv')
		csv_files = ftp_utils.insensitive_glob(ftp_ls_folder + '/*.csv')

		for csv_file in csv_files:
			if csv_file.upper().find('CUST') != -1:
				self.insert_ls_customer(cr, uid, csv_file, context=context)
			elif csv_file.upper().find('CASH') != -1:
				self.insert_ls_cash(cr, uid, csv_file, context=context)
			elif csv_file.upper().find('STOCK') != -1:
				self.insert_ls_stock(cr, uid, csv_file, context=context)
		return 

	###########################################################
	# read the CSV into ls partner
	###########################################################
	def insert_ls_customer(self, cr, uid, csv_file, context=None):

		_logger.warning('importing csv data insert_ls_customer')
		ftp_utils = ftp.ftp_utils()
		import_ls = self.pool.get('reliance.import_ls')

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import LS Cust to Partner")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import LS Cust to Partner") )

		fields_map = [
			"client_id"				,
			"client_sid"			,
			"client_name"			,
			"place_birth"			,
			"date_birth"			,
			"cr_address"			,
			"cr_city"				,
			"cr_country"			,
			"cr_zip"				,
			"id_card_type"			,
			"id_card"				,
			"id_card_expire_date"	,
			"npwp"					,
			"nationality"			,
			"marital_status"		,
			"phone"					,
			"cellular"				,
			"fax"					,
			"couplenames"			,
			"email"					,
			"education"				,
			"religion"				,
			"mother_name"			,
			"mothers_maiden_name"	,
			"title"					,
			"organization"			,
			"original_location"		,
			"occupation"			,
			"occupation_desc"		,
			"company_name"			,
			"client_sid2"			,
			"company_address"		,
			"company_city"			,
			"company_country"		,
			"company_description"	,
			"company_zip"			,
			"company_phone"			,
			"company_fax"			,
			"source_of_fund"		,
			"source_of_fund_desc"	,
			"gross_income_per_year"	,
			"house_status"			,
			"registered"			,
			"void"					,
		]

		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_ls, 
			delimiter=DELIMITER, quotechar=QUOTECHAR,
			cron_id=cron_id,
			cron_obj=cron_obj,
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
		return 

	###########################################################
	# read the CSV into ls cash
	###########################################################
	def insert_ls_cash(self, cr, uid, csv_file, context=None):
		
		_logger.warning('importing csv data insert_ls_cash')
		ftp_utils = ftp.ftp_utils()
		import_ls_cash = self.pool.get('reliance.import_ls_cash')

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import LS Cash to Partner Cash")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import LS Cash to Partner Cash") )


		fields_map = [
			"client_id"		,
			"date"			,
			"cash_on_hand"	,
			"saldo_t1"		,
			"saldo_t2"		,
		]
		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_ls_cash, 
			delimiter=DELIMITER, quotechar=QUOTECHAR,
			cron_id=cron_id,
			cron_obj=cron_obj,
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

		return 


	###########################################################
	# read the CSV into ls stock
	###########################################################
	def insert_ls_stock(self, cr, uid, csv_file, context=None):

		_logger.warning('importing csv data insert_ls_cash')
		ftp_utils = ftp.ftp_utils()

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import LS Stock to Partner Stock")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import LS Stock to Partner Stock") )


		import_ls_stock = self.pool.get('reliance.import_ls_stock')
		fields_map = [
			"date"				,
			"client_id"			,
			"stock_id"			,
			"stock_name"		,
			"avg_price"			,
			"close_price"		,
			"balance"			,
			"lpp"				,
			"stock_avg_value"	,
			"market_value"		,
			"stock_type"		,
			"sharesperlot"		,
		]
		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_ls_stock, 
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
			'notes'	: 'moved to %s' % (done),
		}
		self.create(cr, uid, data, context=context )

		return 
