from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class kebijakan(osv.osv):
	_name 		= "anggaran.kebijakan"
	_columns 	= {
		'name'      : fields.text('Nama'),
		'code'      : fields.char('Kode'),
		'tridharma' : fields.char('Tridharma'),
	}

