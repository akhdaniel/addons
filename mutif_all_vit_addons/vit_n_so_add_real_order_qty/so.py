from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc


class sale_order_line(osv.osv):

	_name = 'sale.order.line'
	_inherit = "sale.order.line"
	


	# def _qty_product(self, cr, uid, ids, field_name, arg, context):
	# 	res = {}
 # 		for so in self.browse(cr, uid, ids, context=context):
 # 			if so.real_order_qty == 0:
 # 				so.product_uom_qty
 # 				res[so.id] = so.product_uom_qty
 #  		return res

  	def _qty_product(self, cr, uid, ids, field_name, arg, context):
		res = {}
 		for so in self.browse(cr, uid, ids, context=context):
			so.product_uom_qty
			res[so.id] = so.product_uom_qty
  		return res


	_columns = {
		'real_order_qty': fields.function(_qty_product, string='Real Order Quantity', store=True, type='float'),
	}

