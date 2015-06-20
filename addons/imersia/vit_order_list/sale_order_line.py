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

            result[obj.id] = customers_description
        return result     

    def hitung_mm_ke_inch(self,bilangan):
        hasil = 0
        if bilangan > 0 :
            hasil = round(bilangan / 25.4,4)
        return hasil  

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
            result[obj.id] = hasil
        return result         

    def hitung_height_mm_ke_inch(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_height
            hasil     = self.hitung_mm_ke_inch(bilangan)
            result[obj.id] = hasil
        return result 

    def hitung_length_mm_ke_inch(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_length
            hasil     = self.hitung_mm_ke_inch(bilangan)           
            result[obj.id] = hasil
        return result 


    _columns = {
        'default_code' : fields.related('product_id','default_code',type='char',string='Ref Product',readonly=True),
        'description_ids': fields.function(_get_customer_description, type='char', string='Customer Description',readonly=True),
        'wood_type_id': fields.related('product_id','wood_type_id',type='many2one',relation='product.wood.type',string='Wood',readonly=True),
        'packaging_id': fields.related('product_id','packaging_id',type='many2one',relation='product.package.type',string='Package Type',readonly=True),
        'remarks':fields.char('Remarks',readonly=False),

        'product_weight_inch': fields.function(hitung_length_mm_ke_inch, type='char', string='Depth (Inch)'),
        'product_height_inch': fields.function(hitung_height_mm_ke_inch, type='char', string='Height (Inch)',),
        'product_larg_inch': fields.function(hitung_width_mm_ke_inch, type='char', string='Width (Inch)'),  

        'image_medium': fields.related('product_id','image_medium',type='binary',relation='product.template',string='Picture',readonly=True),
        'image_small': fields.related('product_id','image_small',type='binary',relation='product.template',string='Picture ',readonly=True),

        'is_order_list': fields.boolean('Order List',readonly=True),

        'description': fields.related('product_id','description',type='text',string='Description',readonly=True),

        'product_length':fields.related('product_id','product_length',type='float',string='Length (mm)'),
        'product_larg':fields.related('product_id','product_larg',type='float',string='Width (mm)'),
        'product_height':fields.related('product_id','product_height',type='float',string='Thickness (mm)'),     
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
        order_list_id = order_list_obj.create(cr,uid,{'partner_id'            : self_obj.partner_id.id,
                                                        'ref'                 : 'OL-'+self_obj.name,
                                                        'purchase_date' : self_obj.date_order,
                                                        'sale_order_line_ids' : [(6,0,detail)]
                                                        })

        self.write(cr,uid,ids[0],{'order_list_id':order_list_id})

        return True    