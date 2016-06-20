import time
import datetime
import openerp.addons.decimal_precision as dp
from collections import OrderedDict
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import float_compare, float_is_zero
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID
from openerp.addons.product import _common

import logging
_logger = logging.getLogger(__name__)

class parent(osv.osv):
	_inherit = 'product.product'

	_columns = {
				'parent_id':fields.many2one('product.product', 'Parent Product')
	}


	# def get_parent(self, cr, uid, ids):
	# 	sql = 'UPDATE product_product pp set parent_id=(select id from product_product where default_code=substr(pp.default_code,1,6) limit 1) where length(default_code=10'

	# return sql