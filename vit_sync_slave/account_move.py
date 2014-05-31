import logging
from osv import osv, fields
import time
from datetime import datetime
from openerp import netsvc
import openerp.tools
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class account_move(osv.osv):
	_inherit = "account.move"
	_columns = {
		'is_exported'	: fields.boolean('Is Exported?'),
		'exported_date'	: fields.datetime('Export Date'),
		'shop_id'	: fields.integer('Shop')
	}
	
	_defaults = {
		'is_exported': False,
	}

account_move()
