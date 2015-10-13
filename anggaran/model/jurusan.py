from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class jurusan(osv.osv):
	_name 		= "anggaran.jurusan"
	_columns 	= {
		'code'        : fields.char('Kode'),
		'name'        : fields.char('Nama'),
		'jurusan_id'  : fields.many2one('anggaran.jurusan', 'Jurusan', required=False),
		'fakultas_id' : fields.many2one('anggaran.fakultas', 'Fakultas', required=True)
	}