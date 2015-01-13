from openerp import tools
from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class product_product(osv.osv):
    _inherit = "product.product"
    _description = "Product"
    # _order = 'sort_size asc'

    _columns = {
        'sort_size': fields.float('Sort Size'),
        'kode_katalog': fields.float('Code'),
        # 'type_product': fields.integer('Type'),
    }
