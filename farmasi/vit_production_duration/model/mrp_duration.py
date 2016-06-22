from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)

class mrp_duration(osv.osv):
	_name 		= "vit.mrp_duration"
	_rec_name 	= "date"
	_columns = {
		"date"			: fields.date("Sampai Dengan"),
		"detail_ids"	: fields.one2many("vit.mrp_duration_line","mrp_duration_id", "Details"),
	}

	def action_reload(self, cr, uid, ids, context=None):
		mo_obj = self.pool.get('mrp.production')

		mo_ids = mo_obj.search(cr, uid, [('state','=','done')], context=context)
		for mo in mo_obj.browse(cr, uid, mo_ids, context=context):

			data = {
				"mrp_duration_id" 	: ids[0],
				"product_id"		: mo.product_id.id,
				"mo_id"				: mo.id,
				"tgl_penimbangan" 	: False,
				"tgl_produksi"		: False,
				"tgl_release"		: False,
				"durasi"			: False,
			}
			self.create(cr, uid, data, context=context)


class mrp_duration_line(osv.
						osv):
	_name 		= "vit.mrp_duration_line"
	_columns = {

		"mrp_duration_id"	: fields.many2one("vit.mrp_duration", "MRP Duration"),
		"product_id"		: fields.many2one("product.product", "Product"),
		"mo_id"				: fields.many2one("mrp.production", "MO"),
		"tgl_penimbangan" 	: fields.date("Tgl. Penimbangan"),
		"tgl_produksi"		: fields.date("Tgl. Produksi"),
		"tgl_release"		: fields.date("Tgl. Release"),
		"durasi"			: fields.float("Durasi"),
	}

