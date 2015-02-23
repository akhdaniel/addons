from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mlm_ads(osv.osv):
	_name 		= "mlm.ads"
	_columns 	= {
		'message': fields.text('Message'),
		'image'	 : fields.binary('Image'),
		'url'	 : fields.char('URL'),
		'partner_id': fields.many2one('res.partner', 'Client'),
		'date_start': fields.datetime('Start Date'),
		'date_end': fields.datetime('End Date'),
		'user_id': fields.many2one('res.users', 'Created By')
	}