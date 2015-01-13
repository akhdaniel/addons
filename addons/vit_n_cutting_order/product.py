from openerp import tools
from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class product_product(osv.osv):
    _inherit = "product.product"
    _description = "Product"
    # _order = 'sort_size asc'

    _columns = {
        # 'master_model_id': fields.many2one('vit.master.type', string = "Type Model"),
        'type_model': fields.char("Type Model"),
    }
