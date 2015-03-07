from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class paket_produk_pendaftaran(osv.osv):
	_name 		= "mlm.paket_produk_pendaftaran"
	_columns 	= {
		'qty' 		: fields.float('Qty'),
		'paket_produk_id': fields.many2one('mlm.paket_produk','Produk Detail', ondelete="cascade"),
		'member_id' : fields.many2one("res.partner", 'Member'),
	}

class paket_produk(osv.osv):
	_name 		= "mlm.paket_produk"
	_columns 	= {
		'name' 		: fields.char('Name'),
		'harga' 		: fields.float('Harga'),
		'description' 		: fields.text('Description'),
		'paket_produk_detail_ids': fields.one2many('mlm.paket_produk_detail','paket_produk_id','Produk Detail', ondelete="cascade"),
	}

class paket_produk_detail(osv.osv):
	_name 		= "mlm.paket_produk_detail"
	_columns 	= {
		'paket_produk_id' : fields.many2one('mlm.paket_produk', 'Paket Produk ID'),
		'product_id'   : fields.many2one('product.product', 'Produk ID'),
		'qty' 		: fields.float('Qty'),
		'uom_id'	: fields.many2one('product.uom', 'Unit of Measure'),
	}
