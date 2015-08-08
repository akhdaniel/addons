from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_modal_factor(osv.osv):
    _name = 'netpro.modal_factor'
    _rec_name = 'currency_id'
    _columns = {
		'currency_id' 		: fields.many2one('res.currency', 'Currency'),
		'annualy' 			: fields.float("Annualy"),
		'semi_annualy' 		: fields.float("Semi Annualy"),
		'quarterly' 		: fields.float("Quarterly"),
		'monthly' 			: fields.float("Monthly"),
        'is_allowed'		: fields.boolean('Allowed'),
        'created_by_id' 	: fields.many2one('res.users', 'Creator'),
        'tpa_id' : fields.many2one('netpro.tpa', 'TPA'),
	}

netpro_modal_factor()