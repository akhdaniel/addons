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

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms production order.
        @return: Newly generated Shipment Id.
        """
        
        user_lang = self.pool.get('res.users').browse(cr, uid, [uid]).partner_id.lang
        context = dict(context, lang=user_lang)
        uncompute_ids = filter(lambda x: x, [not x.product_lines and x.id or False for x in self.browse(cr, uid, ids, context=context)])
        self.action_compute(cr, uid, uncompute_ids, context=context)
        
        for production in self.browse(cr, uid, ids, context=context):
            self._make_production_produce_line(cr, uid, production, context=context)

            ########################### modify disini ##############################
            #Tahun
            tahun_digit1 = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)[2]
            tahun_digit2 = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)[3]
            tahun_2_digit = tahun_digit1+tahun_digit2
            #Sediaan
            sediaan_code = '-'
            if production.product_id.categ_id.sediaan_id:                   
                sediaan_code =  production.product_id.categ_id.sediaan_id.code
            #Bulan
            bulan_digit1 = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)[5]
            bulan_digit2 = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)[6]
            bulan_2_digit = bulan_digit1+bulan_digit2  
            if bulan_2_digit == '01':
                bulan_huruf = 'A'              
            elif bulan_2_digit == '02':
                bulan_huruf = 'B'  
            elif bulan_2_digit == '03':
                bulan_huruf = 'C'  
            elif bulan_2_digit == '04':
                bulan_huruf = 'D'
            elif bulan_2_digit == '05':
                bulan_huruf = 'E'
            elif bulan_2_digit == '06':
                bulan_huruf = 'F'
            elif bulan_2_digit == '07':
                bulan_huruf = 'G'
            elif bulan_2_digit == '08':
                bulan_huruf = 'H'            
            elif bulan_2_digit == '09':
                bulan_huruf = 'I'
            elif bulan_2_digit == '10':
                bulan_huruf = 'J'  
            elif bulan_2_digit == '11':
                bulan_huruf = 'K'
            elif bulan_2_digit == '12':
                bulan_huruf = 'L'
            
            batch_rule = str(tahun_2_digit+sediaan_code+'%')

            # SUBSTRING ( expression ,start , length )
            cr.execute("SELECT batch_number,SUBSTRING(batch_number, 5, 3) AS Initial FROM mrp_production " \
                            "WHERE state NOT IN ('draft','cancel') " \
                            "AND batch_number like %s ORDER BY Initial DESC" \
                            , (batch_rule,))         
            batch_ids      = cr.fetchall()
            # jika belum punya batch number buat dari 001
            new_batch_number = str(tahun_2_digit+sediaan_code+bulan_huruf+'001')
            if batch_ids :
                seq_batch = int(batch_ids[0][1])+1
                #import pdb;pdb.set_trace()
                #mengakali angka 0 di depan angka positif
                if len(str(seq_batch)) == 1:
                    new_seq_batch = '00'+ str(seq_batch)
                elif len(str(seq_batch)) == 2 :
                    new_seq_batch = '0'+ str(seq_batch)
                else:
                    new_seq_batch = str(seq_batch)

                new_batch_number = str(tahun_2_digit+sediaan_code+bulan_huruf+new_seq_batch)
                       
            stock_moves = []
            for line in production.product_lines:
                if line.product_id.type != 'service':
                    stock_move_id = self._make_production_consume_line(cr, uid, line, context=context)
                    stock_moves.append(stock_move_id)
                else:
                    self._make_service_procurement(cr, uid, line, context=context)
            if stock_moves:
                self.pool.get('stock.move').action_confirm(cr, uid, stock_moves, context=context)
            production.write({'state': 'confirmed','batch_number':new_batch_number})
        return 0
    # def create(self, cr, uid, vals, context=None):
        
    #     if 'batch_number_id' in vals:
    #         batch_id = vals['batch_number_id']        
    #         mo_obj = self.pool.get('mrp.production')
    #         mo_search = mo_obj.search(cr,uid,[('batch_number_id','=',batch_id)])
    #         mo_browse = mo_obj.browse(cr,uid,mo_search)

    #         if mo_search :
    #             raise osv.except_osv(_('Error!'), _('Batch Number already in use !'))
    #         #set is_used di batch number agar tidak bisa lagi dipakai oleh MO yang lain    
    #         self.pool.get('batch.number').write(cr,uid,batch_id,{'is_used':True})
    #     return super(mrp_production, self).create(cr, uid, vals, context=context)  


    # def write(self, cr, uid, ids, vals, context=None, update=True, mini=True):
    #     direction = {}
        
    #     if 'batch_number_id' in vals:
    #         batch_id = vals['batch_number_id']        
    #         mo_obj = self.pool.get('mrp.production')
    #         mo_search = mo_obj.search(cr,uid,[('batch_number_id','=',batch_id)])

    #         if mo_search :
    #             raise osv.except_osv(_('Error!'), _('Batch Number already in use !'))                 
    #         self.pool.get('batch.number').write(cr,uid,batch_id,{'is_used':True}) 

    #     if vals.get('date_start', False):
    #         for po in self.browse(cr, uid, ids, context=context):
    #             direction[po.id] = cmp(po.date_start, vals.get('date_start', False))
    #     result = super(mrp_production, self).write(cr, uid, ids, vals, context=context)
    #     if (vals.get('workcenter_lines', False) or vals.get('date_start', False) or vals.get('date_planned', False)) and update:
    #         self._compute_planned_workcenter(cr, uid, ids, context=context, mini=mini)
    #     for d in direction:
    #         if direction[d] == 1:
    #             # the production order has been moved to the passed
    #             self._move_pass(cr, uid, [d], context=context)
    #             pass
    #         elif direction[d] == -1:
    #             self._move_futur(cr, uid, [d], context=context)
    #             # the production order has been moved to the future
    #             pass       
    #     return result

    _columns = {
        'batch_number_id': fields.many2one('batch.number', string='Batch Number',
            domain="[('is_used','=',False)]",required=False,readonly=True,states={'draft':[('readonly',False)]}),
        'batch_number': fields.char('Batch Number',readonly=True,),
        'sediaan_id': fields.related('product_id','categ_id','sediaan_id',type='many2one',relation='vit.sediaan',string='Sediaan',readonly=True)
    }

    def hitung_batch_number(self, cr, uid, date_planned, date_batch, context=None):
        date        = datetime.datetime.strptime(date_planned,"%Y-%m-%d %H:%M:%S")
        total_date  = date + datetime.timedelta(days=date_batch)
        str_date    = str(total_date)
        return str_date

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce in the uom of the production order
        @param production_mode: specify production mode (consume/consume&produce).
        @param wiz: the mrp produce product wizard, which will tell the amount of consumed products needed
        @return: True
        """
        stock_mov_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get("product.uom")
        production = self.browse(cr, uid, production_id, context=context)
        production_qty_uom = uom_obj._compute_qty(cr, uid, production.product_uom.id, production_qty, production.product_id.uom_id.id)
        precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Product Unit of Measure')
        main_production_move = False
        if production_mode == 'consume_produce':
            # To produce remaining qty of final product
            produced_products = {}
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty
            for produce_product in production.move_created_ids:
                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                lot_id = False
                if wiz:
                    #lot_id = wiz.lot_id.id

                    ########### Custom untuk batch number disini ##################################
                    date_planned    = production.date_planned
                    best_date       = False
                    life_date       = False
                    remove_date     = False
                    alt_date        = False

                    best_before_days = wiz.product_id.best_before_days
                    if best_before_days <= 0 :
                        best_before_days = wiz.product_id.categ_id.best_before_days
                    if best_before_days > 0 :    
                        best_date = self.hitung_batch_number(cr, uid, date_planned, best_before_days, context=context)

                    end_of_life_days = wiz.product_id.end_of_life_days
                    if end_of_life_days <= 0 :
                        end_of_life_days = wiz.product_id.categ_id.end_of_life_days
                    if end_of_life_days > 0 :    
                        life_date = self.hitung_batch_number(cr, uid, date_planned, end_of_life_days, context=context)

                    removal_days = wiz.product_id.removal_days
                    if removal_days <= 0 :
                        removal_days = wiz.product_id.categ_id.removal_days
                    if removal_days > 0 :    
                        remove_date  = self.hitung_batch_number(cr, uid, date_planned, removal_days, context=context)                        

                    alert_days = wiz.product_id.alert_days
                    if alert_days <= 0 :
                        alert_days = wiz.product_id.categ_id.alert_days
                    if alert_days > 0 :    
                        alt_date   = self.hitung_batch_number(cr, uid, date_planned, alert_days, context=context)                    

                    lot_id = self.pool.get('stock.production.lot').create(cr,uid,{'product_id'      : production.product_id.id,
                                                                                    'name'          : production.batch_number,
                                                                                    'use_date'      : best_date,
                                                                                    'life_date'     : life_date,
                                                                                    'removal_date'  : remove_date,
                                                                                    'alert_date'    : alt_date,
                                                                        })
                    ###############################################################################

                qty = min(subproduct_factor * production_qty_uom, produce_product.product_qty) #Needed when producing more than maximum quantity
                new_moves = stock_mov_obj.action_consume(cr, uid, [produce_product.id], qty,
                                                         location_id=produce_product.location_id.id, restrict_lot_id=lot_id, context=context)
                stock_mov_obj.write(cr, uid, new_moves, {'production_id': production_id}, context=context)
                remaining_qty = subproduct_factor * production_qty_uom - qty
                if not float_is_zero(remaining_qty, precision_rounding=precision):
                    # In case you need to make more than planned
                    #consumed more in wizard than previously planned
                    extra_move_id = stock_mov_obj.copy(cr, uid, produce_product.id, default={'product_uom_qty': remaining_qty,
                                                                                             'production_id': production_id}, context=context)
                    stock_mov_obj.action_confirm(cr, uid, [extra_move_id], context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)

                if produce_product.product_id.id == production.product_id.id:
                    main_production_move = produce_product.id

        if production_mode in ['consume', 'consume_produce']:
            if wiz:
                consume_lines = []
                for cons in wiz.consume_lines:
                    consume_lines.append({'product_id': cons.product_id.id, 'lot_id': cons.lot_id.id, 'product_qty': cons.product_qty})
            else:
                consume_lines = self._calculate_qty(cr, uid, production, production_qty_uom, context=context)
            for consume in consume_lines:
                remaining_qty = consume['product_qty']
                for raw_material_line in production.move_lines:
                    if raw_material_line.state in ('done', 'cancel'):
                        continue
                    if remaining_qty <= 0:
                        break
                    if consume['product_id'] != raw_material_line.product_id.id:
                        continue
                    consumed_qty = min(remaining_qty, raw_material_line.product_qty)
                    stock_mov_obj.action_consume(cr, uid, [raw_material_line.id], consumed_qty, raw_material_line.location_id.id,
                                                 restrict_lot_id=consume['lot_id'], consumed_for=main_production_move, context=context)
                    remaining_qty -= consumed_qty
                if not float_is_zero(remaining_qty, precision_rounding=precision):
                    #consumed more in wizard than previously planned
                    product = self.pool.get('product.product').browse(cr, uid, consume['product_id'], context=context)
                    extra_move_id = self._make_consume_line_from_data(cr, uid, production, product, product.uom_id.id, remaining_qty, False, 0, context=context)
                    stock_mov_obj.write(cr, uid, [extra_move_id], {'restrict_lot_id': consume['lot_id'],
                                                                    'consumed_for': main_production_move}, context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)

        self.message_post(cr, uid, production_id, body=_("%s produced") % self._description, context=context)

        # Remove remaining products to consume if no more products to produce
        if not production.move_created_ids and production.move_lines:
            stock_mov_obj.action_cancel(cr, uid, [x.id for x in production.move_lines], context=context)

        self.signal_workflow(cr, uid, [production_id], 'button_produce_done')
        return True    