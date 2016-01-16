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

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class stock_move_serial_number_wizard(osv.osv_memory):
    _name = "stock.move.serial.number.wizard"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(stock_move_serial_number_wizard, self).default_get(cr, uid, fields, context=context)   
        #jika input SN langsung per DO line 
        if context.get('active_model') == 'stock.move':            
            if context.get('active_id'):
                move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
                if 'product_id' in fields:
                    res.update({'product_id': move.product_id.id})
                if 'product_uom' in fields:
                    res.update({'product_uom': move.product_uom.id})
                if 'qty' in fields:
                    res.update({'qty': move.product_qty})
                if 'type' in fields:
                    res.update({'type': move.type})
        #jika input SN langsung per DO             
        else :
            if context.get('active_id'):
                picking = self.pool.get('stock.picking').browse(cr, uid, context['active_id'], context=context)
                if 'type' in fields:
                    res.update({'type': picking.type})            

        return res

    _columns = {
        'qty'                   : fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'different_total_sn'    : fields.boolean('Allow Different Total Serial Number',help='Centang jika megizinkan jumlah input serial number kurang dari jumlah DO product ini'),
        'date_input'            : fields.date('Date'),
        'product_id'            : fields.many2one('product.product', 'Product', select=True),#jika input SN langsung per DO line
        'product_uom'           : fields.many2one('product.uom', 'Unit of Measure'),     
        'type'                  : fields.selection([('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal')], string='Shipping Type'),
        'line_in_ids'           : fields.one2many('stock.move.serial.number.wizard.lines.in', 'wizard_id', 'Serial Numbers'),
        'line_out_ids'          : fields.one2many('stock.move.serial.number.wizard.lines.out', 'wizard_id', 'Serial Numbers'),
        ### tambah ####
        'serial_number_date'    : fields.date('Input Date',required=True),
        'serial_number_total'   : fields.integer('Total Serial Number',readonly=True), 
        'serial_number_id'      : fields.many2one('stock.production.lot','Serial Number Problem',readonly=True),
     }

    _defaults = {
        'serial_number_date' : fields.date.context_today,
     }
        

    def update_serial_number(self, cr, uid, ids, context=None):
        """ To update product in SN"""
        
        if context is None:
            context = {}
        res = self.update_product_in_serial_number(cr, uid, ids, context.get('active_ids'), context=context)
        return {'type': 'ir.actions.act_window_close'}


    def execute_serial_number_per_picking_out(self, cr, uid, ids, lines, active_id, sale_order_id,
                                                prodlot_obj, move_obj, move_sn_obj, picking_obj, product_ids, total_qty_product, context=None):
        
        if not lines:
            raise osv.except_osv(_('Error!'), _('Daftar Serial Number tidak boleh kosong !'))         
        for pick in picking_obj.browse(cr, uid, [active_id], context=context):
            movelines   = pick.move_lines 
            ser_no = [] 
            qty_total_input = 0          
            for line in movelines :
                move_id = line.id                           
                #looping stock move yang akan di masukan SN
                mv           = move_obj.browse(cr, uid, move_id, context=context)
                product_move = mv.product_id.id
                qty_move     = mv.product_qty
                if mv.picking_id.sale_id :
                    sale_order_id = mv.picking_id.sale_id.id
                #cari SN yang di input berdasarkan stock move
                sn_per_product = self.pool.get('stock.move.serial.number.wizard.lines.out').search(cr,uid,[('wizard_id','=',ids[0])])
                # jika qty satu stock move tidak sama dengan jumalh SN yang di inputkan
                if total_qty_product != len(sn_per_product):
                    raise osv.except_osv(_('Warning!'), _("Jumlah total product sebesar %s pcs tidak sama dengan \
                     yang di inputkan di SN sebanyak %s pcs !") % (total_qty_product,len(sn_per_product)))
                qty_move_sn = 0.0
                #looping SN yang diinputkan per stock move
                for sn in self.pool.get('stock.move.serial.number.wizard.lines.out').browse(cr,uid,sn_per_product,context=context):
                    sn_no       = str(sn.serial_number)
                    sn_qty      = sn.qty
                    #import pdb;pdb.set_trace()
                    if sn_no not in ser_no :
                        prodlot_id = prodlot_obj.search(cr,uid,[('name','=',sn_no),('product_id','in',product_ids),('is_used','=',False)])
                        if not prodlot_id:
                            raise osv.except_osv(_('Warning!'), _("Serial number %s belum di input \
                                        atau sudah dipakai atau tidak sesuai dengan product di DO ini !") % (sn_no))
                        #jika qty di stock move di picking details belum terpenuhi bisa di create lagi sn nya    
                        if qty_move_sn < qty_move:    
                            #ceklis fields is_used agar di DO sebelumnya tidak bisa digunakan kembali
                            prodlot_obj.write(cr,uid,prodlot_id[0],{'is_used': True},context=context)

                            # create stock_move_serial_number yang related ke stock_move ini
                            move_sn_obj.create(cr,uid,{'stock_move_id'      : mv.id,
                                                        'serial_number_id'  : prodlot_id[0],
                                                        'picking_id'        : active_id,
                                                        'product_id'        : product_move,
                                                        'qty'               : -sn_qty,
                                                        'type'              : 'out',
                                                        'sale_order_id'     : sale_order_id,
                                                    })       
                            ser_no.append(sn_no)
                            qty_move_sn += 1 
                            qty_total_input += 1          
                #untuk mengilangkan tombol insert SN di movelines
                move_obj.write(cr,uid,mv.id,{'is_serial_number':True},context=context)

            # By  pass dulu    
            # if total_qty_product != qty_total_input :
            #     raise osv.except_osv(_('Mismatch!'), _("Total qty product di DO / Picking %s pcs, \
            #                             Yang di inputkan di SN %s pcs !") % (total_qty_product,qty_total_input))
            #untuk mengilangkan tombol insert SN di form picking   
            self.pool.get('stock.picking.out').write(cr,uid,active_id,{'used_sn':True},context=context)   

    def update_product_in_serial_number(self, cr, uid, ids, move_ids, context=None):
        """ To update product in object stock.production.lot

        :param move_ids: the ID or list of IDs of stock move we want to update
        """
        if context is None:
            context = {}

        prodlot_obj     = self.pool.get('stock.production.lot')
        move_sn_obj     = self.pool.get('stock.move.serial.number')
        picking_obj     = self.pool.get('stock.picking')
        move_obj        = self.pool.get('stock.move')
        
        sale_order_id   = False
        picking_id      = False
        lines           = []
        for data in self.browse(cr, uid, ids, context=context):
            date_sn = data.date_input
            if not date_sn:
                date_sn = fields.date.today()              
            wz_type     = data.type
            if wz_type == 'in' :
                lines = data.line_in_ids 
            elif wz_type in ('out','internal') :
                lines =  data.line_out_ids
            active_model = context.get('active_model')        
            if active_model == 'stock.picking.out':
                active_id = context.get('active_id')
                for pick in picking_obj.browse(cr, uid, [active_id], context=context):
                    movelines   = pick.move_lines
                    if not movelines:
                        raise osv.except_osv(_('Error!'), _('Product tidak boleh kosong !'))  
                    product_ids = []
                    total_qty_product = 0           
                    for line in movelines :
                        product_id = line.product_id.id 
                        #data semua product di picking
                        product_ids.append(product_id)
                        #hitung total qty product dalam satu picking
                        total_qty_product += line.product_qty                
                    self.execute_serial_number_per_picking_out(cr, uid, ids, lines, active_id, sale_order_id,
                                                prodlot_obj, move_obj, move_sn_obj, picking_obj, product_ids, total_qty_product, context=context) 
            elif active_model == 'stock.move':                
                for move in move_obj.browse(cr, uid, move_ids, context=context): 

                    move_qty        = move.product_qty
                    uos_qty_rest    = move.product_uos_qty
                    if move.picking_id :
                        picking_id  = move.picking_id.id
                    if move.picking_id.sale_id :
                        sale_order_id   = move.picking_id.sale_id.id
                    if not lines:
                        raise osv.except_osv(_('Error!'), _('Daftar Serial Number tidak boleh kosong !'))
                    total_move_qty = 0.0
                    sn_free_text = []
                    for line in lines: 
                        quantity = line.qty
                        total_move_qty += quantity
                        #jika out kasih minus karena barang keluar
                        if wz_type == 'out' :
                            raise osv.except_osv(_('Warning!'), _("DO tidak bisa memasukan serial number di fitur ini !"))
                        #jika internal kasih 0 karena barang pindah di internal
                        if wz_type == 'internal' :
                            quantity = 0                                           
                        if data.type == 'in' :
                            prodlot_id = prodlot_obj.search(cr,uid,[('name','=',line.serial_number),('product_id','=',False),('is_used','=',False)])
                            if not prodlot_id:
                                raise osv.except_osv(_('Warning!'), _("Serial number %s belum di input \
                                    atau sudah digunakan product lain !") % (line.serial_number))
                            if line.serial_number in sn_free_text:
                                continue
                            sn_free_text.append(line.serial_number)                                
                            # update SN dengan product di wizard ini
                            prodlot_obj.write(cr,uid,prodlot_id[0],{'product_id':data.product_id.id,'date_sn_input_in': date_sn,},context=context)
                        # create stock_move_serial_number yang related ke stock_move ini
                        move_sn_obj.create(cr,uid,{'stock_move_id'      : move.id,
                                                    'serial_number_id'  : prodlot_id[0],
                                                    'picking_id'        : picking_id,
                                                    'product_id'        : move.product_id.id,
                                                    'qty'               : quantity,
                                                    'type'              : 'in',
                                                    'sale_order_id'     : sale_order_id,
                                                })   
                    
                    if not data.different_total_sn:                    
                        if move_qty != total_move_qty:
                            raise osv.except_osv(_('Processing Error!'), _('Jumlah Qty serial number (%d) tidak sama dengan jumlah qty product(%d)!') \
                                % (total_move_qty, move_qty))
                    #untuk mengilangkan tombol insert SN
                    move_obj.write(cr,uid,move.id,{'is_serial_number':True},context=context)   

        #delete dulu semua data di wizard
        cr.execute('DELETE FROM stock_move_serial_number_wizard_lines_in')
        cr.execute('DELETE FROM stock_move_serial_number_wizard_lines_out')
        return True


class stock_move_serial_number_wizard_lines_in(osv.osv_memory):
	_name = 'stock.move.serial.number.wizard.lines.in'

	_columns = {
        'wizard_id'         : fields.many2one('stock.move.serial.number.wizard', 'Wizard'),
        'serial_number'     : fields.char('Serial Number',size=100,required=True),
		'serial_number_id' 	: fields.many2one('stock.production.lot',string='Serial Number'),
        'product_id'        : fields.related('serial_number_id','product_id',type='many2one',relation='product.product',string='Product',store=True),
		'qty'				: fields.float('Qty'),
	}    

	_defaults = {
		'qty'	: 1,
	}
	
stock_move_serial_number_wizard_lines_in()		

class stock_move_serial_number_wizard_lines_out(osv.osv_memory):
    _name = 'stock.move.serial.number.wizard.lines.out'

    _columns = {
        'wizard_id'         : fields.many2one('stock.move.serial.number.wizard', 'Wizard'),
        'serial_number'     : fields.char('Serial Number',size=100,required=True),
        'serial_number_id'  : fields.many2one('stock.production.lot',string='Serial Number'),
        'product_id'        : fields.related('serial_number_id','product_id',type='many2one',relation='product.product',string='Product',store=True),
        'qty'               : fields.float('Qty'),
    }    

    _defaults = {
        'qty'   : 1,
    }
    
stock_move_serial_number_wizard_lines_out()  