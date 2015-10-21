from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

PRODUCT_STATES = [
	('draft','Draft'),
	('open','Confirmed'),
	('approval1','QA Approved'),
	('approval2', 'Accounting Approved'), 
	('sellable','Active'),
	('reject','Reject'),
	('end','End of Lifecycle'),
    ('obsolete','Obsolete'),
]

class product_template(osv.osv):
	_name 		= "product.template"
	_inherit 		= "product.template"
	_columns 	= {
		'state'	: fields.selection(PRODUCT_STATES,'Status',readonly=True,required=True),
	}

	_defaults = {
		'state' : PRODUCT_STATES[0][0],
	}

	def action_draft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':PRODUCT_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':PRODUCT_STATES[1][0]},context=context)
	
	def action_approval1(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':PRODUCT_STATES[2][0]},context=context)
	
	def action_approval2(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':PRODUCT_STATES[3][0]},context=context)
	
	def action_active(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':PRODUCT_STATES[4][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':PRODUCT_STATES[5][0]},context=context)
