import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re
import logging
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)



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

    def find_bom(self, cr, uid, product_id, context=None):
        mrp_bom = self.pool.get('mrp.bom')
        bom_ids = mrp_bom.search(cr, uid, [('product_tmpl_id','=', product_id.product_tmpl_id.id)], context=context)
        if not bom_ids:
            raise osv.except_osv(_('error'),_("no BOM for %s" % (product_id.name )) ) 
        
        bom = mrp_bom.browse(cr, uid, bom_ids[0], context=context)
        return bom

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
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m1, detail.product_id )
                if m == "Feb":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m2, detail.product_id )
                if m == "Mar":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m3, detail.product_id )
                if m == "Apr":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m4, detail.product_id )
                if m == "May":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m5, detail.product_id )
                if m == "Jun":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m6, detail.product_id )
                if m == "Jul":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m7, detail.product_id )
                if m == "Aug":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m8, detail.product_id )
                if m == "Sep":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m9, detail.product_id )
                if m == "Oct":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m10, detail.product_id )
                if m == "Nov":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m11, detail.product_id )
                if m == "Dec":
                    self.update_line_mps(cr,uid,ids,mps_obj, detail.m12, detail.product_id )


    def update_line_mps(self,cr,uid,ids,mps_obj, detail_m, detail_product_id,context=None):
        
        product_id = detail_product_id.id
        bom = self.find_bom(cr, uid, detail_product_id, context)
        if bom.product_qty == 0:
            raise osv.except_osv(_('error'),_("BOM qty cannot zero: %s" % (bom.product_tmpl_id.name)) ) 
        prod_order = detail_m / bom.product_qty         

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