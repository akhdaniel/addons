from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class program(osv.osv):
	_name 		= "anggaran.program"
	_columns 	= {
		'name'      : fields.text('Nama'),
		'code'      : fields.char('Kode'),
		'kebijakan_id' : fields.many2one('anggaran.kebijakan', 'Kebijakan', required=True),
	}

