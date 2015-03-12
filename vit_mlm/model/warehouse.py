from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class warehouse(osv.osv):
	_name 		= "stock.warehouse"
	_inherit 	= "stock.warehouse"
	_columns 	= {
		'state_id' 	: fields.related('partner_id', 'state_id' , type="many2one", 
			relation="res.country.state", string="State", store=True),

		'city' 	: fields.related('partner_id', 'city' , type="char", 
			relation="res.partner", string="City", 
			store=True,
			#store={'partner_id': (lambda self, cr, uid, ids, c={}: ids, ['street', 'city', 'state_id'], 50)} 
		),
		
		'street' 	: fields.related('partner_id', 'street' , type="char", 
			relation="res.partner", string="Street", store=True),		

		'phone' 	: fields.related('partner_id', 'phone' , type="char", 
			relation="res.partner", string="Phone", store=True),

		'bbm' 	: fields.related('partner_id', 'bbm' , type="char", 
			relation="res.partner", string="BBM", store=True),

	}