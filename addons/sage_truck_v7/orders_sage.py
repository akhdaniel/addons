from osv import fields, osv, orm


class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
		res=super(sale_order,self)._prepare_invoice(cr, uid, order, lines, context=context)
		res['pricing_per']=order.pricing_per
		return res
	
    _columns = {
	
		'pricing_per': fields.char('Pricing Period', size=64, select=True, readonly=True, states={'draft':[('readonly',False)]}),
	
	 
	}
sale_order()

class sale_order_line(osv.osv):
	_name = 'sale.order.line'
	_inherit ='sale.order.line'
	def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
		res=super(sale_order_line,self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
		res['location']=line.location
		res['truck_numb']=line.truck_numb
		return res
		
	_columns = {
		'truck_numb': fields.char('Truck Number', size=20, required=True),
		'location':fields.char('Location', size=64, required=True),
	 }
sale_order_line()


class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice" 
    
    _columns = {
	
		'pricing_per': fields.char('Pricing Period', size=64, select=True, readonly=True, states={'draft':[('readonly',False)]}),
		
		
    }
account_invoice()


class account_invoice_line(osv.osv):
	 _name = "account.invoice.line"
	 _inherit = "account.invoice.line"
	 
	 _columns = {
	
		'truck_numb': fields.char('Truck Number', size=64, required=True),

		'location':fields.char('Location', size=64, required=True),
		
		
    } 
	 
	 
account_invoice_line()
