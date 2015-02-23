from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mlm_broadcast(osv.osv):
	_name 		= "mlm.broadcast"
	_columns 	= {
		'channel'			: fields.selection([('sms','SMS'),
			('android','Android')],'Channel',readonly=False,required=True),
		'scheduled_date'	: fields.datetime('Scheduled Date'),
		'message'			: fields.text('Message'),
	}