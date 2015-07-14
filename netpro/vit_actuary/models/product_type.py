from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_product_type(osv.osv):
    _name = 'netpro.product_type'
    _columns = {
        'name': fields.char('Product Type'),
        'description': fields.text('Description'),
    }
netpro_product_type()
