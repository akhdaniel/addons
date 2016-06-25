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
DELIMITER=';'
QUOTECHAR='"'

class import_ftp_health(osv.osv):
	_name 		= "reliance.import_ftp_health"
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
		_logger.warning('running FTP HEALTH cron_process')
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

		ftp_health_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_health_folder')

		ftp_utils.check_done_folder(ftp_health_folder)

		if context==None:
			context={}
		context.update({'date_start':time.strftime('%Y-%m-%d %H:%M:%S')})


		# search and extract ZIP and move zip to done folder
		# zip_files = glob.glob(ftp_health_folder + '/*.zip')
		zip_files = ftp_utils.insensitive_glob(ftp_health_folder + '/*.zip')

		for f in zip_files:
			if zipfile.is_zipfile(f):
				ftp_utils.unzip(f, ftp_health_folder)
				done = ftp_utils.done_filename(cr, uid, f, context=context)
				shutil.move(f, done)
			else:
				_logger.error('wrong zip file')

		# search CSV
		# csv_files = glob.glob(ftp_health_folder + '/*.csv')
		csv_files = ftp_utils.insensitive_glob(ftp_health_folder + '/*.csv')

		for csv_file in csv_files:
			if csv_file.upper().find('POLIS') != -1:
				self.insert_health_polis(cr, uid, csv_file, context=context)

			elif csv_file.upper().find('PESERTA') != -1:
				self.insert_health_peserta(cr, uid, csv_file, context=context)

			elif csv_file.upper().find('LIMIT') != -1:
				self.insert_health_limit(cr, uid, csv_file, context=context)
		return 


	###########################################################
	# read the CSV into ls partner
	###########################################################
	def insert_health_polis(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data polis health')
		ftp_utils = ftp.ftp_utils()
		import_health_polis = self.pool.get('reliance.import_health_polis')

		cron_obj = self.pool.get('ir.cron') 
		cron_id = cron_obj.search(cr, uid, 
			[('name','=', "Auto Import Health Polis Partner")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import Health Polis Partner") ) 

		fields_map = [
			"policyno"		,
			"clientname"	,
			"phone"			,
			"fax"			,
			"email"			,
			"product"		,
			"effdt"			,
			"expdt"			,
		]
		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_health_polis, 
			delimiter=DELIMITER, quotechar=QUOTECHAR, 
			cron_id=cron_id,
			cron_obj=cron_obj,
			context=context)

		#resume cron
		
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
		_logger.warning('import_health_ftp: insert_health_polis done')

		return 

	###########################################################
	# read the CSV into ls cash
	###########################################################
	def insert_health_peserta(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data peserta health')
		ftp_utils = ftp.ftp_utils()
		import_health_peserta = self.pool.get('reliance.import_health_peserta')

		cron_obj = self.pool.get('ir.cron') 
		cron_id = cron_obj.search(cr, uid, 
			[('name','=', "Auto Import Health Peserta Partner")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import Health Peserta Partner") ) 

		fields_map = [
			"policyno"		,
			"memberid"		,
			"membername"	,
			"sex"			,
			"birthdate"		,
			"status"		,
			"relationship"	,
		]

		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_health_peserta, 
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
		_logger.warning('import_health_ftp: insert_health_peserta done')

		return 


	###########################################################
	# read the CSV into ls stock
	# deactivate Import Healt Limit jobs
	# and activate after finished
	###########################################################
	def insert_health_limit(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data limit health')
		ftp_utils = ftp.ftp_utils()
		import_health_limit = self.pool.get('reliance.import_health_limit')

		cron_obj = self.pool.get('ir.cron') 
		cron_id = cron_obj.search(cr, uid, 
			[('name','=', "Auto Import Health Partner Limit")], context=context)
		if not cron_id:
			raise osv.except_osv(_('error'),_("no cron job Auto Import Health Partner Limit") ) 



		fields_map = [
			"policyno"		,
			"membid"		,
			"manfaat"		,
			"limit"			,
		]


		i = ftp_utils.read_csv_insert(cr, uid, csv_file, fields_map, import_health_limit, 
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
			'notes'	: 'moved to %s' % (done),
		}
		self.create(cr, uid, data, context=context )
		cr.commit()
		_logger.warning('import_health_ftp: insert_health_limit done')

		return 


