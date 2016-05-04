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

_logger = logging.getLogger(__name__)

DONE_FOLDER = '/done'

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
		ftp_ls_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_ls_folder')
		# ftp_arg_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_arg_folder')
		# ftp_ajri_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_ajri_folder')
		# ftp_refi_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_refi_folder')
		# ftp_rmi_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_rmi_folder')
		# ftp_health_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_health_folder')

		if context==None:
			context={}
		context.update({'date_start':time.strftime('%Y-%m-%d %H:%M:%S')})


		# check done folders
		if not os.path.exists(ftp_ls_folder + DONE_FOLDER):
			os.makedirs(ftp_ls_folder + DONE_FOLDER)

		# search and extract ZIP and move zip to done folder
		zip_files = glob.glob(ftp_ls_folder + '/*.zip')

		for f in zip_files:
			if zipfile.is_zipfile(f):
				self.unzip(f, ftp_ls_folder)
				done = os.path.dirname(f) + DONE_FOLDER
				shutil.move(f, done)
			else:
				_logger.error('wrong zip file')

		# search CSV
		csv_files = glob.glob(ftp_ls_folder + '/*.csv')

		for csv_file in csv_files:
			if csv_file.upper().find('CUST') != -1:
				self.insert_ls_customer(cr, uid, csv_file, context=context)
			elif csv_file.upper().find('CASH') != -1:
				self.insert_ls_cash(cr, uid, csv_file, context=context)
			elif csv_file.upper().find('STOCK') != -1:
				self.insert_ls_stock(cr, uid, csv_file, context=context)
		return 

	###########################################################
	# unzip the uploaded file
	###########################################################
	def unzip(self, source_filename, dest_dir):
		files = []

		with zipfile.ZipFile(source_filename) as zf:
			for member in zf.infolist():
				words = member.filename.split('/')
				path = dest_dir
				for word in words[:-1]:
					drive, word = os.path.splitdrive(word)
					head, word = os.path.split(word)
					if word in (os.curdir, os.pardir, ''): continue
					path = os.path.join(path, word)
				zf.extract(member, path)
				files.append(member.filename)
				
		return files

	###########################################################
	# read the CSV into ls partner
	###########################################################
	def insert_ls_customer(self, cr, uid, csv_file, context=None):
		import_ls = self.pool.get('reliance.import_ls')


		with open( csv_file, 'rb') as csvfile:
			spamreader = csv.reader(csvfile)
			i = 0
			for row in spamreader:
				if i==0:
					print "header",row 
					# data = self.map_fields(cr, uid, 'reliance.import_ls', row)
					i = i+1
					continue

				data = {
					"client_id"				: row[0],
					"client_sid"			: row[1],
					"client_name"			: row[2],
					"place_birth"			: row[3],
					"date_birth"			: row[4],
					"cr_address"			: row[5],
					"cr_city"				: row[6],
					"cr_country"			: row[7],
					"cr_zip"				: row[8],
					"id_card_type"			: row[9],
					"id_card"				: row[10],
					"id_card_expire_date"	: row[11],
					"npwp"					: row[12],
					"nationality"			: row[13],
					"marital_status"		: row[14],
					"phone"					: row[15],
					"cellular"				: row[16],
					"fax"					: row[17],
					"couplenames"			: row[18],
					"email"					: row[19],
					"education"				: row[20],
					"religion"				: row[21],
					"mother_name"			: row[22],
					"mothers_maiden_name"	: row[23],
					"title"					: row[24],
					"organization"			: row[25],
					"original_location"		: row[26],
					"occupation"			: row[27],
					"occupation_desc"		: row[28],
					"company_name"			: row[29],
					"client_sid2"			: row[30],
					"company_address"		: row[31],
					"company_city"			: row[32],
					"company_country"		: row[33],
					"company_description"	: row[34],
					"company_zip"			: row[35],
					"company_phone"			: row[36],
					"company_fax"			: row[37],
					"source_of_fund"		: row[38],
					"source_of_fund_desc"	: row[39],
					"gross_income_per_year"	: row[40],
					"house_status"			: row[41],
					"registered"			: row[42],
					"void"					: row[43],				
				}
				import_ls.create(cr, uid, data, context=context)

				i = i +1
		# move csv_file to processed folder
		done = os.path.dirname(csv_file) + DONE_FOLDER
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
		import_ls_cash = self.pool.get('reliance.import_ls_cash')
		with open( csv_file, 'rb') as csvfile:
			spamreader = csv.reader(csvfile)
			i = 0
			for row in spamreader:
				if i==0:
					print "header",row 
					i = i+1
					continue

				data = {
					"client_id"		:	row[0],
					"date"			:	row[1],
					"cash_on_hand"	:	row[2],
					"saldo_t1"		:	row[3],
					"saldo_t2"		:	row[4],
				}
				import_ls_cash.create(cr, uid, data, context=context)

				i = i +1


		done = os.path.dirname(csv_file) + DONE_FOLDER
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
		import_ls_stock = self.pool.get('reliance.import_ls_stock')
		with open( csv_file, 'rb') as csvfile:
			spamreader = csv.reader(csvfile)
			i = 0
			for row in spamreader:
				if i==0:
					print "header",row 
					i = i+1
					continue

				data = {
					"date"				:	row[0],
					"client_id"			:	row[1],
					"stock_id"			:	row[2],
					"stock_name"		:	row[3],
					"avg_price"			:	row[4],
					"close_price"		:	row[5],
					"balance"			:	row[6],
					"lpp"				:	row[7],
					"stock_avg_value"	:	row[8],
					"market_value"		:	row[9],
					"stock_type"		:	row[10],
					"sharesperlot"		:	row[11],
				}
				import_ls_stock.create(cr, uid, data, context=context)

				i = i +1

		done = os.path.dirname(csv_file) + DONE_FOLDER
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





