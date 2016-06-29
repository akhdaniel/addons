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

class parent_template(osv.osv):
	_inherit = 'product.template'


	# def init(self, cr, context=None):
	# 	cr.execute("update product_template pp set \
	# 				parent_id=(select id from product_template where \
	#               	name=substr(pp.name,1,position(',' in pp.name )-1) limit 1) \
	#               	where  position(',' in pp.name )>0")


	_columns = {
				'parent_id':fields.many2one('product.template', 'Parent Product')
	}