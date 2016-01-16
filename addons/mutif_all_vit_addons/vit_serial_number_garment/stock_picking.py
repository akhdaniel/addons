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


class stock_picking_in(osv.osv):
    _inherit = 'stock.picking.in'

    _columns ={
        'move_lines'                    : fields.one2many('stock.move', 'picking_id', 'Internal Moves', states={'cancel': [('readonly', True)]}),
        }

class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'

    def _get_total_qty_do(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr,uid,ids,context=context):
            total_qty_move = 0           
            for line in obj.move_lines :
                #hitung total qty product dalam satu picking
                total_qty_move += line.product_qty 
            
            result[obj.id] = total_qty_move
            total_qty_sn = obj.serial_number_ids
        return result

    def _get_total_qty_sn(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr,uid,ids,context=context):          
            total_qty_sn = obj.serial_number_ids
            result[obj.id] = len(total_qty_sn)
        return result

    def _get_serial_number_per_box(self, cr, uid, ids, field_name, arg, context=None):
        sql = "delete from picking_serial_number_print where picking_id = %s" % (ids[0])
        
        cr.execute(sql)        
        if context is None:
            context = {}
        result = {}
        sn_print_obj = self.pool.get('picking.serial.number.print')
        self_obj     = self.browse(cr,uid,ids[0],context=context)

        box = self_obj.box
        if not box :
            return result
        box = int(self_obj.box)
        if box > 0 :
            box_sign = 0
            no_urut  = 1
            for line in self_obj.serial_number_ids:
                box_line  = int(line.box)
                if box_line < box:
                    pass
                if box_line == box:    
                    box_sign += 1
                    # create line utk preview print pertama
                    sn_print_obj.create(cr,uid,{'picking_id': ids[0],
                                                'no_1'      : no_urut,
                                                'desc_1'    : line.description,
                                                'sn_1'      : line.serial_number},context=context)
                    no_urut += 1
                    continue
                if line.box == False and box_sign == 1: 
                    if no_urut <= 30:   
                        # create line utk preview print selanjutnya (box = False)
                        sn_print_obj.create(cr,uid,{'picking_id': ids[0],
                                                    'no_1'      : no_urut,
                                                    'desc_1'    : line.description,
                                                    'sn_1'      : line.serial_number},context=context)
                        no_urut += 1                    
                        continue
                    if no_urut > 30 :
                        cr.commit()
                        # cari preview print yang sudah di
                        sn_print_exist = sn_print_obj.search(cr,uid,[('picking_id','=',ids[0]),
                                                                     ('no_1','<=',30),
                                                                     ('second','=',False)])
                        if sn_print_exist :
                            sn_print_exist = sorted(sn_print_exist)
                            sn_print_obj.write(cr,uid,sn_print_exist[0],{'no_2'     : no_urut,
                                                                        'desc_2'    : line.description,
                                                                        'sn_2'      : line.serial_number,
                                                                        'second'    : True},context=context)
                            no_urut += 1
                            continue

                if box_line > box:    
                    break 
            #import pdb;pdb.set_trace()        
            self.write(cr,uid,self_obj.id,{'sn_qty':no_urut-1},context=context)                                  
        
        return result

    _columns = {
        'used_sn'			            : fields.boolean('Is Used SN'),
        'serial_number_ids'             : fields.one2many('picking.serial_number','picking_id',string="Serial Number Line"),
        'sn_date'                       : fields.date('Tanggal',help='Kosongkan jika tanggal input sesuai tanggal ketika confirm serial number'),
        'serial_number_total'           : fields.integer('Total Serial Number',readonly=True), 
        'serial_number_problem_id'      : fields.many2one('stock.production.lot','Serial Number Problem',readonly=True),
        'total_qty_move'                : fields.function(_get_total_qty_do,type='integer',string='Total Qty DO'),
        'total_qty_sn'                  : fields.function(_get_total_qty_sn,type='integer',string='Total Qty Serial Number'),
        'different_total_sn'            : fields.boolean('Allow Different Total Serial Number',help='Centang jika megizinkan jumlah input serial number kurang dari jumlah DO product'),
        'duplicate_sn'                  : fields.text('Serial Number Problem'),
        'ekspeditor_id'                 : fields.many2one('vit.ekspeditor','Ekspeditor'),
        'box'                           : fields.char('Box'),
        'sn_qty'                        : fields.integer('Total Qty'),
        'serial_number_priview_ids'     : fields.function(_get_serial_number_per_box, type="many2many", relation="picking.serial_number", string="Serial Number per Box"),
        'serial_number_print_ids'       : fields.one2many('picking.serial.number.print','picking_id','Serial Number to Print'),
    }
    _defaults = {
        'used_sn' 	: False,
        'box'       : False,
        }

    def delete_sn_ids(self, cr, uid, sn, picking_id, lot_ids,context=None):
        cr.execute("delete from picking_serial_number where serial_number = '%s' and picking_id = %d" % (sn, picking_id) )
        if lot_ids:
            cr.execute("update stock_production_lot set is_used = False, date_sn_input = null where id in %s ", (tuple(lot_ids),))
        cr.commit()

    def search_duplicate_entry(self, cr, uid, picking_id, context=None):
        cr.execute("""SELECT * FROM (
                      SELECT id,serial_number,
                      ROW_NUMBER() OVER(PARTITION BY serial_number ORDER BY id asc) AS Row
                      FROM picking_serial_number
                      WHERE picking_id = """+str(picking_id)+"""
                        ) dups
                        WHERE 
                        dups.Row > 1   
                    """)     
        duplicate = cr.fetchall()
        return duplicate

    def execute_serial_number_picking_out(self, cr, uid, ids, context=None):
        prodlot_obj     = self.pool.get('stock.production.lot')   
        move_obj        = self.pool.get('stock.move') 
        move_sn_obj     = self.pool.get('stock.move.serial.number')
        sn_ids_obj      = self.pool.get('picking.serial_number')
        sale_obj        = self.pool.get('sale.order')
        for pick in self.browse(cr, uid, ids, context=context):
            date_sn = pick.sn_date
            if not date_sn:
                date_sn = fields.date.today()             
            movelines   = pick.move_lines 
            if not movelines :
                raise osv.except_osv(_('Error!'), _('Daftar product tidak boleh kosong !')) 
            serial_number_ids   = pick.serial_number_ids
            if not serial_number_ids:
                raise osv.except_osv(_('Error!'), _('Daftar Serial Number tidak boleh kosong !'))           

            # search duplicate dulu
            duplicate = self.search_duplicate_entry(cr, uid, ids[0], context=context)
            if duplicate :
                duplicates = []
                for dup in duplicate:
                    duplicates.append(dup[1])
                    #hapus otomatis jika duplicate
                    sn_ids_obj.unlink(cr,uid,dup[0],context=context)
                self.write(cr,uid,pick.id,{'duplicate_sn':str(duplicates)},context=context) 
                cr.commit() 
                raise osv.except_osv(_('Warning!'), _("Duplicates serial number entry %s !") % (str(duplicates)))                               

            prodlot_ids = []
            sale_order_id = False
            for sn in pick.serial_number_ids:
                sn_no       = str(sn.serial_number)
                sn_qty      = sn.qty

                # cari di lot atas sn ini
                cr.execute('SELECT id as id '\
                'FROM stock_production_lot '\
                'WHERE name ilike \''+sn_no+'\' '\
                'AND is_used = False '\
                'AND product_id in (SELECT product_id AS product_id '\
                                    'FROM stock_move '\
                                    'WHERE picking_id ='+str(pick.id)+') '\
                            )

                prodlot_id = cr.fetchone()
                if not prodlot_id : 
                    #self.delete_sn_ids(cr,uid,str(sn_no),int(pick.id),prodlot_ids,context=context)                   
                    raise osv.except_osv(_('Warning!'), _("Serial number %s belum di input \
                                atau sudah di Delivery Order !") % (sn_no))
                prodlot_id = prodlot_obj.search(cr,uid,[('name','ilike',sn_no),('is_used','=',False)])    
                prodlot = prodlot_obj.browse(cr,uid,prodlot_id[0],context=context)
                #ceklis fields is_used agar di DO sebelumnya tidak bisa digunakan kembali
                #prodlot_obj.write(cr,uid,prodlot_id[0],{'is_used': True, 'date_sn_input': date_sn,'name':sn_no},context=context)
                prodlot_obj.write(cr,uid,prodlot_id[0],{'is_used': True, 'date_sn_input': date_sn},context=context)
                prodlot_ids.append(prodlot_id[0])
                
                cr.execute("""SELECT 
                            sm.id AS move
                            FROM stock_move sm
                            LEFT JOIN stock_picking sp on sp.id = sm.picking_id
                            WHERE sm.product_id = """+str(prodlot.product_id.id)+"""
                            AND sp.id = """+str(pick.id)+"""
                            """
                            )
                mv = cr.fetchone()
                if not mv :
                    raise osv.except_osv(_('Warning!'), _("Serial number %s atas product %s \
                                tidak ada di DO ini !") % (sn_no,prodlot.product_id.name))                    
                sale = sale_obj.search(cr,uid,[('name','=',pick.origin)],context=context)
                if sale :
                    sale_order_id = sale[0]
                
                # create stock_move_serial_number yang related ke stock_move ini
                move_sn_obj.create(cr,uid,{'stock_move_id'      :  mv[0],
                                            'serial_number_id'  : prodlot_id[0],
                                            'picking_id'        : pick.id,
                                            'product_id'        : prodlot.product_id.id,
                                            'qty'               : -sn_qty,
                                            'type'              : 'out',
                                            'sale_order_id'     : sale_order_id,
                                            'date_sn_input'     : date_sn,

                                        })   
            qty_total_input = sn_ids_obj.search(cr,uid,[('picking_id','=',pick.id)],context=context)
            if not pick.different_total_sn:
                if pick.total_qty_move != len(qty_total_input) :
                    raise osv.except_osv(_('Mismatch!'), _("Total qty product di DO %s pcs, \
                                            Yang di inputkan di SN %s pcs !") % (pick.total_qty_move,len(qty_total_input)))                                                                                 
                #untuk mengilangkan tombol insert SN di movelines
                #move_obj.write(cr,uid,line.id,{'is_serial_number':True},context=context)
            #import pdb;pdb.set_trace()    
            sql = "update stock_move set is_serial_number = True, date_input_sn = '%s' where picking_id = %s" % (str(date_sn),pick.id)
            cr.execute(sql)

            #untuk mengilangkan tombol insert SN di form picking   
            self.write(cr,uid,pick.id,{'used_sn':True,'sn_date':date_sn},context=context) 

        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_picking_form')
        view_id = view_ref and view_ref[1] or False,    
        return {
            'warning': {'title': _('OK!'),'message': _('Done processing. %s Serial Numbers Confirm' % (len(pick.serial_number_ids)) )}, 
        }

stock_picking_out()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _get_total_qty_do(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr,uid,ids,context=context):
            total_qty_move = 0           
            for line in obj.move_lines :
                #hitung total qty product dalam satu picking
                total_qty_move += line.product_qty 
            
            result[obj.id] = total_qty_move
            total_qty_sn = obj.serial_number_ids
            self.write(cr,uid,obj.id,{'total_qty_sn':len(total_qty_sn)})
        return result

    def _get_total_qty_sn(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr,uid,ids,context=context):          
            total_qty_sn = obj.serial_number_ids
            result[obj.id] = len(total_qty_sn)
        return result

    _columns = {
        'used_sn'                       : fields.boolean('Is Used SN'),
        'serial_number_ids'             : fields.one2many('picking.serial_number','picking_id',string="Serial Number Line"),
        'sn_date'                       : fields.date('Tanggal',help='Kosongkan jika tanggal input sesuai tanggal ketika confirm serial number'),
        'serial_number_total'           : fields.integer('Total Serial Number',readonly=True), 
        'serial_number_problem_id'      : fields.many2one('stock.production.lot','Serial Number Problem',readonly=True),
        'total_qty_move'                : fields.function(_get_total_qty_do,type='integer',string='Total Qty DO'),
        'total_qty_sn'                  : fields.function(_get_total_qty_sn,type='integer',string='Total Qty Serial Number'),
        'different_total_sn'            : fields.boolean('Allow Different Total Serial Number',help='Centang jika megizinkan jumlah input serial number kurang dari jumlah DO product'),

    }
    _defaults = {
            'used_sn'   : False,
        }


stock_picking_out()

class picking_serial_number(osv.osv):
    _name = 'picking.serial_number'

    def onchange_serial_number(self, cr, uid, ids, serial_number, context=None):
        if not serial_number:
            return {}        
        prodlot_id = self.pool.get('stock.production.lot').search(cr,uid,[('name','ilike',serial_number),('is_used','=',False)])

        if not prodlot_id :
            raise osv.except_osv(_('Warning!'), _("Serial number %s belum di input atau sudah di Delivery Order!") % (serial_number))
        desc = self.pool.get('stock.production.lot').browse(cr,uid,prodlot_id[0],context=context).product_id.name   

        return {'value':{'description':desc}} 


    _columns = {
        'picking_id'            : fields.many2one('stock.picking.out', 'Picking'),
        'serial_number'         : fields.char('Serial Number',size=50,required=True),
        'description'           : fields.char('Description',size=128),
        'serial_number_id'      : fields.many2one('stock.production.lot',string='Serial Number ID'),
        'product_id'            : fields.related('serial_number_id','product_id',type='many2one',relation='product.product',string='Product',store=True),
        'qty'                   : fields.float('Qty'),
        'box'                   : fields.char('Box'),
    }    

    _defaults = {
        'qty'   : 1,
        'box'   : False,
    }
 

class picking_serial_number_in(osv.osv):
    _name = 'picking.serial_number_in'

    _columns = {
        'move_id'               : fields.many2one('stock.move', 'Move ID'),
        'serial_number'         : fields.char('Serial Number',size=50,),
        'qty'                   : fields.float('Qty'),
    }    

    _defaults = {
        'qty'   : 1,
    }

picking_serial_number()

class vit_ekspeditor(osv.osv):
    _name = 'vit.ekspeditor'

    _columns = {
        'name'            : fields.char('Name',size=128, required=True),
    }  
vit_ekspeditor()

class picking_serial_number_print(osv.osv):
    _name = 'picking.serial.number.print'

    _columns ={
        'picking_id': fields.many2one('stock.picking.out', 'Picking'),
        'no_1'      : fields.integer('No'),
        'no_2'      : fields.integer('No'),
        'sn_1'      : fields.char('Serial Number'),
        'sn_2'      : fields.char('Serial Number'),
        'desc_1'    : fields.char('Product'),
        'desc_2'    : fields.char('Product'),
        'second'    : fields.boolean('Used'),
    }    
picking_serial_number_print()    