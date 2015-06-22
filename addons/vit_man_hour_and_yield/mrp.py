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
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID
from openerp.addons.product import _common

class mrp_workcenter(osv.osv):
    _inherit = 'mrp.workcenter'


    _columns = {
        'man_hour': fields.float('Man Hour', help="Time in hours for employee",digits=(16,4)),

    }
  
class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    def _get_man_hour(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result              = {}
        routing_obj         = self.pool.get('mrp.routing')
        detail_routing_obj  = self.pool.get('mrp.routing.workcenter')
        man_hour            = 0.00
        for obj in self.browse(cr,uid,ids,context=context):
            #import pdb;pdb.set_trace()
            routing   = obj.production_id.routing_id
            if routing :
                routing_id = routing.id
                if routing_id :
                    routing_workcenter = detail_routing_obj.search(cr,uid,[('routing_id','=',routing_id)],context=context)
                    if routing_workcenter :
                        man_hour = detail_routing_obj.browse(cr,uid,routing_workcenter[0]).man_hour

            result[obj.id] = man_hour
        return result 

    def _get_yield(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result      = {}
        y           = 0.00
        for obj in self.browse(cr,uid,ids,context=context):
            y = (obj.result_qty/obj.qty) *100
            result[obj.id] = y
        return result

    _columns = {
        'man_hour': fields.function(_get_man_hour, type="float",string='Number Man of Hour', digits=(16, 4)),
        'actual_man_hour': fields.float('Actual Man of Hours', digits=(16, 4)),
        'result_qty' : fields.float('Result Qty', digits=(16, 2)),
        'yield': fields.function(_get_yield, type="float",string='Yield', digits=(16, 4)),

    }


class mrp_routing_workcenter(osv.osv):

    _inherit = 'mrp.routing.workcenter'

    _columns={
        'man_hour': fields.float('Man Hour', help="Time in hours for employee",digits=(16,4)),
    }