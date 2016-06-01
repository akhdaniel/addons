import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import netsvc
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval
import math,pprint

class hr_holidays(osv.osv):
    _name = "hr.holidays"
    _description = "Leave"
    _inherit = "hr.holidays"

    def holidays_first_validate(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        #brw =obj_emp.browse(cr,uid,ids2)[0]
        manager = ids2 and ids2[0] or False
        self.holidays_first_validate_notificate(cr, uid, ids, context=context)
        objk = self.browse(cr,uid,ids)[0] 
        emp = objk.employee_id.id
        dep = objk.department_id.manager_id
        if dep :
            dep = objk.department_id.manager_id.id
        state =objk.state
        self.write(cr, uid, [objk.id], {'state': 'validate1', 'manager_id': manager})
        return True

    def holidays_validate(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        #brw =obj_emp.browse(cr,uid,ids2)[0]
        manager = ids2 and ids2[0] or False
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            if record.holiday_type == 'lokasi':
                emp_ids = obj_emp.search(cr, uid, [('work_location2','=' ,record.lokasi_id)])
                leave_ids = []
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=None))
                wf_service = netsvc.LocalService("workflow")
                for leave_id in leave_ids:
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
            self.write(cr, uid, [record.id], {'state': 'validate', 'manager_id': manager})
        return True

    _columns = {
    	'lokasi_id': fields.selection([('lucas','Lucas'),('marin','Marin')],'Alamat Kantor', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
    }

hr_holidays()