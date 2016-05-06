from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

CAMPAIGN_STATES =[('draft','Draft'),('open','Open'), ('done','Done')]

class reliance_campaign(osv.osv):
	_name 		= "reliance.campaign"
	_columns 	= {
		'name'					: fields.char('Name', select=1, required=True),
		'date_start' 			: fields.date('Start Date', select=1, required=True),
		'date_end' 				: fields.date('End Date', select=1, required=True),

		'criteria_age_start' 	: fields.integer('Start Age'),
		'criteria_age_end' 		: fields.integer('To Age'),
		'criteria_product_ids'	: fields.many2many(
					'product.product', 	# 'other.object.name' dengan siapa dia many2many
					'campaign_product',     # 'relation object'
					'campaign_id',            # 'actual.object.id' in relation table
					'product_id',           # 'other.object.id' in relation table
					'Have Product(s)',              # 'Field Name'
					required=False),


		'partner_ids' 	: fields.many2many(
					'res.partner', 	# 'other.object.name' dengan siapa dia many2many
					'reliance_campaign_partner',     # 'relation object'
					'campaign_id',            # 'actual.object.id' in relation table
					'partner_id',           # 'other.object.id' in relation table
					'Matched Partner',              # 'Field Name'
					required=False,
					),
		'state'			: fields.selection(CAMPAIGN_STATES,'Status',readonly=True,required=True),
		'user_id'		: fields.many2one('res.users', 'Created By'),

		# 'distribution_list_id' : fields.many2one('distribution.list', 'Distribution List'),
	}

	_defaults = {
		'date_start'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'date_end'     		: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'			: lambda obj, cr, uid, context: uid,
		'name'				: lambda obj, cr, uid, context: '/',		
		'state'       		: CAMPAIGN_STATES[0][0],
	}

	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':CAMPAIGN_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':CAMPAIGN_STATES[1][0]},context=context)
		
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':CAMPAIGN_STATES[2][0]},context=context)

	def action_reload(self,cr,uid,ids,context=None):
		return True

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'reliance.campaign') or '/'
		new_id = super(reliance_campaign, self).create(cr, uid, vals, context=context)
		return new_id

