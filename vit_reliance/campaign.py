from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class reliance_campaign(osv.osv):
	_name 		= "reliance.campaign"
	_columns 	= {
		'name'			: fields.char('Name', select=1),
		'date_start' 	: fields.date('Start Date', select=1),
		'date_end' 		: fields.date('End Date', select=1),
		'campaign_partner_ids' : fields.one2many('reliance.campaign_partner','campaign_id','Parnter', ondelete="cascade"),
	}

class reliance_campaign_partner(osv.osv):
	_name 		= "reliance.campaign_partner"
	_columns 	= {
		'campaign_id'		: fields.many2one('reliance.campaign', 'Campaign'),
		'partner_id'		: fields.many2one('res.partner', 'Partner'),
	}