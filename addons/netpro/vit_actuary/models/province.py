from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_province(osv.osv):
    _name = 'netpro.province'
    _columns = {
        'name': fields.char('Name'),
        'country_id': fields.many2one('res.country', 'Country'),
    }
netpro_province()