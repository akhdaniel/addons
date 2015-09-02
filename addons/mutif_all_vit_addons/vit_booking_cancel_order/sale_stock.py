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
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _
import pytz
from openerp import SUPERUSER_ID


class sale_order(osv.osv):
    _inherit = "sale.order"

    # def action_button_confirm(self, cr, uid, ids, context=None):
    #     res = super(sale_order, self).action_button_confirm(cr, uid, ids,context={})
    #     return res
    
    def action_cancel(self, cr, uid, ids, context=None):
        
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        proc_obj = self.pool.get('procurement.order')
        for sale in self.browse(cr, uid, ids, context=context):
            for pick in sale.picking_ids:
                self.action_cancel_on_picking_ids(cr, uid, pick, context) 
                # import pdb;pdb.set_trace()
        res = super(sale_order, self).action_cancel(cr, uid, ids,context={})
        return res


    def action_cancel_on_picking_ids(self, cr, uid, pick, context=None):
        """ Changes picking state to cancel.
        @return: True
        """
        # import pdb;pdb.set_trace()
        picking_obj = self.pool.get('stock.picking')
        ids = pick.id
        for pick in picking_obj.browse(cr, uid, [ids], context=context):
            ids2 = [move.id for move in pick.move_lines]
            self.pool.get('stock.move').action_cancel(cr, uid, ids2, context)
        picking_obj.write(cr, uid, ids, {'state': 'cancel', 'invoice_state': 'none'})
        return True


   