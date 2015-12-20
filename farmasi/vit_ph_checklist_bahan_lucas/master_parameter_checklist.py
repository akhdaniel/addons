from openerp.osv import osv, fields
import platform
import os
import csv
import logging
import time
import openerp.addons.decimal_precision as dp


_logger = logging.getLogger(__name__)


class master_checklist(osv.osv):
	_name = "vit_ph_checklist_bahan_lucas.master_checklist"
	_description = 'Master Checklist'

	_columns = {
		'name'       : fields.char('Name', required=True),
		'appeareance': fields.many2one('ir.model', string="Appearance"), #appearance
		'product_id' : fields.many2one('product.product', 'Product', select=True),
	}

	def _get_default_appeareance(self, cr, uid, context=None):
		if context is None:
			context = {}
		overhead_value_ids = []

		ir_model_id   = self.pool.get('ir.model').search(cr,uid,[('model','=','stock.move')])
		return ir_model_id[0]

	_defaults = {
		'appeareance' : _get_default_appeareance
	}


class master_advance_checklist(osv.osv):
	_name = "vit_ph_checklist_bahan_lucas.master_advance_checklist"
	_description = 'Master Advance Checklist'

	_columns = {
		'name'       : fields.char('Name', required=True),
		'appeareance': fields.many2one('ir.model', string="Appearance"), #appearance
		'product_id' : fields.many2one('product.product', 'Product', select=True),
	}

	def _get_default_appeareance(self, cr, uid, context=None):
		if context is None:
			context = {}
		overhead_value_ids = []

		ir_model_id   = self.pool.get('ir.model').search(cr,uid,[('model','=','stock.move')])
		return ir_model_id[0]

	_defaults = {
		'appeareance' : _get_default_appeareance
	}
