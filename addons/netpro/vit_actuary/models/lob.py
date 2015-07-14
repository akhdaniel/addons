from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_lob(osv.osv):
    _name = 'netpro.lob'
    _columns = {
        'name': fields.char('LOB'),
        'description': fields.text('Description'),
    }
netpro_lob()