# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import pytz
from openerp import SUPERUSER_ID
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

class sale_order(osv.osv):

    _name = "sale.order"
    _inherit = "sale.order"
    _description = "Sales Order"

    
    def _qty_total_real_max_order(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in ids:
            val = 0.0
            for line in self.browse(cr, uid, i, context=context).order_line:
               if  line.real_max_order > 0.00:
                    val += line.real_max_order
                    continue
            res[i] = val
        return res

    def _qty_total_price_max_order(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in ids:
            val = 0.0
            for line in self.browse(cr, uid, i, context=context).order_line:
               if  line.price_max_order > 0.00:
                    val+= line.price_max_order
                    continue
            res[i] = val
        return res

    # def create( self, cr, uid, ids, context):
    #     for so in self.browse(cr, uid, ids, context=context):
    #         for line in so.order_line:
    #             price = line.product_id.list_price
    #             id = line.id
    #             discount = so.partner_id.discount
    #             qty_available = line.product_id.qty_available
    #             outgoing_qty  = line.product_id.outgoing_qty
    #             virtual_available = line.product_id.virtual_available
    #             max_order = qty_available + outgoing_qty
       
    #     return super(sale_order, self).create(cr, uid, ids, context=context)
    

    _columns = {

        'qty_total_real_max_order': fields.function(_qty_total_real_max_order, digits_compute= dp.get_precision('Account'), string='Total That Can Be Ordered',readonly=True),

        'qty_total_price_max_order': fields.function(_qty_total_price_max_order, digits_compute= dp.get_precision('Account'), string='The Total Price Can Be Ordered',readonly=True),

    }    

sale_order()





 # def _amount_price(self, cr, uid, ids, field_name, arg, context=None):

 #        cur_obj = self.pool.get('res.currency')
 #        res = {}
 #        for order in self.browse(cr, uid, ids, context=context):
 #            res[order.id] = {
 #                'qty_total_real_max_order': 0.0,
 #                'qty_total_price_max_order': 0.0,    
 #            }
 #            val = val1 = val2= 0.0
 #            cur = order.pricelist_id.currency_id


 #            for line in order.order_line:
 #                if line.product_id.name is not None:
 #                    val2+= line.product_uom_qty
 #                    continue
           
 #            for line in order.order_line:
 #                if  line.real_max_order > 0.00:
 #                    val += line.real_max_order
 #                    # import pdb;pdb.set_trace()
 #                    continue

 #            for line in order.order_line:
 #                if  line.price_max_order > 0.00:
 #                    # import pdb;pdb.set_trace()
 #                    val1+= line.price_max_order
 #                    continue

 #            res[order.id]['qty_total_real_max_order'] = cur_obj.round(cr, uid, cur, val)
 #            res[order.id]['qty_total_price_max_order'] = cur_obj.round(cr, uid, cur, val1)
 #            res[order.id]['qty_total'] = cur_obj.round(cr, uid, cur, val2)

 #        return res


 #    def _get_order2(self, cr, uid, ids, context=None):
 #        result = {}
 #        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
 #            result[line.order_id.id] = True
 #        return result.keys()


# _columns = {

#         'qty_total_real_max_order': fields.function(_amount_price, digits_compute= dp.get_precision('Account'), string='Total That Can Be Ordered',
#          store={
#                 'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
#                 'sale.order.line': (_get_order2, None, 10),
#             }, multi="sums", help="Total That Can Be Ordered"),

#         'qty_total_price_max_order': fields.function(_amount_price, digits_compute= dp.get_precision('Account'), string='The Total Price Can Be Ordered',
#          store={
#                 'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
#                 'sale.order.line': (_get_order2, None, 10),
#             }, multi="sums", help="Price Total Max Order"),

#     }    