from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mlm_paket(osv.osv):
	_name 		= "mlm.paket"
	_columns 	= {
		'code'		: fields.char('Code'),
		'name'		: fields.char('Name'),
		'price'		: fields.float('Price'),
		'cashback'		: fields.float('Cashback'),
		'hak_usaha'		: fields.integer('Hak Usaha'),
		'description'	: fields.text('Description'),
		'is_affiliate'  : fields.boolean('Affiliate Member ?', help="Hanya mendapat bonus sponsor saja"),
		'is_upgradable'  : fields.boolean('Upgrade-able ?', help="Apakah bisa diupgrade"),
	}

