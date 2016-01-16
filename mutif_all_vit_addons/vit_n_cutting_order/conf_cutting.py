from osv import osv, fields
import platform
import os
import csv
import logging
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.addons.vit_upi_uang_persediaan import terbilang_func

_logger = logging.getLogger(__name__)



class conf_cutting(osv.osv):
	_name = "conf.cutting"
	_description = 'Configuration'
	_rec_name = 'loop_size'
		
	
	_columns = {
		'categ_id' : fields.many2one('product.category','Category'),
		'loop_size' : fields.integer('Jumlah Size'),
		'notes' :fields.text('Notes',translate=True),

	

}


class vit_master_journal(osv.osv):
	_name = "vit.master.journal"
	_description = 'Master Journal'
	# _rec_name = 'loop_size'
		
	_columns = {
		# 'target_model_id': fields.many2one('ir.model', 'Target Model'),
		'name'       : fields.char('Name', required=True),
		'appeareance': fields.many2one('ir.model', string="Appearance"), #appearance
		'journal_id' : fields.many2one('account.journal', 'Journal', required=True),     
		'credit_account_id'    : fields.many2one('account.account', 'Credit Account', 
			required=True,
			domain="[('type','!=','view')]" ),
		'debit_account_id'     : fields.many2one('account.account', 'Debit Account', 
			required=True,
			domain="[('type','!=','view')]"),
		'product_id' : fields.many2one('product.product', 'Product Jasa',),
		'is_active'  : fields.boolean('Active?'),	
}

	def _get_default_appeareance(self, cr, uid, context=None):
		if context is None:
			context = {}
		overhead_value_ids = []

		ir_model_id   = self.pool.get('ir.model').search(cr,uid,[('model','=','vit.cutting.order')])
		return ir_model_id[0]

	_defaults = {
		'appeareance' : _get_default_appeareance,
		'is_active'	  : True,
	}



class vit_master_location(osv.osv):
	_name = "vit.master.location"
	_description = 'Master Location'
		
	_columns = {
		'name'       : fields.char('Name Method', required=True),
		'source_loc_id': fields.many2one('stock.location', string="Source Location",required=True),
		'dest_loc_id': fields.many2one('stock.location', string="Destination Location",required=True),
}

	