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


class retur_serial_number(osv.osv):
	_name = 'retur.serial.number'

	def _get_stock_move_serial_number(self, cr, uid, ids, field_name, arg, context=None):
		#import pdb;pdb.set_trace()
		if context is None:
			context = {}
		result = {}
		move_analisys 		= self.pool.get('stock.move.serial.number')
		for self_obj in self.browse(cr,uid,ids,context=context):
			picking_id = self_obj.picking_id.id
			sn_detai_ids = move_analisys.search(cr,uid,[('picking_id','=',picking_id)],context=context)
			result[self_obj.id] = sn_detai_ids
		return result

	_columns = {
		'name'				: fields.char('Nomor',size=36,required=True),
		'date'				: fields.date('Tanggal',required=True),
		'partner_id' 		: fields.many2one('res.partner','Customer',domain="[('customer','=',True)]",required=True),
		'user_id'			: fields.many2one('res.users','User',readonly=True),
		'state'				: fields.selection([('draft','Draft'),('open','Open'),('approved','Aproved')],string='Status'),
		'serial_number_ids' : fields.one2many('retur.serial.number.detail','retur_serial_number_id','Serial Number'),
		'notes'				: fields.text('Notes'),
		'picking_id'		: fields.many2one('stock.picking','Picking',readonly=True),
		'stock_move_serial_number_ids' : fields.function(_get_stock_move_serial_number,type='many2many',relation='stock.move.serial.number',string='Details'),
	}

	_defaults = {
		'user_id': lambda obj, cr, uid, context: uid,
		'date': fields.date.context_today,
		'state' : 'draft',
		'name': '/',
	}

	def create(self, cr, uid, vals, context=None):
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'retur.serial.number.seq') or '/'
		return super(retur_serial_number, self).create(cr, uid, vals, context=context)

	def confirm(self,cr,uid,ids,context=None):
		for my_form in self.browse(cr,uid,ids):
			if not my_form.serial_number_ids:
				raise osv.except_osv(_('Error!'), _('Data Barcode tidak boleh kosong !'))	             
		return  self.write(cr,uid,ids[0],{'state':'open'},context=context)

	def cancel(self,cr,uid,ids,context=None):
		return  self.write(cr,uid,ids[0],{'state':'draft'},context=context)

	def approve(self,cr,uid,ids,context=None):
		picking_in_obj    	= self.pool.get('stock.picking.in')
		picking_out_obj   	= self.pool.get('stock.picking.out')
		sale_order_obj    	= self.pool.get('sale.order')
		move_analisys 		= self.pool.get('stock.move.serial.number')
		prodlot_obj         = self.pool.get('stock.production.lot')
		move_obj			= self.pool.get('stock.move')
		mod_obj = self.pool.get('ir.model.data')
		picking_id 	= False
		order_id 	= False
		
		for my_form in self.browse(cr,uid,ids):
			if my_form.serial_number_ids:
				seq_obj_name = 'stock.picking.in'
				new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
				picking_id = picking_in_obj.create(cr,uid,{'name':_('%s-return') % (new_pick_name),
															'partner_id':my_form.partner_id.id,
															'origin': my_form.name})

				for bcd in my_form.serial_number_ids:
					barcode = bcd.serial_number
					sn_id = prodlot_obj.search(cr,uid,[('name','=',barcode)])
					if not sn_id:
						raise osv.except_osv(_('Error!'), _('Serial Number %s tidak ditemukan !') % (barcode))
					sn_move_id = move_analisys.search(cr,uid,[('serial_number_id','=',sn_id[0]),('type','=','out')])
					if not sn_move_id :
						raise osv.except_osv(_('Error!'), _('Serial Number %s belum pernah delivery order !') % (barcode))

					move = move_analisys.browse(cr,uid,sn_move_id[0])
					product_id = move.product_id.id
					product_name = move.product_id.name
					product_qty = move.stock_move_id.product_qty
					product_uom = move.stock_move_id.product_uom.id

					location_source_id = 'stock_location_suppliers'
					location_dest_id = 'stock_location_stock'

					try:
						source_location = mod_obj.get_object_reference(cr, uid, 'stock', location_source_id)
						with tools.mute_logger('openerp.osv.orm'):
							self.pool.get('stock.location').check_access_rule(cr, uid, [source_location[1]], 'read', context=context)
					except (orm.except_orm, ValueError):
						source_location = False
					try:
						dest_location = mod_obj.get_object_reference(cr, uid, 'stock', location_dest_id)
						with tools.mute_logger('openerp.osv.orm'):
							self.pool.get('stock.location').check_access_rule(cr, uid, [dest_location[1]], 'read', context=context)
					except (orm.except_orm, ValueError):
						dest_location = False

					mv_id = move_obj.create(cr,uid,{'picking_id':picking_id,
													'product_id':product_id,
													'product_qty':1,#product_qty,
													'product_uom':product_uom,
													'name':'Retur - '+product_name,
													'type':'in',
													'location_id':source_location[1],
													'location_dest_id':dest_location[1],
													'is_serial_number':True,#set agar tidak bisa input SN lagi
													'picking_id2': move.picking_id.id,
													'sn_retur_id': sn_id[0],
													})
					# create stock_move_serial_number yang related ke stock_move ini
					move_analisys.create(cr,uid,{'stock_move_id'    : mv_id,
												'serial_number_id'  : sn_id[0],
												'picking_id'        : picking_id,
												'product_id'        : product_id,
												'qty'               : 1,
												'type'				: 'in',
												'sale_order_id'     : move.sale_order_id.id or False,
												}) 
					prodlot_obj.write(cr,uid,sn_id[0],{'is_used':False},context=context)
		self.write(cr,uid,ids[0],{'state':'approved','picking_id':picking_id},context=context)
		return True

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(retur_serial_number, self).unlink(cr, uid, ids, context=context)

class retur_serial_number_detail(osv.osv):
	_name = 'retur.serial.number.detail' 
	_rec_name = 'serial_number' 

	_columns = {
		'retur_serial_number_id' 	: fields.many2one('retur.serial.number','Retur ID'),
		'serial_number'				: fields.char('Serial Number',size=50,required=True),
	}