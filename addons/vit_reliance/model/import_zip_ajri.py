from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class import_zip_ajri(osv.osv):
	_name 		= "reliance.import_zip_ajri"
	_columns 	= {
		'date_import'			: 	fields.date("Import Date"),
		'date_processed'		: 	fields.date("Processed Date"),
		'ajri_customer_file'	:	fields.binary('AJRI Customer File (ZIP)'),
		'is_imported' 			: 	fields.boolean("Imported to Partner?", select=1),
		"notes"					:	fields.char("Notes"),
	}
	_defaults = {
		'date_import'   : lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
	}
	