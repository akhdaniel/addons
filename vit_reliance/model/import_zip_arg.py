from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class import_zip_arg(osv.osv):
	_name 		= "reliance.import_zip_arg"
	_columns 	= {
		'date_import'			: 	fields.datetime("Import Date"),
		'date_processed'		: 	fields.datetime("Processed Date"),

		'zip_arg_polis'			: 	fields.binary('Polis ZIP File', required=True),
		'zip_arg_risk'			: 	fields.binary('Polis Risk ZIP File', required=True),

		'is_imported' 			: 	fields.boolean("Imported to Partner?", select=1),
		"notes"					:	fields.char("Notes"),
		'user_id'				: 	fields.many2one('res.users', 'User')

	}

	_defaults = {
		'date_import'   : lambda *a : time.strftime("%Y-%m-%d %H:%M:%S") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
	}
