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

		'date_start' : fields.date('Date Start'),
		'date_end'   : fields.date('Date End'),
	
		# 'model_forecast_type_id' : fields.many2one('vit.master.type', 'Model'),
		's_forcest' 		: fields.integer('S/2'),
		'm_forcest' 		: fields.integer('M/4'),
		'l_forcest' 		: fields.integer('L/6'),
		'xl_forcest' 		: fields.integer('XL/8'),
		'xxl_forcest' 		: fields.integer('XXL/10'),
		'xxxl_forcest' 		: fields.integer('LM 12'),
		'qty_forecast' 		: fields.function(_qty_forecast, string='Total Forecast',type="integer",store=True, method=True),
		'sisa'				: fields.function(_qty_sisa, string='Sisa',type="integer",store=True, method=True),
	
		'spk_id' 			: fields.many2one('vit.cutting.order', 'No SPK cutting'),
		'model_type_id' 	: fields.many2one('vit.master.type', 'Model'),
		's_cutting'			: fields.related('spk_id','s_order', type="integer", relation="vit.cutting.order", string="Rencana Cutting S/2 ", store=True),
		'm_cutting'			: fields.related('spk_id','m_order', type="integer", relation="vit.cutting.order", string="Rencana Cutting M/4 ", store=True),
		'l_cutting'			: fields.related('spk_id','l_order', type="integer", relation="vit.cutting.order", string="Rencana Cutting L/6 ", store=True),
		'xl_cutting'		: fields.related('spk_id','xl_order', type="integer", relation="vit.cutting.order", string="Rencana Cutting XL/8 ", store=True),
		'xxl_cutting'		: fields.related('spk_id','xxl_order', type="integer", relation="vit.cutting.order", string="Rencana Cutting XXL/10 ", store=True),
		'xxxl_cutting'		: fields.related('spk_id','xxxl_order', type="integer", relation="vit.cutting.order", string="Rencana Cutting LM 12 ", store=True),
		'qty_cutting' 		:fields.function(_qty_cutting, string='Total Rencana Cutting',type="integer",store=True),

		's_real_cutting'	: fields.related('spk_id','s_cut', type="integer", relation="vit.cutting.order", string="Realisasi Cutting S/2 ", store=True),
		'm_real_cutting'	: fields.related('spk_id','m_cut', type="integer", relation="vit.cutting.order", string="Realisasi Cutting M/4 ", store=True),
		'l_real_cutting'	: fields.related('spk_id','l_cut', type="integer", relation="vit.cutting.order", string="Realisasi Cutting L/6 ", store=True),
		'xl_real_cutting'	: fields.related('spk_id','xl_cut', type="integer", relation="vit.cutting.order", string="Realisasi Cutting XL/8 ", store=True),
		'xxl_real_cutting'	: fields.related('spk_id','xxl_cut', type="integer", relation="vit.cutting.order", string="Realisasi Cutting XXL/10 ", store=True),
		'xxxl_real_cutting'	: fields.related('spk_id','xxxl_cut', type="integer", relation="vit.cutting.order", string="Realisasi Cutting LM 12 ", store=True),
		'qty_real_cutting' 	: fields.function(_qty_real_cutting, string='Total Realisasi Cutting',type="integer",store=True),

		's_qc_prod'			: fields.related('spk_id','s_qc', type="integer", relation="vit.cutting.order", string="QC Produksi S/2", store=True),
		'm_qc_prod'			: fields.related('spk_id','m_qc', type="integer", relation="vit.cutting.order", string="QC Produksi M/4", store=True),
		'l_qc_prod'			: fields.related('spk_id','l_qc', type="integer", relation="vit.cutting.order", string="QC Produksi L/6", store=True),
		'xl_qc_prod'		: fields.related('spk_id','xl_qc', type="integer", relation="vit.cutting.order", string="QC Produksi XL/8", store=True),
		'xxl_qc_prod'		: fields.related('spk_id','xxl_qc', type="integer", relation="vit.cutting.order", string="QC Produksi XXL/10 ", store=True),
		'xxxl_qc_prod'		: fields.related('spk_id','xxxl_qc', type="integer", relation="vit.cutting.order", string="QC Produksi LM 12", store=True),
		'qty_qc_prod' 		:fields.function(_qty_qc_prod, string='Total Produksi',type="integer",store=True, method=True),
		

		# 's_mkl'			: fields.related('spk_id','s_order', type="integer", relation="vit.makloon.order", string="Makloon S/2", store=True),
		# 'm_mkl'			: fields.related('spk_id','m_order', type="integer", relation="vit.makloon.order", string="Makloon M/4", store=True),
		# 'l_mkl'			: fields.related('spk_id','l_order', type="integer", relation="vit.makloon.order", string="Makloon L/6", store=True),
		# 'xl_mkl'		: fields.related('spk_id','xl_order', type="integer", relation="vit.makloon.order", string="Makloon XL/8", store=True),
		# 'xxl_mkl'		: fields.related('spk_id','xxl_order', type="integer", relation="vit.makloon.order", string="Makloon XXL/10 ", store=True),
		# 'xxxl_mkl'		: fields.related('spk_id','xxxl_order', type="integer", relation="vit.makloon.order", string="Makloon LM 12", store=True),


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
		'xxxl_sisa_mkl'		: fields.integer('Sisa Makloon LM 12'),
		'qty_sisa_mkl' 		: fields.function(_qty_sisa_mkl, string='Total Sisa Makloon',type="integer",store=True, method=True),


		's_finish'		: fields.integer('Finish Good S/2'),
		'm_finish'		: fields.integer('Finish Good M/2'),
		'l_finish'		: fields.integer('Finish Good L/2'),
		'xl_finish'		: fields.integer('Finish Good XL/2'),
		'xxl_finish'	: fields.integer('Finish Good XXL/2'),
		'xxxl_finish'	: fields.integer('Finish Good LM 12'),
		'qty_finish'    : fields.function(_qty_finish, string='Total Finish Good',type="integer",store=True, method=True),

	}