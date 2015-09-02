from osv import osv,fields
from openerp.tools.translate import _
import datetime 

class report_wizard(osv.TransientModel): 
	_name = 'vit_n_cutting_analysis.report_wizard' 

	_columns = {
		'date_start' : fields.date('Date Start'),
		'date_end'   : fields.date('Date End'),
	}

	_defaults = {
		'date_start'  : lambda *a : (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),	
		'date_end'	: lambda *a : (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),	
	}

	def fill_table(self, cr, uid, ids, context=None):
		wizard = self.browse(cr, uid, ids[0], context=context)
		# import pdb;pdb.set_trace()

		sql = "delete from vit_n_cutting_analysis_cutting_analysis"
		cr.execute(sql)
		sql ="""INSERT INTO vit_n_cutting_analysis_cutting_analysis(
				date_start,
				date_end,
				model_type_id,
				spk_id,
				s_cutting,
				m_cutting,
				l_cutting,
				xl_cutting,
				xxl_cutting,
				xxxl_cutting,
				s_real_cutting,
				m_real_cutting,
				l_real_cutting,
				xl_real_cutting,
				xxl_real_cutting,
				xxxl_real_cutting,
				s_qc_prod,
				m_qc_prod,
				l_qc_prod,
				xl_qc_prod,
				xxl_qc_prod,
				xxxl_qc_prod,
				s_mkl,
				m_mkl,
				l_mkl,
				xl_mkl,
				xxl_mkl,
				xxxl_mkl,
				s_sisa_mkl,
				m_sisa_mkl,
				l_sisa_mkl,
				xl_sisa_mkl,
				xxl_sisa_mkl,
				xxxl_sisa_mkl,
				s_finish,
				m_finish,
				l_finish,
				xl_finish,
				xxl_finish,
				xxxl_finish
			)
				select
					vco.date_start_cutting,
					vco.date_end_cutting,
					vco.type_product_id,
					vco.id,
					sum(vco.s_order),
					sum(vco.m_order),
					sum(vco.l_order),
					sum(vco.xl_order),
					sum(vco.xxl_order),
					sum(vco.xxxl_order),
					sum(vco.s_cut),
					sum(vco.m_cut),
					sum(vco.l_cut),
					sum(vco.xl_cut),
					sum(vco.xxl_cut),
					sum(vco.xxxl_cut),
					sum(vco.s_qc),
					sum(vco.m_qc),
					sum(vco.l_qc),
					sum(vco.xl_qc),
					sum(vco.xxl_qc),
					sum(vco.xxxl_qc),
					(select sum(s_order) from vit_makloon_order where origin = vco.id and state!='draft'),
					(select sum(m_order) from vit_makloon_order where origin = vco.id and state!='draft'),
					(select sum(l_order) from vit_makloon_order where origin = vco.id and state!='draft'),
					(select sum(xl_order) from vit_makloon_order where origin = vco.id and state!='draft'),
					(select sum(xxl_order) from vit_makloon_order where origin = vco.id and state!='draft'),
					(select sum(xxxl_order) from vit_makloon_order where origin = vco.id and state!='draft'),


					(select sum(sm.product_qty) from stock_move sm
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where vmo.origin = vco.id and (sm.state = 'draft' or sm.state = 'assigned') and sm.name = 'S') as  s_sisa_per_move,

					(select sum(sm.product_qty) from stock_move sm
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where vmo.origin = vco.id and (sm.state = 'draft' or sm.state = 'assigned') and sm.name = 'M') as  s_sisa_per_move,

					(select sum(sm.product_qty) from stock_move sm
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where vmo.origin = vco.id and (sm.state = 'draft' or sm.state = 'assigned') and sm.name = 'L') as  s_sisa_per_move,

					(select sum(sm.product_qty) from stock_move sm
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where vmo.origin = vco.id and (sm.state = 'draft' or sm.state = 'assigned') and sm.name = 'XL') as  s_sisa_per_move,

					(select sum(sm.product_qty) from stock_move sm
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where vmo.origin = vco.id and (sm.state = 'draft' or sm.state = 'assigned') and sm.name = 'XXL') as  s_sisa_per_move,

					(select sum(sm.product_qty) from stock_move sm
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where vmo.origin = vco.id and (sm.state = 'draft' or sm.state = 'assigned') and sm.name = 'XXXL') as  s_sisa_per_move,

					(select sum(sm.product_qty) from stock_move sm 
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where  vmo.origin = vco.id and sm.state = 'done' and sm.name = 'S') as s_finish,
					
					(select sum(sm.product_qty) from stock_move sm 
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where  vmo.origin = vco.id and sm.state = 'done' and sm.name = 'M') as s_finish,

					(select sum(sm.product_qty) from stock_move sm 
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where  vmo.origin = vco.id and sm.state = 'done' and sm.name = 'L') as s_finish,
					
					(select sum(sm.product_qty) from stock_move sm 
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where  vmo.origin = vco.id and sm.state = 'done' and sm.name = 'XL') as s_finish,
					
					(select sum(sm.product_qty) from stock_move sm 
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where  vmo.origin = vco.id and sm.state = 'done' and sm.name = 'XXL') as s_finish,
					
					(select sum(sm.product_qty) from stock_move sm 
						inner join vit_makloon_order vmo on spk_mkl_id = vmo.id
						where  vmo.origin = vco.id and sm.state = 'done' and sm.name = 'XXXL') as s_finish
					
					/*
					(select sum(product_qty) from stock_move  
						where spk_mkl_id = vmo.id and (state = 'draft' or state = 'assigned') and name = 'S') as  s_sisa,
					(select product_qty from stock_move 
						where spk_mkl_id = vmo.id and (state = 'draft' or state = 'assigned') and name = 'M') as m_sisa,
					(select product_qty from stock_move 
						where spk_mkl_id = vmo.id and (state = 'draft' or state = 'assigned') and name = 'L') as l_sisa,
					(select product_qty from stock_move 
						where spk_mkl_id = vmo.id and (state = 'draft' or state = 'assigned') and name = 'XL') as xl_sisa,
					(select product_qty from stock_move 
						where spk_mkl_id = vmo.id and (state = 'draft' or state = 'assigned') and name = 'XXL') as xxl_sisa,
					(select sum(product_qty) from stock_move 
						where spk_mkl_id = vmo.id and (state = 'draft' or state = 'assigned') and name = 'XXXL') as xxxl_sisa,
					

					(select sum(product_qty) from stock_move 
						where spk_mkl_id = vmo.id and state = 'done' and name = 'S') as s_finish,
					(select sum(product_qty) from stock_move 
						where spk_mkl_id = vmo.id and state = 'done' and name = 'M') as m_finish,
					(select sum(product_qty) from stock_move 
						where spk_mkl_id = vmo.id and state = 'done' and name = 'L') as l_finish,
					(select sum(product_qty) from stock_move 
						where spk_mkl_id = vmo.id and state = 'done' and name = 'XL') as xl_finish,
					(select sum(product_qty) from stock_move 
						where spk_mkl_id = vmo.id and state = 'done' and name = 'XXL') as xxl_finish,
					(select sum(product_qty) from stock_move 
						where spk_mkl_id = vmo.id and state = 'done' and name = 'XXXL') as s_finish
					
					*/
				from
					vit_cutting_order vco
					inner join vit_makloon_order vmo
					on vco.id = vmo.origin
				where 
					vco.date_start_cutting >='%s' 
					and vco.date_end_cutting <='%s'
					and vco.state ='finish_qc' 
					or vco.state ='open'
				group by 
					vco.type_product_id,vco.id,vmo.id
 			 """%(wizard.date_start, wizard.date_end)

 		cr.execute(sql)
 		cr.commit()

 		# update Kolom2 jumlah
		sql = """update vit_n_cutting_analysis_cutting_analysis set qty_cutting = coalesce(s_cutting,0) + coalesce(m_cutting,0) + coalesce(l_cutting,0) + coalesce(xl_cutting,0) + coalesce(xxl_cutting,0) + coalesce(xxxl_cutting,0) ,
				qty_real_cutting = coalesce(s_real_cutting,0) + coalesce(m_real_cutting,0) + coalesce(l_real_cutting,0) + coalesce(xl_real_cutting,0) + coalesce(xxl_real_cutting,0) + coalesce(xxxl_real_cutting,0),
				qty_qc_prod = coalesce(s_qc_prod,0) + coalesce(m_qc_prod,0) + coalesce(l_qc_prod,0) + coalesce(xl_qc_prod,0) + coalesce(xxl_qc_prod,0) + coalesce(xxxl_qc_prod,0),
				qty_mkl = coalesce(s_mkl,0) + coalesce(m_mkl,0) + coalesce(l_mkl,0) + coalesce(xl_mkl,0) + coalesce(xxl_mkl,0) + coalesce(xxxl_mkl,0),
				qty_sisa_mkl = coalesce(s_sisa_mkl,0) + coalesce(m_sisa_mkl,0) + coalesce(l_sisa_mkl,0) + coalesce(xl_sisa_mkl,0) + coalesce(xxl_sisa_mkl,0) + coalesce(xxxl_sisa_mkl,0),
				qty_finish = coalesce(s_finish,0) + coalesce(m_finish,0) + coalesce(l_finish,0) + coalesce(xl_finish,0) + coalesce(xxl_finish,0) + coalesce(xxxl_finish,0)
				
				""" 
		cr.execute(sql)
		cr.commit()

		sql="""update vit_n_cutting_analysis_cutting_analysis set sisa = coalesce(qty_forecast,0) - coalesce(qty_cutting,0)"""
		cr.execute(sql)
		cr.commit()


		return{}
