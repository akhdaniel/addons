from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_term_condition(osv.osv):
    _name = 'netpro.term_condition'
    _columns = {
        'tc_id': fields.char('TC ID'),
        'name': fields.text('TC Name'),
    }
netpro_term_condition()