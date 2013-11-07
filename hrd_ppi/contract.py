from openerp.osv import fields, osv
#import pprint

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'
    
    def onchange_employee(self, cr, uid, ids, employee_id):
        employ  = self.pool.get('hr.employee').browse(cr,uid,[employee_id],)[0]
        res={};res['wage']=False; res['job_id']=False       
        res['wage']=employ.wage
        res['job_id']=employ.job_id.id
        return {'value':res}

hr_contract()