from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
import os
import io
import base64

EXTRACT_DIR = '/home'
_logger = logging.getLogger(__name__)

###############################################################
# upload ZIP from web (binary field) => store to /home/reliance/ls/
# reliance.ftp will continue to process these zip files
###############################################################
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
		files = self.pool.get('reliance.ftp').unzip(ls_customer, EXTRACT_DIR )
		return 

	def process_cash(self, cr, uid,  zip_ls_cash, context=None):
		ls_cash = io.BytesIO(zip_ls_cash)
		files = self.pool.get('reliance.ftp').unzip(ls_cash, EXTRACT_DIR )
		return 

	def process_stock(self, cr, uid,  zip_ls_stock, context=None):
		ls_stock = io.BytesIO(zip_ls_stock)
		files = self.pool.get('reliance.ftp').unzip(ls_stock, EXTRACT_DIR )
		return

