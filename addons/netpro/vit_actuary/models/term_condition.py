from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_term_condition(osv.osv):
    _name = 'netpro.term_condition'
    _columns = {
        'tc_id': fields.char('TC ID'),
        'name': fields.text('TC Name'),
        'description' : fields.text('Description'),
        'type' : fields.selection([('standard','Standard'),('nonstandard','Non Standard')],'Type'),
        'created_by_id' : fields.many2one('res.users', 'Creator'),
        'tpa_id' : fields.many2one('netpro.tpa', 'TPA'),
    }

    def create(self, cr, uid, vals, context=None):
        cur_user = self.pool.get('res.users').browse(cr, uid, uid, context=None)
        tpa_val = False
        if cur_user.tpa_id:
            tpa_val = cur_user.tpa_id.id
            pass
        vals.update({
            'created_by_id':uid,
            'tpa_id':tpa_val,
        })
        
        new_record = super(netpro_term_condition, self).create(cr, uid, vals, context=context)
        return new_record
netpro_term_condition()