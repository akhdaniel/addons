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
from openerp.tools import float_compare, float_is_zero
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID
from openerp.addons.product import _common


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    _columns = {
        'split': fields.boolean('Split ?'),
    }    

    _defaults = {
        'split' : False,
    }
     


class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    _columns = {
        'split': fields.boolean('Split ?'),
    }    

    _defaults = {
        'split' : False,
    }

    def split_work_orders(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        result      = {}
        for obj in self.browse(cr,uid,ids,context=context):            
            routing       = obj.production_id.routing_id
            mo_id         = obj.production_id.id
            
            if routing :
                routing_id = routing.id
                if routing_id :
                    # cari wo dengan MO yang sama dan sequence sama dengan atau lebih besar
                    wo_ids   = self.search(cr,uid,[('production_id','=',mo_id),('sequence','>=',obj.sequence)],context=context)
                    if wo_ids :
                        qty_split = obj.qty / 2
                        for old_wo in wo_ids:
                            wo_duplicate = self.copy(cr, uid, old_wo, default=None, context=None)
                            self.write(cr,uid,wo_duplicate,{'qty':qty_split,'split':True},context=context)
                            self.write(cr,uid,old_wo,{'qty':qty_split,'split':True},context=context)       
                        self.pool.get('mrp.production').write(cr,uid,mo_id,{'product_qty':qty_split*2,'split':True},context=context)
        return True
