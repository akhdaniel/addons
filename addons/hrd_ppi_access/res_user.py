from openerp.osv import fields,osv

class res_users(osv.osv):
    _inherit = "res.users"

    _columns = {
        'acc_level': fields.many2one('hr.acc_level','Access Level'),
        'dept_related' :fields.many2one('hr.department','Related Department'),
        }