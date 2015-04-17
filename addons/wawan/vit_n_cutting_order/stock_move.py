from osv import osv, fields
import platform
import os
import csv
import logging
import time
import openerp.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)


class stock_move(osv.osv):
	_inherit = "stock.move"
	_columns = {
	'spk_mkl_id':fields.many2one('vit.makloon.order', 'Makloon Order'),
	'is_copy':fields.boolean('Is Copied ?'),
	}

stock_move()

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
	_name = "stock.picking"
	_inherit = "stock.picking"
	_description = "Picking List"

	_columns = {  
		'makloon_id':fields.many2one('vit.makloon.order', 'Makloon Order'),
		'reward_steam':fields.float('Reward Steam'),
		'is_updated' : fields.boolean('Updated Cost Price ?'),
		'is_invoiced'  : fields.boolean('Is Invoiced Makloon ?'),
		'is_makloon_categ'  : fields.boolean('Is Category Makloon ?'),

	}

	_defaults = {
		'reward_steam' : 0.0,
	}




class stock_picking_in(osv.osv):
	_inherit = "stock.picking.in"
	_columns = {
		'reward_steam':fields.float('Reward Steam'),
		'is_updated' : fields.boolean('Updated Cost Price ?'),
		'is_invoiced'  : fields.boolean('Is Invoiced Makloon ?'),
		'is_makloon_categ'  : fields.boolean('Is Category Makloon ?'),
		
	}

	_defaults = {
		'reward_steam' : 0.0,
	}

	def create_invoice(self, cr, uid, ids, context=None):
		
		#search jurnal purchase
		jurnal = self.pool.get('account.journal').search(cr,uid,[('type','=','purchase')],context=context)[0]
		prod = self.pool.get('product.product').browse(cr,uid,self._get_ongkos_jahit(cr,uid,context),context=context)
		prod_name = self.pool.get('product.product').browse(cr,uid,self._get_ongkos_jahit(cr,uid,context),context=context).name		
		
		## Salah Satu Price 
		spk_id= self.pool.get('vit.makloon.order').search(cr,uid,[('name','=',self.browse(cr,uid,ids[0],).origin)],context=context)[0]
		spk = self.pool.get('vit.makloon.order').browse(cr,uid,spk_id,context=context)

		sql = """select sum(product_qty) from stock_move WHERE picking_id =' %s'"""%(self.browse(cr,uid,ids[0],).id)
		cr.execute(sql)
		qty = cr.fetchone()
		qty = qty[0]
		# spk.jurnal_value_ids[0].master_jurnal_id.name
		for overhead in spk.jurnal_value_ids:
			# create juga supplier invoicenya
			inv_makloon = self.pool.get('account.invoice').create(cr,uid,{'partner_id' : self.browse(cr,uid,ids[0],).partner_id.id,
																	'origin'  : self.browse(cr,uid,ids[0],).name,
																	'account_id' :overhead.master_jurnal_id.credit_account_id.id, 
																	'journal_id' : jurnal,
																	'type' : 'in_invoice',
																	}),

			#search product (id 1 bawaan dari openerp pasti product service)
			self.pool.get('account.invoice.line').create(cr,uid,{'invoice_id' : inv_makloon,
																	# 'product_id': overhead.master_jurnal_id.product_id.id,
																	'name':overhead.master_jurnal_id.name,
																	'account_id':overhead.master_jurnal_id.debit_account_id.id,
																	'quantity' : qty,
																	'price_unit': overhead.value,
																	})
			

		# Create Invoice Reward
		reward_id = self.pool.get('vit.master.journal').search(cr,uid,[('name','=','Reward Steam')],context=context)[0]
		reward = self.pool.get('vit.master.journal').browse(cr,uid,reward_id,context=context)
		inv_makloon = self.pool.get('account.invoice').create(cr,uid,{'partner_id' : self.browse(cr,uid,ids[0],).partner_id.id,
																	'origin'  : self.browse(cr,uid,ids[0],).name,
																	'account_id' :reward.credit_account_id.id, 
																	'journal_id' : jurnal,
																	'type' : 'in_invoice',
																	}),

		#search product (id 1 bawaan dari openerp pasti product service)
		self.pool.get('account.invoice.line').create(cr,uid,{'invoice_id' : inv_makloon,
																	# 'product_id': overhead.master_jurnal_id.product_id.id,
																	'name':reward.name,
																	'account_id':reward.debit_account_id.id,
																	'price_unit': self.browse(cr,uid,ids[0],).reward_steam,})
		

		""" Kembalikan Lagi Field is_invoiced = False, supaya tombol Create Invoice di Stok picking menjadi Hide"""
		self.write(cr,uid,ids,{'is_invoiced':False},context=context)
		
		# import pdb;pdb.set_trace()

		return {
		
		}


	def _get_ongkos_jahit(self, cr, uid, context=None):
		
		product = self.pool.get('product.product').search(cr,uid,[('name','=','Ongkos Jahit')])
		if product ==[] :
			raise osv.except_osv( 'Tidak Ditemukan!' , 'Setting --> Product : Name :Ongkos Jahit, Categ_id : Jasa, Income Account : 1-131006 Persediaan Dalam Proses Makloon, Expense Account: 2-110006 Hutang Maklun upah jahit ')
		else:
			prod = self.pool.get('product.product').browse(cr,uid,product)[0]
			prod_id = prod.id
			return prod_id

stock_picking_in()
