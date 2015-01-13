from osv import osv, fields
import platform
import os
import csv
import logging
import time

_logger = logging.getLogger(__name__)


class stock_in(osv.osv):
	_inherit = "stock.picking"
	# _name = "stock.picking"

	_columns = {
	'makloon_id':fields.many2one('vit.makloon.order', 'Makloon Order'),
	# 'makloon_order' : fields.char('Makloon Order'),
	}

stock_in()