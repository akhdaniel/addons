from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_annual_income(osv.osv):
    _name = 'netpro.annual_income'
    _columns = {
        'name': fields.char('Name'),
        'code': fields.text('Code'),
        'description': fields.text('Description'),
        'created_by_id' : fields.many2one('res.users', 'Creator', readonly=True),
    }

    def create(self, cr, uid, vals, context=None):
        vals.update({
            'created_by_id':uid,
        })
        
        new_record = super(netpro_age_band, self).create(cr, uid, vals, context=context)
        return new_record
netpro_annual_income()