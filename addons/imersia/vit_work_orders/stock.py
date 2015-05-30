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

from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging

class stock_move(osv.osv):
    _inherit = "stock.move"

    def _get_position(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        bom_obj         = self.pool.get('mrp.bom')
        work_center_obj = self.pool.get('mrp.production.workcenter.line')
        prod_obj        = self.pool.get('mrp.production')

        position = False
        for obj in self.browse(cr,uid,ids,context=context):
            #import pdb;pdb.set_trace()
            name     = obj.name
            production_id   = prod_obj.search(cr,uid,[('name','=',name)], context=context) 

            if production_id:
                position = False
                for bom_line in prod_obj.browse(cr,uid,production_id[0]).bom_id.bom_line_ids:
                    if bom_line.product_id.id == obj.product_id.id :
                        if bom_line.position:
                            position = bom_line.position
                result[obj.id] = position
            
        return result 
       

    _columns = {
        'colection_ids': fields.related('product_id','colection_ids',type='many2many',relation='product.collection',string='Collection',readonly=True),
        'default_code' : fields.related('product_id','default_code',type='char',string='Ref Product',readonly=True),

        'description': fields.related('product_id','description',type='char',string='Description'),
        'wood_type_id': fields.related('product_id','wood_type_id',type='many2one',relation='product.wood.type',string='Wood',readonly=True),   

        'material_id': fields.related('product_id','material_id',type='many2one',relation='product.material',string='Material',readonly=True), 
        'quality_id': fields.related('product_id','quality_id',type='many2one',relation='product.quality',string='Quality',readonly=True),

        'product_unbuilt_volume12': fields.related('product_id','product_unbuilt_volume12',type='float',string='Unbuilt Volume (m3)',readonly=True),

        #'product_cubic_volume': fields.related('product_id',type='float',string='Volume'),
        'finishing_id': fields.related('product_id','finishing_id',type='many2one',relation='product.finishing',string='Finishing',readonly=True),
        'image_medium': fields.related('product_id','image_medium',type='binary',relation='product.template',string='Picture',readonly=True),

        'ean_barcode': fields.related('product_id','ean13',type='char',relation='product.template',string='Barcode',readonly=True),
        'origin': fields.related('production_id','origin',type='char',relation='mrp.production',string='Order List Ref',readonly=True),

		'product_category':fields.related('product_id','product_category',type='char',readonly=True,string='Product Category'),
        'product_length':fields.related('product_id','product_length',type='float',readonly=True,string='Length (mm)'),
        'product_diameter':fields.related('product_id','product_diameter',type='float',readonly=True,string='Diameter (mm)'),
        'product_larg':fields.related('product_id', 'product_larg',type='float',readonly=True,string='Larg (mm)'),
        'product_height':fields.related('product_id','product_height',type='float',readonly=True,string='Height (mm)'),
        'product_weight':fields.related('product_id',type='float',readonly=True,string='Weight (Kg)'),
        'product_cylindrical_volume': fields.related('product_id','product_cylindrical_volume',type='float',readonly=True,string='Volume (m3)'),
        'product_cubic_volume': fields.related('product_id','product_cubic_volume',type='float',readonly=True,string='Component (m3)'),
        'product_volume_volume': fields.related('product_id','product_volume_volume',type='float',readonly=True,string='Volume (Liter)'),
        'product_cylindrical_density':fields.related('product_id',type='float',readonly=True,string='Density (Kg/m3)'),
        'product_cubic_density':fields.related('product_id','product_cubic_density',type='float',readonly=True,string='Density (Kg/m3)'),
        'product_volume_density':fields.related('product_id','product_volume_density',type='float',readonly=True,string='Density (Kg/Liter)'),
        'product_classic_volume12':fields.related('product_id','product_classic_volume12',type='float',readonly=True,string='Classic Volume (m3)',help="Length x width x Height"),
        'product_unbuilt_volume12':fields.related('product_id',type='float',readonly=True,string='Unbuilt (m3)',help="Volume of the disassemble furniture, ready to be packed"),
        'product_packed_volume12':fields.related('product_id','product_packed_volume12',type='float',readonly=True,string='Packed (m3)',help="Volume of the packed furniture"),

   	    'position' : fields.function(_get_position,type="char",string='Position'),
        
    }