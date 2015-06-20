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
from openerp import api
from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow


class sale_order_list(osv.Model):
	_name 			= "sale.order.list"
	_description 	= "Order List"
	_order = "ref desc, name desc"

	def _get_default_company(self, cr, uid, context=None):
		company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
		if not company_id:
			raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
		return company_id

	def _get_manufacturing_order(self, cr, uid, ids, field_name, arg, context=None):
		
		if context is None:
			context = {}
		result = {}
		
		self_obj		= self.browse(cr,uid,ids[0],context=context)
		mrp_prod_obj	= self.pool.get('mrp.production')
		mo_ids 			= mrp_prod_obj.search(cr,uid,[('origin','=',self_obj.name)], context=context)

		if mo_ids :
			result[ids[0]] = mo_ids
		return result		

	def _get_sale_order_line_ids(self, cr, uid, ids, field_name, arg, context=None):
		#import pdb;pdb.set_trace()
		if context is None:
			context = {}
		result = {}
		
		self_obj		= self.browse(cr,uid,ids[0],context=context)
		order_line_id = []
		for line in self_obj.sale_order_line_ids:
			order_line_id.append(line.id)

		if order_line_id :
			result[ids[0]] = order_line_id
		return result


	def _get_total(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		res = {}
		
		sol_id = self.browse(cr,uid,ids[0],context=context)
		sub_total = 0.00
		if sol_id.sale_order_line_ids:
			for line in sol_id.sale_order_line_ids:
				sub_total += line.price_subtotal

		res[ids[0]] = sub_total

		return res


	_columns = {
		'ref'					: fields.char('Ref', size=64, required=True,readonly=True,states={'draft':[('readonly',False)]}),
		'name'					: fields.char('Name',readonly=True,),
		'partner_id' 			: fields.many2one('res.partner','Customer',required=True,readonly=True,states={'draft':[('readonly',False)]},select=1),
		'purchase_date'			: fields.date('Purchase Order Date',readonly=True,states={'draft':[('readonly',False)]}),
		'up_to_date'			: fields.date('Up to Date',readonly=True,states={'draft':[('readonly',False)]}),
		'delivery_date'			: fields.date('Delivery date',readonly=True,states={'draft':[('readonly',False)]}),
		'sale_order_line_ids'	: fields.many2many(
			'sale.order.line',   	
			'sale_order_list_rel',        
			'sale_order_line_id',              
			'sale_order_list_id',          
			'Order Lines',    
			domain="[('state','=','confirmed'),\
			('is_order_list','=',False),\
			('order_partner_id','=',partner_id)]",\
			readonly=True,states={'draft':[('readonly',False)]},
			required=True),	
		'sale_order_line_ids2'	: fields.function(_get_sale_order_line_ids, type="many2many", relation="sale.order.line", string="Measurement"),
		#'sale_order_line_ids2'	: fields.many2many("sale.order.line", string="Measurement",compute='_get_sale_order_line_ids'),
		'state'					: fields.selection([('draft', 'Draft'),('confirm', 'Confirm')], 'Status'),
		'note'					: fields.text('Note'),
		'user_id'				: fields.many2one('res.users','User',readonly=True, select=True, track_visibility='onchange'),
		'company_id'			: fields.many2one('res.company', 'Company'),
		#'manufacturing_order_ids' : fields.many2many("mrp.production", string="Manufacturing Order List",compute='_get_manufacturing_order'),
		'manufacturing_order_ids' : fields.function(_get_manufacturing_order, type='many2many', relation="mrp.production", string="Manufacturing Order List"),
		'total' 				: fields.function(_get_total, type='float', string="Total",store=True),
		
	}

	_defaults ={
		'state' 				:'draft',
		'ref'					:'/',
		'user_id'				: lambda obj, cr, uid, context: uid,
		'company_id'			: _get_default_company,
		'name' 					: "/",
	}


	# def partner_change(self, cr, uid, ids, partner_id, name):
	# 	partner = name or ''
	# 	if partner_id:
	# 		partner = 'Order List ' + self.pool.get('res.partner').browse(cr,uid,partner_id,).name
	# 	return {'value': {'name': partner}}

	def create(self, cr, uid, vals, context=None):

		if vals.get('ref','/')=='/':
			vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order.list') or '/'

		partner 		= vals['partner_id']
		par_obj 		= self.pool.get('res.partner').browse(cr,uid,partner,context=context)
		partner_name 	= par_obj.name
		ref 			= vals['ref']

		order_list_name = {'name':'Order List '+partner_name}
		vals = dict(vals.items()+order_list_name.items()) 
		
		return super(sale_order_list, self).create(cr, uid, vals, context=context)	

	def action_confirm(self,cr,uid,ids,context=None):
		#set true field is_order_list agar tidak bisa di search ketika add new di order list detail
		for order_list in self.browse(cr,uid,ids[0],context=context).sale_order_line_ids:
			self.pool.get('sale.order.line').write(cr,uid,order_list.id,{'is_order_list':True},context=context)

		self.write(cr,uid,ids,{'state':'confirm'},context=context)			

		return True

	def action_cancel(self,cr,uid,ids,context=None):
		#set false field is_order_list agar bisa di search ketika add new di order list detail
		for order_list in self.browse(cr,uid,ids[0],context=context).sale_order_line_ids:
			self.pool.get('sale.order.line').write(cr,uid,order_list.id,{'is_order_list':False},context=context)	
		self.write(cr,uid,ids,{'state':'draft'},context=context)

		return True

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Invalid Action!'), _('The data can be removed only with the status of the draft'))
		return super(sale_order_list, self).unlink(cr, uid, ids, context=context)		


	def action_order_list_send(self, cr, uid, ids, context=None):
		'''
		This function opens a window to compose an email, with the edi sale template message loaded by default
		'''
		assert len(ids) == 1, 'This option should only be used for a single id at a time.'
		ir_model_data = self.pool.get('ir.model.data')
		try:
			template_id = ir_model_data.get_object_reference(cr, uid, 'vit_order_list', 'email_template_edi_sale_order_list')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False 
		ctx = dict(context)
		ctx.update({
			'default_model': 'sale.order.list',
			'default_res_id': ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'mark_so_as_sent': True
		})
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

	def action_create_manufacturing_orders(self, cr, uid, ids, context=None):

		mrp_bom_obj = self.pool.get('mrp.bom')
		self_obj	= self.browse(cr,uid,ids[0],context=context)

		for line in self_obj.sale_order_line_ids:
			
			#cari product di BoM
			product_bom_id = mrp_bom_obj.search(cr,uid,[('product_tmpl_id','=',line.product_id.product_tmpl_id.id)])
			if product_bom_id ==[]:
				raise osv.except_osv(_('Error!'), _("Product %s don't have Bill of Materials!") % (line.product_id.name))	
			else:
				bom = mrp_bom_obj.browse(cr,uid,product_bom_id,context=context)[0]		
				
				mo_create = self.pool.get('mrp.production').create(cr,uid,{'product_id' 		: line.product_id.id,
																			'bom_id'			: bom.id,
																			'product_qty'		: line.product_uom_qty,
																			'product_uom'		: line.product_uom.id,
																			#'date_planned'		: lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
																			'routing_id'		: bom.routing_id.id or False,
																			'user_id'			: uid,
																			'origin'			: self_obj.name

																		})
				#workflow.trg_validate(uid, 'mrp.production', mo_create, 'moves_ready', cr)
			self.pool.get('sale.order.line').write(cr,uid,line.id,{'is_order_list':True},context=context)

		self.write(cr,uid,ids,{'state':'confirm'},context=context)	
		#self.write(cr,uid,ids,{'state': 'done'},context=context)
						  
		return  True
