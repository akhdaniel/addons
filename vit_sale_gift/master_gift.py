from openerp.osv import fields,osv
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class master_gift(osv.osv):
    _name = "vit_sale_gift.master_gift"

    _columns = {
        'name'       : fields.char('Name', required=True),
        'product_id' : fields.many2one('product.product','Bonus Product', required=True),
        'qty'        : fields.float('Bonus Qty', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'multiple'   : fields.boolean('Multiple Apply'),
        'is_active'  : fields.boolean('Active?'),
        'date_from'  : fields.date('Start Date'),
        'date_to'    : fields.date('End Date'),
        'total_qty'  : fields.integer('Total Qty All Condition', help=""),
        'product_condition_ids' : fields.one2many('vit_sale_gift.product_condition','master_gift_id','Products Condition', ondelete="cascade"),
        'categ_condition_ids'   : fields.one2many('vit_sale_gift.categ_condition','master_gift_id','Categories Condition', ondelete="cascade")
    } 

    _defaults = {
        'qty'        : 1,
        'multiple'   : True,
        'is_active'  : True,
        'date_from'  : lambda *a : time.strftime("%Y-%m-%d") ,
        'date_to'    : lambda *a : time.strftime("%Y-%m-%d") ,
    }  



class categ_condition(osv.osv):
    _name         = "vit_sale_gift.categ_condition"
    _columns     = {
        'master_gift_id'    : fields.many2one('vit_sale_gift.master_gift', 'Master Gift'),
        'product_categ_id'  : fields.many2one('product.category', 'Product Categories'),
        'min_qty'           : fields.integer('Minimum Qty'),
    }

class product_condition(osv.osv):
    _name         = "vit_sale_gift.product_condition"
    _columns     = {
        'master_gift_id'    : fields.many2one('vit_sale_gift.master_gift', 'Master Gift'),
        'product_id'        : fields.many2one('product.product', 'Products'),
        'min_qty'           : fields.integer('Minimum Qty'),
    }