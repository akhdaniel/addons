from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)

class mrp_duration(osv.osv):
	_name 		= "vit.mrp_duration"
	_rec_name 	= "date_start"
	_columns = {
		"date_start"	: fields.date("Start Date"),
		"date_end"		: fields.date("End Date"),
		"detail_ids"	: fields.one2many("vit.mrp_duration_line","mrp_duration_id", "Details"),
	}

	def action_reload(self, cr, uid, ids, context=None):
		mo_obj = self.pool.get('mrp.production')
		mrp_duration_line = self.pool.get('vit.mrp_duration_line')


		for report in self.browse(cr, uid, ids, context=context):
			sql = "delete from vit_mrp_duration_line where mrp_duration_id=%s" %(report.id)
			cr.execute(sql)

			mo_ids = mo_obj.search(cr, uid, [
				('state','=','done'),
				('date_planned','>=',report.date_start),
				('date_planned','<=',report.date_end),
			], context=context)

			for mo in mo_obj.browse(cr, uid, mo_ids, context=context):
				tgl_penimbangan	= self.get_tgl_penimbangan(cr,uid,mo,context=context)
				tgl_produksi 	= self.get_tgl_produksi(cr,uid,mo,context=context)
				tgl_release 	= self.tgl_release(cr,uid,mo,context=context)
				data = {
					"mrp_duration_id" 	: ids[0],
					"product_id"		: mo.product_id.id,
					"mo_id"				: mo.id,
					"tgl_penimbangan" 	: tgl_penimbangan,
					"tgl_produksi"		: tgl_produksi,
					"tgl_release"		: tgl_release,
					"durasi"			: False,
				}
				mrp_duration_line.create(cr, uid, data, context=context)

	def get_tgl_penimbangan(self,cr,uid,mo,context=None):
		for wo in mo.workcenter_lines:
			if wo.sequence == 1:
				return wo.date_start
		return False

	def get_tgl_produksi(self,cr,uid,mo,context=None):
		# return mo.date_planned

		for wo in mo.workcenter_lines:
			if wo.sequence == 2:
				return wo.date_start
		return False

	def tgl_release(self,cr,uid,mo,context=None):
		sp_obj = self.pool.get('stock.picking')
		sp_ids = sp_obj.search(cr, uid, [('origin','=', "%s:%s"%(mo.name, mo.batch_number))] ,context=context)
		if sp_ids:
			sp = sp_obj.browse(cr, uid, sp_ids[0], context=context)
			return sp.min_date
		return False

class mrp_duration_line(osv.
						osv):
	_name 		= "vit.mrp_duration_line"
	_columns = {

		"mrp_duration_id"	: fields.many2one("vit.mrp_duration", "MRP Duration"),
		"product_id"		: fields.many2one("product.product", "Product"),
		"mo_id"				: fields.many2one("mrp.production", "MO"),
		"batch_number"		: fields.related("mo_id", "batch_number", string="Batch Number",
									relation="mrp.producion", type="char"),
		"tgl_penimbangan" 	: fields.date("Tgl. Penimbangan"),
		"tgl_produksi"		: fields.date("Tgl. Produksi"),
		"tgl_release"		: fields.date("Tgl. Release"),
		"durasi"			: fields.float("Durasi"),
	}
