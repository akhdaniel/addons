from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class gl_notes(osv.osv):
    _name = 'netpro.gl_notes'
    _columns = {
        'name': fields.char('Name'),
        'code': fields.char('Code'),
        'is_allowed': fields.boolean('Allowed'),
        'created_by_id' : fields.many2one('res.users', 'Creator', readonly=True),
        'tpa_id' : fields.many2one('netpro.tpa', 'TPA'),
    }
gl_notes()