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
DELIMITER="\t"
QUOTECHAR='"'

class import_ftp_arg(osv.osv):
	_name 		= "reliance.import_ftp_arg"
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
		_logger.warning('running FTP ARG cron_process')
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

		ftp_arg_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_arg_folder')

		ftp_utils.check_done_folder(ftp_arg_folder)

		if context==None:
			context={}
		context.update({'date_start':time.strftime('%Y-%m-%d %H:%M:%S')})


		# search and extract ZIP and move zip to done folder
		zip_files = ftp_utils.insensitive_glob(ftp_arg_folder + '/*.zip')

		for f in zip_files:
			if zipfile.is_zipfile(f):
				ftp_utils.unzip(f, ftp_arg_folder)
				done = ftp_utils.done_filename(cr, uid, f, context=context)
				shutil.move(f, done)
			else:
				_logger.error('wrong zip file')

		# search CSV
		# csv_files = glob.glob(ftp_arg_folder + '/*.csv')
		csv_files = ftp_utils.insensitive_glob(ftp_arg_folder + '/*.csv')

		for csv_file in csv_files:
			if csv_file.upper().find('POLIS') != -1:
				self.insert_arg_polis(cr, uid, csv_file, context=context)

			elif csv_file.upper().find('RISK') != -1:
				self.insert_arg_risk(cr, uid, csv_file, context=context)

		return 


	###########################################################
	# read the CSV into ls partner
	###########################################################
	def insert_arg_polis(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data polis arg')
		ftp_utils = ftp.ftp_utils()
		import_arg = self.pool.get('reliance.import_arg')

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import ARG to Partner")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import ARG to Partner") )

		fields_map = [
			"policy_no"			,	
			"product_class"		,	
			"subclass"			,	
			"eff_date"			,	
			"exp_date"			,	
			"company_code"		,	
			"company_name"		,	
			"company_type"		,	
			"marketing_code"	,	
			"marketing_name"	,	
			"cust_code"			,	
			"cust_name"			,	
			"cust_fullname"		,	
			"qq"				,	
			"cust_cp"			,	
			"cust_addr_1"		,	
			"cust_addr_2"		,	
			"cust_city"			,	
			"cust_postal_code"	,	
			"cust_province"		,	
			"cust_country_name"	,	
			"status_policy"		,	
			"source_of_business",	
		]
		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_arg, 
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
	# read the CSV into ls cash
	###########################################################
	def insert_arg_risk(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data risk arg')
		ftp_utils = ftp.ftp_utils()
		import_arg_polis_risk = self.pool.get('reliance.import_arg_polis_risk')

		cron_obj = self.pool.get('ir.cron')
		cron_id = cron_obj.search(cr, uid,
			[('name','=', "Auto Import ARG to Polis Risk")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import ARG to Polis Risk") )

		fields_map = [
			"policy_no"					,
			"asset_description"			,
			"total_premi"				,
			"total_nilai_pertanggungan"	,
		]
		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_arg_polis_risk, 
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



