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

    def _get_image_product(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        
        self_obj        = self.browse(cr,uid,ids[0],context=context)
        product_id      = self_obj.product_id.id
        prod_obj        = self.pool.get('product.product')
        #tmpl_obj    = self.pool.get('product.template')
        product         = prod_obj.search(cr,uid,[('id','=',product_id)], context=context)
        
        if product :
            image = prod_obj.browse(cr,uid,product)[0].product_tmpl_id.image_medium
            result[ids[0]] = image

        return result

    def _get_image(self, cr, uid, ids, name, args, context=None):

        self_obj        = self.browse(cr,uid,ids[0],context=context)
        prod_obj        = self.pool.get('product.product')
        id_obj          = self_obj.id
        product_id      = self_obj.product_id.id
        import pdb;pdb.set_trace()
        result = dict.fromkeys([id_obj], False)
        for obj in prod_obj.pool.get('product.product').browse(cr, uid, id_obj, context=context).product_tmpl_id:
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    _columns = {
        'colection_ids': fields.related('product_id','colection_ids',type='many2many',relation='product_collection_rel',string='Collection'),
        'default_code' : fields.related('product_id','default_code',type='char',string='Ref Product'),
        'description_ids': fields.related('product_id','description_ids',type='one2many',relation='product.collection',string='Customer Description'),
        #'description': fields.related('product_id','description',type='char',string='Description'),
        'wood_type_id': fields.related('product_id','wood_type_id',type='many2one',relation='product.wood.type',string='Wood'),
        
        'product_weight': fields.related('product_id','product_weight',type='float',string='Weight'),
        'product_height': fields.related('product_id','product_height',type='float',string='Height'),
        'product_larg': fields.related('product_id','product_larg',type='float',string='Large'),

        'product_material_volume12': fields.related('product_id','product_material_volume12',type='float',string='Volume'),

        #'product_cubic_volume': fields.related('product_id',type='float',string='Volume'),
        'finishing_id': fields.related('product_id','finishing_id',type='many2one',relation='product.finishing',string='Finishing'),
        'image_medium': fields.related('product_id','image_medium',type='binary',relation='product.template',string='Picture'),
     
    }