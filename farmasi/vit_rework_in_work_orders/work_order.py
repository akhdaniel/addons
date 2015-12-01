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


class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    def _write_origin_internal_move(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result              = {}

        for obj in self.browse(cr,uid,ids,context=context):
            #import pdb;pdb.set_trace()
            moves   = obj.picking_ids
            if moves :
                for ori in moves:
                    int_move_id = ori.picking_id.id
                    self.pool.get('stock.picking').write(cr,uid,int_move_id,{'origin':obj.production_id.name},context=context)

        return result 

    _columns = {
        'picking_ids'   : fields.one2many('stock.picking','workorder_id',string='Internal Move',readonly=True, states={'draft':[('readonly',False)]}),
        'notes'         : fields.text('Notes'),
        'move_ids'      : fields.one2many('stock.move','workorder_id',string='Internal Moves',readonly=True, states={'draft':[('readonly',False)]}),
        'is_origin'     : fields.boolean('Origin'),
    } 



class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    _columns = {
        'workorder_id'  : fields.many2one('mrp.production.workcenter.line',string='Internal Move'),
    } 

class stock_move(osv.osv):
    _inherit = 'stock.move'

    _columns = {
        'workorder_id'  : fields.many2one('mrp.production.workcenter.line',string='Work Orders'),
    }     