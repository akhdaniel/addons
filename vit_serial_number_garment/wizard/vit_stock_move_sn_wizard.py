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
        return res

    _columns = {
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'type': fields.selection([('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal')], string='Shipping Type'),
        'line_in_ids': fields.one2many('stock.move.serial.number.wizard.lines.in', 'wizard_id', 'Serial Numbers'),
        'line_out_ids': fields.one2many('stock.move.serial.number.wizard.lines.out', 'wizard_id', 'Serial Numbers'),
     }
    def update_serial_number(self, cr, uid, ids, context=None):
        """ To update product in SN"""
        if context is None:
            context = {}
        res = self.update_product_in_serial_number(cr, uid, ids, context.get('active_ids'), context=context)
        return {'type': 'ir.actions.act_window_close'}

    def update_product_in_serial_number(self, cr, uid, ids, move_ids, context=None):
        """ To update product in object stock.production.lot

        :param move_ids: the ID or list of IDs of stock move we want to update
        """
        if context is None:
            context = {}
            
        assert context.get('active_model') == 'stock.move',\
             'Incorrect use of the stock move split wizard'
        inventory_id    = context.get('inventory_id', False)
        prodlot_obj     = self.pool.get('stock.production.lot')
        inventory_obj   = self.pool.get('stock.inventory')
        move_obj        = self.pool.get('stock.move')
        inv_obj         = self.pool.get('account.invoice')
        move_sn_obj     = self.pool.get('stock.move.serial.number')

        sale_order_id   = False
        invoice_id      = False
        picking_id      = False
        lines           = []
        for data in self.browse(cr, uid, ids, context=context):
            wz_type     = data.type
            if wz_type == 'in' :
                lines = data.line_in_ids 
            elif wz_type in ('out','internal') :
                lines =  data.line_out_ids               
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                
                move_qty        = move.product_qty
                uos_qty_rest    = move.product_uos_qty
                if move.picking_id :
                    picking_id  = move.picking_id.id
                if move.picking_id.sale_id :
                    sale_order_id   = move.picking_id.sale_id.id
                    #inv_origin      = str(move.picking_id.name)+':'+str(move.picking_id.sale_id.name)
                    inv_origin      = move.picking_id.sale_id.name
                    invoice         = inv_obj.search(cr,uid,[('origin','=','inv_origin')],context=context)
                    if invoice :
                        invoice_id  = invoice[0]
                if not lines:
                    raise osv.except_osv(_('Error!'), _('Daftar Serial Number tidak boleh kosong !'))
                total_move_qty = 0.0
                
                for line in lines: 
                    sn       = line.serial_number_id.id
                    quantity = line.qty
                    total_move_qty += quantity
                    #jika out kasih minus karena barang keluar
                    if wz_type == 'out' :
                        quantity = -quantity 
                    #jika internal kasih 0 karena barang pindah di internal
                    if wz_type == 'internal' :
                        quantity = 0                                           
                    if data.type == 'in' :
                        # update SN dengan product di wizard ini
                        prodlot_obj.write(cr,uid,sn,{'product_id':data.product_id.id},context=context)
                    # create stock_move_serial_number yang reated ke stock_ove ini
                    move_sn_obj.create(cr,uid,{'stock_move_id'      : move.id,
                                                'serial_number_id'  : sn,
                                                'picking_id'        : picking_id,
                                                'product_id'        : move.product_id.id,
                                                'qty'               : quantity,
                                                'sale_order_id'     : sale_order_id,
                                                #'invoice_id'        : invoice_id,
                                            })                   
                #import pdb;pdb.set_trace()
                if move_qty != total_move_qty:
                    raise osv.except_osv(_('Processing Error!'), _('Jumlah Qty serial number (%d) tidak sama dengan jumlah qty product(%d)!') \
                        % (total_move_qty, move_qty))

                move_obj.write(cr,uid,move_ids[0],{'is_serial_number':True},context=context)   

        return True


class stock_move_serial_number_wizard_lines_in(osv.osv_memory):
	_name = 'stock.move.serial.number.wizard.lines.in'

	_columns = {
        'wizard_id'         : fields.many2one('stock.move.serial.number.wizard', 'Wizard'),
		'serial_number_id' 	: fields.many2one('stock.production.lot',string='Serial Number',required=True),
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
        'serial_number_id'  : fields.many2one('stock.production.lot',string='Serial Number',required=True),
        'product_id'        : fields.related('serial_number_id','product_id',type='many2one',relation='product.product',string='Product',store=True),
        'qty'               : fields.float('Qty'),
    }    

    _defaults = {
        'qty'   : 1,
    }
    
stock_move_serial_number_wizard_lines_out()