from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class member_paket_produk(osv.osv):
	_name 		= "mlm.member_paket_produk"
	_columns 	= {
		'qty' 		: fields.float('Qty',required=True),
		'paket_produk_id': fields.many2one('mlm.paket_produk','Product Detail', ondelete="cascade",required=True),
		'member_id' : fields.many2one("res.partner", 'Member'),
	}

class paket_produk(osv.osv):
	_name 		= "mlm.paket_produk"

	def _get_harga(self, cr, uid, ids, field_name, arg, context=None):
		result = {}
		for paket in self.browse(cr,uid,ids,context=context):
			lines 			= paket.paket_produk_detail_ids
			if not lines :
				return result

			uom_obj			= self.pool.get('product.uom')
			total_harga = 0
			for product in lines :
				product_price 	= product.harga
				qty 			= product.qty

				harga 			= product_price*qty

				total_harga		+= harga 
			result[paket.id] = total_harga

		return result

	_columns 	= {
		'name' 						: fields.char('Name',required=True),
		#'harga' 					: fields.float('Harga'),
		'description' 				: fields.text('Description'),
		'paket_produk_detail_ids'	: fields.one2many('mlm.paket_produk_detail','paket_produk_id',
			'Product Detail', ondelete="cascade"),
		#'discount'					: fields.float('Discount',help="Ketik minus untuk mendapatkan potongan harga paket"),		
		'harga'						: fields.function(_get_harga,type="float",string="Total Price", readonly=True), # harga otomatis dihitung dari harga dan jumlah produk yang di input
	}


class paket_produk_detail(osv.osv):
	_name 		= "mlm.paket_produk_detail"
	_columns 	= {
		'paket_produk_id' : fields.many2one('mlm.paket_produk', 'Product Package ID'),
		'product_id'   : fields.many2one('product.product', 'Product',required=True),
		'qty' 		: fields.float('Qty',required=True),
		'harga'		: fields.float('Harga',required=True),
		'uom_id'	: fields.many2one('product.uom', 'Unit of Measure',required=True),
	}

	_defaults ={
		'qty'	: 1,
		}

	def onchange_product_id(self, cr, uid, ids, product_id):
		product_obj = self.pool.get('product.product')
		if not product_id:
			return {'value': {
				'uom_id': False,
				}}
		product = product_obj.browse(cr, uid, product_id)
		return {'value': {
			'harga' : product.lst_price,
			'uom_id': product.uom_id.id,
			}}