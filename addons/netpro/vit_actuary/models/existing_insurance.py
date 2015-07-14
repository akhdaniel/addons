from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class existing_insurance(osv.osv):
    _name = 'netpro.existing_insurance'
    _columns = {
        'name': fields.char('Name'),
        'code': fields.char('Code'),
        'is_allowed': fields.boolean('Allowed'),

    }
existing_insurance()