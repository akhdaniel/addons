# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
import time
from openerp.osv import fields, osv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _

class student_transport(osv.Model):
    
    _name = 'student.transport'
    _description = 'Transport Information'

class hr_employee(osv.Model):
    
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _description = 'Driver Information'
    _columns = {
        'licence_no': fields.char('Licence No', size=50)
    }

#class for points on root
class transport_point(osv.Model):
    
    _name = 'transport.point'
    _description = 'Transport Point Information'
    _columns = {
        'name': fields.char('Point Name', size=50, required=True),
        'amount': fields.float('Amount'),
    }
    _defaults = {
        'amount' : 0,
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        ''' This method search IDs of transport point  
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param args : [(‘field_name’, ‘operator’, value), ...]. Pass an empty list to match all records.
        @param limit : max number of records to return (default: None)
        @param order : columns to sort by (default: self._order=id )
        @param context : context arguments, like lang, time zone
        @param count : (default: False), if True, returns only the number of records matching the criteria, not their ids
        @return : id or list of ids of records matching the criteria          
        '''
        
        if context is None:
            context = {}
        if context.get('name'):
            transport_obj = self.pool.get('student.transport')
            transport_data = transport_obj.browse(cr, uid, context['name'], context=context)
            point_ids = [point_id.id for point_id in transport_data.trans_point_ids]
            args.append(('id', 'in', point_ids))
        
        return super(transport_point, self).search(cr, uid, args, offset, limit, order, context, count)

#class for vehicle detail
class transport_vehicle(osv.Model):

    def _participants(self, cr, uid, ids, name, vals, context=None):
        ''' This method calculate total participants
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param vals : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the total participants as value 
        '''
        
        res = {}
        for vehi in self.browse(cr, uid, ids, context=context):
            res[vehi['id']] = len(vehi.vehi_participants_ids)
        return res

    _name = 'transport.vehicle'
    _rec_name = 'vehicle'
    _description = 'Transport vehicle Information'
    _columns = {
        'driver_id': fields.many2one('hr.employee', 'Driver Name', required=True),
        'vehicle': fields.char('Vehicle No', size=50, required=True),
        'capacity': fields.integer('Capacity'),
        'participant': fields.function(_participants, string='Total Participants', type="integer", readonly=True),
        'vehi_participants_ids':fields.many2many('transport.participant', 'vehicle_participant_student_rel', 'vehicle_id', 'student_id', ' vehicle Participants'),
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        ''' This method search IDs of Vehicle 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param args : [(‘field_name’, ‘operator’, value), ...]. Pass an empty list to match all records.
        @param limit : max number of records to return (default: None)
        @param order : columns to sort by (default: self._order=id )
        @param context : context arguments, like lang, time zone
        @param count : (default: False), if True, returns only the number of records matching the criteria, not their ids
        @return : id or list of ids of records matching the criteria          
        '''

        if context is None:
            context = {}
        if context.get('name'):
            transport_obj = self.pool.get('student.transport')
            transport_data = transport_obj.browse(cr, uid, context['name'], context=context)
            vehicle_ids = [std_id.id for std_id in transport_data.trans_vehicle_ids]
            args.append(('id', 'in', vehicle_ids))
        return super(transport_vehicle, self).search(cr, uid, args, offset, limit, order, context, count)

#class for participants
class transport_participant(osv.Model):
    
    _name = 'transport.participant'
    _rec_name = 'stu_pid_id'
    _description = 'Transport Participent Information'
    _columns = {
        'name': fields.many2one('student.student', 'Participent Name' , readonly=True,required=True),
        'amount': fields.float('Amount', readonly=True),
        'transport_id': fields.many2one('student.transport', 'Transport Root', readonly=True,required=True),
        'stu_pid_id': fields.char('Personal Identification Number', size=50, required=True),
        'tr_reg_date': fields.date('Transportation Registration Date'),
        'tr_end_date': fields.date('Registration End Date'),
        'months': fields.integer('Registration For Months'),
        'vehicle_id': fields.many2one('transport.vehicle', 'Vehicle No'),
        'point_id': fields.many2one('transport.point', 'Point Name'),
        'state':fields.selection([('running', 'Running'),
                                     ('over', 'Over'), ],
                                     'State', readonly=True),
    }
    _defaults = {
        'state': 'running'
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        ''' This method search IDs of transport   
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param args : [(‘field_name’, ‘operator’, value), ...]. Pass an empty list to match all records.
        @param limit : max number of records to return (default: None)
        @param order : columns to sort by (default: self._order=id )
        @param context : context arguments, like lang, time zone
        @param count : (default: False), if True, returns only the number of records matching the criteria, not their ids
        @return : id or list of ids of records matching the criteria          
        '''
        
        if context is None:
            context = {}
        if context.get('name'):
            student_obj = self.pool.get('student.student')
            student_data = student_obj.browse(cr, uid, context['name'], context=context)
            transport_ids = [transport_id.id for transport_id in student_data.transport_ids]
            args.append(('id', 'in', transport_ids))
        
        return super(transport_participant, self).search(cr, uid, args, offset, limit, order, context, count)

#class for root detail
class student_transports(osv.Model):

    def _total_participantes(self, cr, uid, ids, name, vals, context=None):
        ''' This method calculate total participants from root 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param vals : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the total participants as value 
        '''
        
        res = {}
        for root in self.browse(cr, uid, ids, context=context):
            res[root['id']] = len(root.trans_participants_ids)
        return res

    _name = 'student.transport'
    _description = 'Student Transport Information'
    _columns = {
        'name':fields.char('Transport Root Name', size=50, required=True),
        'start_date': fields.date('Start Date', required=True),
        'contact_per_id': fields.many2one('hr.employee', 'Contact Person'),
        'end_date': fields.date('End Date', required=True),
        'total_participantes': fields.function(_total_participantes, method=True, string='Total Participantes', type="integer", readonly=True),
        'trans_participants_ids':fields.many2many('transport.participant', 'transport_participant_rel', 'participant_id', 'transport_id', 'Participants', readonly=True),
        'trans_vehicle_ids':fields.many2many('transport.vehicle', 'transport_vehicle_rel', 'vehicle_id', 'transport_id', ' vehicles'),
        'trans_point_ids':fields.many2many('transport.point', 'transport_point_rel', 'point_id', 'root_id', ' Points'),
        'state': fields.selection([('draft', 'Draft'),
                                    ('open', 'Open'),
                                    ('close', 'Close')],
                                    'State', readonly=True),
    }
    _defaults = {
        'state':'draft',
    }

    def transport_open(self, cr, uid, ids, context=None):
        ''' This method change the state of transport
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        self.write(cr, uid, ids, {'state' : 'open'}, context=context)
        return True

    def transport_close(self, cr, uid, ids, context=None):
        ''' This method change the state of transport
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        self.write(cr, uid, ids, {'state' : 'close'}, context=context)
        return True

    def delet_entry(self, cr, uid, transport_ids=None, context=None):
        ''' This method delete entry of participants
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param transport_ids : list of transport ids
        @param context : standard Dictionary
        @return : True 
        '''

        prt_obj = self.pool.get('transport.participant')
        vehi_obj = self.pool.get('transport.vehicle')
        
        trans_ids = self.search(cr, uid, [('state', '=', 'open')], context=context)
        vehi_ids = vehi_obj.search(cr, uid, [], context=context)
        
        for trans in self.browse(cr, uid, trans_ids, context=context):
            stu_ids = [stu_id.id for stu_id in trans.trans_participants_ids]
            participants = []
            trans_parti = []
            for prt_data in prt_obj.browse(cr, uid, stu_ids, context=context):
                date = time.strftime("%Y-%m-%d")
                if date > prt_data.tr_end_date:
                    if prt_data.state != 'over':
                        trans_parti.append(prt_data.id)
                else :
                    participants.append(prt_data.id)
            if trans_parti:
                prt_obj.write(cr, uid, prt_data.id, {'state' : 'over'}, context=context)
            if participants:
                self.write(cr, uid, trans.id, {'trans_participants_ids':[(6, 0, participants)]}, context=context)
        
        for vehi in vehi_obj.browse(cr, uid, vehi_ids, context=context):
            stu_ids = [stu_id.id for stu_id in vehi.vehi_participants_ids]
            list1 = []
            for prt_data in prt_obj.browse(cr, uid, stu_ids, context=context):
                if prt_data.state != 'over':
                    list1.append(prt_data.id)
            vehi_obj.write(cr, uid, vehi.id, {'vehi_participants_ids':[(6, 0, list1)]}, context=context)
        return True

class student_student(osv.Model):
    
    _name = 'student.student'
    _inherit = 'student.student'
    _description = 'Student Information'
    _columns = {
        'transport_ids': fields.many2many('transport.participant', 'std_transport', 'trans_id', 'stud_id', 'Transport', readonly=True),
    }

#class for registration
class transport_registration(osv.Model):
    
    _name = 'transport.registration'
    _description = 'Transport Registration'
    _columns = {
        'name': fields.many2one('student.transport', 'Transport Root Name', domain=[('state', '=', 'open')], required=True),
        'part_name': fields.many2one('student.student', 'Participant Name', required=True),
        'reg_date': fields.date('Registration Date', readonly=True),
        'reg_end_date': fields.date('Registration End Date', readonly=True),
        'for_month': fields.integer('Registration For Months'),
        'state':fields.selection([('draft', 'Draft'),
                                      ('confirm', 'Confirm'),
                                      ('cancel', 'Cancel')
                                     ], 'State', readonly=True),
        'vehicle_id': fields.many2one('transport.vehicle', 'Vehicle No', required=True),
        'point_id': fields.many2one('transport.point', 'Point', widget='selection', required=True),
        'm_amount': fields.float('Monthly Amount', readonly=True),
        'amount': fields.float('Final Amount', readonly=True),
    }
    _defaults = {
        'state':'draft',
        "reg_date": lambda * a: time.strftime("%Y-%m-%d %H:%M:%S")
    }

    
    def create(self, cr, uid, vals, context=None):
        ''' This method create transport registration
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param vals : dict of new values to be set
        @param context : standard Dictionary
        @return :ID of newly created record.
        '''
        
        ret_val = super(transport_registration, self).create(cr, uid, vals, context=context)
        m_amt = self.onchange_point_id(cr, uid, ret_val, vals['point_id'])
        ex_dt = self.onchange_for_month(cr, uid, ret_val, vals['for_month'])
        self.write(cr, uid, ret_val, {'m_amount':m_amt['value']['m_amount'], 'reg_end_date':ex_dt['value']['reg_end_date']})
        return ret_val
        
    def onchange_point_id(self, cr, uid, ids, point, context=None):
        '''This method automatically change value of transport point 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @point : Apply method on this Field name
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the value of point
        '''
        
        if not point:
            return {}
        point_obj = self.pool.get('transport.point').browse(cr, uid, point)
        return {'value': {'m_amount': point_obj.amount}}

    def onchange_for_month(self, cr, uid, ids, month, context=None):
        '''This method automatically change value of month 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @point : Apply method on this Field name
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the value of month
        '''
        
        if not month:
            return {}
        tr_start_date = time.strftime("%Y-%m-%d")
        tr_end_date = datetime.strptime(tr_start_date, '%Y-%m-%d') + relativedelta(months= +month)
        date = datetime.strftime(tr_end_date, '%Y-%m-%d')
        return {'value': {'reg_end_date': date}}

    def trans_regi_cancel(self, cr, uid, ids, context=None):
        ''' This method cancel transport registration
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        self.write(cr, uid, ids, {'state' : 'cancel'}, context=context)
        return True

    def trans_regi_confirm(self, cr, uid, ids, context=None):
        ''' This method confirm transport registration
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        self.write(cr, uid, ids, {'state' : 'confirm'}, context=context)
        trans_obj = self.pool.get('student.transport')
        prt_obj = self.pool.get('student.student')
        stu_prt_obj = self.pool.get('transport.participant')
        vehi_obj = self.pool.get('transport.vehicle')
        
        for reg_data in self.browse(cr, uid, ids, context=context):
            #registration months must one or more then one
            if reg_data.for_month <= 0:
                raise osv.except_osv(_('Error !'), _('Sorry Registration months must one or more then one.'))
            # First Check Is there vacancy or not
            person = int(reg_data.vehicle_id.participant) + 1
            if reg_data.vehicle_id.capacity < person:
                raise osv.except_osv(_('Error !'), _('There is No More vacancy on this vehicle.'))

            #calculate amount and Registration End date
            amount = reg_data.point_id.amount * reg_data.for_month

            tr_start_date = (reg_data.reg_date)
            month = reg_data.for_month
            tr_end_date = datetime.strptime(tr_start_date, '%Y-%m-%d') + relativedelta(months= +month)
            date = datetime.strptime(reg_data.name.end_date, '%Y-%m-%d')
            if tr_end_date > date:
                raise osv.except_osv(_('Error !'), _('For this much Months Registration is not Possibal because Root end date is Early.'))

            # make entry in Transport
            temp = stu_prt_obj.create(cr, uid, {
                                        'stu_pid_id': str(reg_data.part_name.pid),
                                        'amount': amount,
                                        'transport_id': reg_data.name.id,
                                        'tr_end_date': tr_end_date,
                                        'name': reg_data.part_name.id,
                                        'months': reg_data.for_month,
                                        'tr_reg_date': reg_data.reg_date,
                                        'point_id' : reg_data.point_id.id,
                                        'vehicle_id': reg_data.vehicle_id.id,
                                        })
            
            #make entry in Transport vehicle. 
            list1 = []
            for prt in reg_data.vehicle_id.vehi_participants_ids:
                list1.append(prt.id)
            flag = True
            for prt in list1:
                data = stu_prt_obj.browse(cr, uid, prt, context=context)
                if data.name.id == reg_data.part_name.id:
                    flag = False
            if flag:
                list1.append(temp)
            vehi_obj.write(cr, uid, reg_data.vehicle_id.id, {'vehi_participants_ids':[(6, 0, list1)]}, context=context)

            #make entry in student.
            list1 = []
            for root in reg_data.part_name.transport_ids:
                list1.append(root.id)
            list1.append(temp)
            prt_obj.write(cr, uid, reg_data.part_name.id, {'transport_ids':[(6, 0, list1)]}, context=context)

            #make entry in transport.
            list1 = []
            for prt in reg_data.name.trans_participants_ids:
                list1.append(prt.id)
            list1.append(temp)
            trans_obj.write(cr, uid, reg_data.name.id, {'trans_participants_ids':[(6, 0, list1)]}, context=context)
        return True
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: