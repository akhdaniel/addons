from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
import ftp_utils as ftp
import io
import base64

_logger = logging.getLogger(__name__)

class import_zip_health(osv.osv):
	_name 		= "reliance.import_zip_health"
	_columns 	= {
		'date_import'			: 	fields.datetime("Import Date"),
		'date_processed'		: 	fields.datetime("Processed Date"),

		'zip_health_polis'		: 	fields.binary('Polis ZIP File', required=True),
		'zip_health_peserta'	: 	fields.binary('Peserta ZIP File', required=True),
		'zip_health_limit'		: 	fields.binary('Limit ZIP File', required=True),

		'is_imported' 			: 	fields.boolean("File Saved?", select=1),
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

		notes = ''

		for import_zip_ls in self.browse(cr, uid, ids, context=context):
			polis_files = self.process_polis( cr, uid,  base64.decodestring(import_zip_ls.zip_health_polis))
			peserta_files = self.process_peserta(  cr, uid, base64.decodestring(import_zip_ls.zip_health_peserta))
			limit_files = self.process_limit(  cr, uid, base64.decodestring(import_zip_ls.zip_health_limit))

		self.write(cr, uid, ids, {
			'date_processed': time.strftime("%Y-%m-%d"),
			'is_imported'	: True,
			'notes'			: ",".join(polis_files+peserta_files+limit_files)  
		} , context=context)

		return True

	def process_polis(self, cr, uid,  zip_health_polis, context=None):
		ftp_health_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_health_folder')
		ftp_utils = ftp.ftp_utils()
		health_polis = io.BytesIO(zip_health_polis)
		files = ftp_utils.unzip(health_polis, ftp_health_folder )
		return files

	def process_peserta(self, cr, uid,  zip_health_peserta, context=None):
		ftp_health_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_health_folder')
		ftp_utils = ftp.ftp_utils()
		health_peserta = io.BytesIO(zip_health_peserta)
		files = ftp_utils.unzip(health_peserta, ftp_health_folder )
		return  files

	def process_limit(self, cr, uid,  zip_health_limit, context=None):
		ftp_health_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_health_folder')
		ftp_utils = ftp.ftp_utils()
		health_limit = io.BytesIO(zip_health_limit)
		files = ftp_utils.unzip(health_limit, ftp_health_folder )
		return files
