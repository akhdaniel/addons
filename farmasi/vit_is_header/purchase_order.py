from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"
    # def wkf_confirm_order(self, cr, uid, ids, context=None):
    # 	ret = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)

    #     todo = []
    #     for po in self.browse(cr, uid, ids, context=context):
    #         if not po.order_line:
    #             raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
    #         for line in po.order_line:
    #             if line.state=='draft':
    #                 todo.append(line.id)        
    #     return ret