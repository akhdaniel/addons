from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mrp_bom_line(osv.osv):
    """
    Defines bills of material for a product.
    """
    _name = 'mrp.bom.line'
    _inherit = 'mrp.bom.line'

    _columns = {
        'qty_onhand': fields.related('product_id', 'virtual_available' , type="float", 
            relation="product.product", string="Qty Available", store=True)

    }
    _defaults = {
        'component_type': lambda *a: 'raw_material',
    }