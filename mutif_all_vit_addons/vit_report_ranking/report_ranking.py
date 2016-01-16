# -*- coding: utf-8 -*-

######################################################################
#
#  Note: Program metadata is available in /__init__.py
#
######################################################################

from openerp.osv import fields, osv
import tools
import time
import openerp.addons.decimal_precision as dp


class vit_customer_order_ranking(osv.osv):
	_name = 'vit.customer.order.ranking'

	_columns = {
		'partner_id' : fields.many2one('res.partner','Customer', readonly=True),
		'total_qty': fields.float('Total Qty'),
		'total_price': fields.float('Total Price'),
		'date_start' : fields.date('Date Start'),
		'date_end'   : fields.date('Date End'),		
	 }

vit_customer_order_ranking()

class vit_customer_seller_ranking(osv.osv):
	_name = 'vit.customer.seller.ranking'

	_columns = {
		'partner_id' : fields.many2one('res.partner','Customer', readonly=True),
		'total_qty': fields.float('Total Qty'),
		'total_price': fields.float('Total Price'),
		'date_start' : fields.date('Date Start'),
		'date_end'   : fields.date('Date End'),			
	 }

vit_customer_seller_ranking()

class vit_supplier1_ranking(osv.osv):
	_name = 'vit.supplier1.ranking'

	_columns = {
		'partner_id' : fields.many2one('res.partner','Supplier', readonly=True),
		'total_qty': fields.float('Total Qty'),
		'total_price': fields.float('Total Price'),
		'date_start' : fields.date('Date Start'),
		'date_end'   : fields.date('Date End'),			
	 }


vit_supplier1_ranking()


class vit_makloon1_ranking(osv.osv):
	_name = 'vit.makloon1.ranking'

	_columns = {
		'partner_id' : fields.many2one('res.partner','Makloon', readonly=True),
		'total_qty': fields.float('Total Qty'),
		'total_price': fields.float('Total Price'),
		'date_start' : fields.date('Date Start'),
		'date_end'   : fields.date('Date End'),			
	 }


vit_makloon1_ranking()


class vit_product_order1_ranking(osv.osv):
	_name = 'vit.product.order1.ranking'	

	_columns = {
		'product_id' : fields.many2one('product.product','Product', readonly=True),
		'total_qty_order': fields.float('Total Qty Order'),
		'date_start' : fields.date('Date Start'),
		'date_end'   : fields.date('Date End'),	
	 }


vit_product_order1_ranking()

class vit_product_seller1_ranking(osv.osv):
	_name = 'vit.product.seller1.ranking'	

	_columns = {
		'product_id' : fields.many2one('product.product','Product', readonly=True),
		'total_qty_seller': fields.float('Total Qty Order'),
		'date_start' : fields.date('Date Start'),
		'date_end'   : fields.date('Date End'),	
	 }

vit_product_seller1_ranking()