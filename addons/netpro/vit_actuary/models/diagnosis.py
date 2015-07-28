from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class netpro_diagnosis(osv.osv):
    _name = 'netpro.diagnosis'
    _columns = {
        'diagnosis': fields.char('Diagnosis'),
        'name': fields.char('Name'),
        'exclusion_f': fields.boolean('ExclusionF'),
        'pre_existing_f': fields.boolean('PreExistingF'),
        'standard_fee': fields.float('StandardFee'),
    }
    def _name_get(self, cr, uid, diagnosis, context=None):
        name = diagnosis.diagnosis + '-' + diagnosis.name
        return name

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for diagnosis in self.browse(cr, uid, ids, context=context):
            res.append((diagnosis.id, self._name_get(cr, uid, diagnosis, context=context)))
        return res

netpro_diagnosis()