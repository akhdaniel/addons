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
		'name'			: fields.char('Name', select=1, required=True),
		'date_start' 	: fields.date('Start Date', select=1, required=True),
		'date_end' 		: fields.date('End Date', select=1, required=True),
		'criteria'		: fields.text('Criteria'),
		# 'campaign_partner_ids' : fields.one2many('reliance.campaign_partner','campaign_id','Parnter', ondelete="cascade"),
		'partner_ids' 	: fields.many2many(
					'res.partner', 	# 'other.object.name' dengan siapa dia many2many
					'reliance_campaign_partner',     # 'relation object'
					'campaign_id',            # 'actual.object.id' in relation table
					'partner_id',           # 'other.object.id' in relation table
					'Matched Partner',              # 'Field Name'
					required=True),
	}

