from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)

class mrp_realisation(osv.osv):
	_name 		= "vit.mrp_realisation"
	_rec_name 	= "date_start"
	_columns = {
		"date_start"	: fields.date("Start Date"),
		"date_end"		: fields.date("End Date"),
		"detail_ids"	: fields.one2many("vit.mrp_realisation_line","mrp_realisation_id", "Details"),
	}

	def action_reload(self, cr, uid, ids, context=None):
		mo_obj = self.pool.get('mrp.production')
		mrp_realisation_line = self.pool.get('vit.mrp_realisation_line')


		for report in self.browse(cr, uid, ids, context=context):
			sql = "delete from vit_mrp_realisation_line where mrp_realisation_id=%s" %(report.id)
			cr.execute(sql)

			mo_ids = mo_obj.search(cr, uid, [
				('state','=','done'),
				('date_planned','>=',report.date_start),
				('date_planned','<=',report.date_end),
			], context=context)

			for mo in mo_obj.browse(cr, uid, mo_ids, context=context):
				tgl_penimbangan	= self.get_tgl_penimbangan(cr,uid,mo,context=context)
				tgl_produksi 	= self.get_tgl_produksi(cr,uid,mo,context=context)
				tgl_release 	= self.get_tgl_release(cr,uid,mo,context=context)

				qty_teoritis 	= self.get_qty_teoritis(cr,uid,mo,context=context)
				qty_release 	= self.get_qty_release(cr,uid,mo,context=context)
				data = {
					"mrp_realisation_id" 	: ids[0],
					"product_id"		: mo.product_id.id,
					"mo_id"				: mo.id,
					"tgl_penimbangan" 	: tgl_penimbangan,
					"tgl_produksi"		: tgl_produksi,
					"tgl_release"		: tgl_release,
					"durasi"			: False,
					"qty_teoritis"		: qty_teoritis,
					"qty_release"		: qty_release,
				}
				mrp_realisation_line.create(cr, uid, data, context=context)

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

	def get_tgl_release(self,cr,uid,mo,context=None):
		sp_obj = self.pool.get('stock.picking')
		sp_ids = sp_obj.search(cr, uid, [('origin','=', "%s:%s"%(mo.name, mo.batch_number))] ,context=context)
		if sp_ids:
			sp = sp_obj.browse(cr, uid, sp_ids[0], context=context)
			return sp.min_date
		return False

	def get_qty_teoritis(self,cr,uid,mo,context=None):
		return mo.product_qty

	def get_qty_release(self,cr,uid,mo,context=None):
		sp_obj = self.pool.get('stock.picking')
		sp_ids = sp_obj.search(cr, uid, [
			('origin','=', "%s:%s"%(mo.name, mo.batch_number)),
			('state','=','done')
		] ,context=context)
		# if mo.name == 'MO01244':
		# 	print "k"
		if sp_ids:
			total = 0.0
			for sp in sp_obj.browse(cr, uid, sp_ids, context=context):
				for move in sp.move_lines:
					total += move.product_uom_qty

			return total

		return False

class mrp_realisation_line(osv.osv):
	_name 		= "vit.mrp_realisation_line"
	_columns = {

		"mrp_realisation_id"	: fields.many2one("vit.mrp_realisation", "MRP Realisation"),
		"product_id"		: fields.many2one("product.product", "Product"),
		"mo_id"				: fields.many2one("mrp.production", "MO"),
		"batch_number"		: fields.related("mo_id", "batch_number", string="Batch Number",
									relation="mrp.producion", type="char"),
		"tgl_penimbangan" 	: fields.date("Tgl. Penimbangan"),
		"tgl_produksi"		: fields.date("Tgl. Produksi"),
		"tgl_release"		: fields.date("Tgl. Release"),
		"qty_teoritis"		: fields.float("Qty Teoritis"),
		"qty_release"		: fields.float("Qty Release"),
	}

