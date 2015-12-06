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
   
class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    def _action_compute_lines(self, cr, uid, ids, properties=None, context=None):
        """ 
            - Cari mrp.production.workcenter.line dengan production_id = ids nya
            - Loop list nya dan masuk ke workcenter_lines bom nya
            - Loop workcenter_lines, lakukan pencarian bedasarkan name work ordernya == name di workcenter di bom nya
            - update fields
        """ 
        # import pdb;pdb.set_trace()
        res = super(mrp_production, self)._action_compute_lines(cr, uid, ids, properties={}, context={})
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        workcenter_line_list = workcenter_line_obj.search(cr, uid, [('production_id','=',ids[0])])
        for wcl in workcenter_line_list:
            """ Update Man Hour diambil dari workcenter_lines di bom"""
            wcl_on_boms = workcenter_line_obj.browse(cr,uid,wcl).production_id.bom_id.workcenter_lines
            product_name_tmpl = workcenter_line_obj.browse(cr,uid,wcl).production_id.bom_id.product_tmpl_id.name
            work_order_name_self = workcenter_line_obj.browse(cr,uid,wcl).name
            for wcl_on_bom in wcl_on_boms:
                work_order_name = wcl_on_bom.workcenter_operation_id.name
                if work_order_name:
                    if work_order_name_self == (work_order_name+" - "+product_name_tmpl):
                        workcenter_line_obj.write(cr, uid, [workcenter_line_obj.browse(cr,uid,wcl).id], {
                            'man_hour_standard': wcl_on_bom.man_hour,
                            'man_number_standard': wcl_on_bom.man_number
                            })

        """ Update Machine Hour diambil dari machine_hour_lines di bom """
        self.update_machine_hour(cr,uid,ids,context)
        return res 
    

    def update_machine_hour(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        work_order_list = workcenter_line_obj.search(cr, uid, [('production_id','=',ids[0])])
        for wo in work_order_list:
            mhl_on_boms = workcenter_line_obj.browse(cr,uid,wo).production_id.bom_id.machine_hour_lines
            product_name_tmpl = workcenter_line_obj.browse(cr,uid,wo).production_id.bom_id.product_tmpl_id.name
            wo_mhl = workcenter_line_obj.browse(cr,uid,wo).wo_machine_hour_lines
            work_order_name_self = workcenter_line_obj.browse(cr,uid,wo).name
            for mhl_on_bom in mhl_on_boms:
                work_order_name = mhl_on_bom.workcenter_operation_id.name
                if work_order_name_self == (work_order_name+" - "+product_name_tmpl):
                    wo_id = workcenter_line_obj.browse(cr,uid,wo).id 
                    workcenter_line_obj.write(cr, uid,[wo_id],
                                                {'wo_machine_hour_lines':
                                                     [(0, 0, {'machine_id'              : mhl_on_bom.machine_id.id,
                                                              'machine_hour_standard'   : mhl_on_bom.machine_hour,
                                                              'is_parallel'             : mhl_on_bom.is_parallel
                                                              })]})
            

    def _compute_planned_workcenter(self, cr, uid, ids, context=None, mini=False):
        res = super(mrp_production, self)._compute_planned_workcenter(cr, uid, ids, context={}, mini={})
        """ Update Scedule Date (date_planned)
            Misal dalam 6 atau 7 hari, workcenter (mesin) dapat digunakan dalam 2 shift per 1 hari
            maka diperkirakan MO atau WO dalam satu minggu kira2 12 atau 14 MO/WO 
        """
        date_planned = self.browse(cr, uid, ids, context=context).date_planned
        # date_planned = strptime(date_planned, '%Y-%m-%d %H:%M:%S')
        wps_id = self.browse(cr, uid, ids, context=context).wps_id
        mrp_id = self.browse(cr, uid, ids, context=context).id
       
        """ Cari Dahulu mrp_id - Terfilter wps_id """
        wps_id_list = self.search(cr, uid, [('wps_id','=',wps_id.id)]) #[466, 465, 467]
        wps_id_list.sort()
        # import pdb;pdb.set_trace() 
        return res
        
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
