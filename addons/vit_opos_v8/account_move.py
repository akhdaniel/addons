from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

class account_move(osv.osv):
	_inherit = "account.move"
	
	_columns = {
		'shop_id' : fields.many2one('stock.warehouse','Shop Warehouse')
	}
