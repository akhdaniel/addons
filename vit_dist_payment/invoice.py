from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
_logger = logging.getLogger(__name__)

class invoice(osv.osv):
	_name 		= "account.invoice"
	_inherit 	= "account.invoice"
	_columns 	= {'based_route_id'  : fields.related(
        	'partner_id',
        	'based_route_id',
        	type='many2one',
        	store=True,
        	relation='master.based.route', string='Route'),		
	}
