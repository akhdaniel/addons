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
		zip_files = glob.glob(ftp_rmi_folder + '/*.zip')

		for f in zip_files:
			if zipfile.is_zipfile(f):
				ftp_utils.unzip(f, ftp_rmi_folder)
				done = ftp_utils.done_filename(cr, uid, f, context=context)
				shutil.move(f, done)
			else:
				_logger.error('wrong zip file')

		# search CSV
		csv_files = glob.glob(ftp_rmi_folder + '/*.csv')

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
		_logger.warning('importing csv data polis arg')
		ftp_utils = ftp.ftp_utils()
		import_rmi = self.pool.get('reliance.import_rmi')

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
						"no"						:	row[0],
						"sid"						:	row[1],
						"nama"						:	row[2],
						"jenis_kelamin"				:	row[3],
						"alamat_ktp"				:	row[4],
						"no_ktp_siup"				:	row[5],
						"propinsi"					:	row[6],
						"kota"						:	row[7],
						"kode_pos"					:	row[8],
						"negara"					:	row[9],
						"agama"						:	row[10],
						"tempat_lahir"				:	row[11],
						"tanggal_lahir"				:	row[12],
						"nomor_tlp"					:	row[13],
						"alamat_surat_menyurat"		:	row[14],
						"propinsi_surat_menyurat"	:	row[15],
						"kota_surat_menyurat"		:	row[16],
						"kode_pos_surat_menyurat"	:	row[17],
						"negara_surat_menyurat"		:	row[18],
						"pendidikan_terakhir"		:	row[19],
						"fax"						:	row[20],
						"telpon"					:	row[21],
						"email"						:	row[22],
						"handphone"					:	row[23],
						"ahli_waris"				:	row[24],
						"hubungan_dengan_ahli_waris":	row[25],
						"pekerjaan"					:	row[26],
						"gaji_pertahun"				:	row[27],
						"alasan_berinvestasi"		:	row[28],
						"kewarganegaraan"			:	row[29],						
						"source"					: 	csv_file,
					}
					import_rmi.create(cr, uid, data, context=context)

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
	# read the CSV into rmi cash
	###########################################################
	def insert_rmi_product_holding(self, cr, uid, csv_file, context=None):
		_logger.warning('importing csv data risk arg')
		ftp_utils = ftp.ftp_utils()
		import_rmi_product_holding = self.pool.get('reliance.import_rmi_product_holding')
		
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
						"no"						:	row[0],
						"sid"						:	row[1],
						"nama_investor"				:	row[2],
						"product_id"				:	row[3],
						"product_name"				:	row[4],
						"unit_penyertaan"			:	row[5],
						"nab_saat_beli"				:	row[6],
						"nab_sampai_hari_ini"		:	row[7],
						"nominal_investasi_awal"	:	row[8],
						"nominal_investasi_akhir"	:	row[9],
						"profit_capital_loss"		:	row[10],					
						"source"					: 	csv_file,
					}
					import_rmi_product_holding.create(cr, uid, data, context=context)

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



