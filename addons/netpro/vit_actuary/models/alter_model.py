from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class res_users(osv.osv):
	_name = 'res.users'
	_inherit = 'res.users'
	_columns = {
		'tpa_id' 		: fields.many2one('netpro.tpa', 'TPA'),
	}
res_users()