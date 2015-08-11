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
from openerp import models, fields, api
from openerp.osv import fields
from openerp.osv import osv
import time
import datetime
from openerp.tools.translate import _
from dateutil import parser

class mrp_production_workcenter_line(osv.osv):
    _name = 'mrp.production.workcenter.line'
    _inherit = 'mrp.production.workcenter.line'
   
    _columns = {
        'man_hour_standard'      : fields.float('Man Hour Standard',digits=(16, 2)),  
        'man_number_standard'    : fields.integer('Man Number Standard'),
        'man_hour_actual'        : fields.float('Man Hour Actual',digits=(16, 2)),  
        'man_number_actual'      : fields.integer('Man Number Actual'),
        'man_hour_diff'          : fields.float('Man Hour Diff',digits=(16, 2)),  
        'man_number_diff'        : fields.integer('Man Number Diff'),
        'wo_machine_hour_lines'  : fields.one2many('vit_pharmacy_wo_hour.wo_machine_hour', 'mpwcl_id', 'Wo Machine Hour'),
    }

    @api.onchange('man_hour_actual','man_number_actual') # if these fields are changed, call method
    def on_change_nett_diff(self): 
        self.man_hour_diff = self.man_hour_standard - self.man_hour_actual
        self.man_number_diff = self.man_number_standard - self.man_number_actual

    # def write(self, cr, uid, ids, vals, context=None):

    #     oper_objs = self.browse(cr, uid, ids, context=context)[0]
    #     vals['man_hour_diff'] = oper_objs.man_hour_standard - oper_objs.man_hour_actual
    #     vals['man_number_diff'] = oper_objs.man_number_standard - oper_objs.man_number_actual

    #     return super(mrp_production_workcenter_line, self).write(cr, uid, ids, vals, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
