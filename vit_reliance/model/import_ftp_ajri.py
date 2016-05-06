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

class import_ftp_ajri(osv.osv):
	_name 		= "reliance.import_ftp_ajri"
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
		_logger.warning('running FTP AJRI cron_process')
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

		ftp_ajri_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_ajri_folder')

		ftp_utils.check_done_folder(ftp_ajri_folder)

		if context==None:
			context={}
		context.update({'date_start':time.strftime('%Y-%m-%d %H:%M:%S')})


		# search and extract ZIP and move zip to done folder
		zip_files = glob.glob(ftp_ajri_folder + '/*.zip')

		for f in zip_files:
			if zipfile.is_zipfile(f):
				ftp_utils.unzip(f, ftp_ajri_folder)
				done = ftp_utils.done_filename(cr, uid, f, context=context)
				shutil.move(f, done)
			else:
				_logger.error('wrong zip file')

		# search CSV
		csv_files = glob.glob(ftp_ajri_folder + '/*.csv')

		for csv_file in csv_files:
			if csv_file.upper().find('AJRI') != -1:
				self.insert_ajri_customer(cr, uid, csv_file, context=context)


		return 


	###########################################################
	# read the CSV into ls partner
	###########################################################
	def insert_ajri_customer(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data polis arg')
		ftp_utils = ftp.ftp_utils()
		import_ajri = self.pool.get('reliance.import_ajri')

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
						"nomor_polis"			:	row[0],
						"nama_pemegang"			:	row[1],
						"nomor_partisipan"		:	row[2],
						"nama_partisipan"		:	row[3],
						"produk"				:	row[4],
						"tgl_lahir"				:	row[5],
						"tgl_mulai"				:	row[6],
						"tgl_selesai"			:	row[7],
						"status"				:	row[8],
						"up"					:	row[9],
						"total_premi"			:	row[10],
						"status_klaim"			:	row[11],
						"status_bayar"			:	row[12],
						"tgl_bayar"				:	row[13],
						"klaim_disetujui"		:	row[14],					
						"source"				: 	csv_file,
					}
					import_ajri.create(cr, uid, data, context=context)

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



