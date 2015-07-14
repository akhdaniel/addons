from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class netpro_membership(osv.osv):
    _name = 'netpro.membership'
    _columns = {
        'membership_id'		: fields.char('Membership ID'),
        'name'				: fields.char('Name (E)'),
        'name_i'			: fields.char('Name (I)'),
        'category'			: fields.char('Category'),
        'age_between_start'	: fields.integer('Age Between Start'),
        'age_between_end'	: fields.integer('Age Between End'),
        'policy_owner'		: fields.boolean('Policy Owner'),
        'allowed'			: fields.boolean('Allowed'),
        'membership_factor_ids' : fields.one2many('netpro.membership_factor','membership_id','Membership Factor', ondelete="cascade")
    }
netpro_membership()

class membership_factor(osv.osv):
    _name         = "netpro.membership_factor"
    _rec_name     = 'factor'
    _columns     = {
        'membership_id'     : fields.many2one('netpro.membership', 'Membership'),
        'sex'               : fields.selection([('M','Male'),('F','Female')],'Sex'),
        'factor'            : fields.float('Factor'),
        'is_allowed'        : fields.boolean('Allowed'),
    }
membership_factor()