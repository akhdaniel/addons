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
		'is_imported' 			: 		fields.boolean("Imported to Partner?", select=1),
		"notes"					:		fields.char("Notes"),	
	}