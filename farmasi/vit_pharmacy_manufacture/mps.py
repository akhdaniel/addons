import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re


""" MPS (Master Production Schedule) """
class mps(osv.osv):
    _name = 'vit_pharmacy_manufacture.mps'
    _description = 'Master Production Schedule'

    _columns = {
        'name': fields.char('Name'),
        'year': fields.char('Year'),
        'month' : fields.char('Month'),
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'created_date': fields.datetime('Created Date', required=True, readonly=True, select=True),
        'mps_detail_ids':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_detail_id','Forecast Details'),
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

    def action_create_wps(self, cr, uid, ids, context=None):
        return

""" Details MPS (Master Production Schedule) """
class mps_detail(osv.osv):
    _name = 'vit_pharmacy_manufacture.mps_detail'
    _description = 'Master Production Schedule Details'

    _columns = {
        'mps_detail_id' : fields.many2one('vit_pharmacy_manufacture.mps', 'MPS Reference',required=True, ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Substance', required=True),
        'production_order' : fields.float('Production Order'), 
        'product_uom': fields.many2one('product.uom', 'Uom'),
        'w1': fields.float('W1'),
        'w2': fields.float('W2'),
        'w3': fields.float('W3'),
        'w4': fields.float('W4'),
        'note'  : fields.char("Note"),
    }


    def on_change_product_id(self, cr, uid, ids, product_id, name, context=None):
        uom = self.pool.get('product.product').browse(cr, uid, product_id, context=context).uom_id.id
        # import pdb;pdb.set_trace()
 
        if product_id!=False:
            return {
                'value' : {
                    'product_uom' : uom,
                }
            }
        else:
            return {
                'value' : {
                    'product_uom' : '',
                } 
            }