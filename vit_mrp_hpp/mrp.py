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
from datetime import datetime

import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp import SUPERUSER_ID

class mrp_production(osv.osv):
	_name = 'mrp.production'
	_description = 'Manufacturing Order'
	_inherit = 'mrp.production'

	def _get_default_overhead(self, cr, uid, context=None):
		if context is None:
			context = {}
		overhead_value_ids = []
		ir_model_id   = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
		master_overhead_obj   = self.pool.get('vit.master.overheads')
		master_ids   = master_overhead_obj.search(cr, uid,[('appeareance','=',ir_model_id[0])])
		for master_id in master_ids:
			overhead_value_ids.append((0,0,{'master_overhead_id':master_id,'value':0}))
		return overhead_value_ids


	_columns = {
		'overhead_value_ids':fields.one2many('vit.overhead.value','mrp_prod_id','Overhead Value'),
		}

	_defaults = {
		'overhead_value_ids' : _get_default_overhead
	}



	def action_produce(self, cr, uid, production_id, production_qty, production_mode, context=None):
		res = super(mrp_production, self).action_produce(cr, uid, production_id, production_qty, production_mode, context=None)
		self.update_jurnal_stock(cr,uid,production_id,production_qty,context)
		return res

	def update_jurnal_stock(self,cr,uid,production_id,production_qty,context=None):
		"""Object-object account move, account move line dan MRP
		"""
		move_obj = self.pool.get('account.move')
		move_line_obj = self.pool.get('account.move.line')
		mrp_obj = self.pool.get('mrp.production')
		mrp_id = mrp_obj.browse(cr,uid,production_id)
		
		account_id = mrp_id.product_id.categ_id.property_stock_valuation_account_id.id
		
		"""Cari Move Line Id dengan Name = Name di MRP
		   dan account_id = account_id di product dengan 
		   property_stock_valuation_account_id nya
		"""
		move_line_id = move_line_obj.search(cr,uid,[('name','=', mrp_id.name),('account_id','=', account_id)])
		if move_line_id ==[]:
			return

		""" Cari date,ref dll"""
		date = move_line_obj.browse(cr,uid,move_line_id[0]).date

		"""Temukan Kembali id account move yang akan ditargetkan di update dengan 
		   COA Overheadnya , dengan id yang di peroleh dari account.move.line nya
		"""
		move_id = move_line_obj.browse(cr,uid,move_line_id[0]).move_id

		""" Loop Overheadnya"""
		for overhead in mrp_id.overhead_value_ids:
			debit ={
					'date'		 : date,
					'name'       : overhead.master_overhead_id.name,
					'account_id' : overhead.master_overhead_id.debit_account_id.id,
					'debit'      : overhead.value * production_qty,
					'credit'     : 0.0 
					}

			credit ={
					'date'		 : date,
					'name'       : overhead.master_overhead_id.name,
					'account_id' : overhead.master_overhead_id.credit_account_id.id,
					'debit'      : 0.0,
					'credit'     : overhead.value * production_qty
					}

			lines = [(0,0,debit), (0,0,credit)]		
			am_data = {
						'line_id'      : lines ,
					   }

			# import pdb;pdb.set_trace()
			am_id = move_obj.write(cr, uid,[move_id.id], am_data, context=context)

class overhead_value(osv.Model):
	_name = "vit.overhead.value"

	_columns = {
		'mrp_prod_id': fields.many2one('mrp.production', 'Mrp Reference',required=True, ondelete='cascade', select=True),
		'master_overhead_id': fields.many2one('vit.master.overheads', 'Overheads',required=True),
		'value' : fields.float('Overhead Per Pcs',required=True),
	}



class mrp_product_produce(osv.osv_memory):
	_name = "mrp.product.produce"
	_description = "Product Produce"
	_inherit = 'mrp.product.produce'


def do_produce(self, cr, uid, ids, context=None):
	res = super(mrp_product_produce, self).do_produce(cr, uid, ids, context=None)
	# import pdb;pdb.set_trace()
	return res