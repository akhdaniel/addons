from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class cutting_analysis(osv.osv):
	_name 		= "vit_n_cutting_analysis.cutting_analysis"
	_description = 'Cutting Analysis'


	def _qty_forecast(self, cr, uid, ids, name, arg, context=None):
		# import pdb;pdb.set_trace()
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_forcest +  qty[0].m_forcest +  qty[0].l_forcest+  qty[0].xl_forcest +  qty[0].xxl_forcest+  qty[0].xxxl_forcest
		return res

	def _qty_cutting(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_cutting +  qty[0].m_cutting +  qty[0].l_cutting +  qty[0].xl_cutting +  qty[0].xxl_cutting +  qty[0].xxxl_cutting 
		return res

	def _qty_real_cutting(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_real_cutting +  qty[0].m_real_cutting +  qty[0].l_real_cutting +  qty[0].xl_real_cutting +  qty[0].xxl_real_cutting +  qty[0].xxxl_real_cutting 
		return res

	def _qty_qc_prod(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_qc_prod +  qty[0].m_qc_prod +  qty[0].l_qc_prod +  qty[0].xl_qc_prod +  qty[0].xxl_qc_prod +  qty[0].xxxl_qc_prod 
		return res


	def _qty_mkl(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_mkl +  qty[0].m_mkl +  qty[0].l_mkl +  qty[0].xl_mkl +  qty[0].xxl_mkl +  qty[0].xxxl_mkl
		return res

	def _qty_sisa_mkl(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_sisa_mkl +  qty[0].m_sisa_mkl +  qty[0].l_sisa_mkl +  qty[0].xl_sisa_mkl +  qty[0].xxl_sisa_mkl +  qty[0].xxxl_sisa_mkl
		return res

	def _qty_finish(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_finish +  qty[0].m_finish +  qty[0].l_finish +  qty[0].xl_finish +  qty[0].xxl_finish +  qty[0].xxxl_finish
		return res

	def _qty_sisa(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].qty_forecast -  qty[0].qty_cutting
		return res



	_columns 	= {
		'forecast_name' : fields.char('Name'),
		'forecast_id' 	: fields.many2one('vit.forecast.master', 'Forecast Master'),
		'month'			: fields.selection([('1','January'), ('2','February'), ('3','March'), ('4','April'),
			('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'),
			('10','October'), ('11','November'), ('12','December')], 'Month', required=False),
		'month_spk'			: fields.selection([('1','January'), ('2','February'), ('3','March'), ('4','April'),
			('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'),
			('10','October'), ('11','November'), ('12','December')], 'Month', required=False),
		'year_id' 		: fields.many2one('account.fiscalyear', 'Year', required=False ),
		'cutting_spk_id': fields.many2one('vit.cutting.order', 'No SPK cutting'),
		'cutting_makloon_id' 	: fields.many2one('vit.makloon.order', 'No SPK Makloon'),
		'model_type_id' 	: fields.many2one('vit.master.type', 'Model'),


		# 'model_forecast_type_id' : fields.many2one('vit.master.type', 'Model'),
		's_forcest' 		: fields.integer('S/2'),
		'm_forcest' 		: fields.integer('M/4'),
		'l_forcest' 		: fields.integer('L/6'),
		'xl_forcest' 		: fields.integer('XL/8'),
		'xxl_forcest' 		: fields.integer('XXL/10'),
		'xxxl_forcest' 		: fields.integer('XXXL/12'),																					
		'qty_forecast' 		: fields.function(_qty_forecast, string='Total Forecast',type="integer",store=True, method=True),
		# 'qty_forecast' 		: fields.function(_qty_forecast, string='Total',type="integer"),
		'sisa'				: fields.function(_qty_sisa, string='Sisa',type="integer",store=True, method=True),


		's_cutting'			: fields.integer('Plan Cut S/2'),
		'm_cutting'			: fields.integer('Plan Cut M/4'),
		'l_cutting'			: fields.integer('Plan Cut L/6'), 
		'xl_cutting'		: fields.integer('Plan Cut XL/8'),
		'xxl_cutting'		: fields.integer('Plan Cut XXL/10'),
		'xxxl_cutting'		: fields.integer('Plan Cut XXXL/12'),
		'qty_cutting' 		: fields.integer('Plan Cut Qty'),

		's_real_cutting'	: fields.integer('Real Cut S/2'),
		'm_real_cutting'	: fields.integer('Real Cut M/4'),
		'l_real_cutting'	: fields.integer('Real Cut L/6'),
		'xl_real_cutting'	: fields.integer('Real Cut XL/8'),
		'xxl_real_cutting'	: fields.integer('Real Cut XXL/10'),
		'xxxl_real_cutting'	: fields.integer('Real Cut XXXL/12'),
		'qty_real_cutting' 	: fields.function(_qty_real_cutting, string='Total Realisasi Cutting',type="integer",store=True),

		's_qc_prod'			: fields.integer('QC Produksi S/2'),
		'm_qc_prod'			: fields.integer('QC Produksi M/4'),
		'l_qc_prod'			: fields.integer('QC Produksi L/6'),
		'xl_qc_prod'		: fields.integer('QC Produksi xL/8'),
		'xxl_qc_prod'		: fields.integer('QC Produksi XXL/10'),
		'xxxl_qc_prod'		: fields.integer('QC Produksi XXXL/12'),
		'qty_qc_prod' 		:fields.function(_qty_qc_prod, string='Total Produksi',type="integer",store=True, method=True),
	
		's_mkl'			: fields.integer('Makloon S/2'),
		'm_mkl'		    : fields.integer('Makloon M/2'),
		'l_mkl'			: fields.integer('Makloon L/2'),
		'xl_mkl'		: fields.integer('Makloon XL/2'),
		'xxl_mkl'		: fields.integer('Makloon XXL/2'),
		'xxxl_mkl'		: fields.integer('Makloon LM 12'),
		'qty_mkl' 		: fields.function(_qty_mkl, string='Total Makloon',type="integer",store=True, method=True),

		

		's_sisa_mkl'		: fields.integer('Sisa Makloon S/2'),
		'm_sisa_mkl'		: fields.integer('Sisa Makloon M/2'),
		'l_sisa_mkl'		: fields.integer('Sisa Makloon L/2'),
		'xl_sisa_mkl'		: fields.integer('Sisa Makloon XL/2'),
		'xxl_sisa_mkl'		: fields.integer('Sisa Makloon XXL/2'),
		'xxxl_sisa_mkl'		: fields.integer('Sisa Makloon XXXL 12'),
		'qty_sisa_mkl' 		: fields.function(_qty_sisa_mkl, string='Total Sisa Makloon',type="integer",store=True, method=True),
		
		'date_start' : fields.date('Date Start'),
		# 'date_end'   : fields.date('Date End'),
	
		
		's_finish'		: fields.integer('Finish Good S/2'),
		'm_finish'		: fields.integer('Finish Good M/2'),
		'l_finish'		: fields.integer('Finish Good L/2'),
		'xl_finish'		: fields.integer('Finish Good XL/2'),
		'xxl_finish'	: fields.integer('Finish Good XXL/2'),
		'xxxl_finish'	: fields.integer('Finish Good XXXL 12'),
		'qty_finish'    : fields.function(_qty_finish, string='Total Finish Good',type="integer",store=True, method=True),

	}

	def _qty_forecast(self, cr, uid, ids, name, arg, context=None):
		# import pdb;pdb.set_trace()
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		res[qty[0].id] = qty[0].s_forcest +  qty[0].m_forcest +  qty[0].l_forcest+  qty[0].xl_forcest +  qty[0].xxl_forcest+  qty[0].xxxl_forcest
		return res