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
        'detail_available': fields.related('product_id', 'detail_available' , type="float", 
            relation="product.product", string="Detail Available", store=False),
        'default_product_uom_id': fields.related('product_id', 'uom_id' , type="many2one", 
            relation="product.uom", string="Default UoM", store=False)

    }
    _defaults = {
        'component_type': lambda *a: 'raw_material',
    }