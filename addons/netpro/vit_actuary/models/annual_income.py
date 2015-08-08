from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_annual_income(osv.osv):
    _name = 'netpro.annual_income'
    _columns = {
        'name': fields.char('Name'),
        'code': fields.text('Code'),
        'description': fields.text('Description'),
        'created_by_id' : fields.many2one('res.users', 'Creator', readonly=True),
    }
netpro_annual_income()