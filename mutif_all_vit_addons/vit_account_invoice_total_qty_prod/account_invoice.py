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

class account_invoice(osv.osv):

    _name = "account.invoice"
    _inherit = "account.invoice"
    _description = 'Invoice'
    
    def _qty_product(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'qty_total': 0.0,        
            } 
            val = 0.0
           
            for line in invoice.invoice_line:
                if line.product_id.name is not None:
                    val += line.quantity
                    continue
           
            res[invoice.id]['qty_total'] = val
        return res

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    _columns = {  
        'qty_total': fields.function(_qty_product, digits_compute= dp.get_precision('Account'), string=' Product Quantity Total', store={
                'account.invoice.line': (_get_invoice_line, None, 10),
            }, multi="sums", help="Product Quantity Total"),
    
    }    