# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import datetime

import netsvc
from osv import fields, osv
from tools.translate import _

class hr_overtime_type(osv.osv):
    _name = "hr.overtime.type"
    _description = "Overtime Type"
    _columns = {
        'name': fields.char('Description', required=True, size=64),
        'double_validation': fields.boolean('Apply Double Validation', help="If its True then its overtime type have to be validated by second validator"),
        'active': fields.boolean('Active', help="If the active field is set to false, it will allow you to hide the overtime type without removing it."),
    }
hr_overtime_type()

class hr_overtime(osv.osv):
    _name = "hr.overtime"
    _description = "Overtime"
    _order = "date_from asc"

    def _hitung_lembur(self, cr, uid, ids, arg, vals, context=None):
        jumlah={}
        obj = self.browse(cr,uid,ids)[0]
        jam = obj.jam_lembur
        overtime_type = obj.overtime_type.jam_ids
        x = 0
        for over in overtime_type :
            sampai = float(over.sampai)
            dari = float(over.name)
            if jam >= sampai and sampai != 0.0:
                tot = (sampai - dari + 1) * over.pengali
            elif sampai == 0.0 and jam >= dari:
                tot = (jam - (dari - 1)) * over.pengali
            x = x + tot
        jumlah[obj.id] = x
        return jumlah

    def _employee_get(obj, cr, uid, context=None):
        ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False

    def _compute_number_of_hours(self, cr, uid, ids, name, args, context=None):
        result = {}
        for hol in self.browse(cr, uid, ids, context=context):
            result[hol.id] = hol.number_of_hours_temp         
        return result

    _columns = {
        'name': fields.char('Description', required=True, size=64),
        'state': fields.selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'), 
            ('validate1', 'Waiting Second Approval'), ('validate', 'Approved'), ('cancel', 'Cancelled')],
            'State', readonly=True, help='When the overtim request is created the state is \'Draft\'.\n It is confirmed by the user and request is sent to admin, the state is \'Waiting Approval\'.\
            If the admin accepts it, the state is \'Approved\'. If it is refused, the state is \'Refused\'.'),
        'user_id':fields.related('employee_id', 'user_id', type='many2one', relation='res.users', string='User', store=True),
        'date_from': fields.datetime('Start Date', readonly=True, states={'draft':[('readonly',False)]}),
        'date_to': fields.datetime('End Date', readonly=True, states={'draft':[('readonly',False)]}),
        'employee_id': fields.many2one('hr.employee', "Employee", select=True, invisible=False, readonly=True, states={'draft':[('readonly',False)]}),
        'manager_id': fields.many2one('hr.employee', 'First Approval', invisible=False, readonly=True),
        'notes': fields.text('Reasons',readonly=True, states={'draft':[('readonly',False)]}),
        'number_of_hours_temp': fields.float('Number of Hours', readonly=True, states={'draft':[('readonly',False)]}),
        'number_of_hours': fields.function(_compute_number_of_hours, method=True, string='Number of Hours', store=True),
        #'department_id':fields.related('employee_id', 'department_id', string='Department', type='many2one', relation='hr.department', readonly=True),
        'manager_id2': fields.many2one('hr.employee', 'Second Approval', readonly=True, help='This area is automaticly filled by the user who validate the leave with second level (If Leave type need second validation)'),
        'overtime_type_id': fields.many2one("hr.overtime.type", "Type Lembur", required=True,readonly=True, states={'draft':[('readonly',False)]}),
        'department_id' : fields.many2one('hr.department', 'Department'),
        'overtime_type' : fields.many2one('hr.overtime.jam','Jenis Lembur',required=True),
        'total_jam':fields.function(_hitung_lembur,type='float',store=True, readonly=True,string='Total Jam Lembur'),
        'jam_lembur':fields.float("Jumlah Jam Lembur"),
    }
    _defaults = {
        'employee_id': _employee_get,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
    }
    _sql_constraints = [
        ('date_check', "CHECK ( number_of_hours_temp > 0 )", "The number of hours must be greater than 0 !"),
        ('date_check2', "CHECK (date_from < date_to)", "The start date must be before the end date !")
    ]

    # TODO: can be improved using resource calendar method
    def _get_number_of_hours(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""

        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state <>'draft':
                #raise osv.except_osv(_('Warning!'),_('You cannot delete a overtime which is not in draft state !'))
                raise Exception(_('You cannot delete a overtime which is not in draft state !'))
        return super(hr_overtime, self).unlink(cr, uid, ids, context)

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        result = {}
        result['value'] = {
            'number_of_hours_temp': 0,
        }
        return result

    def set_to_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
            'state': 'draft',
            'manager_id': False,
        })
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_create(uid, 'hr.overtime', id, cr)
        return True

    def overtime_validate(self, cr, uid, ids, *args):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        return self.write(cr, uid, ids, {'state':'validate1', 'manager_id': manager})

    def overtime_validate2(self, cr, uid, ids, *args):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate', 'manager_id2': manager})
        return True

    def overtime_cancel(self, cr, uid, ids, *args):
        for record in self.browse(cr, uid, ids):
            wf_service = netsvc.LocalService("workflow")
            for id in []:
                wf_service.trg_validate(uid, 'hr.overtime', id, 'cancel', cr)

        return True

    def overtime_confirm(self, cr, uid, ids, *args):
        return self.write(cr, uid, ids, {'state':'confirm'})

    def overtime_refuse(self, cr, uid, ids, *args):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state': 'refuse', 'manager_id2': manager})
        self.overtime_cancel(cr, uid, ids)
        return True

hr_overtime()

class overtime_jam(osv.osv):
    _name = 'hr.overtime.jam'
    _description = 'pengali jam lembur'

    _columns = {
        'name' : fields.char('Nama Perhitungan Lembur'),
        'jam_ids' : fields.one2many('hr.jam','overtime_jam', 'Perhitungan Jam')  
    }
overtime_jam()

class jam(osv.osv):
    _name = 'hr.jam'

    _columns ={
        'name' :fields.selection([('1','Jam 1'),('2','Jam 2'),('3','Jam 3'),('4','Jam 4'),('5','Jam 5'),('6','Jam 6'),('7','Jam 7'),
            ('8','Jam 8'),('9','Jam 9'),('10','Jam 10'),('11','Jam 11'),('12','Jam 12'),('13','Jam 13'),('14','Jam 14'),('15','Jam 15')
            ,('16','Jam 16'),('17','Jam 17'),('18','Jam 18'),('19','Jam 19'),('20','Jam 20'),('21','Jam 21'),('22','Jam 22'),('23','Jam 23'),('24','Jam 24')], 'Jam Ke'),
        'sampai' :fields.selection([('1','Jam 1'),('2','Jam 2'),('3','Jam 3'),('4','Jam 4'),('5','Jam 5'),('6','Jam 6'),('7','Jam 7'),
            ('8','Jam 8'),('9','Jam 9'),('10','Jam 10'),('11','Jam 11'),('12','Jam 12'),('13','Jam 13'),('14','Jam 14'),('15','Jam 15')
            ,('16','Jam 16'),('17','Jam 17'),('18','Jam 18'),('19','Jam 19'),('20','Jam 20'),('21','Jam 21'),('22','Jam 22'),('23','Jam 23'),('24','Jam 24')], 'Sampai Jam Ke'),
        'pengali' :fields.float('Pengali'),
        'overtime_jam' :fields.many2one('hr.overtime.jam'),
    }
jam()