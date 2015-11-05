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


class vit_rework_wizard(osv.osv_memory):
    _name = 'vit.rework.wizard'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(vit_rework_wizard, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
            if 'workorder_id' in fields:
                res.update({'workorder_id': context['active_id']})               
        return res



    _columns = {
        'workorder_id'          : fields.many2one('mrp.production.workcenter.line','Work Order',),
        'partner_id'            : fields.many2one('res.partner','Partner'),
        'date'                  : fields.datetime('Schedule Date',required=True,help='waktu yang diminta untuk barang-barang ini'),
        'rework_detail_ids'     : fields.one2many('vit.rework.detail.wizard','wizard_id',string='Details Product'),
     }

    _defaults = {
        'date': fields.datetime.now,
     }


    def create_internal_move(self, cr, uid, ids, context=None):

        picking_obj     = self.pool.get('stock.picking')
        move_obj        = self.pool.get('stock.move')

        partner_id      = False
        #import pdb;pdb.set_trace()
        for data in self.browse(cr, uid, ids, context=context):
            if not data.rework_detail_ids:
                raise osv.except_osv(_('Error'),
                        _('Data Product tidak boleh kosong !.'))
            if data.partner_id :
                partner_id = data.partner_id.id 
            # create picking
            # picking_id = picking_obj.create(cr,uid,{'partner_id': partner_id,
            #                                         'origin': data.workorder_id.production_id.name+' ['+data.workorder_id.name+']',
            #                                         'workorder_id':context['active_id'],
            #                                         'picking_type_id':3,#internal transfer
            #                                         'min_date': data.date,
            #                                         'invoice_state':'none',
            #                                         'move_type':'direct'},context=context)   

            # diganti langsung ke stock.move karena jadi ada error:
            # MissingError: ('MissingError', u'One of the documents you are trying to access has been deleted, please try again after refreshing.')

            moves           = []          
            for move in data.rework_detail_ids:
                product_id      = move.product_id.id
                product_name    = move.product_id.name
                move_qty        = move.qty
                move_uom        = move.uom_id.id

                # Create stock.move
                move_id      = move_obj.create(cr,uid,{'product_id':product_id,
                                                        #'picking_id':picking_id,
                                                        'workorder_id':context['active_id'],
                                                        'origin': data.workorder_id.production_id.name+' ['+data.workorder_id.name+']',
                                                        'name':product_name,
                                                        'product_uom_qty':move_qty,
                                                        'product_uom':move_uom,
                                                        'location_id':12,# WH/stock
                                                        'location_dest_id':5,#virtual loss
                                                        },context=context)
  
                moves.append(move_id)

                


        return moves
	

class vit_rework_detail_wizard(osv.osv_memory):
    _name = 'vit.rework.detail.wizard'

    _columns = {
        'wizard_id'         : fields.many2one('vit.rework.wizard', 'Wizard'),
        'product_id'        : fields.many2one('product.template',string='Product',required=True),
        'qty'               : fields.float('Qty',required=True),
        'uom_id'            : fields.many2one('product.uom','UoM',required=True)
    }    

    _defaults = {
        'qty'   : 1,
    }

    def onchange_product_id(self, cr, uid, ids, product_id):  
        uom_id = False    
        if not product_id:
            return {'value': {
                'uom_id': uom_id,
                }}
        product = self.pool.get('product.template').search(cr, uid,[('id','=',product_id)])
        if product:
            uom_id = self.pool.get('product.template').browse(cr,uid,product[0]).uom_id.id 
        return {'value': {
            'uom_id' : uom_id,
            }}
    
vit_rework_detail_wizard()