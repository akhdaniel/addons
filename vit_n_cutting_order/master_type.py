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



class vit_master_type(osv.osv):
	_name = "vit.master.type"
	_description = 'Master Type'
	_rec_name = 'model_product'
		
	
	_columns = {
		'model_product' : fields.char('Model/Type', required=True,),
		'product_id' : fields.many2one('product.product','Sample Product', domain="['|',('categ_id.name','=','Mutif'),('categ_id.name','=','Little Mutif')]"),
		'main_qty'		: fields.integer('Body'),
		'variation_qty'	: fields.integer('Variation'),
		'categ_id' : fields.char('Category'),
		'cost_model': fields.float('Makloon Price'),
		'cost_model_cut' :fields.float('Cutting Price'),
		'image': fields.binary('image',type="binary"),
	}

	_sql_constraints = [
		('model_product_uniq', 'unique(model_product)', 'Model Ini Sudah Tersedia, Silahkan Buat Model lain dengan Product Sample Lain!'),
	]

	def on_change_categ_id(self, cr, uid, ids, categ_id, context=None):
		categ_id_obj = self.pool.get('product.category')
		categ_id = categ_id_obj.browse(cr,uid,categ_id,context=context)

	def on_change_product_id(self, cr, uid, ids, product_id, context=None):
		product_obj = self.pool.get('product.product')
		product = product_obj.browse(cr, uid, product_id, context=context)

		if product_id != False:
			return {
				'value' : {
					'model_product' : product.type_model,
					'categ_id'		: product.categ_id.name,
			}
		}
		else:
			return {
				'value' : {
					'model_product' :'',
					'categ_id'		:'',
			}
		}
		


class vit_category(osv.osv):
	_name = "vit.category"
	_description = 'Category'
	
	_columns = {
		# 'name' : fields.char('Name'),
		'name': fields.many2one('product.category','Category', change_default=True, domain="[('type','=','normal')]" ,help="Select category for the current product"),

	}


	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['name'], context=context)
		
		res = []
		for record in reads:
			name = record['name'][1]
			if record['name'][1]:
				name = record['name'][1]
			res.append((record['id'], name))
		return res



	