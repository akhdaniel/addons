from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class res_users(osv.osv):
    _name = 'res.users'
    _inherit = 'res.users'
    _columns = {
        'tpa_id' 		: fields.many2one('netpro.tpa', 'TPA'),
        'provider_id'             : fields.many2one('netpro.provider', 'Provider'),
    }

    def onchange_tpa(self,cr,uid,ids,tpa_id,provider_id):
        value = {}
        if tpa_id and provider_id:
            value.update({'provider_id':False})
        return {'value':value}

    def onchange_pro(self,cr,uid,ids,tpa_id,provider_id):
        value = {}
        if tpa_id and provider_id:
            value.update({'tpa_id':False})
        return {'value':value}
res_users()