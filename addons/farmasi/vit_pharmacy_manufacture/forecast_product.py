import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re



class forecast_product(osv.osv):
    _name = 'vit_pharmacy_manufacture.forecast_product'
    _description = 'Forecast Product'

    _columns = {
        'name': fields.char('Name',required=True),
        'year': fields.char('Year'),
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'created_date': fields.datetime('Created Date', required=True, readonly=True, select=True),
        'forecast_detail_ids':fields.one2many('vit_pharmacy_manufacture.forecast_product_detail','forecast_product_id','Forecast Details'),
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

    def action_create_mps(self, cr, uid, ids, context=None):
        """ Buat MPS Sebanyak 12 Bulan, kelompokan dalam tiap MPS (perbulan) """
        month = ['Jan','Feb','Mar','Apr','May','Jun','jul','Aug','Sep','Nov','Oct','Dec']
        for m,r in zip(month,range(1,13)):
            mps_obj = self.pool.get('vit_pharmacy_manufacture.mps').create(cr,uid,{
                'name' : 'MPS'+''+self.browse(cr,uid,ids[0],).year+''+m,
                'year' : self.browse(cr,uid,ids[0],).year,
                'month': m,
                })

            """ Update Details Di MRP, dengan mengambil item di Detail Forecast """  
            for detail in self.browse(cr,uid,ids[0],).forecast_detail_ids:
                # import pdb;pdb.set_trace()
                if m == "Jan":
                    product_id = detail.product_id.id
                    prod_order = detail.m1
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "Feb":
                    product_id = detail.product_id.id
                    prod_order = detail.m2
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "Mar":
                    product_id = detail.product_id.id
                    prod_order = detail.m3
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "Apr":
                    product_id = detail.product_id.id
                    prod_order = detail.m4
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "May":
                    product_id = detail.product_id.id
                    prod_order = detail.m5
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "Jun":
                    product_id = detail.product_id.id
                    prod_order = detail.m6
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "Jul":
                    product_id = detail.product_id.id
                    prod_order = detail.m7
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "Aug":
                    product_id = detail.product_id.id
                    prod_order = detail.m8
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "Sep":
                    product_id = detail.product_id.id
                    prod_order = detail.m9
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "Oct":
                    product_id = detail.product_id.id
                    prod_order = detail.m10
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "Nov":
                    product_id = detail.product_id.id
                    prod_order = detail.m11
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)
                if m == "Dec":
                    product_id = detail.product_id.id
                    prod_order = detail.m12
                    self.update_line_mps(cr,uid,ids,mps_obj,product_id,prod_order)


    def update_line_mps(self,cr,uid,ids,mps_obj,product_id,prod_order,context=None):
        if prod_order > 0:
            data_line = {
                'product_id' : product_id,
                'production_order' : prod_order,
            }

            mps_detail_line = [(0,0,data_line)]
            datas = {'mps_detail_ids' : mps_detail_line,}
            self.pool.get('vit_pharmacy_manufacture.mps').write(cr,uid,mps_obj,datas)

class forecast_product_detail(osv.osv):
    _name = 'vit_pharmacy_manufacture.forecast_product_detail'
    _description = 'Forecast Product Detail'

    _columns = {
        'forecast_product_id' : fields.many2one('vit_pharmacy_manufacture.forecast_product', 'Forecast Product Reference',required=True, ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Substance', required=True),
        'product_uom': fields.many2one('product.uom', 'Uom'),
        # 'year': fields.char('Year'),
        'm1': fields.float('Jan'),
        'm2': fields.float('Feb'),
        'm3': fields.float('Mar'),
        'm4': fields.float('Apr'),
        'm5': fields.float('May'),
        'm6': fields.float('Jun'),
        'm7': fields.float('Jul'),
        'm8': fields.float('Aug'),
        'm9': fields.float('Sep'),  
        'm10': fields.float('Oct'),
        'm11': fields.float('Nov'),
        'm12': fields.float('Dec'), 
        'mTotal'  : fields.float("Total", store=True),
    }


    @api.onchange('m1', 'm2','m3','m4','m5','m6','m7','m8','m9','m10','m11','m12') # if these fields are changed, call method
    def on_change_total(self):
        self.mTotal = self.m1 + self.m2 + self.m3 + self.m4 + self.m5 + self.m6 + self.m7 + self.m8 + self.m9 + self.m10 + self.m11 + self.m12

    def on_change_product_id(self, cr, uid, ids, product_id, name, context=None):
        uom = self.pool.get('product.product').browse(cr, uid, product_id, context=context).uom_id.id 
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