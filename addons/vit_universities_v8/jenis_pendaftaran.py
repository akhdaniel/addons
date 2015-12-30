from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class jenis_pendaftaran(osv.osv):
	_name 		= "akademik.jenis_pendaftaran"
	_columns 	= {
		'name'	: fields.char('Nama'),
		'code'	: fields.char('Kode'),
		'code_dikti'	: fields.char('Kode DIKTI'),
	}