from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_reason(osv.osv):
	_name = 'netpro.reason'
    _columns = {
        'name': fields.char('Name'),
        'description': fields.text('Description'),
        'type': fields.selection([('H', 'Header'), ('D', 'Detail Purpose')], 'Type'),
        'allowed' : fields.boolean('Allowed'),
    }
