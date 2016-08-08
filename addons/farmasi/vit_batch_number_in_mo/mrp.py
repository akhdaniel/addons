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

import logging
_logger = logging.getLogger(__name__)

# from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    ########################### pembuatan char batch number ##############################
    def create_batch_number(self,cr,uid,production,context=None):

        # import pdb; pdb.set_trace()

        #Tahun 2015 => 15
        tahun_digit1 = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)[2]
        tahun_digit2 = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)[3]
        tahun_2_digit = tahun_digit1+tahun_digit2

        #Sediaan
        sediaan_code = '-'
        if production.product_id.categ_id.sediaan_id:                   
            sediaan_code =  production.product_id.categ_id.sediaan_id.code

        #Bulan dec 12, jan 01
        # bulan_digit1 = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)[5]
        # bulan_digit2 = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)[6]


        bulan_digit1 = production.date_planned [5]
        bulan_digit2 = production.date_planned [6]

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
            bulan_huruf = 'J' # tanpa I
        elif bulan_2_digit == '10':
            bulan_huruf = 'K'  
        elif bulan_2_digit == '11':
            bulan_huruf = 'L'
        elif bulan_2_digit == '12':
            bulan_huruf = 'M'
        
        # jika belum punya batch number buat dari 001
        if production.batch_numbering_start == 'besar':
            new_batch_number = str(tahun_2_digit+sediaan_code+bulan_huruf+'500')
            # batch_rule       = str(tahun_2_digit+sediaan_code+bulan_huruf+'5%')
        else:
            new_batch_number = str(tahun_2_digit+sediaan_code+bulan_huruf+'001')
            # batch_rule       = str(tahun_2_digit+sediaan_code+bulan_huruf+'0%')
        
        batch_rule       = str(tahun_2_digit+sediaan_code+bulan_huruf+'%')

        # 15SM001 SUBSTRING ( expression ,start , length )
        # 123456
        cr.execute("SELECT batch_number,SUBSTRING(batch_number, 5, 3) AS Initial " \
            "FROM mrp_production " \
            "WHERE state NOT IN ('draft','cancel') " \
            "AND batch_number like %s and batch_numbering_start=%s ORDER BY Initial DESC" \
            , (batch_rule,production.batch_numbering_start))         
        batch_ids      = cr.fetchall()
        
        # import pdb; pdb.set_trace()

        if batch_ids :
            seq_batch = int(batch_ids[0][1])+1

            #mengakali angka 0 di depan angka positif
            if len(str(seq_batch)) == 1:
                new_seq_batch = '00'+ str(seq_batch)
            elif len(str(seq_batch)) == 2 :
                new_seq_batch = '0'+ str(seq_batch) 
            else:
                new_seq_batch = str(seq_batch)

            new_batch_number = str(tahun_2_digit+sediaan_code+bulan_huruf+new_seq_batch) 

            #jika ada batch yang di cancel cek dulu di MO yang state=cancel dan allow_batch = False
            cr.execute("SELECT batch_number,SUBSTRING(batch_number, 5, 3) AS Initial FROM mrp_production " \
                            "WHERE state = 'cancel' AND allow_batch = False " \
                            "AND batch_number like %s ORDER BY Initial ASC" \
                            , (batch_rule,))  
            batch_cancel_ids      = cr.fetchall()
            if batch_cancel_ids:
                #import pdb;pdb.set_trace()
                for batch in batch_cancel_ids:
                    cancel_batch = str(batch[0])
                    #cek dulu apakah batch yang di cancel ini sudah pernah di buat lagi
                    cr.execute("SELECT batch_number FROM mrp_production " \
                                    "WHERE state NOT IN ('draft','cancel') " \
                                    "AND batch_number = %s" \
                                    , (cancel_batch,)) 
                    batch_cancel_cek      = cr.fetchall()
                    #jika belum pernah di buat langsung break
                    if not batch_cancel_cek:
                        new_batch_number = cancel_batch
                        break

        return new_batch_number

    def _vit_create_stock_move_make_consume_line_from_data(self, cr, uid, production, product, uom_id, qty, uos_id, uos_qty, lot, qty_available, source_location_id, destination_location_id, prev_move, context=None):
        move_id = self.pool.get('stock.move').create(cr, uid, {
            'name': production.name,
            'date': production.date_planned,
            'product_id': product.id,
            'restrict_lot_id' : lot or False,
            'product_uom_qty': qty,
            'product_uom': uom_id,
            'product_uos_qty': uos_id and uos_qty or False,
            'product_uos': uos_id or False,
            'qty_available': qty_available,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'company_id': production.company_id.id,
            'procure_method': prev_move and 'make_to_stock' or 
            self._get_raw_material_procure_method(cr, uid, product, 
                #location_id=source_location_id,
                #location_dest_id=destination_location_id, 
                context=context), #Make_to_stock avoids creating procurement
            'raw_material_production_id': production.id,
            #this saves us a browse in create()
            'price_unit': product.standard_price,
            'origin': production.name,
            'warehouse_id': self.pool.get('stock.location').get_warehouse(cr, uid, production.location_src_id, context=context),
            'group_id': production.move_prod_id.group_id.id,
        }, context=context)
        return move_id

    def _vit_make_consume_line_from_data(self, cr, uid, line_id, production, product, uom_id, qty, uos_id, uos_qty, context=None):
        stock_move = self.pool.get('stock.move')
        # loc_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        uom_obj = self.pool.get('product.uom')

        uom = uom_obj.browse(cr, uid, uom_id, context=context)

        # Internal shipment is created for Stockable and Consumer Products
        if product.type not in ('product', 'consu'):
            return False

        # Take routing location as a Source Location.
        # source_location_id = production.location_src_id.id

        # Take routing location from category default MRP source location
        source_location_id = product.categ_id.mrp_location_id.id
        if not source_location_id:
            raise osv.except_osv(_('error'),_("No MRP location for category %s")%(product.category_id) )
        prod_location_id = source_location_id
        prev_move= False

        if production.bom_id.routing_id and production.bom_id.routing_id.location_id and production.bom_id.routing_id.location_id.id != source_location_id:
            source_location_id = production.bom_id.routing_id.location_id.id
            prev_move = True


        destination_location_id = production.product_id.property_stock_production.id

        lot_id = False
        qty_available = 0
        move_ids = [] # untuk semua actual products yang terambil
        deleted_move_ids = []

        if product.default_code == 'AGS002':
            print "AGS002"


        # cari produk yang is_header = false dan kode produknya 6 digit pertama sama
        # aka. cari child products
        same_product = self.pool.get('product.product').search(cr,uid,
            [('parent_id','=',product.product_tmpl_id.id),('is_header','=',False)])

        if not same_product:
            raise osv.except_osv(_('error'),_("Product '%s' has no children. Child product name should contain comma eg '%s, manufacturer' and is_header = True") % (product.display_name, product.name) )

        #- cek satu per satu di serial number yang produk_id nya sama,
        #   ambil yang ED nya paling dekat expired
        # produk aslinya yg is_header dihapus dari daftar

        cr.execute("SELECT id,product_id FROM stock_production_lot \
                    WHERE product_id IN %s AND life_date IS NOT NULL \
                    ORDER BY life_date ASC" , (tuple(same_product),))
        lot_ids    = cr.fetchall()

        # jika di temukan   ada lot
        # print "lot_ids",lot_ids
        # print "bom line uom_id",uom.name

        total_lot_qty = 0.00

        if lot_ids : # ada lot / serial number
            qty_bom = qty
            for lot in lot_ids:

                # cari dulu apa sudah ada stock move dengan lot_id yang ini
                sql = 'SELECT id FROM stock_move WHERE restrict_lot_id = %s \
                AND product_id = %s and \
                raw_material_production_id = %s' % (lot[0], lot[1], production.id)

                cr.execute(sql)
                ada = cr.fetchone()
                if ada:
                    print "lot sudah ada di move line MO " , ada
                    self.pool.get('stock.move').action_confirm(cr, uid, ada, context=context)
                    continue

                #cari apakah ada stock barang dengan lot tsb pada suatu location
                #cari di quant qty product sesuai dengan id lot
                # harus dikurangi dengan yang reserved !!!
                sql  = 'SELECT sum(qty) FROM stock_quant WHERE location_id = %s \
                AND lot_id = %s' % (source_location_id,lot[0])
                cr.execute (sql)
                # print sql
                hasil   = cr.fetchone()
                # print "hasil, yang ada di gudang: ",hasil
                if hasil:
                    if hasil[0] != None : # ada stock lot
                        create_is_header_move = False
                        lot_id = lot[0]
                        hasil = hasil[0]
                        actual_product = product_obj.browse(cr, uid, lot[1], context=context)
                        print("actual_product", actual_product.code)
                        print "actual_product wh uom ", actual_product.uom_id.name

                        #konversi uom supaya sama dengan uom bom
                        # misal : actual_produk Kg, bom g
                        if actual_product.uom_id.id != uom.id:
                            hasil *= uom.factor / actual_product.uom_id.factor
                            print("converted hasil ", hasil)

                        # stock lebih banyak daripada yang diperlukan di BOM
                        if hasil >= qty_bom :
                            move_id = self._vit_create_stock_move_make_consume_line_from_data(cr, uid,
                                production, actual_product, uom_id, qty, uos_id, uos_qty, lot_id, hasil,
                                source_location_id, destination_location_id, prev_move, context=context)
                            qty_bom -= qty_bom
                            move_ids.append(move_id)

                            # delete produk asli yg is_header
                            # sql = "delete from stock_move where raw_material_production_id=%s and product_id=%s and id=%s"  % (production.id, product.id, line_id)
                            # _logger.error(sql)
                            # cr.execute(sql)
                            deleted_move_ids.append(line_id)
                            total_lot_qty = total_lot_qty + hasil
                            break

                        # stock kurang daripada yang diperlukan di BOM
                        elif hasil < qty_bom :
                            move_id = self._vit_create_stock_move_make_consume_line_from_data(cr, uid,
                                production, actual_product, uom_id, hasil, uos_id, uos_qty, lot_id, hasil, source_location_id, destination_location_id, prev_move, context=context)

                            qty_bom -= hasil
                            move_ids.append(move_id)

                            # delete produk asli yg is_header
                            # sql = "delete from stock_move where raw_material_production_id=%s and product_id=%s and id=%s"  % (production.id, product.id, line_id)
                            # _logger.error(sql)
                            deleted_move_ids.append(line_id)
                            # cr.execute(sql)
                    else: # tidak ada stock lot
                        hasil = 0.00
                total_lot_qty = total_lot_qty + hasil

            # jika sesudah di looping dari lot, permintaan dari bom belum terpenuhi maka buatkan
            # move sisanya tanpa Lot (produk is_header)
            # qty_bom = sisa qty
            # total_lot_qty = qty yang diambil dari lot

            if qty_bom != 0.00 and total_lot_qty != 0.00:
                lot_id = False
                move_id = self._vit_create_stock_move_make_consume_line_from_data(cr, uid,
                        production, product,
                        uom_id, qty_bom,
                        uos_id, uos_qty,
                        lot_id,
                        qty_available,
                        source_location_id, destination_location_id, prev_move, context=context)
                move_ids.append(move_id)

            if qty_bom == 0.00:
                cr.execute("update mrp_production_product_line set state='%s' where id=%s" % ("done", line_id))
        else:
            qty_bom = qty #yang diminta
            lot_id = False
            _logger.warning("no lot, cek bahan kemas?")

            for actual_product in product_obj.browse(cr, uid, same_product, context=context):

                # product_obj = self.pool.get('product.product')
                # hasil = product_obj._product_available(cr, uid,[actual_product.id],
                #     context={'location': source_location_id})[actual_product.id]['virtual_available']

                sql  = 'SELECT sum(qty) FROM stock_quant WHERE location_id = %s \
                    AND product_id = %s' % (source_location_id,actual_product.id)
                cr.execute (sql)
                hasil   = cr.fetchone()
                if hasil:
                    if hasil[0] != None and hasil[0] > 0: # ada stock di gudang
                        hasil = hasil[0]
                    else:
                        hasil = 0.0
                else:
                    hasil = 0.0

                # print "hasil, yang ada di gudang: ",actual_product.default_code, actual_product.name,hasil
                # import pdb; pdb.set_trace()

                # konversi uom supaya sama dengan uom bom
                # misal : actual_produk Kg, bom g

                if actual_product.uom_id.id != uom.id:
                    hasil *= uom.factor / actual_product.uom_id.factor
                    # print("converted hasil ", hasil)

                if hasil >= qty_bom:
                    move_id = self._vit_create_stock_move_make_consume_line_from_data(cr, uid,
                        production, actual_product, uom_id, qty_bom, uos_id, uos_qty, lot_id,
                        hasil,
                        source_location_id, destination_location_id, prev_move, context=context)
                    move_ids.append(move_id)
                    qty_bom -= qty_bom
                    total_lot_qty = total_lot_qty + hasil

                    # sql = "delete from stock_move where raw_material_production_id=%s and product_id=%s and id=%s"  % (production.id, product.id, line_id)
                    # _logger.error(sql)
                    # cr.execute(sql)
                    deleted_move_ids.append(line_id)
                    break;

                elif hasil > 0 and  hasil < qty_bom:
                    #cr, uid, production, product, uom_id, qty, uos_id, uos_qty, lot, qty_available, source_location_id, destination_location_id, prev_move, context
                    move_id = self._vit_create_stock_move_make_consume_line_from_data(
                        cr, uid, production, actual_product, uom_id, hasil, uos_id, uos_qty, lot_id, hasil, source_location_id, destination_location_id, prev_move, context=context)

                    move_ids.append(move_id)

                    qty_bom -= hasil

                    # sql = "delete from stock_move where raw_material_production_id=%s and product_id=%s and id=%s"  % (production.id, product.id, line_id)
                    deleted_move_ids.append(line_id)
                    # _logger.error(sql)
                    # cr.execute(sql)

                elif hasil <= 0.0:
                    hasil = 0.0
                    break


                total_lot_qty = total_lot_qty + hasil


            if qty_bom != 0.00 and total_lot_qty > 0.00:
                lot_id = False
                move_id = self._vit_create_stock_move_make_consume_line_from_data(cr, uid,
                        production, product,
                        uom_id, qty_bom,
                        uos_id, uos_qty,
                        lot_id,
                        qty_available,
                        source_location_id, destination_location_id, prev_move, context=context)
                move_ids.append(move_id)

            # tab Scheduled Products
            if qty_bom == 0.00:
                cr.execute("update mrp_production_product_line set state='%s' where id=%s" % ("done", line_id))


        if prev_move:
            # karena array, maka harus di looping
            for mv in move_ids:
                prev_move = self._create_previous_move(cr, uid, mv, product, 
                    prod_location_id, source_location_id, 
                    context=context)
                stock_move.action_confirm(cr, uid, [prev_move], context=context)
        return move_ids, deleted_move_ids

    # default produk terpilih otomatis berdasarkan:
    # - ED
    # - stock

    # pada waktu confirm MO:
    # - didapatkan produk header dari BOM
    # - utk setiap produk yang di BOM:
    #    - cari produk yang is_header = false dan kode produknya 6 digi pertama sama
    #    - cek satu per satu di serial number yang produk_id nya sama, 
    #       ambil yang ED nya paling dekat expired 
    #    - jika qty kurang dari yg diminta BOM, ambil ED terdekat berikutnya: jadi ada 2 record BB dengan serial no yang berbeda

    # muncukan field di produk to consume:
    # - ED
    # - Serial Nunber
    # - On Hand sebleum di kurangi
    # - Nomor Analisa (internal Reference)

    def _vit_make_production_consume_line(self, cr, uid, line, context=None):
        return self._vit_make_consume_line_from_data(cr, uid, line.id, line.raw_material_production_id, line.product_id, line.product_uom.id, line.product_uom_qty, False , False, context=context)
        # return self._vit_make_consume_line_from_data(cr, uid, line.id, line.raw_material_production_id, line.product_id, line.product_uom.id, line.product_uom_qty, line.product_uos.id, line.product_uos_qty, context=context)

    def action_assign(self, cr, uid, ids, context=None):
        _logger.info('action assign')
        stock_move_obj = self.pool.get('stock.move')

        for production in self.browse(cr, uid, ids, context=context):
            stock_moves = []
            deleted_move_ids = []

            #looping scheduled product
            # for line in production.product_lines:
            for line in production.move_lines:
                if line.product_id.code == 'BME001':
                    print line.lot_ids, line.product_id.code, line.state

                # skip kalau sudah terisi lot
                # kalau sudah available: skip
                if line.state =='assigned':
                    continue
                    
                # jika sudah ada lot_id atau (bukan produk header dan state [confirmer,drfat] )
                # maka create move baru yang masih draft utk produk ini dan delete yang lama
                if (line.restrict_lot_id.id != False) or \
                        (line.product_id.is_header == False and (line.state == 'confirmed' or line.state == 'draft') ) :
                    
                    if not line.product_id.parent_id:
                        raise osv.except_osv(_('error'),_("Product '%s' has no parent. Please set it up.") %(line.product_id.display_name) )

                    data = {
                        'name' : line.product_id.parent_id.name,
                        'product_id' : line.product_id.parent_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom'   : line.product_uom.id,
                        'location_id'   : line.product_id.categ_id.mrp_location_id.id,
                        'location_dest_id'   : line.location_dest_id.id,
                        'raw_material_production_id': line.raw_material_production_id.id,

                    }
                    new_id = stock_move_obj.create(cr, uid, data, context=context)
                    cr.execute('delete from stock_move where id = %s', (line.id,))
                    stock_moves.append(new_id)
                    continue

                # cek jenis barang: service ?
                if (line.product_id.type != 'service') :
                    # ganti dg fungsi custom
                    stock_move_id, deleted_move_id = self._vit_make_production_consume_line(cr, uid, line, context=context)
                    for smi in stock_move_id:
                        stock_moves.append(smi)
                    for dmi in deleted_move_id:
                        deleted_move_ids.append(dmi)

                else:
                    self._make_service_procurement(cr, uid, line, context=context)       

            # confirm dan assign stock moves ids yang berhasil dibentuk (10 digit , ada lots)
            if stock_moves:
                stock_move_obj.action_confirm(cr, uid, stock_moves, context=context)
                stock_move_obj.action_assign(cr, uid, stock_moves, context=context)

            # hapus stock move ids yang lama (6 digit)
            if deleted_move_ids:
                cr.execute('delete from stock_move where id in %s' , (tuple(deleted_move_ids),) )

            # kalau cunsumed produk sudah kosong, assign MO to Ready to Producet
            if not production.move_lines:
                super(mrp_production, self).action_assign(cr, uid, ids, context=None)

        return True
    
    # def create(self, cr, uid, vals, context=None):

    def action_confirm(self, cr, uid, ids, context=None):
        super(mrp_production, self).action_confirm(cr, uid, ids, context=context)

        for production in self.browse(cr, uid, ids, context=context):
            new_batch_number = self.create_batch_number(cr,uid,production,context=context)                   
            production.write({'state': 'confirmed','batch_number':new_batch_number})
       
        ## Update Batch Number Di WO nya ##
        self.update_batch_wo(cr,uid, ids, new_batch_number,context=context)
        return 0

    def update_batch_wo(self,cr,uid,ids,new_batch_number,context=None):
        for wo in self.browse(cr,uid,ids,context=context)[0].workcenter_lines:
            if new_batch_number:
                workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
                workcenter_line_obj.write(cr, uid, [wo.id],{'batch_number':new_batch_number})

    #########################################################################
    # jika status line bukan assign dan
    #########################################################################
    def _get_wo_start_ok(self, cr, uid, ids, field_name, args, context=None):
        result = {}
        res = True

        for mo in self.browse(cr, uid, ids, context=context):
            if not mo.move_lines and mo.move_lines2:
                result[mo.id] = True
                return result
            elif not mo.move_lines:
                result[mo.id] = False
                return result

            result[mo.id] = res
            for mov in mo.move_lines:
                if mov.state != 'assigned' and mov.product_id.categ_id.wo_start_no_stock is False:
                    res = False
                    break

            result[mo.id] = res
        return result

    _columns = {
        'batch_number_id': fields.many2one('batch.number', string='Batch Number',
            domain="[('is_used','=',False)]",required=False,
            # readonly=True,states={'draft':[('readonly',False)]}
            ),
        'batch_number': fields.char('Batch Number',
            readonly=False,
            states={'done':[('readonly',True)], 
                'cancel':[('readonly',True)],
                'in_production':[('readonly',True)]},
            # readonly=True,

            ),
        'sediaan_id': fields.related('product_id','categ_id','sediaan_id',type='many2one',relation='vit.sediaan',string='Sediaan',readonly=True),
        'allow_batch' : fields.boolean('Batch Number tidak bisa digunakan kembali?',readonly=True),
        'wo_start_ok'   : fields.function(_get_wo_start_ok, type='boolean', string="WO Start Allowed?"),
        }

    def hitung_batch_number(self, cr, uid, date_planned, date_batch, context=None):
        date        = datetime.datetime.strptime(date_planned,"%Y-%m-%d %H:%M:%S")
        total_date  = date + datetime.timedelta(days=(date_batch*30))#kali 30 karena perbulan
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
        # if not production.move_created_ids and production.move_lines:
        #     stock_mov_obj.action_cancel(cr, uid, [x.id for x in production.move_lines], context=context)

        if not production.move_created_ids and production.move_lines:
            stock_mov_obj.action_done(cr, uid, [x.id for x in production.move_lines], context=context)

        self.signal_workflow(cr, uid, [production_id], 'button_produce_done')



        #create QA release move
        # GOJ Inpout > GOJ Stock
        # proses di atas cuman bikin stock move dari Production > GOJ/Input
        if production_mode in [ 'consume_produce']:
            self.create_qa_release(cr, uid, production, lot_id, context=context)

        return True

    def create_qa_release(self, cr, uid, production, lot_id, context=None):
        warehouse_obj           = self.pool.get('stock.warehouse')
        location_obj            = self.pool.get('stock.location')
        picking_obj             = self.pool.get('stock.picking')
        picking_type_obj        = self.pool.get('stock.picking.type')
        move_obj                = self.pool.get('stock.move')

        warehouse_dest_id = warehouse_obj.search(cr, uid, [('name','=','Gudang Obat Jadi Pusat')], 
            context=context)

        if not warehouse_dest_id:
            raise osv.except_osv(_('error'),_("No Warehouse name Gudang Obat Jadi Pusat") ) 

        warehouse_dest      = warehouse_obj.browse(cr, uid, warehouse_dest_id, context=context)
        picking_type_id     = warehouse_dest[0].int_type_id
        location_dest_id    = warehouse_dest[0].lot_stock_id # destination GOJ / Stock
        location_id         = production.location_dest_id    # source GOJ / Quality Control 

        picking_id = picking_obj.create(cr,uid,{
            'origin': "%s:%s" % (production.name , production.batch_number) ,
            'picking_type_id'   : picking_type_id.id,}) 

        for move in production.move_created_ids2:
            move_obj.create(cr,uid,{'picking_id'        : picking_id,
                                    'product_id'        : move.product_id.id,
                                    'product_uom_qty'   : move.product_uom_qty,
                                    'product_uom'       : move.product_uom.id,
                                    'name'              : move.name,
                                    'location_id'       : location_id.id,
                                    'location_dest_id'  : location_dest_id.id,
                                    'restrict_lot_id'   : lot_id,
            })
        picking_obj.action_confirm(cr, uid, picking_id, context=context)
        picking_obj.action_pack(cr, uid, [picking_id], operation_filter_ids=None, context=None)
        picking_obj.action_assign(cr, uid, picking_id, context=context)
        return 0

    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancels the production order and related stock moves.
        @return: True
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        for production in self.browse(cr, uid, ids, context=context):
            if production.move_created_ids:
                move_obj.action_cancel(cr, uid, [x.id for x in production.move_created_ids])
            procs = proc_obj.search(cr, uid, [('move_dest_id', 'in', [x.id for x in production.move_lines])], context=context)
            if procs:
                proc_obj.cancel(cr, uid, procs, context=context)
            move_obj.action_cancel(cr, uid, [x.id for x in production.move_lines])

            # overwrite utk limit batch yang bisa digunakan kembali ketika cancel
            limit = False
            if production.workcenter_lines :
                if production.routing_id:
                    if production.routing_id.workcenter_lines:
                        for rout in production.routing_id.workcenter_lines:
                            workcenter_rout = rout.workcenter_id.id
                            #cek di wo routing apakah limit batch ada yang di set True 
                            #jika ada, cek dengan wo yang berasal dari MO
                            #import pdb;pdb.set_trace()
                            if rout.limit_batch_number_cancel == True:
                                for wo in production.workcenter_lines:
                                    if wo.workcenter_id.id == workcenter_rout:
                                        if wo.state != 'draft':
                                            limit = True
                                        break
                                break        
        self.write(cr, uid, ids, {'state': 'cancel','allow_batch':limit})
        # Put related procurements in exception
        proc_obj = self.pool.get("procurement.order")
        procs = proc_obj.search(cr, uid, [('production_id', 'in', ids)], context=context)
        if procs:
            proc_obj.write(cr, uid, procs, {'state': 'exception'}, context=context)
        return True


class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    def action_start_working(self, cr, uid, ids, context=None):
        wo = self.browse(cr,uid,ids,context=context)
        wo_start_ok = wo.production_id.wo_start_ok
        if not wo_start_ok:
            raise osv.except_osv(_('error'),_("WO can't start, check the MO consumed product availibility.\nAll Starting Material products should be available.") )
        return super(mrp_production_workcenter_line, self).action_start_working(cr, uid, ids, context=context)

    def _get_batch(self, cr, uid, ids, field_name, arg, context=None):

        # if context is None:
        #     context = {}
        # result      = {}
        # y           = 0.00
        # for obj in self.browse(cr,uid,ids,context=context):
        #     y = (obj.result_qty/obj.qty) *100
        #     result[obj.id] = y
        # return result
        return

    _columns={
        'batch_number': fields.char('Batch Number',readonly=True,),
    } 



class mrp_routing_workcenter(osv.osv):

    _inherit = 'mrp.routing.workcenter'

    _columns={
        'limit_batch_number_cancel': fields.boolean('Limit Batch Number Cancel', 
            help="Centang, jika WO ini sudah di start maka menjadi batasan batch number untuk tidak bisa di gunakan kembali"),
    }

    _defaults = {
        'limit_batch_number_cancel' : False
    }   

class stock_move_consume(osv.osv_memory):
    _name = "stock.move.consume"
    _inherit = "stock.move.consume"

    def default_get(self, cr, uid, fields, context=None):
        res = super(stock_move_consume, self).default_get(cr, uid, fields, context=context)
        move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
        if 'restrict_lot_id' in fields:
            res.update({'restrict_lot_id': move.restrict_lot_id.id})
        return res


class mrp_product_produce(osv.osv_memory):
    _name = "mrp.product.produce"
    _inherit = "mrp.product.produce"

    def on_change_qty(self, cr, uid, ids, product_qty, consume_lines, context=None):
        # prod_obj = self.pool.get("mrp.production")
        # # uom_obj = self.pool.get("product.uom")
        # production = prod_obj.browse(cr, uid, context['active_id'], context=context)
        # consume_lines = []
        # new_consume_lines = []
        # if product_qty > 0.0:
        #     # product_uom_qty = uom_obj._compute_qty(cr, uid, production.product_uom.id, product_qty, production.product_id.uom_id.id)
        #     consume_lines = production.move_lines
        
        # for consume in consume_lines:
        #     new_consume_lines.append([0, False, consume])
        # return {'value': {'consume_lines': new_consume_lines}}
        return False

