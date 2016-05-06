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
DELIMITER = ','
QUOTECHAR = '"'

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
		zip_files = glob.glob(ftp_arg_folder + '/*.zip')

		for f in zip_files:
			if zipfile.is_zipfile(f):
				ftp_utils.unzip(f, ftp_arg_folder)
				done = ftp_utils.done_filename(cr, uid, f, context=context)
				shutil.move(f, done)
			else:
				_logger.error('wrong zip file')

		# search CSV
		csv_files = glob.glob(ftp_arg_folder + '/*.csv')

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

		try:
			with open( csv_file, 'rb') as csvfile:
				spamreader = csv.reader(csvfile,delimiter= DELIMITER, quotechar=QUOTECHAR)
				i = 0
				for row in spamreader:
					if i==0:
						_logger.warning("header")
						_logger.warning(row)
						i = i+1
						continue

					data = {
						"policy_no"			:	row[0],
						"product_class"		:	row[1],
						"subclass"			:	row[2],
						"eff_date"			:	row[3],
						"exp_date"			:	row[4],
						"company_code"		:	row[5],
						"company_name"		:	row[6],
						"company_type"		:	row[7],
						"marketing_code"	:	row[8],
						"marketing_name"	:	row[9],
						"cust_code"			:	row[10],
						"cust_name"			:	row[11],
						"cust_fullname"		:	row[12],
						"qq"				:	row[13],
						"cust_cp"			:	row[14],
						"cust_addr_1"		:	row[15],
						"cust_addr_2"		:	row[16],
						"cust_city"			:	row[17],
						"cust_postal_code"	:	row[18],
						"cust_province"		:	row[19],
						"cust_country_name"	:	row[20],
						"status_policy"		:	row[21],
						"source_of_business":	row[22],		
						"source"			: 	csv_file,
					}
					import_arg.create(cr, uid, data, context=context)

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
		cr.commit()

		return 

	###########################################################
	# read the CSV into ls cash
	###########################################################
	def insert_arg_risk(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data risk arg')
		ftp_utils = ftp.ftp_utils()
		import_arg_polis_risk = self.pool.get('reliance.import_arg_polis_risk')
		
		try:	
			with open( csv_file, 'rb') as csvfile:
				spamreader = csv.reader(csvfile,delimiter=DELIMITER, quotechar=QUOTECHAR)
				i = 0
				for row in spamreader:
					if i==0:
						_logger.warning("header")
						_logger.warning(row)
						i = i+1
						continue

					data = {
						"policy_no"					:	row[0],
						"asset_description"			:	row[1],
						"total_premi"				:	row[2],
						"total_nilai_pertanggungan"	:	row[3],
						"source"					: 	csv_file,
					}
					import_arg_polis_risk.create(cr, uid, data, context=context)

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

		cr.commit()

		return 



