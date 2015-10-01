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
import datetime
import openerp.addons.decimal_precision as dp
from collections import OrderedDict
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import float_compare, float_is_zero
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID
from openerp.addons.product import _common

# from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    #mengakali field readonly yang di beri nilai melalui event onchange
    def create(self, cr, uid, vals, context=None):

        #import pdb;pdb.set_trace()
        if 'bom_id' in vals:
            bom_obj = self.pool.get('mrp.bom')
            bom_id = vals['bom_id']
            qty_from_bom = bom_obj.browse(cr,uid,bom_id).product_qty
            product_qty = {'product_qty':qty_from_bom}
            vals = dict(vals.items()+product_qty.items()) 
        return super(mrp_production, self).create(cr, uid, vals, context=context)

    #onchange product
    def product_id_change(self, cr, uid, ids, product_id, product_qty=0, context=None):
        """ Finds UoM of changed product.
        @param product_id: Id of changed product.
        @return: Dictionary of values.
        """

        result = {}
        if not product_id:
            return {'value': {
                'product_uom': False,
                'bom_id': False,
                'routing_id': False,
                'product_uos_qty': 0,
                'product_uos': False
            }}
        bom_obj = self.pool.get('mrp.bom')
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        bom_id = bom_obj._bom_find(cr, uid, product_id=product.id, properties=[], context=context)

        routing_id = False
        if bom_id:
            bom_point = bom_obj.browse(cr, uid, bom_id, context=context)
            routing_id = bom_point.routing_id.id or False
            ####### custom disini #########
            bom_qty = bom_point.product_qty
            ###############################
        product_uom_id = product.uom_id and product.uom_id.id or False
        result['value'] = {'product_uos_qty': 0, 'product_uos': False, 'product_uom': product_uom_id, 'bom_id': bom_id, 'routing_id': routing_id, 'product_qty':bom_qty}
        if product.uos_id.id:
            result['value']['product_uos_qty'] = bom_qty * product.uos_coeff
            result['value']['product_uos'] = product.uos_id.id
        return result

    _columns = {
        'product_qty': fields.float('Product Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True, readonly=True, states={'draft': [('readonly', True)]}),
        # 'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True, readonly=True, states={'draft': [('readonly', False)]},write=['mrp.group_mrp_manager'],read=['mrp.group_mrp_user'],),    
    }
