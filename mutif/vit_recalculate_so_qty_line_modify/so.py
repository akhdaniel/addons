from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"


    def recalculate(self, cr, uid, ids, context=None):
    	res = super(sale_order, self).recalculate(cr, uid, ids,context={})
       	for so in self.browse(cr, uid, ids, context=context):
			for line in so.order_line:
				id = line.id
				can_be_ordered = line.real_max_order
				cr.execute('update sale_order_line set product_uom_qty=%d where id=%d' %(can_be_ordered,id))
        return res
        
sale_order()

