import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re
from datetime import date, timedelta


""" WPS (Week Production Schedule) """
class wps(osv.osv):
    _name = 'vit_pharmacy_manufacture.wps'
    _description = 'Week Production Schedule'

    _columns = {
        'name'      : fields.char('Name'),
        'mps_id'    : fields.many2one('vit_pharmacy_manufacture.mps','MPS'),
        'week_on_month'   : fields.integer('Week On Month'),
        'week_on_year'   : fields.integer('Week On Year'),
        'product_id': fields.many2one('product.product', 'Substance', required=True),
        'categ_id'  : fields.many2one('product.category','Category'),
        'batch'     : fields.float('Batch'),
        'start_date': fields.datetime('Start Date',select=True),
        'end_date'  : fields.datetime('End Date', select=True),
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'created_date': fields.datetime('Created Date', required=True, readonly=True, select=True),
        # 'mrp_detail_ids':fields.one2many('vit_pharmacy_manufacture.mrp_detail','mrp_detail_id','MRP Details'),
        'mrp_detail_ids':fields.one2many('mrp.production','wps_id','MRP Details'),
        'year': fields.char('Year'),

        # 'name': fields.char('Name'),
        # 'year': fields.char('Year'),
        # 'month' : fields.char('Month'),
        # 'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        # 'created_date': fields.datetime('Created Date', required=True, readonly=True, select=True),
        # 'mps_detail_ids':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_detail_id','Forecast Details'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="", select=True),

    }

    _defaults = {
                 'created_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                 'state': 'draft',
    }

    def action_confirm(self, cr, uid, ids, context=None):
        
        
        return self.write(cr, uid, ids, {'state':'done'}, context=context)

    def action_create_mo(self, cr, uid, ids, context=None):
        """ Create Sejumlah MO dari Batch nya"""

        return

""" Details MRP """
class mrp_detail(osv.osv):
    _name = 'vit_pharmacy_manufacture.mrp_detail'
    _description = 'MRP'

    _columns = {
        'mrp_detail_id' : fields.many2one('vit_pharmacy_manufacture.mrp', 'MRP Reference',required=True, ondelete='cascade', select=True),
        'mrp_id': fields.many2one('mrp.production', 'Manufacture Order', required=True),

    }


#     def on_change_product_id(self, cr, uid, ids, product_id, name, context=None):
#         uom = self.pool.get('product.product').browse(cr, uid, product_id, context=context).uom_id.id
#         # import pdb;pdb.set_trace()
 
#         if product_id!=False:
#             return {
#                 'value' : {
#                     'product_uom' : uom,
#                 }
#             }
#         else:
#             return {
#                 'value' : {
#                     'product_uom' : '',
#                 } 
#             }