from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_product_plan_base(osv.osv):
    _name = 'netpro.product_plan_base'
    _columns = {
        'pplan': fields.char('PPlan'),
        'name': fields.char('Name'),
        'created_by_id' : fields.many2one('res.users', 'Creator', readonly=True),
        'tpa_id' : fields.many2one('netpro.tpa', 'TPA'),
    }
netpro_product_plan_base()