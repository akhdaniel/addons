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

class import_zip_ajri(osv.osv):
	_name 		= "reliance.import_zip_ajri"
	_columns 	= {
		'date_import'			: 	fields.date("Import Date"),
		'date_processed'		: 	fields.date("Processed Date"),
		'zip_ajri_customer'		:	fields.binary('AJRI Cust. File (ZIP)'),
		'is_imported' 			: 	fields.boolean("Saved to AJRI FTP Folder?", select=1),
		"notes"				:	fields.char("Notes"),
		"test"				:	fields.char("Test"),
	}
	_defaults = {
		'date_import'   : lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
	}

	def button_process(self, cr, uid, ids, context=None):
		return self.actual_process(cr, uid, ids, context=context)

	def actual_process(self, cr, uid, ids, context=None):

		notes = ''

		for import_zip_ajri in self.browse(cr, uid, ids, context=context):
			cust_files = self.process_cust( cr, uid,  base64.decodestring(import_zip_ajri.zip_ajri_customer))

		self.write(cr, uid, ids, {
			'date_processed': time.strftime("%Y-%m-%d"),
			'is_imported'	: True,
			'notes'			: ",".join(cust_files)  
		} , context=context)

		return True


	def process_cust(self, cr, uid,  zip_ajri_cust, context=None):
		ftp_ajri_folder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_ajri_folder')
		ftp_utils = ftp.ftp_utils()
		ajri_cust = io.BytesIO(zip_ajri_cust)
		return ftp_utils.unzip(ajri_cust, ftp_ajri_folder )

