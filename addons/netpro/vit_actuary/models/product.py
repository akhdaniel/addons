from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_product(osv.osv):
    _name = 'netpro.product'
    _columns = {
        'code': fields.char('Product Code'),
        'name': fields.char('Name'),
        'alternative_name': fields.char('Name (alt)'),
        'short_name': fields.char('Short Name'),
        'description': fields.text('Description'),
        'alternative_description': fields.text('Description (alt)'),
        'rider': fields.boolean('Rider'),
        'age_band_id': fields.many2one('netpro.age_band', 'Age Band'),
        'sub_class': fields.many2one('netpro.toc', 'Sub Class'),
        'product_type_id': fields.many2one('netpro.product_type', 'Product Type'),
        'min_member': fields.integer('Min. Member'),
        'max_age_coverage': fields.integer('Max. Age Coverage'),
        'release_date': fields.date('Release Date'),
        'status': fields.char('Status'),
        'provider_limit': fields.float('Provider Limit'),
        'reimbursement_limit': fields.float('Reimbursement Limit'),
        'allowed_changing_inner_limit': fields.boolean('Allowed Changing Inner Limit'),
        'allowed_changing_overall_limit': fields.boolean('Allowed Changing Overall Limit'),
        'benefit_ids': fields.one2many('netpro.product_benefit', 'product_id', 'Benefits', ondelete='cascade'),
        'term_condition_ids': fields.one2many('netpro.product_term_condition', 'product_id', 'Term And Condition', ondelete='cascade'),
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
        
        new_record = super(netpro_product, self).create(cr, uid, vals, context=context)
        return new_record
netpro_product()

class netpro_product_term_condition(osv.osv):
    _name = 'netpro.product_term_condition'
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one('netpro.product', 'Product'),
        'term_condition_id': fields.many2one('netpro.term_condition', 'Term And Condition'),
    }
netpro_product_term_condition()

class netpro_product_benefit(osv.osv):
    _name = 'netpro.product_benefit'
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one('netpro.product', 'Product'),
        'benefit_id': fields.many2one('netpro.benefit', 'Benefit'),
    }
netpro_product_benefit()