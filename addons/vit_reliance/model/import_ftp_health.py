from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
import zipfile,os.path
import glob
import csv
import shutil
import ftp_utils as ftp

_logger = logging.getLogger(__name__)


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
		zip_files = glob.glob(ftp_health_folder + '/*.zip')

		for f in zip_files:
			if zipfile.is_zipfile(f):
				ftp_utils.unzip(f, ftp_health_folder)
				done = ftp_utils.done_filename(cr, uid, f, context=context)
				shutil.move(f, done)
			else:
				_logger.error('wrong zip file')

		# search CSV
		csv_files = glob.glob(ftp_health_folder + '/*.csv')

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

		try:
			with open( csv_file, 'rb') as csvfile:
				spamreader = csv.reader(csvfile,delimiter=';', quotechar='"')
				i = 0
				for row in spamreader:
					if i==0:
						_logger.warning("header")
						_logger.warning(row)
						# data = self.map_fields(cr, uid, 'reliance.import_health', row)
						i = i+1
						continue

					data = {
						"policyno"		: row[0],
						"clientname"	: row[1],
						"phone"			: row[2],
						"fax"			: row[3],
						"email"			: row[4],
						"product"		: row[5],
						"effdt"			: row[6],
						"expdt"			: row[7],				
						"source"		: csv_file,
					}
					import_health_polis.create(cr, uid, data, context=context)

					i = i +1
		except IOError as e:
			data = {
				'notes': "I/O error({0}): {1}".format(e.errno, e.strerror),
				'date_start' : context.get('date_start',False),
				'date_end' 	: time.strftime('%Y-%m-%d %H:%M:%S'),
				'input_file' : csv_file,
			}
			self.create(cr, uid, data, context=context )
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
	def insert_health_peserta(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data peserta health')
		ftp_utils = ftp.ftp_utils()
		import_health_peserta = self.pool.get('reliance.import_health_peserta')
		
		try:	
			with open( csv_file, 'rb') as csvfile:
				spamreader = csv.reader(csvfile,delimiter=';', quotechar='"')
				i = 0
				for row in spamreader:
					if i==0:
						_logger.warning("header")
						_logger.warning(row)
						i = i+1
						continue

					data = {
						"policyno"		:	row[0],
						"memberid"		:	row[1],
						"membername"	:	row[2],
						"sex"			:	row[3],
						"birthdate"		:	row[4],
						"status"		:	row[5],
						"relationship"	:	row[6],			
						"source"		: 	csv_file,
					}
					import_health_peserta.create(cr, uid, data, context=context)

					i = i +1
		except IOError as e:
			data = {
				'notes': "I/O error({0}): {1}".format(e.errno, e.strerror),
				'date_start' : context.get('date_start',False),
				'date_end' 	: time.strftime('%Y-%m-%d %H:%M:%S'),
				'input_file' : csv_file,
			}
			self.create(cr, uid, data, context=context )
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
	def insert_health_limit(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data limit health')
		ftp_utils = ftp.ftp_utils()
		import_health_limit = self.pool.get('reliance.import_health_limit')

		try:	
			with open( csv_file, 'rb') as csvfile:
				spamreader = csv.reader(csvfile,delimiter=';', quotechar='"')
				i = 0
				for row in spamreader:
					if i==0:
						_logger.warning("header")
						_logger.warning(row)
						i = i+1
						continue

					data = {
						"policyno"		:	row[0],
						"membid"		:	row[1],
						"manfaat"		:	row[2],
						"limit"			:	row[3],
						"source"		: 	csv_file,
					}
					import_health_limit.create(cr, uid, data, context=context)

					i = i +1
		except IOError as e:
			data = {
				'notes': "I/O error({0}): {1}".format(e.errno, e.strerror),
				'date_start' : context.get('date_start',False),
				'date_end' 	: time.strftime('%Y-%m-%d %H:%M:%S'),
				'input_file' : csv_file,
			}
			self.create(cr, uid, data, context=context )
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


