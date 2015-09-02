from osv import osv,fields
from openerp.tools.translate import _
import datetime 

class report_wizard(osv.TransientModel): 
	_name = 'vit_order_analysis.report_wizard' 

	_columns = {
		'date_start' : fields.date('Invoice Date Start'),
		'date_end'   : fields.date('Invoice Date End'),
	}

	_defaults = {
		'date_start'  : lambda *a : (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),	
		'date_end'	: lambda *a : (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),	
	}

	def fill_table(self, cr, uid, ids, context=None):
		wizard = self.browse(cr, uid, ids[0], context=context) 

		sql = "delete from vit_order_analysis_sale_order_analysis"
		cr.execute(sql)
		sql = """INSERT INTO vit_order_analysis_sale_order_analysis( 
order_id,
product_id ,
categ_id,
order_date,
name_template ,
real_order,
qty_order ,
delivered ,
back_order
)
select 
	so.id,
	p.id,
	tmpl.categ_id,
	so.date_order,
	p.name_template,
	so_l.real_order_qty,
	so_l.product_uom_qty,
	(select sum(product_qty) from stock_move 
		where 
		sale_line_id=so_l.id and state='done'
		and location_dest_id = (select id from stock_location where name = 'Customers' )
		and location_id=(select id from stock_location where name = 'Lokasi Barang Jadi' )
	) as delivered,
	(select sum(product_qty) from stock_move 
		where sale_line_id=so_l.id and state<>'done' and state<>'draft'
		and location_dest_id = (select id from stock_location where name = 'Customers' )
		and location_id=(select id from stock_location where name = 'Lokasi Barang Jadi' )
	) as back_order

from 
	sale_order_line so_l 
	inner join product_product p on so_l.product_id = p.id
	inner join sale_order so on so_l.order_id = so.id
	inner join product_template tmpl on p.product_tmpl_id = tmpl.id 
where 
	so.date_order >= '%s' 
	and so.date_order <= '%s' 
	and so.state <> 'draft'
""" % (wizard.date_start, wizard.date_end)

		cr.execute(sql)
		cr.commit()


		# update unfilled record
		sql = "update vit_order_analysis_sale_order_analysis set unfilled = real_order - coalesce(delivered,0) - coalesce(back_order,0)"
		cr.execute(sql)

		return {
			# 'name': 'Report Wizard',
			# 'view_type': 'tree',
			# 'view_mode': 'tree',
			# 'res_model': 'vit_order_analysis.sale_order_analysis',
			# 'type': 'ir.actions.act_window',
			# 'context': context,		
		}

