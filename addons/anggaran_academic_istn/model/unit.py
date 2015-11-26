from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class unit(osv.osv):
	_name 		= "anggaran.unit"
	_columns 	= {
		'code':	fields.char('Kode', required=True, select=True),
		'name':	fields.char('Nama', required=True),
		'fakultas_id' : fields.many2one('anggaran.fakultas', 'Fakultas'),
		'jurusan_id'  : fields.many2one('anggaran.jurusan', 'Jurusan'),
		'company_id'  : fields.many2one('res.company', 'Universitas', required=True),
	}