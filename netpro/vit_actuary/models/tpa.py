from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_tpa(osv.osv):
    _name = 'netpro.tpa'
    _columns = {
        'name': fields.char('Name'),
        'code': fields.char('Code'),
        'created_by_id' : fields.many2one('res.users', 'Creator')
    }

    def create(self, cr, uid, vals, context=None):
        vals.update({
            'created_by_id':uid,
        })
        
        new_record = super(netpro_tpa, self).create(cr, uid, vals, context=context)
        return new_record
netpro_tpa()