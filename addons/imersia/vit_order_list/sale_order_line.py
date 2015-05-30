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
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow
from openerp import tools


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def _get_customer_description(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        
        prod_obj            = self.pool.get('product.template')
        cust_desc_obj       = self.pool.get('product.customers.description')
        
        for obj in self.browse(cr,uid,ids,context=context):
            partner_name            = obj.name
            product                 = obj.product_id.product_tmpl_id.id
            desc_search             = cust_desc_obj.search(cr,uid,[('produk_id','=',product)])
            customers_description   = '-'
            if desc_search :
                for desc in cust_desc_obj.browse(cr,uid,desc_search,context=context):
                    if desc.partner_id.name == obj.order_id.partner_id.name :
                        customers_description = desc.name

            result[ids[0]] = customers_description
        return result   

    def hitung_mm_ke_cm(self,bilangan):
        hasil = 0
        if bilangan > 0 :
            hasil =  bilangan / 10
        return hasil    

    def hitung_mm_ke_inch(self,bilangan):
        hasil = 0
        if bilangan > 0 :
            hasil = round(bilangan / 25.4,4)
        return hasil 

    ####################################
    #konversi mm ke cm
    ####################################
    def hitung_width_mm_ke_cm(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_larg
            hasil     = self.hitung_mm_ke_cm(bilangan)
            result[ids[0]] = hasil
        return result         

    def hitung_height_mm_ke_cm(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_height
            hasil     = self.hitung_mm_ke_cm(bilangan)
            result[ids[0]] = hasil
        return result 

    def hitung_length_mm_ke_cm(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_length
            hasil     = self.hitung_mm_ke_cm(bilangan)
            result[ids[0]] = hasil
        return result         

    ####################################
    #konversi mm ke inch
    ####################################
    def hitung_width_mm_ke_inch(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_larg
            hasil     = self.hitung_mm_ke_inch(bilangan)
            result[ids[0]] = hasil
        return result         

    def hitung_height_mm_ke_inch(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_height
            hasil     = self.hitung_mm_ke_inch(bilangan)
            result[ids[0]] = hasil
        return result 

    def hitung_length_mm_ke_inch(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_length
            hasil     = self.hitung_mm_ke_inch(bilangan)
            result[ids[0]] = hasil
        return result 

    def hitung_total_volume_m3(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan1  = obj.product_id.product_length
            hasil1     = 0
            if bilangan1 > 0:
                hasil1 = bilangan1 / 1000

            bilangan2  = obj.product_id.product_height
            hasil2     = 0
            if bilangan2 > 0:
                hasil2 = bilangan2 / 1000  

            bilangan3  = obj.product_id.product_larg
            hasil3     = 0
            if bilangan1 > 0:
                hasil3 = bilangan3 / 1000                          

            qty        = obj.product_uom_qty

            hasil      = round((hasil1 * hasil2 *hasil3)*qty,4)
            result[ids[0]] = hasil
        return result  

    _columns = {
        'colection_ids': fields.related('product_id','colection_ids',type='many2many',relation='product.collection',string='Collection',readonly=True),
        'default_code' : fields.related('product_id','default_code',type='char',string='Ref Product',readonly=True),
        'description_ids': fields.function(_get_customer_description, type='char', string='Customer Description',readonly=True),
        #'description': fields.related('product_id','description',type='char',string='Description'),
        'wood_type_id': fields.related('product_id','wood_type_id',type='many2one',relation='product.wood.type',string='Wood',readonly=True),
        
        'product_weight_cm': fields.function(hitung_length_mm_ke_cm, type='char', string='Length (cm)'),
        'product_height_cm': fields.function(hitung_height_mm_ke_cm, type='char', string='Height (cm)'),
        'product_larg_cm': fields.function(hitung_width_mm_ke_cm, type='char', string='Width (cm)'),

        'product_weight_inch': fields.function(hitung_length_mm_ke_inch, type='char', string='Length (Inch)'),
        'product_height_inch': fields.function(hitung_height_mm_ke_inch, type='char', string='Height (Inch)',),
        'product_larg_inch': fields.function(hitung_width_mm_ke_inch, type='char', string='Width (Inch)'),  

        'product_volume_total': fields.function(hitung_total_volume_m3, type='char', string='Total Volume (m3)'),      

        'product_unbuilt_volume12': fields.related('product_id','product_unbuilt_volume12',type='float',string='Unbuilt Volume (m3)',readonly=True),

        #'product_cubic_volume': fields.related('product_id',type='float',string='Volume'),
        'finishing_id': fields.related('product_id','finishing_id',type='many2one',relation='product.finishing',string='Finishing',readonly=True),
        'image_medium': fields.related('product_id','image_medium',type='binary',relation='product.template',string='Picture',readonly=True),

        'is_order_list': fields.boolean('Order List',readonly=True),
     
    }


class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns = {
        'order_list_id' : fields.many2one('sale.order.list','Order List',readonly=True),
    }


    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.signal_workflow(cr, uid, ids, 'order_confirm')

        ###################################
        # Create Ordr list per SO
        ###################################
        order_list_obj = self.pool.get('sale.order.list')
        self_obj    = self.browse(cr,uid,ids[0],context=context)
        detail=[]
        if self_obj.order_line:
            for line in self_obj.order_line:
                detail.append(line.id)
    
        #import pdb;pdb.set_trace()
        order_list_id = order_list_obj.create(cr,uid,{'partner_id'       : self_obj.partner_id.id,
                                                        'ref'                : 'OL-'+self_obj.name,
                                                        'sale_order_line_ids': [(6,0,detail)]
                                                        })

        self.write(cr,uid,ids[0],{'order_list_id':order_list_id})

        return True    