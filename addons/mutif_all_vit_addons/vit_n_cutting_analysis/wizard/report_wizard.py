from osv import osv,fields
from openerp.tools.translate import _
import datetime 
from datetime import datetime

class report_wizard(osv.TransientModel): 
	_name = 'vit_n_cutting_analysis.report_wizard' 

	_columns = {
		'month'		:fields.selection([('0','All'),('1','January'), ('2','February'), ('3','March'), ('4','April'),
			('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'),
			('10','October'), ('11','November'), ('12','December')], 'Month', required=True),
		'year_id' 	: fields.many2one('account.fiscalyear', 'Year', required=True ),
	}

	def fill_table(self, cr, uid, ids, context=None):
		wizard = self.browse(cr, uid, ids[0], context=context)
		# date = wizard.date_start # String : 2015-10-1
		# dt = datetime.strptime(date,'%Y-%m-%d')
		# year_id = self.pool.get('account.fiscalyear').search(cr,uid,[('name','=',dt.year)])
		# 
		# import pdb;pdb.set_trace()
		sql = "delete from vit_n_cutting_analysis_cutting_analysis"
		cr.execute(sql)
		if wizard.month !='0':
			sql ="""INSERT INTO vit_n_cutting_analysis_cutting_analysis(
					forecast_name,
					forecast_id,
					model_type_id,
					month,
					year_id,
					s_forcest,
					m_forcest,
					l_forcest,
					xl_forcest,
					xxl_forcest,
					xxxl_forcest,

					cutting_spk_id,
					month_spk,
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

					cutting_makloon_id,
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
					   A.name 
					  ,A.id
					  ,A.type_product_id
				      ,A.month 
				      ,A.year_id 
				
				      ,A.s_forecast 
				      ,A.m_forecast 
				      ,A.l_forecast 
				      ,A.xl_forecast 
				      ,A.xxl_forecast 
				      ,A.xxxl_forecast 
				      ,C.id as cutting_spk
				      ,to_char(C.date_start_cutting, 'MM') as month2
				      ,C.s_order
				      ,C.m_order
				      ,C.l_order
				      ,C.xl_order
				      ,C.xxl_order
				      ,C.xxxl_order
				      ,C.s_cut
				      ,C.m_cut
				      ,C.l_cut
				      ,C.xl_cut
				      ,C.xxl_cut
				      ,C.xxxl_cut
				      ,C.s_qc
				      ,C.m_qc
				      ,C.l_qc
				      ,C.xl_qc
				      ,C.xxl_qc
				      ,C.xxxl_qc

				      ,D.id as makloon_spk
				      ,D.s_order
				      ,D.m_order
				      ,D.l_order
				      ,D.xl_order
				      ,D.xxl_order
				      ,D.xxxl_order
				      ,Es0.product_qty as s_sisa
				      ,Em0.product_qty as m_sisa
				      ,El0.product_qty as l_sisa
				      ,Exl0.product_qty as xl_sisa
				      ,Exxl0.product_qty as xxl_sisa
				      ,Exxxl0.product_qty as xxxl_sisa
				      ,Es.product_qty as s_finish
				      ,Em.product_qty as m_finish
				      ,El.product_qty as l_finish
				      ,Exl.product_qty as xl_finish
				      ,Exxl.product_qty as xxl_finish
				      ,Exxxl.product_qty as xxxl_finish
				    
									
					from
						vit_forecast_master A
						left join vit_forecast_cutting_order_list B on A.id = B.cutting_order_list_id 
						left join vit_cutting_order C on C.id = B.cutting_id 
						left join vit_makloon_order D on C.id = D.origin
						left join stock_move Es0 on Es0.spk_mkl_id = D.id and  Es0.name = 'S' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Em0 on Em0.spk_mkl_id = D.id and  Em0.name = 'M' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move El0 on El0.spk_mkl_id = D.id and  El0.name = 'L' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exl0 on Exl0.spk_mkl_id = D.id and  Exl0.name = 'XL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exxl0 on Exxl0.spk_mkl_id = D.id and  Exxl0.name = 'XXL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exxxl0 on Exxxl0.spk_mkl_id = D.id and  Exxxl0.name = 'XXXL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Es on Es.spk_mkl_id = D.id and  Es.name = 'S' and D.state ='done'
						left join stock_move Em on Em.spk_mkl_id = D.id and  Em.name = 'M' and D.state ='done'
						left join stock_move El on El.spk_mkl_id = D.id and  El.name = 'L' and D.state ='done'
						left join stock_move Exl on Exl.spk_mkl_id = D.id and  Exl.name = 'XL' and D.state ='done'
						left join stock_move Exxl on Exxl.spk_mkl_id = D.id and  Exxl.name = 'XXL' and D.state ='done'
						left join stock_move Exxxl on Exxxl.spk_mkl_id = D.id and  Exxxl.name = 'XXXL' and D.state ='done'
					where 
					 	A.month = '%s' and A.year_id = '%s'
						
					group by 
						A.name,A.id,A.month,A.s_forecast,A.year_id,month2,cutting_spk,makloon_spk,s_sisa,m_sisa,l_sisa,xl_sisa,xxl_sisa,xxxl_sisa,s_finish,m_finish,l_finish,xl_finish,xxl_finish,xxxl_finish
	 			 """%(wizard.month, wizard.year_id.id)

 		else:
 			sql ="""INSERT INTO vit_n_cutting_analysis_cutting_analysis(
					forecast_name,
					forecast_id,
					model_type_id,
					month,
					year_id,
					s_forcest,
					m_forcest,
					l_forcest,
					xl_forcest,
					xxl_forcest,
					xxxl_forcest,

					cutting_spk_id,
					month_spk,
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

					cutting_makloon_id,
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
					   A.name 
					  ,A.id
				      ,A.type_product_id
				      ,A.month 
				      ,A.year_id 
				      ,A.s_forecast 
				      ,A.m_forecast 
				      ,A.l_forecast 
				      ,A.xl_forecast 
				      ,A.xxl_forecast 
				      ,A.xxxl_forecast 
				      ,C.id as cutting_spk
				      ,to_char(C.date_start_cutting, 'MM') as month2
				      ,C.s_order
				      ,C.m_order
				      ,C.l_order
				      ,C.xl_order
				      ,C.xxl_order
				      ,C.xxxl_order
				      ,C.s_cut
				      ,C.m_cut
				      ,C.l_cut
				      ,C.xl_cut
				      ,C.xxl_cut
				      ,C.xxxl_cut
				      ,C.s_qc
				      ,C.m_qc
				      ,C.l_qc
				      ,C.xl_qc
				      ,C.xxl_qc
				      ,C.xxxl_qc

				      ,D.id as makloon_spk
				      ,D.s_order
				      ,D.m_order
				      ,D.l_order
				      ,D.xl_order
				      ,D.xxl_order
				      ,D.xxxl_order
				      ,Es0.product_qty as s_sisa
				      ,Em0.product_qty as m_sisa
				      ,El0.product_qty as l_sisa
				      ,Exl0.product_qty as xl_sisa
				      ,Exxl0.product_qty as xxl_sisa
				      ,Exxxl0.product_qty as xxxl_sisa
				      ,Es.product_qty as s_finish
				      ,Em.product_qty as m_finish
				      ,El.product_qty as l_finish
				      ,Exl.product_qty as xl_finish
				      ,Exxl.product_qty as xxl_finish
				      ,Exxxl.product_qty as xxxl_finish
				    
									
					from
						vit_forecast_master A
						left join vit_forecast_cutting_order_list B on A.id = B.cutting_order_list_id 
						left join vit_cutting_order C on C.id = B.cutting_id 
						left join vit_makloon_order D on C.id = D.origin
						left join stock_move Es0 on Es0.spk_mkl_id = D.id and  Es0.name = 'S' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Em0 on Em0.spk_mkl_id = D.id and  Em0.name = 'M' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move El0 on El0.spk_mkl_id = D.id and  El0.name = 'L' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exl0 on Exl0.spk_mkl_id = D.id and  Exl0.name = 'XL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exxl0 on Exxl0.spk_mkl_id = D.id and  Exxl0.name = 'XXL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exxxl0 on Exxxl0.spk_mkl_id = D.id and  Exxxl0.name = 'XXXL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Es on Es.spk_mkl_id = D.id and  Es.name = 'S' and D.state ='done'
						left join stock_move Em on Em.spk_mkl_id = D.id and  Em.name = 'M' and D.state ='done'
						left join stock_move El on El.spk_mkl_id = D.id and  El.name = 'L' and D.state ='done'
						left join stock_move Exl on Exl.spk_mkl_id = D.id and  Exl.name = 'XL' and D.state ='done'
						left join stock_move Exxl on Exxl.spk_mkl_id = D.id and  Exxl.name = 'XXL' and D.state ='done'
						left join stock_move Exxxl on Exxxl.spk_mkl_id = D.id and  Exxxl.name = 'XXXL' and D.state ='done'
					where 
					 	A.year_id = '%s'
						
					group by 
						A.name,A.id,A.month,A.s_forecast,A.year_id,month2,cutting_spk,makloon_spk,s_sisa,m_sisa,l_sisa,xl_sisa,xxl_sisa,xxxl_sisa,s_finish,m_finish,l_finish,xl_finish,xxl_finish,xxxl_finish
	 			 """%(wizard.year_id.id)


 		cr.execute(sql)
 		cr.commit()


 		# Query Untuk Special Request
 		if wizard.month !='0':
			sql ="""INSERT INTO vit_n_cutting_analysis_cutting_analysis(
 					model_type_id,
					month,
					cutting_spk_id,
					month_spk,
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

					cutting_makloon_id,
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
					  c.type_product_id
					  ,to_char(C.date_start_cutting, 'MM') as month2
				      ,C.id as cutting_spk
				      ,to_char(C.date_start_cutting, 'MM') as month2
				      ,C.s_order
				      ,C.m_order
				      ,C.l_order
				      ,C.xl_order
				      ,C.xxl_order
				      ,C.xxxl_order
				      ,C.s_cut
				      ,C.m_cut
				      ,C.l_cut
				      ,C.xl_cut
				      ,C.xxl_cut
				      ,C.xxxl_cut
				      ,C.s_qc
				      ,C.m_qc
				      ,C.l_qc
				      ,C.xl_qc
				      ,C.xxl_qc
				      ,C.xxxl_qc

				      ,D.id as makloon_spk
				      ,D.s_order
				      ,D.m_order
				      ,D.l_order
				      ,D.xl_order
				      ,D.xxl_order
				      ,D.xxxl_order
				      ,Es0.product_qty as s_sisa
				      ,Em0.product_qty as m_sisa
				      ,El0.product_qty as l_sisa
				      ,Exl0.product_qty as xl_sisa
				      ,Exxl0.product_qty as xxl_sisa
				      ,Exxxl0.product_qty as xxxl_sisa
				      ,Es.product_qty as s_finish
				      ,Em.product_qty as m_finish
				      ,El.product_qty as l_finish
				      ,Exl.product_qty as xl_finish
				      ,Exxl.product_qty as xxl_finish
				      ,Exxxl.product_qty as xxxl_finish
				    
									
					from
						--vit_forecast_master A
						vit_cutting_order C
						--left join vit_forecast_cutting_order_list B on A.id = B.cutting_order_list_id 
						--left join vit_cutting_order C on C.id = B.cutting_id 
						left join vit_makloon_order D on C.id = D.origin
						left join stock_move Es0 on Es0.spk_mkl_id = D.id and  Es0.name = 'S' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Em0 on Em0.spk_mkl_id = D.id and  Em0.name = 'M' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move El0 on El0.spk_mkl_id = D.id and  El0.name = 'L' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exl0 on Exl0.spk_mkl_id = D.id and  Exl0.name = 'XL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exxl0 on Exxl0.spk_mkl_id = D.id and  Exxl0.name = 'XXL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exxxl0 on Exxxl0.spk_mkl_id = D.id and  Exxxl0.name = 'XXXL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Es on Es.spk_mkl_id = D.id and  Es.name = 'S' and D.state ='done'
						left join stock_move Em on Em.spk_mkl_id = D.id and  Em.name = 'M' and D.state ='done'
						left join stock_move El on El.spk_mkl_id = D.id and  El.name = 'L' and D.state ='done'
						left join stock_move Exl on Exl.spk_mkl_id = D.id and  Exl.name = 'XL' and D.state ='done'
						left join stock_move Exxl on Exxl.spk_mkl_id = D.id and  Exxl.name = 'XXL' and D.state ='done'
						left join stock_move Exxxl on Exxxl.spk_mkl_id = D.id and  Exxxl.name = 'XXXL' and D.state ='done'
					where 
					 	C.is_special = 'True' and C.state != 'draft' and to_char(C.date_start_cutting, 'MM') = '%s' and to_char(C.date_start_cutting, 'YYYY') = '%s'
						
					group by 
						month2,cutting_spk,makloon_spk,s_sisa,m_sisa,l_sisa,xl_sisa,xxl_sisa,xxxl_sisa,s_finish,m_finish,l_finish,xl_finish,xxl_finish,xxxl_finish
	 			 """ %(wizard.month,wizard.year_id.name)


 		else:
 			sql ="""INSERT INTO vit_n_cutting_analysis_cutting_analysis(
 					model_type_id,
					month,
					cutting_spk_id,
					month_spk,
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

					cutting_makloon_id,
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
					  c.type_product_id
					  ,to_char(C.date_start_cutting, 'MM') as month2
				      ,C.id as cutting_spk
				      ,to_char(C.date_start_cutting, 'MM') as month2
				      ,C.s_order
				      ,C.m_order
				      ,C.l_order
				      ,C.xl_order
				      ,C.xxl_order
				      ,C.xxxl_order
				      ,C.s_cut
				      ,C.m_cut
				      ,C.l_cut
				      ,C.xl_cut
				      ,C.xxl_cut
				      ,C.xxxl_cut
				      ,C.s_qc
				      ,C.m_qc
				      ,C.l_qc
				      ,C.xl_qc
				      ,C.xxl_qc
				      ,C.xxxl_qc

				      ,D.id as makloon_spk
				      ,D.s_order
				      ,D.m_order
				      ,D.l_order
				      ,D.xl_order
				      ,D.xxl_order
				      ,D.xxxl_order
				      ,Es0.product_qty as s_sisa
				      ,Em0.product_qty as m_sisa
				      ,El0.product_qty as l_sisa
				      ,Exl0.product_qty as xl_sisa
				      ,Exxl0.product_qty as xxl_sisa
				      ,Exxxl0.product_qty as xxxl_sisa
				      ,Es.product_qty as s_finish
				      ,Em.product_qty as m_finish
				      ,El.product_qty as l_finish
				      ,Exl.product_qty as xl_finish
				      ,Exxl.product_qty as xxl_finish
				      ,Exxxl.product_qty as xxxl_finish
				    
									
					from
						--vit_forecast_master A
						vit_cutting_order C
						--left join vit_forecast_cutting_order_list B on A.id = B.cutting_order_list_id 
						--left join vit_cutting_order C on C.id = B.cutting_id 
						left join vit_makloon_order D on C.id = D.origin
						left join stock_move Es0 on Es0.spk_mkl_id = D.id and  Es0.name = 'S' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Em0 on Em0.spk_mkl_id = D.id and  Em0.name = 'M' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move El0 on El0.spk_mkl_id = D.id and  El0.name = 'L' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exl0 on Exl0.spk_mkl_id = D.id and  Exl0.name = 'XL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exxl0 on Exxl0.spk_mkl_id = D.id and  Exxl0.name = 'XXL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Exxxl0 on Exxxl0.spk_mkl_id = D.id and  Exxxl0.name = 'XXXL' and ( D.state ='draft' or D.state ='assigned')
						left join stock_move Es on Es.spk_mkl_id = D.id and  Es.name = 'S' and D.state ='done'
						left join stock_move Em on Em.spk_mkl_id = D.id and  Em.name = 'M' and D.state ='done'
						left join stock_move El on El.spk_mkl_id = D.id and  El.name = 'L' and D.state ='done'
						left join stock_move Exl on Exl.spk_mkl_id = D.id and  Exl.name = 'XL' and D.state ='done'
						left join stock_move Exxl on Exxl.spk_mkl_id = D.id and  Exxl.name = 'XXL' and D.state ='done'
						left join stock_move Exxxl on Exxxl.spk_mkl_id = D.id and  Exxxl.name = 'XXXL' and D.state ='done'
					where 
					 	C.is_special = 'True' and C.state != 'draft' and to_char(C.date_start_cutting, 'YYYY') = '%s'
						
					group by 
						month2,cutting_spk,makloon_spk,s_sisa,m_sisa,l_sisa,xl_sisa,xxl_sisa,xxxl_sisa,s_finish,m_finish,l_finish,xl_finish,xxl_finish,xxxl_finish
	 			 """ %(wizard.year_id.name)

 		cr.execute(sql)
 		cr.commit()

 		# update kolom year_id
		sql = """ update vit_n_cutting_analysis_cutting_analysis set
				year_id = '%s'
				""" %(wizard.year_id.id)
		cr.execute(sql)
		cr.commit()

 		# update Kolom2 jumlah
		sql = """update vit_n_cutting_analysis_cutting_analysis set
				qty_forecast = coalesce(s_forcest,0) + coalesce(m_forcest,0) + coalesce(l_forcest,0) + coalesce(xl_forcest,0) + coalesce(xxl_forcest,0) + coalesce(xxxl_forcest,0) ,
				qty_cutting = coalesce(s_cutting,0) + coalesce(m_cutting,0) + coalesce(l_cutting,0) + coalesce(xl_cutting,0) + coalesce(xxl_cutting,0) + coalesce(xxxl_cutting,0) ,
				qty_real_cutting = coalesce(s_real_cutting,0) + coalesce(m_real_cutting,0) + coalesce(l_real_cutting,0) + coalesce(xl_real_cutting,0) + coalesce(xxl_real_cutting,0) + coalesce(xxxl_real_cutting,0),
				qty_qc_prod = coalesce(s_qc_prod,0) + coalesce(m_qc_prod,0) + coalesce(l_qc_prod,0) + coalesce(xl_qc_prod,0) + coalesce(xxl_qc_prod,0) + coalesce(xxxl_qc_prod,0),
				qty_mkl = coalesce(s_mkl,0) + coalesce(m_mkl,0) + coalesce(l_mkl,0) + coalesce(xl_mkl,0) + coalesce(xxl_mkl,0) + coalesce(xxxl_mkl,0),
				qty_sisa_mkl = coalesce(s_sisa_mkl,0) + coalesce(m_sisa_mkl,0) + coalesce(l_sisa_mkl,0) + coalesce(xl_sisa_mkl,0) + coalesce(xxl_sisa_mkl,0) + coalesce(xxxl_sisa_mkl,0),
				qty_finish = coalesce(s_finish,0) + coalesce(m_finish,0) + coalesce(l_finish,0) + coalesce(xl_finish,0) + coalesce(xxl_finish,0) + coalesce(xxxl_finish,0)
				
				""" 
		cr.execute(sql)
		cr.commit()


 		
		return{}
