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
    # _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'name': fields.char('Name',required=True, 
            readonly=True,
            states={'draft':[('readonly',False)]} ),
        'year': fields.integer('Year',
            readonly=True,
            states={'draft':[('readonly',False)]} ),
        'create_uid': fields.many2one('res.users', 'Created by',  
            readonly=True,
            states={'draft':[('readonly',False)]} ),
        'created_date': fields.datetime('Created Date', required=True, 
            readonly=True,
            states={'draft':[('readonly',False)]} ,
            select=True),
        'forecast_detail_ids':fields.one2many('vit_pharmacy_manufacture.forecast_product_detail','forecast_product_id','Forecast Details',
            readonly=True,
            states={'draft':[('readonly',False)]} ),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="", select=True),
        'notes': fields.text("Notes"),
        'revision': fields.integer("Revision Number", readonly=True)
    }

    _defaults = {
                 'created_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                 'state': 'draft',
                 'revision': 1
    }

    def copy(self, cr, uid, id, default=None, context=None):
        default = dict(context or {})
        old = self.browse(cr, uid, id, context=context)
        forecast_detail_ids = [(0,0,{ 
            'product_id' : fd.product_id.id,
            'product_uom' : fd.product_uom.id,
            'm1' : fd.m1, 
            'm2' : fd.m2, 
            'm3' : fd.m3, 
            'm4' : fd.m4, 
            'm5' : fd.m5, 
            'm6' : fd.m6, 
            'm7' : fd.m7, 
            'm8' : fd.m8, 
            'm9' : fd.m9, 
            'm10' : fd.m10,
            'm11' : fd.m11,
            'm12' : fd.m12,
            'mTotal' : fd.mTotal
        }) for fd in old.forecast_detail_ids]
        default.update({'forecast_detail_ids' : forecast_detail_ids , 'revision': old.revision+1})
        return super(forecast_product, self).copy(cr, uid, id, default, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'open'}, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        # delete mps/wps
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)

    def find_bom(self, cr, uid, product_id, context=None):
        mrp_bom = self.pool.get('mrp.bom')
        bom_ids = mrp_bom.search(cr, uid, [('product_tmpl_id','=', product_id.product_tmpl_id.id)], context=context)
        if not bom_ids:
            raise osv.except_osv(_('error'),_("no BOM for %s" % (product_id.name )) ) 
        
        bom = mrp_bom.browse(cr, uid, bom_ids[0], context=context)
        return bom

    def action_create_mps(self, cr, uid, ids, context=None):
        """ 
        Buat MPS Sebanyak 12 Bulan, kelompokan dalam tiap MPS (perbulan) 
        dimundurkan 1 bulan karena forecast januari 2016 artinya produksi harus 
        sudah dimulai dec 2015


        TODO: harus mengecek MPS tahun sebelumnya yang bulan Dec 
        kalau masih ada reminder maka buatkan juga MPS nya di tahun ini.

        """
        forecast = self.browse(cr,uid,ids[0],context=context)

        month = ['Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov']
        
        for m,r in zip(month,range(1,13)):
            year = forecast.year
            if m=="Dec":
                year = year - 1
            mps_obj = self.pool.get('vit_pharmacy_manufacture.mps').create(cr,uid,{
                'name' : "MPS/%s/%s" % (year, m),
                'year' : "%s" % (year),
                'month': m,
                'month_id': r,
                'forecast_id': forecast.id
                })

            """ 
            isi / Update Details Di MRP, dengan mengambil item di Detail Forecast 
            isi ke detail MPS per sediaan 
            sediaan 1 ke mps_detail_ids1
            sediaan 2 ke mps_detail_ids2
            dst 
            """  
            # default_company=self._default_company(cr, uid, context=context)
            sediaan_ids = self.pool.get('vit.sediaan').search(cr, uid, [], context=context)

            for detail in forecast.forecast_detail_ids:
                # import pdb; pdb.set_trace()
                product_sediaan_id = detail.product_id.categ_id.sediaan_id.id
                i = 0
                for sediaan in self.pool.get('vit.sediaan').browse(cr, uid, sediaan_ids,context=context):
                    # i = i + 1
                    sediaan_id = sediaan.index 
                    i = sediaan.index
                    if i == 11:
                        print "dsf"
                    if product_sediaan_id == sediaan.id:
                        print m, i, detail.product_id.name, detail.product_id.categ_id.sediaan_id.name 
                        self.fill_mps_line(cr, uid, ids, i, m, sediaan_id, mps_obj, detail )
                        break

        # self.write(cr, uid, ids, {'state':'done'}, context=context)                
    
    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]


    def fill_mps_line(self, cr, uid,ids, i, m, sediaan_id, mps_obj, detail):

        if m == "Dec":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m1, detail.product_id, detail.product_uom )                
        if m == "Jan":   
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m2, detail.product_id, detail.product_uom )
        if m == "Feb":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m3, detail.product_id, detail.product_uom )
        if m == "Mar":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m4, detail.product_id, detail.product_uom )
        if m == "Apr":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m5, detail.product_id, detail.product_uom )
        if m == "May":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m6, detail.product_id, detail.product_uom )
        if m == "Jun":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m7, detail.product_id, detail.product_uom )
        if m == "Jul":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m8, detail.product_id, detail.product_uom )
        if m == "Aug":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m9, detail.product_id, detail.product_uom )
        if m == "Sep":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m10, detail.product_id, detail.product_uom )
        if m == "Oct":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m11, detail.product_id, detail.product_uom )
        if m == "Nov":
            self.update_line_mps(cr,uid,ids,i,mps_obj, detail.m12, detail.product_id, detail.product_uom )


    def update_line_mps(self,cr,uid,ids,i,mps_obj, detail_m, detail_product_id, detail_product_uom, context=None):
        
        product_id = detail_product_id.id
        product_uom = detail_product_uom.id

        bom = self.find_bom(cr, uid, detail_product_id, context)
        if bom.product_qty == 0:
            raise osv.except_osv(_('error'),_("BOM qty cannot zero: %s" % (bom.product_tmpl_id.name)) ) 
        prod_order = math.ceil(detail_m / bom.product_qty)

        if prod_order > 0:
            w1 = 0
            w2 = 0
            w3 = 0
            w4 = 0
            w5 = 0
            data_line = {
                'product_id' : product_id,
                'production_order' : prod_order,
                'product_uom' : product_uom,
                'w1': w1,
                'w2': w2,
                'w3': w3,
                'w4': w4,
                'w5': w5
            }

            mps_detail_line = [(0,0,data_line)]
            datas = {'mps_detail_ids%s' % (i) : mps_detail_line,}
            print "mps_obj, datas" , mps_obj, datas
            # import pdb;pdb.set_trace()
            self.pool.get('vit_pharmacy_manufacture.mps').write(cr,uid,mps_obj,datas)


class forecast_product_detail(osv.osv):
    _name = 'vit_pharmacy_manufacture.forecast_product_detail'
    _description = 'Forecast Product Detail'

    _columns = {
        'forecast_product_id' : fields.many2one('vit_pharmacy_manufacture.forecast_product', 'Forecast Product Reference',required=True, ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Substance', required=True),
        'product_uom': fields.many2one('product.uom', 'Uom'),
        # 'year': fields.char('Year'),
        'm1': fields.integer('Jan'),
        'm2': fields.integer('Feb'),
        'm3': fields.integer('Mar'),
        'm4': fields.integer('Apr'),
        'm5': fields.integer('May'),
        'm6': fields.integer('Jun'),
        'm7': fields.integer('Jul'),
        'm8': fields.integer('Aug'),
        'm9': fields.integer('Sep'),  
        'm10': fields.integer('Oct'),
        'm11': fields.integer('Nov'),
        'm12': fields.integer('Dec'), 
        'mTotal'  : fields.integer("Total", store=True),
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