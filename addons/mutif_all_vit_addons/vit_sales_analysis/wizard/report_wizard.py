from osv import osv,fields
from openerp.tools.translate import _
import datetime 

class report_wizard(osv.TransientModel): 
	_name = 'vit_sales_analysis.report_wizard' 

	_columns = {
		'date_start' : fields.date('Invoice Date Start'),
		'date_end'   : fields.date('Invoice Date End'),
		'type'		 : fields.selection([('all','Penjualan L/R'),('produksi','Harga Pokok Produksi'),('pembelian','Harga Pokok Pembelian')],string='Type',required=True),
	}

	_defaults = {
		'date_start'  	: lambda *a : (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),	
		'date_end'		: fields.date.context_today,	
		'type'			: 'all',
	}

	def hasil(self, cr, uid, desc, report, view_id, domain, context):
		return {
			'name' : _(desc),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'vit_sales_analysis.sale_order_analysis',
			'res_id': report,
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			'domain' : domain,
			'context': context,
			'nodestroy': False,
			}

	def fill_table(self, cr, uid, ids, context=None):
		wizard  = self.browse(cr, uid, ids[0], context=context) 
		
		tp 		= wizard.type

		if tp == 'all':
			sub1	= ''
			sub2   	= 'Penjualan Bersih'
			sub3  	= ['Penjualan Kotor','Discount Normal','Retur Penjualan']
			desc 	= 'Laporan Laba / Rugi'
			domain 	= [('amount','!=',0),('sub2','=','Penjualan Bersih')]
			context = {"search_default_sub2_all":1,"search_default_sub3":1,"search_default_category":1,"search_default_product":1}			
		if tp == 'produksi':
			sub1	= 'Laba Kotor'
			sub2   	= 'Total Harga Pokok Produksi'
			sub3  	= ['Penjualan Kotor','Discount Normal','Retur Penjualan']
			desc 	= 'Laporan Harga Pokok Produksi'
			domain 	= [('amount','!=',0),('sub2','=','Total Harga Pokok Produksi'),('report_type','=','produksi')]
			context = {"search_default_sub1":1,"search_default_sub2_prod":1,"search_default_sub3":1,"search_default_category":1,"search_default_product":1}				
		if tp == 'pembelian':
			sub1	= 'Laba Kotor'	
			sub2   	= 'Total Harga Pokok Pembelian'
			sub3 	= ['Penjualan Kotor','Discount Normal','Retur Penjualan']
			desc	='Laporan Harga Pokok Pembelian'
			domain 	= [('amount','!=',0),('sub2','=','Total Harga Pokok Pembelian'),('report_type','=','pembelian')]
			context = {"search_default_sub1":1,"search_default_sub2_beli":1,"search_default_sub3":1,"search_default_category":1,"search_default_product":1}				
		#import pdb;pdb.set_trace()

		sql = "delete from vit_sales_analysis_sale_order_analysis"
		cr.execute(sql)
		for data in sub3 :
			sql = """INSERT INTO vit_sales_analysis_sale_order_analysis( 
				sub1,
				sub2,
				sub3,
				partner_id,
				product_id ,
				categ_id,
				report_type,
				quantity,
				amount
				)
			select 
				'%s' as sub1,
				'%s' as sub2,
				'%s' as sub3,
				ai.partner_id,	
				ail.product_id,
				tmpl.categ_id,
				pc.report_type,

				CASE WHEN '%s' = 'Penjualan Kotor' AND ai.type='out_invoice' THEN ail.quantity 
					WHEN '%s' = 'Discount Normal' AND ai.type='out_invoice' THEN -(ail.quantity)
					WHEN '%s' = 'Retur Penjualan' AND ai.type='out_refund' THEN -(ail.quantity)
					ELSE 0 END AS quantity,				

				CASE WHEN '%s' = 'Penjualan Bersih' AND '%s' = 'Penjualan Kotor' AND ai.type='out_invoice' THEN ail.quantity*ail.price_unit 
					WHEN '%s' <> 'Penjualan Bersih' AND '%s' = 'Penjualan Kotor' AND ai.type='out_invoice' THEN ail.quantity*tmpl.standard_price

					WHEN '%s' = 'Penjualan Bersih' AND '%s' = 'Discount Normal' AND ai.type='out_invoice' THEN -((ail.quantity*ail.price_unit)*(ail.discount/100))
					WHEN '%s' <> 'Penjualan Bersih' AND '%s' = 'Discount Normal' AND ai.type='out_invoice' THEN -((ail.quantity*tmpl.standard_price)*(ail.discount/100))

					WHEN '%s' = 'Penjualan Bersih' AND '%s' = 'Retur Penjualan' AND ai.type='out_refund' THEN -((ail.quantity*ail.price_unit)-(ail.quantity*ail.price_unit)*(ail.discount/100))
					WHEN '%s' <> 'Penjualan Bersih' AND '%s' = 'Retur Penjualan' AND ai.type='out_refund' THEN -((ail.quantity*ail.price_unit)-(ail.quantity*ail.price_unit)*(ail.discount/100))

					WHEN '%s' = 'Retur Penjualan' AND ai.type='out_refund' THEN -((ail.quantity*ail.price_unit)-(ail.quantity*ail.price_unit)*(ail.discount/100))
					ELSE 0 END AS amount

			from 
				account_invoice_line ail
				left join product_product p on ail.product_id = p.id
				left join product_template tmpl on p.product_tmpl_id = tmpl.id 
				left join product_category pc on pc.id = tmpl.categ_id
				left join account_invoice ai on ail.invoice_id = ai.id

				where 
					ai.date_invoice >= '%s' 
					and ai.date_invoice <= '%s' 
					and ai.type in ('out_invoice','out_refund')
					and ai.state in ('open','paid')

			""" % (
				sub1, #1
				sub2, #2
				data, #3
				data, #4
				data, #5
				data, #6

				sub2,
				data,
				sub2,
				data,

				sub2,
				data,
				sub2,
				data,

				sub2,
				data,
				sub2,
				data,

				data, 
				wizard.date_start, 
				wizard.date_end)

			cr.execute(sql)
			cr.commit()

		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_sales_analysis', 'view_sales_analysis_name_tree')
		view_id = view_ref and view_ref[1] or False,	

		return self.hasil(cr, uid, desc, ids[0], view_id, domain, context)