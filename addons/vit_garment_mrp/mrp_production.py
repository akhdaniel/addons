from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mrp_production(osv.osv):
    _name         = "mrp.production"
    _inherit      = "mrp.production"

    _columns      ={
        'move_created_ids3': fields.one2many('stock.move', 'production_id', 'Grade B Products',
            domain=[('state','in', ('done', 'cancel')),('name','ilike','grade b')], 
            readonly=True, 
            states={'draft':[('readonly',False)]}),

        'move_created_ids4': fields.one2many('stock.move', 'production_id', 'Waste Products',
            domain=[('state','in', ('done', 'cancel')), ('name','ilike','waste')], 
            readonly=True, 
            states={'draft':[('readonly',False)]}),

    }
