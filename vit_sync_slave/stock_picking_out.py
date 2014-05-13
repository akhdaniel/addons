import logging
from osv import osv, fields
import time
from datetime import datetime
from openerp import netsvc
import openerp.tools
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class stock_picking_out(osv.osv):
	_inherit = 'stock.picking.out'
	_columns = {
		'is_exported': fields.boolean('Is Exported?'),
		'exported_date': fields.datetime('Export Date')
	}
	_defaults = {
		'is_exported': False 
	}
stock_picking_out()
