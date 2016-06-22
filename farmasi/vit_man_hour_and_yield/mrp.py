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

    def _get_process_yield(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result      = {}
        y           = 0.00
        for obj in self.browse(cr,uid,ids,context=context):
            if obj.input_qty != 0.0:
                y = (obj.output_qty/obj.input_qty) *100

            result[obj.id] = y
        return result

    _columns = {
        # 'man_hour': fields.function(_get_man_hour, type="float",string='Planned Man of Hour', digits=(16, 4)),
        'man_hour': fields.float('Planned Man of Hour', digits=(16, 4)),
        'actual_man_hour': fields.float('Actual Man of Hours', digits=(16, 4)),
        'result_qty' : fields.float('Result Qty', digits=(16, 2)),
        'yield': fields.function(_get_yield, type="float",string='Yield', digits=(16, 4)),

        'input_qty' : fields.float('Input Qty', digits=(16, 2)),
        'output_qty' : fields.float('Output Qty', digits=(16, 2)),
        'process_uom_id': fields.many2one('product.uom', 'Process UOM'),
        'process_yield': fields.function(_get_process_yield, type="float",string='Process Yield', digits=(16, 4)),

    }

    def action_done(self, cr, uid, ids, context=None):
        super(mrp_production_workcenter_line, self).action_done(cr, uid, ids, context=context)
        wo = self.browse(cr, uid, ids[0], context=context)

        #find next wo in sequence
        wo_ids = self.search(cr, uid, [('production_id','=', wo.production_id.id),
                ('sequence','>', wo.sequence)], limit=1, order='sequence,id', context=context)
        if wo_ids:
			self.write(cr,uid,wo_ids, {'input_qty':wo.output_qty}, context=context)

        return True





class mrp_routing_workcenter(osv.osv):

    _inherit = 'mrp.routing.workcenter'

    _columns={
        'man_hour': fields.related('workcenter_id','man_hour',type='float',string='Man Hour',readonly=True)#float('Man Hour', help="Time in hours for employee",digits=(16,4)),
    }


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    # overwrite fungsi utk generate WO
    def _action_compute_lines(self, cr, uid, ids, properties=None, context=None):
        """ Compute product_lines and workcenter_lines from BoM structure
        @return: product_lines
        """
        
        if properties is None:
            properties = []
        results = []
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids, context=context):
            #unlink product_lines
            prod_line_obj.unlink(cr, SUPERUSER_ID, [line.id for line in production.product_lines], context=context)
            #unlink workcenter_lines
            workcenter_line_obj.unlink(cr, SUPERUSER_ID, [line.id for line in production.workcenter_lines], context=context)

            res = self._prepare_lines(cr, uid, production, properties=properties, context=context)
            results = res[0] # product_lines
            results2 = res[1] # workcenter_lines

            # reset product_lines in production order
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            #import pdb;pdb.set_trace()
            #reset workcenter_lines in production order
            for line in results2:
                # overwrite fungsi utk generate WO
                if 'workcenter_id' in line:
                    # wc_obj = self.pool.get('mrp.workcenter')
                    # man_hour = wc_obj.browse(cr,uid,line['workcenter_id']).man_hour
                    if production.bom_id.workcenter_lines:
                        man_hour = 0
                        for man in production.bom_id.workcenter_lines:
                            if man.workcenter_operation_id.workcenter_id.id == line ['workcenter_id']:
                                man_hour = man.man_hour
                                break
                        line['man_hour'] = man_hour
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line, context)
        return results