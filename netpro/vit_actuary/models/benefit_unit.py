from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class netpro_benefit_unit(osv.osv):
    _name = 'netpro.benefit_unit'
    _columns = {
        'name'			: fields.char('Name'),
        'description'	: fields.char('Description'),
        'unit_limit'	:  fields.selection([('ANN','Annum'),('CON','Confinement'),('OCC','Occurence')],'Unit Limit By'),
        'created_by_id' : fields.many2one('res.users', 'Creator', readonly=True),
        'tpa_id' 		: fields.many2one('netpro.tpa', 'TPA'),
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
        
        new_record = super(netpro_benefit_unit, self).create(cr, uid, vals, context=context)
        return new_record
netpro_benefit_unit()