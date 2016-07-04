from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mlm_paket(osv.osv):
	_name 		= "mlm.paket"

	def _get_price(self, cr, uid, ids, field_name, arg, context=None):
		result = {}
		for paket in self.browse(cr,uid,ids,context=context):
			paket_price 	= paket.harga
			hak_usaha 		= paket.hak_usaha
			harga 			= paket_price*hak_usaha

			result[paket.id] = harga

		return result

	_columns 	= {
		'code'		: fields.char('Code',required=True),
		'name'		: fields.char('Name',required=True),
		'paket_product_id': fields.many2one('mlm.paket_produk', 'Package Product Ref'),
		'harga'		: fields.float('Harga',required=True),
		'price'		: fields.function(_get_price,type="float",string="Total Price", readonly=True),
		'cashback'		: fields.float('Cashback'),
		'hak_usaha'		: fields.integer('Business Package',required=True),
		'description'	: fields.text('Description'),
		'is_affiliate'  : fields.boolean('Affiliate Member ?', 
			help="Only get the sponsor bonus"),
			# help="Hanya mendapat bonus sponsor saja"),
		'is_upgradable' : fields.boolean('Upgrade-able ?', 
			help="Is upgradeable, for example from 1 to 3 business packages"),
			# help="Apakah bisa diupgrade, misalkan dari 1 hak usaha menjadi 3 hak usaha"),
		'is_submember'  : fields.boolean('Sub-member ?', 
			help="When upgraded, this status is used at the new member from the upgrade process"),
			# help="Jika diupgrade, status ini dipakai pada member baru hasil proses upgrade"),
	}

	def onchange_paket_product_id(self, cr, uid, ids, paket_product_id):
		paket_product_obj = self.pool.get('mlm.paket_produk')
		
		if not paket_product_id:
			return {'value': {
				'harga': 0.00,
				}}
		paket = paket_product_obj.browse(cr, uid, paket_product_id)
		return {'value': {
			'harga' : paket.harga,
			}}

mlm_paket()