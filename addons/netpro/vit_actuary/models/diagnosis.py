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
        'description': fields.text('Description'),
        'description_1': fields.text('Description 1'),
        'exclusion_f': fields.boolean('ExclusionF'),
        'pre_existing_f': fields.boolean('PreExistingF'),
        'standard_fee': fields.float('StandardFee'),
        'standard_treatment_day': fields.integer('StandardTreatmentDay'),
        'diagnosis_map': fields.char('DiagnosisMap'),
        'poly': fields.char('Poly'),
        'last_opr': fields.char('Poly'),
        'allowed_f': fields.boolean('AllowedF'),
        'last_update': fields.date('Last Update'),
    }
    _order = "name"
    # def create(self, cr, uid, vals, context=None):
    #     cur_user = self.pool.get('res.users').browse(cr, uid, uid, context=None)
    #     tpa_val = False
    #     if cur_user.tpa_id:
    #         tpa_val = cur_user.tpa_id.id
    #         pass
    #     vals.update({
    #         'created_by_id':uid,
    #         'tpa_id':tpa_val,
    #     })
        
    #     new_record = super(netpro_diagnosis, self).create(cr, uid, vals, context=context)
    #     return new_record

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for r in self.browse(cr, uid, ids, context=context):
            if r.diagnosis and r.name:
                name = "[%s] %s" % (r.diagnosis, r.name)
                res.append((r.id,name))
            else :
                res.append((r.id,r.diagnosis))

        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Be sure name_search is symetric to name_get
            # name = name.split(' / ')[-1]
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)

            if not ids:
                ids = self.search(cr, uid, [('diagnosis', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)
netpro_diagnosis()