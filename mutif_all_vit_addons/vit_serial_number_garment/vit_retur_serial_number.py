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

	def _default_location_destination(self, cr, uid, context=None):
		mod_obj = self.pool.get('ir.model.data')
		location_dest_id = 'stock_location_stock'
		try:
			dest_location = mod_obj.get_object_reference(cr, uid, 'stock', location_dest_id)
			with tools.mute_logger('openerp.osv.orm'):
				self.pool.get('stock.location').check_access_rule(cr, uid, [dest_location[1]], 'read', context=context)
		except (orm.except_orm, ValueError):
			dest_location = False

		return dest_location[1]

	def _default_location_source(self, cr, uid, context=None):
		mod_obj = self.pool.get('ir.model.data')
		location_source_id = 'stock_location_customers'
		try:
			source_location = mod_obj.get_object_reference(cr, uid, 'stock', location_source_id)
			with tools.mute_logger('openerp.osv.orm'):
				self.pool.get('stock.location').check_access_rule(cr, uid, [source_location[1]], 'read', context=context)
		except (orm.except_orm, ValueError):
			source_location = False

		return source_location[1]

	def _get_journal(self, cr, uid, context=None):
		res = self._get_journal_id(cr, uid, context=context)
		if res:
			return res[0][0]
		return False

	def _get_journal_id(self, cr, uid, context=None):
		if context is None:
			context = {}
		journal_obj = self.pool.get('account.journal')
		vals = []
		journal_type = 'sale_refund'
		value = journal_obj.search(cr, uid, [('type', '=',journal_type )])
		for jr_type in journal_obj.browse(cr, uid, value, context=context):
			t1 = jr_type.id,jr_type.name
			if t1 not in vals:
				vals.append(t1)
		return vals

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
		'location_id'		: fields.many2one('stock.location', 'Location',required=True, select=True),
		'location_dest_id'	: fields.many2one('stock.location', 'Dest. Location', required=True,select=True),
		'invoicing'			: fields.selection([('2binvoiced', 'To be refunded/invoiced'), ('none', 'No invoicing')], 'Invoicing',required=True),
		'invoice_id'		: fields.many2one('account.invoice','Invoice',readonly=True),
		'journal_id'		: fields.many2one('account.journal','Destination Journal',domain="[('type','=','sale_refund')]"),

		}

	_defaults = {
		'user_id': lambda obj, cr, uid, context: uid,
		'date': fields.date.context_today,
		'state' : 'draft',
		'name': '/',
		'invoicing':'none',
		'location_id': _default_location_source,
		'location_dest_id': _default_location_destination,		
		'journal_id' : _get_journal,
	}

	def create(self, cr, uid, vals, context=None):
		prodlot_obj     = self.pool.get('stock.production.lot')
		partner_obj     = self.pool.get('res.partner')
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'retur.serial.number.seq') or '/'

		if not vals['serial_number_ids']:
			raise osv.except_osv(_('Error!'), _('Data Barcode tidak boleh kosong !'))
		for sn in vals['serial_number_ids'] :
			#	import pdb;pdb.set_trace()	
			patner_name = partner_obj.browse(cr,uid,vals['partner_id']).name
			serial_number = str(sn[2].get('serial_number'))
			sn_match = prodlot_obj.search(cr,uid,[('name','=',serial_number)])
			if not sn_match :
				patner_name = partner_obj.browse(cr,uid,vals['partner_id']).name
				raise osv.except_osv(_('Error!'), _('Serial Number %s untuk customer %s tidak ditemukan !') % (serial_number,patner_name))
			sn_match_do = prodlot_obj.search(cr,uid,[('name','=',serial_number),
													('is_used','=',False)])
			if sn_match_do :
				raise osv.except_osv(_('Error!'), _('Serial Number %s untuk customer %s belum pernah di Delivery Order !') % (serial_number,patner_name))
		return super(retur_serial_number, self).create(cr, uid, vals, context=context)

	def write(self, cr, uid, ids, vals, context=None):
		
		prodlot_obj     = self.pool.get('stock.production.lot')
		partner_obj     = self.pool.get('res.partner')		
		if 'serial_number_ids' in vals:
			for sn in  vals['serial_number_ids']:
				if 'partner_id' in vals:
					patner 		= partner_obj.browse(cr,uid,vals['partner_id'])
					patner_name = patner.name
					partner_id 	= partner.id
				else:
					partner 		= self.browse(cr,uid,ids)[0]
					patner_name = partner.partner_id.name
					partner_id 	= partner.partner_id.id
				if sn[2]:
					serial_number = str(sn[2].get('serial_number'))
					sn_match = prodlot_obj.search(cr,uid,[('name','=',serial_number)])
					if not sn_match :
						raise osv.except_osv(_('Error!'), _('Serial Number %s untuk customer %s tidak ditemukan !') % (serial_number,patner_name))
					sn_match_do = prodlot_obj.search(cr,uid,[('name','=',serial_number),
															('is_used','=',True)])
					if not sn_match_do :
						raise osv.except_osv(_('Error!'), _('Serial Number %s untuk customer %s belum pernah di Delivery Order !') % (serial_number,patner_name))
		return super(retur_serial_number, self).write(cr, uid, ids, vals, context=context)

	def confirm(self,cr,uid,ids,context=None):
		for my_form in self.browse(cr,uid,ids):
			if not my_form.serial_number_ids:
				raise osv.except_osv(_('Error!'), _('Data Barcode tidak boleh kosong !'))	             
		return  self.write(cr,uid,ids[0],{'state':'open'},context=context)

	def cancel(self,cr,uid,ids,context=None):
		return  self.write(cr,uid,ids[0],{'state':'draft'},context=context)

	def approve(self,cr,uid,ids,context=None):
		partner_obj    		= self.pool.get('res.partner')
		picking_in_obj    	= self.pool.get('stock.picking.in')
		invoice_obj   		= self.pool.get('account.invoice')
		invoice_line_obj   	= self.pool.get('account.invoice.line')
		move_analisys 		= self.pool.get('stock.move.serial.number')
		prodlot_obj         = self.pool.get('stock.production.lot')
		move_obj			= self.pool.get('stock.move')
		picking_id 	= False
		order_id 	= False
		
		for my_form in self.browse(cr,uid,ids):
			partner_id 		= my_form.partner_id.id
			name 			= my_form.name
			source_location	= my_form.location_id.id
			dest_location 	= my_form.location_dest_id.id
			invoice_id		= False
			if my_form.serial_number_ids:
				seq_obj_name = 'stock.picking.in'
				new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
				#create picking
				picking_id = picking_in_obj.create(cr,uid,{'name'		:_('%s-return') % (new_pick_name),
															'partner_id':partner_id,
															'origin'	: name})
				if my_form.invoicing == '2binvoiced':
					#create invoice
					invoice_id = invoice_obj.create(cr,uid,{'partner_id' 	: partner_id,
															'type'			: 'out_refund',
															'journal_id'	: my_form.journal_id.id,
															'account_id'	: my_form.partner_id.property_account_receivable.id,
															'origin'		: name})
				for bcd in my_form.serial_number_ids:
					barcode = bcd.serial_number
					sn_id = prodlot_obj.search(cr,uid,[('name','=',barcode),('is_used','=',True)])
					if not sn_id:
						raise osv.except_osv(_('Error!'), _('Serial Number %s untuk customer %s tidak ditemukan ! !') % (barcode,my_form.partner_id.name))
					sn_move = move_analisys.search(cr,uid,[('serial_number_id','=',sn_id[0]),('type','=','out')])
					# antisipasi jika barang ini pernah di retur 2 x maka cari id terbesar(terbaru)
					sn_move_id = sorted(sn_move,reverse=True)
					if not sn_move_id :
						raise osv.except_osv(_('Error!'), _('Serial Number %s belum pernah di Delivery Order !') % (barcode))

					move = move_analisys.browse(cr,uid,sn_move_id[0])
					product_id = move.product_id.id
					product_name = move.product_id.name
					product_qty = move.stock_move_id.product_qty
					product_uom = move.stock_move_id.product_uom.id

					mv_id = move_obj.create(cr,uid,{'picking_id':picking_id,
													'product_id':product_id,
													'product_qty':1,#product_qty,
													'product_uom':product_uom,
													'name':'Retur - '+product_name,
													'type':'in',
													'location_id':source_location,
													'location_dest_id':dest_location,
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
					if my_form.invoicing == '2binvoiced':
						account = move.product_id.property_account_income.id
						if not account:
							account = move.product_id.categ_id.property_account_income_categ.id
						#create invoice refund details
						invoice_line_obj.create(cr,uid,{'invoice_id':invoice_id,
														'product_id':product_id,
														'name'		:'Retur - '+product_name,
														'account_id':account,
														'quatity'	: 1,
														'uos_id'	: product_uom,
														'price_unit':move.product_id.list_price,
														})
					prodlot_obj.write(cr,uid,sn_id[0],{'is_used':False},context=context)
		self.write(cr,uid,ids[0],{'state':'approved','picking_id':picking_id,'invoice_id':invoice_id},context=context)
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