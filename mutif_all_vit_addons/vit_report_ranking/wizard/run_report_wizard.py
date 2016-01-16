#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import netsvc
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class report_wizard(osv.TransientModel): 
	_name = 'report.wizard' 

	_columns = {
		'date_start' : fields.date('Date Start',required=True),
		'date_end'   : fields.date('Date End',required=True),
		'type'		 : fields.selection([('customer_order','Top Customer Order'),
										('customer_seller','Top Customer Seller'),
										('supplier','Top Supplier'),
										('makloon','Top makloon'),
										('product_order','Top Product Order'),
										('product_seller','Top Product Seller')],'Type',required=True),
	}

	_defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-01'),
        'date_end': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
	}

	def hasil(self, cr, uid, desc, report, view_id, domain, model, context):
		return {
			'name' : _(desc),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': model,
			'res_id': report,
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			'domain' : domain,
			'context': context,
			'nodestroy': True,
			}


	def fill_table(self, cr, uid, ids, context=None):
		wizard  = self.browse(cr, uid, ids[0], context=context) 
		like	= '%'
		desc	= 'Top 20 Ranking '+str(wizard.date_start)+' to '+str(wizard.date_end)+' ('+str(wizard.type)+')'
		domain 	= []
		context = {}
		##################################
		# Customer Order Ranking
		##################################
		if wizard.type == 'customer_order':
			model   = 'vit.customer.order.ranking'			
			#import pdb;pdb.set_trace()
			sql = "delete from vit_customer_order_ranking"
			cr.execute(sql)
			sql = """INSERT INTO vit_customer_order_ranking( 
				partner_id,
				total_qty,
				date_start,
				date_end)
				select 
					foo.partner_id as partner_id,
					foo.total_qty as total_qty,
					'%s' as date_start,
					'%s' as date_end
				from
					(select 
						so.partner_id as partner_id,	
						sum(so_l.real_max_order) as total_qty
					from 
						sale_order_line so_l
						inner join sale_order so on so_l.order_id = so.id
					where 
						so.date_order >= '%s' 
						and so.date_order <= '%s' 
						and so.state <> 'cancel'
					group by partner_id
					order by total_qty desc) as foo
				where total_qty >0

				limit 20				
				""" % (wizard.date_start, wizard.date_end,wizard.date_start, wizard.date_end)

			cr.execute(sql)
			cr.commit()

			view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_report_ranking', 'view_customer_order_ranking_tree_temporary')
			view_id = view_ref and view_ref[1] or False,

		#####################################
		# Customer Seller ranking
		#####################################
		elif wizard.type == 'customer_seller':
			model   = 'vit.customer.seller.ranking'			
			#import pdb;pdb.set_trace()
			sql = "delete from vit_customer_seller_ranking"
			cr.execute(sql)
			sql = """INSERT INTO vit_customer_seller_ranking( 
				partner_id,
				total_qty,
				total_price,
				date_start,
				date_end)
				select foo.partner as partner_id,
					sum(foo.total_qty) as total_qty,
					sum(foo.total_price) as total_price,
					'%s' as date_start,
					'%s' as date_end					
				from
					(select so.partner_id as partner,
						sum(sol.real_order_qty) as total_qty,
						ai.sub_total as total_price
					from sale_order so 
						left join sale_order_line sol on sol.order_id=so.id
						left join account_invoice ai on ai.partner_id=so.partner_id and ai.origin ilike ('%s'||so.name||'%s')

					where ai.date_invoice >= '%s'
						and ai.date_invoice <= '%s'
						and so.state not in ('draft','cancel')
						and ai.state not in ('draft','cancel')
						and ai.type = 'out_invoice'

					group by so.partner_id,ai.sub_total) as foo
				group by foo.partner
				order by total_qty desc

				limit 20				
				""" % (wizard.date_start, wizard.date_end,like,like,wizard.date_start, wizard.date_end)

			cr.execute(sql)
			cr.commit()

			view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_report_ranking', 'view_customer_seller_ranking_tree_temporary')
			view_id = view_ref and view_ref[1] or False,			

		#####################################
		# Supplier
		#####################################
		elif wizard.type == 'supplier':
			model   = 'vit.supplier1.ranking'			
			#import pdb;pdb.set_trace()
			sql = "delete from vit_supplier1_ranking"
			cr.execute(sql)
			sql = """INSERT INTO vit_supplier1_ranking( 
				partner_id,
				total_qty,
				total_price,
				date_start,
				date_end)
				select
					foo.partner as partner_id,
					sum(foo.total_qty) as total_qty,
					sum(foo.total_price) as total_price,
					'%s' as date_start,
					'%s' as date_end					
				from
					(select po.partner_id as partner,sum(pol.product_qty) as total_qty,ai.sub_total as total_price
						from purchase_order po
							left join purchase_order_line pol on pol.order_id=po.id
							left join account_invoice ai on ai.partner_id=po.partner_id and ai.origin ilike ('%s'||po.name||'%s')
							left join res_partner_res_partner_category_rel res_rel on res_rel.partner_id = po.partner_id
							left join res_partner_category rpc on res_rel.category_id = rpc.id

						where ai.date_invoice >= '%s'
							and ai.date_invoice <= '%s'
							and po.state not in ('draft','cancel')
							and ai.state not in ('draft','cancel')
							and ai.type = 'in_invoice'
							and rpc.name = 'Supplier'

						group by po.partner_id,ai.sub_total) as foo
				group by foo.partner
				order by total_price desc

				limit 20				
				""" % (wizard.date_start, wizard.date_end,like,like,wizard.date_start, wizard.date_end)

			cr.execute(sql)
			cr.commit()

			view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_report_ranking', 'view_supplier_ranking_tree_temporary')
			view_id = view_ref and view_ref[1] or False,

		#####################################
		# Makloon
		#####################################
		elif wizard.type == 'makloon':
			model   = 'vit.makloon1.ranking'			
			#import pdb;pdb.set_trace()
			sql = "delete from vit_makloon1_ranking"
			cr.execute(sql)
			sql = """INSERT INTO vit_makloon1_ranking( 
				partner_id,
				total_qty,
				total_price,
				date_start,
				date_end)
				select vmo.partner_id as partner_id,
					(sum(vmo.s_order)+sum(vmo.m_order)+sum(vmo.l_order)+sum(vmo.xl_order)+sum(vmo.xxl_order)+sum(vmo.xxxl_order)) as total_qty,
					ai.sub_total as total_price,
					'%s' as date_start,
					'%s' as date_end
				from vit_makloon_order vmo
					left join account_invoice ai on ai.partner_id=vmo.partner_id and ai.spk_mkl_id = vmo.id
					left join res_partner_res_partner_category_rel res_rel on res_rel.partner_id = vmo.partner_id
					left join res_partner_category rpc on res_rel.category_id = rpc.id

				where ai.date_invoice >= '%s'
					and ai.date_invoice <= '%s'
					and vmo.state <> 'draft'
					and ai.state not in ('draft','cancel')
					and ai.type = 'in_invoice'
					and rpc.code = 'MKLN'

				group by vmo.partner_id,ai.sub_total

				limit 20				
				""" % (wizard.date_start, wizard.date_end,wizard.date_start, wizard.date_end)

			cr.execute(sql)
			cr.commit()

			view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_report_ranking', 'view_makloon_ranking_tree_temporary')
			view_id = view_ref and view_ref[1] or False,

		#####################################
		# Product Order
		#####################################
		elif wizard.type == 'product_order':
			model   = 'vit.product.order1.ranking'			
			#import pdb;pdb.set_trace()
			sql = "delete from vit_product_order1_ranking"
			cr.execute(sql)
			sql = """INSERT INTO vit_product_order1_ranking( 
				product_id,
				total_qty_order,
				date_start,
				date_end)
				select 
					foo.product as product_id,
					sum(foo.qty) as total_qty_order,
					'%s' as date_start,
					'%s' as date_end
				from
					(select 
						sol.product_id as product,
						sum(sol.real_max_order) as qty		
					from sale_order_line sol
						left join product_product pp on sol.product_id = pp.id
						left join product_template pt on pp.product_tmpl_id = pt.id
						left join sale_order so on sol.order_id = so.id
					where so.date_order >= '%s' 
						and so.date_order <= '%s' 
						and sol.real_max_order is not null
						and (pt.categ_id <> 19 and pt.categ_id <> 23)
						and sol.state not in ('draft','cancel')
					group by sol.product_id,sol.real_max_order
					order by sol.real_max_order desc) as foo
				group by foo.product
				order by total_qty_order desc

				limit 20			
				""" % (wizard.date_start, wizard.date_end,wizard.date_start, wizard.date_end)

			cr.execute(sql)
			cr.commit()

			view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_report_ranking', 'view_product_order_ranking_tree_temporary')
			view_id = view_ref and view_ref[1] or False,

		#####################################
		# Product Seller
		#####################################
		elif wizard.type == 'product_seller':
			model   = 'vit.product.seller1.ranking'			
			#import pdb;pdb.set_trace()
			sql = "delete from vit_product_seller1_ranking"
			cr.execute(sql)
			sql = """INSERT INTO vit_product_seller1_ranking( 
				product_id,
				total_qty_seller,
				date_start,
				date_end)
				select foo.product as product_id, 
					sum(foo.qty) as total_qty_seller,
					'%s' as date_start,
					'%s' as date_end
				from
					(select 
						ail.product_id as product,
						sum(ail.quantity) as qty		
					from account_invoice_line ail
						left join product_product pp on ail.product_id = pp.id
						left join product_template pt on pp.product_tmpl_id = pt.id
						left join account_invoice ai on ai.id=ail.invoice_id
					where (pt.categ_id <> 19 and pt.categ_id <> 23)
						and ai.date_invoice >= '%s'
						and ai.date_invoice <= '%s'
						and ai.state not in ('draft','cancel')
						and ai.type = 'out_invoice'
					group by ail.product_id,ail.quantity
					order by ail.quantity desc) as foo
				group by foo.product
				order by total_qty_seller desc

				limit 20			
				""" % (wizard.date_start, wizard.date_end,wizard.date_start, wizard.date_end)

			cr.execute(sql)
			cr.commit()

			view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_report_ranking', 'view_product_seller_ranking_tree_temporary')
			view_id = view_ref and view_ref[1] or False,

		return self.hasil(cr, uid, desc, ids[0], view_id, domain, model,  context)

report_wizard()	