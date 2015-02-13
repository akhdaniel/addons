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

	