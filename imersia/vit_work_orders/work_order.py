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

    def _get_partner(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        partner_obj     = self.pool.get('res.partner')
        order_list_obj  = self.pool.get('sale.order.list')
        partner = False
        for obj in self.browse(cr,uid,ids,context=context):
            source_doc  = obj.production_id.origin
            if source_doc:
                sol_id   = order_list_obj.search(cr,uid,[('name','=',source_doc)], context=context)
                if sol_id :
                    partner = order_list_obj.browse(cr,uid,sol_id[0]).partner_id.id

            result[obj.id] = partner
        return result   


    def _get_product_to_consume_cylindrical(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        mrp_obj     = self.pool.get('mrp.production')
        move_obj  = self.pool.get('stock.move')
        is_cylindrical = False
        for obj in self.browse(cr,uid,ids,context=context):
            move_lines  = obj.production_id.move_lines
            if move_lines:
                line_ids = []
                for line in move_lines:
                    if line.product_category == 'cylindrical':
                        line_ids.append(line.id)
                        is_cylindrical = True
                result[obj.id] = line_ids
            self.write(cr,uid,obj.id,{'is_cylindrical': is_cylindrical},context=context)
        return result

    def _get_product_to_consume_cubic(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        mrp_obj     = self.pool.get('mrp.production')
        move_obj  = self.pool.get('stock.move')
        is_cubic = False
        for obj in self.browse(cr,uid,ids,context=context):
            move_lines  = obj.production_id.move_lines
            if move_lines:
                line_ids = []
                for line in move_lines:
                    if line.product_category == 'cubic':
                        line_ids.append(line.id)
                        is_cubic = True
                result[obj.id] = line_ids
            self.write(cr,uid,obj.id,{'is_cubic': is_cubic},context=context)
        return result

    def _get_product_to_consume_volume(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        mrp_obj     = self.pool.get('mrp.production')
        move_obj  = self.pool.get('stock.move')
        is_volume = False
        for obj in self.browse(cr,uid,ids,context=context):
            move_lines  = obj.production_id.move_lines
            if move_lines:
                line_ids = []
                for line in move_lines:
                    if line.product_category == 'volume':
                        line_ids.append(line.id)
                        is_volume = True
                result[obj.id] = line_ids
            self.write(cr,uid,obj.id,{'is_volume': is_volume},context=context)
        return result        



    def _get_product_to_produce_cylindrical(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        mrp_obj     = self.pool.get('mrp.production')
        move_obj  = self.pool.get('stock.move')
        is_cylindrical2 = False
        for obj in self.browse(cr,uid,ids,context=context):
            move_lines  = obj.production_id.move_created_ids
            if move_lines:
                line_ids = []
                for line in move_lines:
                    if line.product_category == 'cylindrical':
                        line_ids.append(line.id)
                        is_cylindrical2 = True
                result[obj.id] = line_ids
            self.write(cr,uid,obj.id,{'is_cylindrical2': is_cylindrical2},context=context)
        return result        

    def _get_product_to_produce_cubic(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        mrp_obj     = self.pool.get('mrp.production')
        move_obj  = self.pool.get('stock.move')
        is_cubic2 = False
        for obj in self.browse(cr,uid,ids,context=context):
            move_lines  = obj.production_id.move_created_ids
            if move_lines:
                line_ids = []
                for line in move_lines:
                    if line.product_category == 'cubic':
                        line_ids.append(line.id)
                        is_cubic2 = True
                result[obj.id] = line_ids
            self.write(cr,uid,obj.id,{'is_cubic2': is_cubic2},context=context)
        return result 

    def _get_product_to_produce_volume(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        mrp_obj     = self.pool.get('mrp.production')
        move_obj  = self.pool.get('stock.move')
        is_volume2 = False
        for obj in self.browse(cr,uid,ids,context=context):
            move_lines  = obj.production_id.move_created_ids
            if move_lines:
                line_ids = []
                for line in move_lines:
                    if line.product_category == 'volume':
                        line_ids.append(line.id)
                        is_volume2 = True
                result[obj.id] = line_ids
            self.write(cr,uid,obj.id,{'is_volume2': is_volume2},context=context)
        return result

    def _get_rate_production_time(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        rate = 0
        for obj in self.browse(cr,uid,ids,context=context):
            working_hour  = obj.delay
            number_of_hours = obj.hour
            if number_of_hours != 0.0 :
                rate = working_hour / number_of_hours
                result[obj.id] = rate

        return result  

    def _get_bom_line_detail_ids(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}

        bom_line_id = []
        for line in self.browse(cr,uid,ids,context=context).production_id.bom_id.bom_line_ids:
            bom_line_id.append(line.id)

        if bom_line_id :
            result[ids[0]] = bom_line_id

        return result

    _columns = {
        'default_code' : fields.related('product','default_code',type='char',string='Ref Product',readonly=True),
        'partner_id' : fields.function(_get_partner, type='many2one', relation="res.partner", string="Customer"),
        'colection_ids': fields.related('product','colection_ids',type='many2many',relation='product.collection',string='Collection',readonly=True),
        'product_name': fields.related('product','name',type='char',string='Product Finished Name',readonly=True),
        'ean_barcode': fields.related('product','ean13',type='char',relation='product.template',string='Barcode',readonly=True),
        'origin': fields.related('production_id','origin',type='char',relation='mrp.production',string='Order List Ref',readonly=True),

        'move_lines' : fields.function(_get_product_to_consume_cylindrical, type='many2many', relation="stock.move", string="Product to Consume Cylindrical"),
        'move_lines2' : fields.function(_get_product_to_consume_cubic, type='many2many', relation="stock.move", string="Product to Consume Cubic"),
        'move_lines3' : fields.function(_get_product_to_consume_volume, type='many2many', relation="stock.move", string="Product to Consume Volume"),
        'is_cylindrical' : fields.boolean('Is Cylindrical'),
        'is_cubic' : fields.boolean('Is Cubic'),
        'is_volume' : fields.boolean('Is Volume'),


        'move_created_ids' : fields.function(_get_product_to_produce_cylindrical, type='many2many', relation="stock.move", string="Product to Produce Cylindrical"),
        'move_created_ids2' : fields.function(_get_product_to_produce_cubic, type='many2many', relation="stock.move", string="Product to Produce Cubic"),
        'move_created_ids3' : fields.function(_get_product_to_produce_volume, type='many2many', relation="stock.move", string="Product to Produce Volume"),
        'is_cylindrical2' : fields.boolean('Is Cylindrical2'),
        'is_cubic2' : fields.boolean('Is Cubic2'),
        'is_volume2' : fields.boolean('Is Volume2'),


        'rate_production_time' : fields.function(_get_rate_production_time,type="char",string='Rate Production Time'),
        'bom_line_detail_ids' : fields.function(_get_bom_line_detail_ids,type="many2many",relation="mrp.bom.line",string='Rate Production Time'),
    }



class mrp_bom_line(osv.osv):
    _inherit = 'mrp.bom.line'


    _columns = {
        'position' : fields.char('position',size=64),
        'ket_bahan' : fields.char('Ket Bahan',size=64),
        'ket_mesin' : fields.char('Ket Mesin',size=64),
    }    


class mrp_workcenter(osv.osv):
    _inherit = 'mrp.workcenter'

    def _convert_time_cycle(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}

        cycle = 0
        for obj in self.browse(cr,uid,ids,context=context):
            c2 = obj.time_cycle2
            #[0]0 - [1]0 - [2]: - [3]0 - [4]0 - [5]: - [6]0 - [7]0 
            #import pdb;pdb.set_trace()
            if len(c2) != 8:
                self.write(cr,uid,obj.id,{'time_cycle2':'00:00:00'},context=context)
                cr.commit()
                raise osv.except_osv(_('Error!'), _('Wrong Input!'))
            if c2[2] != ':' or c2[5] != ':':
                self.write(cr,uid,obj.id,{'time_cycle2':'00:00:00'},context=context)
                cr.commit()
                raise osv.except_osv(_('Error!'), _('Wrong Input!'))                

            second      = c2[6]+c2[7]
            full_sec    = float(second)/3600
            minute      = c2[3]+c2[4] 
            full_min    = float(minute)/60
            hour        = c2[0]+c2[1]
            full_hour   = float(hour)

            total_hour  = float(full_sec+full_min+full_hour)

            self.write(cr,uid,obj.id,{'time_cycle':total_hour},context=context)
            result[obj.id] = result

        return result 

    _columns = {
        'time_cycle': fields.float('Time for 1 cycle (hour)', help="Time in hours for doing one cycle.",digits=(16,4)),
        'time_cycle2': fields.char('Time for 1 cycle (hour)',size=8, help="Time in hours for doing one cycle."),
        'convert_tc1_ke_tc' : fields.function(_convert_time_cycle,type="boolean",string="Convert"),

    }
    _defaults = {
        'time_cycle2': '00:00:00',

     }    