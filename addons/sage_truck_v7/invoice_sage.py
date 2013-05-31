from osv import fields, osv, orm

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice" 
    
    _columns = {
	
		'pricing_per2': fields.char('Pricing Period', size=64, select=True, readonly=True, states={'draft':[('readonly',False)]}),
		
		
    }
account_invoice()
