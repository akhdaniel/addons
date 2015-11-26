from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mata_anggaran_kegiatan(osv.osv):
    _name = "anggaran.mata_anggaran_kegiatan"
    _description = 'Description'
    _columns = {
        'name'				:fields.char('', size=64, required=False, readonly=False),
        'code'				:fields.char('', size=64, required=False, readonly=False),
        'rka_kegiatan_id' 	:fields.many2one('anggaran.rka_kegiatan', 'RKA Kegiatan'),
        'unit_id' 			:fields.many2one('anggaran.unit', 'unit'),
        'cost_type_id'		:fields.many2one('anggaran.cost_type', 'Cost type'),
    }
