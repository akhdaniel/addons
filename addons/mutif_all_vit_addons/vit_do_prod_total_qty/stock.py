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
import logging
_logger = logging.getLogger(__name__)
#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking_out(osv.osv):
    _name = "stock.picking.out"
    _inherit = "stock.picking"
    _table = "stock_picking"
    _description = "Delivery Orders"
   
    
    def _qty_product(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            res[move.id] = {
                'qty_total': 0.0,        
            } 
            val = 0.0           
            for line in move.move_lines:
                if line.product_id.name is not None:
                    val += line.product_qty
                    continue
            res[move.id]['qty_total'] = val
            # import pdb;pdb.set_trace()
            self.qty_total_field_write(cr, uid, ids, val, context)
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.move_id.id] = True
        return result.keys()
    

    def qty_total_field_write(self, cr, uid, ids, val, context=None):
        return self.write(cr,uid,ids,{'qty_total_field':val},context)


    _columns = {  
        'qty_total': fields.function(_qty_product, digits_compute= dp.get_precision('Account'), string=' Product Quantity Total' ,multi="sums", help="Product Quantity Total"),
        'qty_total_field' : fields.float('Product Quantity Total'),
    }


stock_picking_out()

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    _description = "Picking List"

    _columns = {  
        'qty_total_field' : fields.float('Product Quantity Total'),
    }