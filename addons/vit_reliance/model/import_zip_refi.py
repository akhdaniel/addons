from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class import_zip_refi(osv.osv):
	_name 		= "reliance.import_zip_refi"
	_columns 	= {
		'date_import'			: 	fields.datetime("Import Date"),
		'date_processed'		: 	fields.datetime("Processed Date"),

		'zip_refi_customer'		: 	fields.binary('Customer ZIP File', required=True),
		'zip_refi_pekerjaan'	: 	fields.binary('Pekerjaan ZIP File', required=True),
		'zip_refi_keluarga'		: 	fields.binary('Keluarga ZIP File', required=True),
		'zip_refi_statement'	: 	fields.binary('Statement ZIP File', required=True),
		'zip_refi_kontrak'		: 	fields.binary('Kontrak ZIP File', required=True),

		'is_imported' 			: 	fields.boolean("Imported to Partner?", select=1),
		"notes"					:	fields.char("Notes"),	

		'user_id'				: 	fields.many2one('res.users', 'User')
	}
	_defaults = {
		'date_import'   : lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
	}
