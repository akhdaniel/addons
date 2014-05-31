import logging
from osv import osv, fields
import time
from datetime import datetime
from openerp import netsvc
import openerp.tools
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mail_message(osv.osv):
	_inherit = "mail.message"
	_columns = {
		'is_imported'	: fields.boolean('Is imported?'),
		'imported_date'	: fields.datetime('Export Date')
	}
	_defaults = {
		'is_imported': False 
	}
mail_message()


class account_move(osv.osv):
	_inherit = "account.move"
	_columns = {
		# 'shop_id' 		: fields.integer('Shop_id'),
		'shop_id' : fields.many2one('sale.shop', 'Shop'),
	}

account_move()