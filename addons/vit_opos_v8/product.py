from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _


class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
    	'property_stock_valuation_account_id': fields.related(
    		'categ_id',
    		'property_stock_valuation_account_id', 
    		type='many2one', 
    		relation='account.account', 
    		string='Category Stock Valuation Account', 
    		store=False,
    		readonly=True
    	),
        'property_expense_account_id': fields.related(
            'categ_id',
            'property_account_expense_categ', 
            type='many2one', 
            relation='account.account', 
            string='Category Expense Account', 
            store=False,
            readonly=True
        ),
        'property_income_account_id': fields.related(
            'categ_id',
            'property_account_income_categ', 
            type='many2one', 
            relation='account.account', 
            string='Category Income Account', 
            store=False,
            readonly=True
        ),
        'x_ppn' : fields.float("X PPN"),
        'barcode': fields.char("Barcode"),


	}

product_product()
