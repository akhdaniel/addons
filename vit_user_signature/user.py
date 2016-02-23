from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class res_partner(osv.osv):
	_inherit 		= "res.partner"
	_columns 	= {
		'signature' : fields.binary('Signature')
	}