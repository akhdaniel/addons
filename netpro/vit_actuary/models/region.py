from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_region(osv.osv):
    _name = 'netpro.region'
    _columns = {
        'name': fields.char('Name'),
        'description': fields.text('Description'),
        'allowed': fields.boolean('Allowed'),
    }
netpro_region()