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

    def create(self,cr,uid,vals,context=None):
		cur_user = self.pool.get('res.users').browse(cr, uid, uid, context=None)
		tpa_val = False
		if cur_user.tpa_id:
			tpa_val = cur_user.tpa_id.id
		pass
		vals.update({
			'created_by_id':uid,
			'tpa_id':tpa_val,
		})
	       
		new_record = super(netpro_modal_factor, self).create(cr, uid, vals, context=context)
		return new_record
    
    _columns = {
		'currency_id' 		: fields.many2one('res.currency', 'Currency'),
		'annualy' 			: fields.float("Annualy"),
		'semi_annualy' 		: fields.float("Semi Annualy"),
		'quarterly' 		: fields.float("Quarterly"),
		'monthly' 			: fields.float("Monthly"),
        'is_allowed'		: fields.boolean('Allowed'),
        'created_by_id' 	: fields.many2one('res.users', 'Creator'),
        'tpa_id' 			: fields.many2one('netpro.tpa', 'TPA'),
	}
netpro_modal_factor()