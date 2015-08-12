from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class netpro_age_band(osv.osv):
    _name = 'netpro.age_band'
    _columns = {
        'name': fields.integer('Band ID'),
        'age_band_detail_ids': fields.one2many('netpro.age_band_detail','age_band_id','Age Band Detail', ondelete="cascade"),
        'created_by_id' : fields.many2one('res.users', 'Creator', readonly=True),
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
        
        new_record = super(netpro_age_band, self).create(cr, uid, vals, context=context)
        return new_record
netpro_age_band()

class netpro_age_band_detail(osv.osv):
    _name = 'netpro.age_band_detail'
    _columns = {
        'age_band_id'	: fields.many2one('netpro.age_band', 'Age Band'),
        'age_lower'		: fields.integer('Age Lower'),
        'age_upper'		: fields.integer('Age Upper'),
        'loading'		: fields.integer('Loading'),

    }
netpro_age_band_detail()

