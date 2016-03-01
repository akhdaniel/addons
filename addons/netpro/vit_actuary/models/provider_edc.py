from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_provider_edc(osv.osv):
	_name = "netpro.provider_edc"

	_columns = {
		'provider_id'	: fields.many2one('netpro.provider', 'Provider'),
		'provider_mid'	: fields.related('provider_id', 'edc_merchant_id' , type="char", relation="many2one", string="MID", store=False),
		'tid' 			: fields.char('TID'),
		'floor' 		: fields.char('Floor'),
		'room' 			: fields.char('Room'),
		'remarks'		: fields.text('Remarks'),
		'allowed_f' 	: fields.boolean('AllowedF'),
		'last_opr'		: fields.char('Last Opr'),
		'last_update' 	: fields.date('Last Update'),
	}

	def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		if not context:
			context = {}
		if name:
			ids = self.search(cr, uid, [('tid', operator, name)] + args, limit=limit, context=context)
			if not ids:
				ids = self.search(cr, uid, [('provider_id', operator, name)] + args, limit=limit, context=context)
		else:
			ids = self.search(cr, uid, args, limit=limit, context=context)
		return self.name_get(cr, uid, ids, context)