from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class product_category(osv.osv):
	_inherit = "product.category"

	_columns = {
		'report_type': fields.selection([('produksi','Harga Pokok Produksi'), ('pembelian','Harga Pokok Pembelian')], 'Report Type', 
			help="Field untuk filter kategori (Harga Pokok Produksi / Harga Pokok Pembelian) pada report penjualan L/R"),
		}
