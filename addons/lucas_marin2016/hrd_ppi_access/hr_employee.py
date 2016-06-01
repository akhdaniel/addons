from openerp.osv import fields, osv

class hr_employee(osv.osv):
    _inherit = "hr.employee"

    _columns = {
        'acc_level': fields.many2one('hr.acc_level','Access Level'),
        'dept_related' :fields.many2one('hr.department','Related Department',readonly=True),
        }

    def onchange_user(self, cr, uid, ids, user_id, context=None):
    	# import pdb;pdb.set_trace()
        if user_id:
            acc_level = self.pool.get('res.users').browse(cr, uid, user_id, context=context).acc_level or False
            dept_related = (self.pool.get('res.users').browse(cr, uid, user_id, context=context).dept_related.id or False)
            if (acc_level != 0and len(ids) != 0): self.write(cr,uid,ids[0],{'acc_level':acc_level},)
            if (dept_related and len(ids) != 0): self.write(cr,uid,ids[0],{'dept_related':dept_related},)
        return {'value': {
        	'acc_level' : acc_level,
        	'dept_related' : dept_related
        	}}

hr_employee()

class hr_acc_level(osv.osv):
    _name= "hr.acc_level"

    _columns = {
        "name" : fields.integer("Access Level"),
        "parent_id" : fields.many2one("hr.acc_level", "Parent", select=True),
        }
hr_acc_level()