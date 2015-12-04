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

    # def _fname(self, cr, uid, ids, field, arg, context=None):
    #     results = {}
    #     for bom in self.browse(cr, uif, ids, context=context):
    #         product = bom.product_id
    #         qty = product.
    #         results[bom.id] = 
    #     # return harus berupa dictionary dengan key id session
    #     # contoh kalau 3 records:
    #     # {
    #     #      1 : 50.8,
    #     #      2 : 25.5,
    #     #      3 : 10.0
    #     # }
    #     return results    

    _columns = {
        'qty_onhand': fields.float('Qty Avail')
        # 'qty_onhand': fields.function(_fgetqty, type='float', string="Qty Avail"),

    }
    _defaults = {
        'component_type': lambda *a: 'raw_material',
    }