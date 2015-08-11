import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re



""" wo_machine_hour """
class wo_machine_hour(osv.osv):
    _name = 'vit_pharmacy_wo_hour.wo_machine_hour'
    _description = 'Wo Machine Hour'

    _columns = {
        'mpwcl_id'	   				: fields.many2one('mrp.production.workcenter.line','Work Orders'),
        # 'mpwcl_id'                  : fields.many2one('mrp.production.workcenter.line', 'MPWL Reference', ondelete='cascade', select=True),
        'machine_id'                : fields.many2one('vit_pharmacy_machine_hour.machine_master','Machine'), 
        'machine_hour_standard'     : fields.float('Machine Hour Standard',digits=(16, 2)), 
        'machine_hour_actual'       : fields.float('Machine Hour Actual',digits=(16, 2)),
        'machine_hour_diff'         : fields.float('Machine Hour Diff',digits=(16, 2)),
        'is_parallel'               : fields.boolean('Parallel'),

    }

    @api.onchange('machine_hour_actual') # if these fields are changed, call method
    def on_change_nett_diff(self): 
        self.machine_hour_diff = self.machine_hour_standard - self.machine_hour_actual 

    # def write(self, cr, uid, ids, vals, context=None):
    #     oper_objs = self.browse(cr, uid, ids, context=context)[0]
    #     vals['machine_hour_diff'] = oper_objs.machine_hour_standard - oper_objs.machine_hour_actual 
    #     # import pdb;pdb.set_trace()  
    #     return super(wo_machine_hour, self).write(cr, uid, ids, vals, context=context)


    