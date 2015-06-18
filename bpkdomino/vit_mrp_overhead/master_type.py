from openerp.osv import osv, fields
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
		# 'product_id' : fields.many2one('product.product','Sample Product', domain="['|',('categ_id.name','=','Mutif'),('categ_id.name','=','Little Mutif')]"),
		'main_qty'		: fields.integer('Body'),
		'variation_qty'	: fields.integer('Variation'),
		'categ_id' : fields.char('Category'),
		'cost_makl': fields.float('Makloon Price'),
		'cost_cut' :fields.float('Cutting Price'),
		'kancing_price' :fields.float('Kancing Price'),
		'image': fields.binary('image',type="binary"),
		'biaya_lain_ids':fields.one2many('vit.biaya.lain.type','master_type_id','Biaya Lain'),
	}

	_sql_constraints = [
		('model_product_uniq', 'unique(model_product)', 'Model Ini Sudah Tersedia, Silahkan Buat Model lain dengan Product Sample Lain!'),
	]

	def on_change_categ_id(self, cr, uid, ids, categ_id, context=None):
		categ_id_obj = self.pool.get('product.category')
		categ_id = categ_id_obj.browse(cr,uid,categ_id,context=context)


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

#class untuk value jurnal-jurnal tambahan dalam cutting relasi dengan master jurnal 
class biaya_lain(osv.Model):
	_name = "vit.biaya.lain.type"

	_columns = {
		'master_type_id': fields.many2one('vit.master.type', 'Master Reference',required=True, ondelete='cascade', select=True),
		'master_jurnal_id': fields.many2one('vit.master.journal', 'Biaya Lain',required=True),
		'value' : fields.float('Biaya Per Pcs',required=True),
	}


	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['master_jurnal_id'], context=context)

		res = []
		for record in reads:
			name = record['master_jurnal_id'][1]
			if record['master_jurnal_id'][1]:
				name = record['master_jurnal_id'][1]
			res.append((record['id'], name))
		return res
biaya_lain()

	