from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class cost_type(osv.osv):
    _name = "anggaran.cost_type"
    _columns = {
        'nama'		:fields.char('', size=64, required=True, readonly=False),
        'code'		:fields.char('', size=64, required=True, readonly=False),
    }

