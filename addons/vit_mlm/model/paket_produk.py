from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class paket_produk(osv.osv):
	_name 		= "mlm.paket_produk"
	_columns 	= {
		'name' 		: fields.char('Name'),
		'harga' 		: fields.float('Harga'),
		'description' 		: fields.text('Description'),
	}

class paket_produk_detail(osv.osv):
	_name 		= "mlm.paket_produk_detail"
	_columns 	= {
		'paket_produk_id' : fields.many2one('mlm.paket_produk', 'Paket Produk ID'),
		'product_id'   : fields.many2one('product.product', 'Produk ID'),
		'qty' 		: fields.float('Qty'),
	}
