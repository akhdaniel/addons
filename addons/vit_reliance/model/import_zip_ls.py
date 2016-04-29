from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
import zipfile,os.path
import os
import io
import base64
import csv

EXTRACT_DIR = '/tmp'
_logger = logging.getLogger(__name__)

class import_zip_ls(osv.osv):
	_name 		= "reliance.import_zip_ls"
	_rec_name 	= "date_import"

	_columns 	= {
		'date_import'			: 	fields.date("Import Date"),
		'date_processed'		: 	fields.date("Processed Date"),

		'zip_ls_customer'		: 	fields.binary('Customer ZIP File', required=True),
		'zip_ls_cash'			: 	fields.binary('Cash ZIP File', required=True),
		'zip_ls_stock'			: 	fields.binary('Stock ZIP File', required=True),

		'is_imported' 			: 	fields.boolean("Imported to Partner?", select=1),
		"notes"					:	fields.char("Notes"),
		'user_id'				: 	fields.many2one('res.users', 'User')

	}

	_defaults = {
		'date_import'   : lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
	}


	def button_process(self, cr, uid, ids, context=None):
		return self.actual_process(cr, uid, ids, context=context)

	def actual_process(self, cr, uid, ids, context=None):

		for import_zip_ls in self.browse(cr, uid, ids, context=context):
			self.process_customer( cr, uid,  base64.decodestring(import_zip_ls.zip_ls_customer))
			self.process_cash(  cr, uid, base64.decodestring(import_zip_ls.zip_ls_cash))
			self.process_stock(  cr, uid, base64.decodestring(import_zip_ls.zip_ls_stock))

		self.write(cr, uid, ids, {
			'date_processed': time.strftime("%Y-%m-%d"),
			'is_imported'	: True
		} , context=context)

		return True

	def process_customer(self, cr, uid,  zip_ls_customer, context=None):
		ls_customer = io.BytesIO(zip_ls_customer)
		files = self.unzip(ls_customer, EXTRACT_DIR )

		for csv_file in files:
			self.insert_ls_customer(cr, uid, csv_file, context=context)

		return 

	def insert_ls_customer(self, cr, uid, csv_file, context=None):
		import_ls = self.pool.get('reliance.import_ls')
		model_id = self.pool.get('ir.model').search(cr, uid, [('name','=','reliance.import_ls')], context=context)
		fields = self.pool.get('ir.model.fields').search_read(cr, uid, 
			[('model_id','=',model_id[0])], fields=['display_name'], context=context)

		fieldNames = [x['display_name'] for x in fields]
		print "fieldNames",fieldNames

		import pdb; pdb.set_trace()
		with open( os.path.join(EXTRACT_DIR, csv_file) , 'rb') as csvfile:
			spamreader = csv.reader(csvfile)
			i = 0
			for row in spamreader:
				if i==0:
					print "header",row 
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

	def process_cash(self, cr, uid,  zip_ls_cash, context=None):
		return 

	def process_stock(self, cr, uid,  zip_ls_stock, context=None):
		return


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
