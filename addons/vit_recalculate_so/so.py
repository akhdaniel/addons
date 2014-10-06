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

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
    	res= super(sale_order, self)._amount_all(cr, uid, ids, field_name, arg, context=context)
    	return res
    
    _columns = {
		'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store = True,
            multi='sums', help="The amount without tax.", track_visibility='always')
	}

    


    def recalculate(self, cr, uid, ids, context=None):
        
        for so in self.browse(cr, uid, ids, context=context):
        	for line in so.order_line:
	        	price = line.product_id.list_price
	        	id = line.id
	        	discount = so.partner_id.discount
	        	qty_available = line.product_id.qty_available
	        	outgoing_qty  = line.product_id.outgoing_qty
	        	virtual_available = line.product_id.virtual_available
	        	
	        	if line.product_uom_qty == 0:
	        		cr.execute('delete from sale_order_line where id = %d' %(id))
	        	else:
	        		cr.execute('update sale_order_line set price_unit=%f, discount=%f, qty_hand=%s, outgoing =%s, forecast=%s  where id=%d' %(price,discount,qty_available,outgoing_qty,virtual_available,id))
       

        self.write(cr,uid,ids,{'order_line':[(0,0,{'name':'-'})]},context=context)    		
        

        for so2 in self.browse(cr, uid, ids, context=context):
        	for line in so2.order_line:
	        	id = line.id	
	        	if line.name == "-":
	        		cr.execute('delete from sale_order_line where id = %d' %(id))
	     
        return True
        
sale_order()



