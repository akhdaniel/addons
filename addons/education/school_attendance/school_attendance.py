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
from openerp.osv import fields, osv
import time
from calendar import monthrange
from datetime import datetime

class attendance_sheet(osv.Model):
    
    ''' Defining Monthly Attendance sheet Information '''
    _description ='Attendance Sheet'
    _name = 'attendance.sheet'

    _columns = {
        'name': fields.char('Description', size=64,readonly=True), 
        'standard_id': fields.many2one('school.standard', 'Academic Class', required=True), 
        'month_id': fields.many2one('academic.month', 'Month', required=True), 
        'year_id': fields.many2one('academic.year', 'Year', required=True), 
        'attendance_ids':fields.one2many('attendance.sheet.line', 'standard_id', 'Attendance'), 
        'user_id':fields.many2one('hr.employee', 'Faculty'),
        'attendance_type':fields.selection([('daily','FullDay'),('lecture','Lecture Wise')],'Type'),
    }
    
    def onchange_class_info(self, cr, uid, ids, standard_id,context = None):
        '''  This method automatically fill up student records on standard field
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param standard_id : Apply method on this Field name
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the value of student
        '''
        res= {}
        student_list = []
        stud_obj = self.pool.get('student.student')
        student_domain=[('standard_id', '=', standard_id)]
        stud_id = stud_obj.search(cr, uid,student_domain)
        for id in stud_id:
            student_ids = stud_obj.browse(cr,uid, id)
            student_dict = {'roll_no':student_ids.roll_no,'name':student_ids.name}
            student_list.append(student_dict)
        res.update({'value': {'attendance_ids':student_list}})
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(attendance_sheet, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if context is None:
            context = {}
        if context.get('month_id', False):
            no_of_days = monthrange(context['year_id'][0], context['month_id'][0])[1]
            if no_of_days == 31:
                pass
            
            elif no_of_days == 30:
                if 'attendance_ids' in res['fields']:
                    att = res['fields']['attendance_ids']
                    if 'views' in att:
                        res['fields']['attendance_ids']['views']['tree']['fields']['three_1'].update({'invisible':1})
                        res['fields']['attendance_ids']['views']['form']['fields']['three_1'].update({'invisible':1})
        
            elif no_of_days == 29:
                if 'attendance_ids' in res['fields']:
                    att = res['fields']['attendance_ids']
                    if 'views' in att:
                        res['fields']['attendance_ids']['views']['tree']['fields']['three_1'].update({'invisible':1})
                        res['fields']['attendance_ids']['views']['form']['fields']['three_1'].update({'invisible':1})
                        res['fields']['attendance_ids']['views']['tree']['fields']['two_0'].update({'invisible':1})
                        res['fields']['attendance_ids']['views']['form']['fields']['two_0'].update({'invisible':1})
            else:
        
                if 'attendance_ids' in res['fields']:
                    att = res['fields']['attendance_ids']
                    if 'views' in att:

                        res['fields']['attendance_ids']['views']['tree']['fields']['three_1'].update({'invisible':1})
                        res['fields']['attendance_ids']['views']['form']['fields']['three_1'].update({'invisible':1})
                        res['fields']['attendance_ids']['views']['tree']['fields']['two_0'].update({'invisible':1})
                        res['fields']['attendance_ids']['views']['form']['fields']['two_0'].update({'invisible':1})
                        res['fields']['attendance_ids']['views']['tree']['fields']['two_9'].update({'invisible':1})
                        res['fields']['attendance_ids']['views']['form']['fields']['two_9'].update({'invisible':1})

        return res

class attendance_sheet_line(osv.Model):
    
    ''' Defining Attendance Sheet Line Information '''
    
    def attendance_percentage(self, cr, uid, ids, name, args, context=None):
        ''' This method calculate percentage of total attendance
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param args : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the percentage as value 
        '''
        res = {}
        for attendance_sheet_data in self.browse(cr, uid, ids, context=context):
            att_count = 0
            percentage = 0.0
            if attendance_sheet_data.one==True:
                att_count=att_count+1
            if attendance_sheet_data.two==True:
                att_count=att_count+1
            if attendance_sheet_data.three==True:
                att_count=att_count+1
            if attendance_sheet_data.four==True:   
                att_count=att_count+1
            if attendance_sheet_data.five==True:
                att_count=att_count+1
            if attendance_sheet_data.six==True:
                att_count=att_count+1
            if attendance_sheet_data.seven==True:
                att_count=att_count+1
            if attendance_sheet_data.eight==True:
                att_count=att_count+1
            if attendance_sheet_data.nine==True:
                att_count=att_count+1
            if attendance_sheet_data.ten==True:
                att_count=att_count+1
            if attendance_sheet_data.one_1==True:
                att_count=att_count+1
            if attendance_sheet_data.one_2==True:
                att_count=att_count+1
            if attendance_sheet_data.one_3==True:
                att_count=att_count+1
            if attendance_sheet_data.one_4==True:
                att_count=att_count+1
            if attendance_sheet_data.one_5==True:
                att_count=att_count+1
            if attendance_sheet_data.one_6==True:
                att_count=att_count+1
            if attendance_sheet_data.one_7==True:
                att_count=att_count+1
            if attendance_sheet_data.one_8==True:
                att_count=att_count+1
            if attendance_sheet_data.one_9==True:
                att_count=att_count+1
            if attendance_sheet_data.one_0==True:
                att_count=att_count+1
                
            if attendance_sheet_data.two_1==True:
                att_count=att_count+1
            if attendance_sheet_data.two_2==True:
                att_count=att_count+1
            if attendance_sheet_data.two_3==True:
                att_count=att_count+1
            if attendance_sheet_data.two_4==True:
                att_count=att_count+1
            if attendance_sheet_data.two_5==True:
                att_count=att_count+1
            if attendance_sheet_data.two_6==True:
                att_count=att_count+1
            if attendance_sheet_data.two_7==True:
                att_count=att_count+1
            if attendance_sheet_data.two_8==True:
                att_count=att_count+1
            if attendance_sheet_data.two_9==True:
                att_count=att_count+1
            if attendance_sheet_data.two_0==True:
                att_count=att_count+1
            if attendance_sheet_data.three_1==True:
                att_count=att_count+1
            percentage = (float(att_count/31.00))*100
            res[attendance_sheet_data.id] = percentage
        return res
    
    _description ='Attendance Sheet Line'
    _name = 'attendance.sheet.line'
    _order = 'roll_no'

    _columns = {
        'roll_no':fields.integer('Roll Number', required=True, help='Roll Number of Student'), 
        'standard_id': fields.many2one('attendance.sheet', 'Standard'), 
#         'name': fields.many2one('student.student','Student Name', required=True),
         'name':fields.char('Student Name',required=True,readonly=True),
        'one': fields.boolean('1'),
        'two': fields.boolean('2'), 
        'three': fields.boolean('3'),
        'four': fields.boolean('4'),
        'five': fields.boolean('5'),
        'seven': fields.boolean('7'), 
        'six': fields.boolean('6'), 
        'eight': fields.boolean('8'), 
        'nine': fields.boolean('9'), 
        'ten': fields.boolean('10'), 
        'one_1': fields.boolean('11'), 
        'one_2': fields.boolean('12'), 
        'one_3': fields.boolean('13'), 
        'one_4': fields.boolean('14'), 
        'one_5': fields.boolean('15'), 
        'one_6': fields.boolean('16'), 
        'one_7': fields.boolean('17'), 
        'one_8': fields.boolean('18'), 
        'one_9': fields.boolean('19'), 
        'one_0': fields.boolean('20'), 
        'two_1': fields.boolean('21'), 
        'two_2': fields.boolean('22'), 
        'two_3': fields.boolean('23'), 
        'two_4': fields.boolean('24'), 
        'two_5': fields.boolean('25'), 
        'two_6': fields.boolean('26'), 
        'two_7': fields.boolean('27'), 
        'two_8': fields.boolean('28'), 
        'two_9': fields.boolean('29'), 
        'two_0': fields.boolean('30'), 
        'three_1': fields.boolean('31'), 
        'percentage': fields.function(attendance_percentage, method=True, string='Attendance (%)', type="float", store= False), 

    }

class daily_attendance(osv.Model):
    
    ''' Defining Daily Attendance Information '''
    _description ='Daily Attendance'
    _name = 'daily.attendance'
    
    def _total(self, cr, uid, ids, name, args, context=None):
        
        res = {}
        count=0
        atten_line_obj=self.pool.get('daily.attendance')
        for att_line in atten_line_obj.browse( cr, uid, ids, context):
            for att in att_line.student_ids:
                count += 1
            res[att_line.id] = count
        return res
    
    def _present(self, cr, uid, ids, name, args, context=None):
        
        res = {}
        count=0
        count_fail=0
        atten_line_obj=self.pool.get('daily.attendance')
        for att_line in atten_line_obj.browse( cr, uid, ids, context):
            for att in att_line.student_ids:
                if att.is_present == True:
                    count += 1
                elif att.is_absent==True:
                    count_fail += 1
            res[att_line.id] = count
        return res  
    
    def _absent(self, cr, uid, ids, name, args, context=None):
        
        res = {}
        count=0
        count_fail=0
        atten_line_obj=self.pool.get('daily.attendance')
        for att_line in atten_line_obj.browse( cr, uid, ids, context):
            for att in att_line.student_ids:
                if att.is_present == True:
                    count += 1
                elif att.is_absent==True:
                    count_fail += 1
            res[att_line.id] = count_fail
        return res 
    
    
    _columns = {
        'date': fields.date("Today's Date"), 
        'standard_id': fields.many2one('school.standard', 'Academic Class', required=True, states={'validate':[('readonly', True)]}), 
        'student_ids':fields.one2many('daily.attendance.line', 'standard_id', 'Students', states={'validate':[('readonly', True)], 'draft':[('readonly', False)]}), 
        'user_id':fields.many2one('hr.employee', 'Faculty', states={'validate':[('readonly', True)]}), 
        'state':fields.selection([('draft', 'Draft'), ('validate', 'Validate')], 'State', readonly=True),
        'total_student': fields.function(_total, method=True, type="integer", store=True, string='Total Students'),
        'total_presence': fields.function(_present, method=True, type="integer", store=True, string='Presenct Students'), 
        'total_absent': fields.function(_absent, method=True, type="integer", store=True, string='Absent Students')
    }
    _defaults={
        'date': lambda *a: time.strftime('%Y-%m-%d'), 
        'state':'draft', 
    }
    
    def create(self, cr, uid, vals, context=None):
        ''' This method is Create new student 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param vals : dict of new values to be set
        @param context : standard Dictionary
        @return :ID of newly created record.
        '''

        child = vals.pop('student_ids')
        ret_val = super(daily_attendance, self).create(cr, uid, vals, context=context)
        self.write(cr, uid, ret_val, {'student_ids' : child})
        return ret_val
    
    def onchange_standard_id(self, cr, uid, ids, standard_id,context = None):
        '''This method automatically change value of standard field 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @standard_id : Apply method on this Field name
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the value of student
        '''
        
        res={}
        student_list = []
        stud_obj = self.pool.get('student.student')
        stud_id = stud_obj.search(cr, uid,[('standard_id', '=', standard_id)])#list
        for id in stud_id:
            student_ids = stud_obj.browse(cr,uid, id)
            student_dict = {'roll_no':student_ids.roll_no,'stud_id':id}
            student_list.append(student_dict)
        res.update({'value': {'student_ids': student_list}})
        return res
    
    def attendance_draft(self, cr, uid, ids, context=None):
        attendance_sheet_obj = self.pool.get('attendance.sheet')
        attendance_sheet_line_obj = self.pool.get('attendance.sheet.line')
        daily_attendance_line_obj = self.pool.get('daily.attendance.line')
        academic_year_obj = self.pool.get('academic.year')
        academic_month_obj = self.pool.get('academic.month')
        daily_attendance_datas = self.browse(cr, uid, ids, context=context)

        for daily_attendance_data in daily_attendance_datas:
            date = datetime.strptime(daily_attendance_data.date, "%Y-%m-%d")
            
            year_search_ids = academic_year_obj.search(cr, uid, [('code', '=', date.year)], context=context)
            month_search_ids = academic_month_obj.search(cr, uid, [('code', '=', date.month)], context=context)
            
            for line in daily_attendance_data.student_ids:
                daily_attendance_line_obj.write(cr, uid, line.id, {'is_present': False, 'is_absent': False}, context=context)
                
            attendance_sheet_domain = [('standard_id', '=', daily_attendance_data.standard_id.id), ('month_id', '=', month_search_ids), ('year_id', '=', year_search_ids)]
            
        search_attendance_sheet_ids = attendance_sheet_obj.search(cr, uid, attendance_sheet_domain, context=context)
       
        
        for attendance_sheet_datas in attendance_sheet_obj.browse(cr, uid, search_attendance_sheet_ids, context=context):
            for attendance_id in attendance_sheet_datas.attendance_ids:
                date = datetime.strptime(daily_attendance_data.date, "%Y-%m-%d")
                if date.day == 1:
                    dic = {'one':False}
                elif date.day == 2:
                    dic = {'two':False}
                elif date.day == 3:
                    dic = {'three':False}
                elif date.day == 4:
                    dic = {'four':False}
                elif date.day == 5:
                    dic = {'five':False}
                elif date.day == 6:
                    dic = {'six':False}
                elif date.day == 7:
                    dic = {'seven':False}
                elif date.day == 8:
                    dic = {'eight':False}
                elif date.day == 9:
                    dic = {'nine':False}
                elif date.day == 10:
                    dic = {'ten':False}
                elif date.day == 11:
                    dic = {'one_1':False}
                elif date.day == 12:
                    dic = {'one_2':False}
                elif date.day == 13:
                    dic = {'one_3':False}
                elif date.day == 14:
                    dic = {'one_4':False}
                elif date.day == 15:
                    dic = {'one_5':False}
                elif date.day == 16:
                    dic = {'one_6':False}
                elif date.day == 17:
                    dic = {'one_7':False}
                elif date.day == 18:
                    dic = {'one_8':False}
                elif date.day == 19:
                    dic = {'one_9':False}
                elif date.day == 20:
                    dic = {'one_0':False}
                elif date.day == 21:
                    dic = {'two_1':False}
                elif date.day == 22:
                    dic = {'two_2':False}
                elif date.day == 23:
                    dic = {'two_3':False}
                elif date.day == 24:
                    dic = {'two_4':False}
                elif date.day == 25:
                    dic = {'two_5':False}
                elif date.day == 26:
                    dic = {'two_6':False}
                elif date.day == 27:
                    dic = {'two_7':False}
                elif date.day == 28:
                    dic = {'two_8':False}
                elif date.day == 29:
                    dic = {'two_9':False}
                elif date.day == 30:
                    dic = {'two_0':False}
                elif date.day == 31:
                    dic = {'three_1':False}
                attendance_sheet_line_obj.write(cr, uid, attendance_id.id, dic, context = context)
                
        self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
        return True
    
    def attendance_validate(self, cr, uid, ids, context=None):
        ''' This method validate values of student attendance 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True          
        '''
        
        attendance_sheet_line_obj = self.pool.get('attendance.sheet.line')
        acadmic_year_obj = self.pool.get('academic.year')
        acadmic_month_obj = self.pool.get('academic.month')
        attendance_sheet_obj = self.pool.get('attendance.sheet')

        for line in self.browse(cr, uid, ids, context = context):
            date = datetime.strptime(line.date, "%Y-%m-%d")
            year = date.year
            year_ids= acadmic_year_obj.search(cr, uid, [('date_start', '<=', date), ('date_stop', '>=', date)])
            month_ids= acadmic_month_obj.search(cr, uid, [('date_start', '<=', date), ('date_stop', '>=', date), ('year_id', 'in', year_ids)])
            
            if month_ids:
                month_data = acadmic_month_obj.browse(cr, uid, month_ids[0])
                att_sheet_ids = attendance_sheet_obj.search(cr, uid, [('month_id', 'in', month_ids), ('year_id', 'in', year_ids)])
                attendance_sheet_id = att_sheet_ids and att_sheet_ids[0] or False
                if not attendance_sheet_id:
                    attendance_sheet_id = attendance_sheet_obj.create(cr, uid, {
                                                        'name':  'Month '+ month_data.name +"-Year "+ str(year),
                                                        'standard_id':line.standard_id.id,
                                                        'user_id': line.user_id.id, 
                                                        'month_id': month_data.id, 
                                                        'year_id': year_ids and year_ids[0] or False})
                    for student_id in line.student_ids:
                        attendance_sheet_line_obj.create(cr, uid, {
                                                                'roll_no': student_id.roll_no,
                                                                'standard_id': attendance_sheet_id,
                                                                'name': student_id.stud_id.id})
                        for student_id in line.student_ids:
                            dict=attendance_sheet_line_obj.read(cr, uid, student_id.roll_no)
                            domain = [('roll_no', '=', student_id.roll_no)]
                            search_id = attendance_sheet_line_obj.search(cr, uid, domain)
                            if date.day == 1 and student_id.is_absent == True:
                                val = {'one':False}
                                                
                            elif date.day == 1 and student_id.is_absent == False: 
                                val = {'one':True}
                                          
                            elif date.day == 2 and student_id.is_absent == True:
                                val = {'two':False}
                            
                            elif date.day == 2 and student_id.is_absent == False: 
                                val = {'two':True}
            
                            elif date.day == 3 and student_id.is_absent == True:
                                val = {'three':False}
                                                
                            elif date.day == 3 and student_id.is_absent == False: 
                                val = {'three':True}
                                            
                            elif date.day == 4 and student_id.is_absent == True:
                                val = {'four':False}
                            
                            elif date.day == 4 and student_id.is_absent == False: 
                                val = {'four':True}
            
                            elif date.day == 5 and student_id.is_absent == True:
                                val = {'five':False}
                                                
                            elif date.day == 5 and student_id.is_absent == False: 
                                val = {'five':True}
                                            
                            elif date.day == 6 and student_id.is_absent == True:
                                val = {'six':False}
                            
                            elif date.day == 6 and student_id.is_absent == False: 
                                val = {'six':True}
            
                            elif date.day == 7 and student_id.is_absent == True:
                                val = {'seven':False}
                                                
                            elif date.day == 7 and student_id.is_absent == False: 
                                val = {'seven':True}
                                            
                            elif date.day == 8 and student_id.is_absent == True:
                                val = {'eight':False}
                            
                            elif date.day == 8 and student_id.is_absent == False: 
                                val = {'eight':True}
            
                            elif date.day == 9 and student_id.is_absent == True:
                                val = {'nine':False}
                                                
                            elif date.day == 9 and student_id.is_absent == False: 
                                val = {'nine':True}
                                            
                            elif date.day == 10 and student_id.is_absent == True:
                                val = {'ten':False}
                            
                            elif date.day == 10 and student_id.is_absent == False: 
                                val = {'ten':True}
            
                            elif date.day == 11 and student_id.is_absent == True:
                                val = {'one_1':False}
                                                
                            elif date.day == 11 and student_id.is_absent == False: 
                                val = {'one_1':True}
                                            
                            elif date.day == 12 and student_id.is_absent == True:
                                val = {'one_2':False}
                            
                            elif date.day == 12 and student_id.is_absent == False: 
                                val = {'one_2':True}
            
                            elif date.day == 13 and student_id.is_absent == True:
                                val = {'one_3':False}
                                                
                            elif date.day == 13 and student_id.is_absent == False: 
                                val = {'one_3':True}
                                            
                            elif date.day == 14 and student_id.is_absent == True:
                                val = {'one_4':False}
                            
                            elif date.day == 14 and student_id.is_absent == False: 
                                val = {'one_4':True}
            
                            elif date.day == 15 and student_id.is_absent == True:
                                val = {'one_5':False}
                                                
                            elif date.day == 15 and student_id.is_absent == False: 
                                val = {'one_5':True}
                                            
                            elif date.day == 16 and student_id.is_absent == True:
                                val = {'one_6':False}
                            
                            elif date.day == 16 and student_id.is_absent == False: 
                                val = {'one_6':True}
            
                            elif date.day == 17 and student_id.is_absent == True:
                                val = {'one_7':False}
                                                
                            elif date.day == 17 and student_id.is_absent == False: 
                                val = {'one_7':True}
                                            
                            elif date.day == 18 and student_id.is_absent == True:
                                val = {'one_8':False}
                            
                            elif date.day == 18 and student_id.is_absent == False: 
                                val = {'one_8':True}
                                
                            elif date.day == 19 and student_id.is_absent == True:
                                val = {'one_9':False}
                            
                            elif date.day == 19 and student_id.is_absent == False: 
                                val = {'one_9':True}
            
                            
                            elif date.day == 20 and student_id.is_absent == True:
                                val = {'one_0':False}
                                                
                            elif date.day == 20 and student_id.is_absent == False: 
                                val = {'one_0':True}
            
                            elif date.day == 21 and student_id.is_absent == True:
                                val = {'two_1':False}
                            
                            elif date.day == 21 and student_id.is_absent == False: 
                                val = {'two_1':True}
            
                            elif date.day == 22 and student_id.is_absent == True:
                                val = {'two_2':False}
                                                
                            elif date.day == 22 and student_id.is_absent == False: 
                                val = {'two_2':True}
            
                            elif date.day == 23 and student_id.is_absent == True:
                                val = {'two_3':False}
                            
                            elif date.day == 23 and student_id.is_absent == False: 
                                val = {'two_3':True}
            
                            
                            elif date.day == 24 and student_id.is_absent == True:
                                val = {'two_4':False}
                                                
                            elif date.day == 24 and student_id.is_absent == False: 
                                val = {'two_4':True}
            
                            elif date.day == 25 and student_id.is_absent == True:
                                val = {'two_5':False}
                            
                            elif date.day == 25 and student_id.is_absent == False: 
                                val = {'two_5':True}
            
                            elif date.day == 26 and student_id.is_absent == True:
                                val = {'two_6':False}
                                                
                            elif date.day == 26 and student_id.is_absent == False: 
                                val = {'two_6':True}
            
                            elif date.day == 27 and student_id.is_absent == True:
                                val = {'two_7':False}
                            
                            elif date.day == 27 and student_id.is_absent == False: 
                                val = {'two_7':True}
            
                            
                            elif date.day == 28 and student_id.is_absent == True:
                                val = {'two_8':False}
                                                
                            elif date.day == 28 and student_id.is_absent == False: 
                                val = {'two_8':True}
            
                            elif date.day == 29 and student_id.is_absent == True:
                                val = {'two_9':False}
                            
                            elif date.day == 29 and student_id.is_absent == False: 
                                val = {'two_9':True}
            
                    
                            elif date.day == 30 and student_id.is_absent == True:
                                val = {'two_0':False}
                                                
                            elif date.day == 30 and student_id.is_absent == False: 
                                val = {'two_0':True}
            
                            elif date.day == 31 and student_id.is_absent == True:
                                val = {'three_1':False}
                                                
                            elif date.day == 31 and student_id.is_absent == False: 
                                val = {'three_1':True}
                            else:
                                val = {}
                                
                            attendance_sheet_line_obj.write(cr, uid, search_id, val, context=context)
                
                if attendance_sheet_id:
                    for student_id in line.student_ids:
                        dict = attendance_sheet_line_obj.read(cr, uid, student_id.roll_no)
                        domain = [('roll_no', '=', student_id.roll_no),('standard_id', '=', attendance_sheet_id)]
                        search_id = attendance_sheet_line_obj.search(cr, uid, domain)
                        if date.day == 1 and student_id.is_absent == True:
                            val = {'one':False}
                                            
                        elif date.day == 1 and student_id.is_absent == False: 
                            val = {'one':True}
                                      
                        elif date.day == 2 and student_id.is_absent == True:
                            val = {'two':False}
                        
                        elif date.day == 2 and student_id.is_absent == False: 
                            val = {'two':True}
        
                        elif date.day == 3 and student_id.is_absent == True:
                            val = {'three':False}
                                            
                        elif date.day == 3 and student_id.is_absent == False: 
                            val = {'three':True}
                                        
                        elif date.day == 4 and student_id.is_absent == True:
                            val = {'four':False}
                        
                        elif date.day == 4 and student_id.is_absent == False: 
                            val = {'four':True}
        
                        elif date.day == 5 and student_id.is_absent == True:
                            val = {'five':False}
                                            
                        elif date.day == 5 and student_id.is_absent == False: 
                            val = {'five':True}
                                        
                        elif date.day == 6 and student_id.is_absent == True:
                            val = {'six':False}
                        
                        elif date.day == 6 and student_id.is_absent == False: 
                            val = {'six':True}
        
                        elif date.day == 7 and student_id.is_absent == True:
                            val = {'seven':False}
                                            
                        elif date.day == 7 and student_id.is_absent == False: 
                            val = {'seven':True}
                                        
                        elif date.day == 8 and student_id.is_absent == True:
                            val = {'eight':False}
                        
                        elif date.day == 8 and student_id.is_absent == False: 
                            val = {'eight':True}
        
                        elif date.day == 9 and student_id.is_absent == True:
                            val = {'nine':False}
                                            
                        elif date.day == 9 and student_id.is_absent == False: 
                            val = {'nine':True}
                                        
                        elif date.day == 10 and student_id.is_absent == True:
                            val = {'ten':False}
                        
                        elif date.day == 10 and student_id.is_absent == False: 
                            val = {'ten':True}
        
                        elif date.day == 11 and student_id.is_absent == True:
                            val = {'one_1':False}
                                            
                        elif date.day == 11 and student_id.is_absent == False: 
                            val = {'one_1':True}
                                        
                        elif date.day == 12 and student_id.is_absent == True:
                            val = {'one_2':False}
                        
                        elif date.day == 12 and student_id.is_absent == False: 
                            val = {'one_2':True}
        
                        elif date.day == 13 and student_id.is_absent == True:
                            val = {'one_3':False}
                                            
                        elif date.day == 13 and student_id.is_absent == False: 
                            val = {'one_3':True}
                                        
                        elif date.day == 14 and student_id.is_absent == True:
                            val = {'one_4':False}
                        
                        elif date.day == 14 and student_id.is_absent == False: 
                            val = {'one_4':True}
        
                        elif date.day == 15 and student_id.is_absent == True:
                            val = {'one_5':False}
                                            
                        elif date.day == 15 and student_id.is_absent == False: 
                            val = {'one_5':True}
                                        
                        elif date.day == 16 and student_id.is_absent == True:
                            val = {'one_6':False}
                        
                        elif date.day == 16 and student_id.is_absent == False: 
                            val = {'one_6':True}
        
                        elif date.day == 17 and student_id.is_absent == True:
                            val = {'one_7':False}
                                            
                        elif date.day == 17 and student_id.is_absent == False: 
                            val = {'one_7':True}
                                        
                        elif date.day == 18 and student_id.is_absent == True:
                            val = {'one_8':False}
                        
                        elif date.day == 18 and student_id.is_absent == False: 
                            val = {'one_8':True}
                            
                        elif date.day == 19 and student_id.is_absent == True:
                            val = {'one_9':False}
                        
                        elif date.day == 19 and student_id.is_absent == False: 
                            val = {'one_9':True}
        
                        
                        elif date.day == 20 and student_id.is_absent == True:
                            val = {'one_0':False}
                                            
                        elif date.day == 20 and student_id.is_absent == False: 
                            val = {'one_0':True}
        
                        elif date.day == 21 and student_id.is_absent == True:
                            val = {'two_1':False}
                        
                        elif date.day == 21 and student_id.is_absent == False: 
                            val = {'two_1':True}
        
                        elif date.day == 22 and student_id.is_absent == True:
                            val = {'two_2':False}
                                            
                        elif date.day == 22 and student_id.is_absent == False: 
                            val = {'two_2':True}
        
                        elif date.day == 23 and student_id.is_absent == True:
                            val = {'two_3':False}
                        
                        elif date.day == 23 and student_id.is_absent == False: 
                            val = {'two_3':True}
        
                        
                        elif date.day == 24 and student_id.is_absent == True:
                            val = {'two_4':False}
                                            
                        elif date.day == 24 and student_id.is_absent == False: 
                            val = {'two_4':True}
        
                        elif date.day == 25 and student_id.is_absent == True:
                            val = {'two_5':False}
                        
                        elif date.day == 25 and student_id.is_absent == False: 
                            val = {'two_5':True}
        
                        elif date.day == 26 and student_id.is_absent == True:
                            val = {'two_6':False}
                                            
                        elif date.day == 26 and student_id.is_absent == False: 
                            val = {'two_6':True}
        
                        elif date.day == 27 and student_id.is_absent == True:
                            val = {'two_7':False}
                        
                        elif date.day == 27 and student_id.is_absent == False: 
                            val = {'two_7':True}
        
                        
                        elif date.day == 28 and student_id.is_absent == True:
                            val = {'two_8':False}
                                            
                        elif date.day == 28 and student_id.is_absent == False: 
                            val = {'two_8':True}
        
                        elif date.day == 29 and student_id.is_absent == True:
                            val = {'two_9':False}
                        
                        elif date.day == 29 and student_id.is_absent == False: 
                            val = {'two_9':True}
        
                
                        elif date.day == 30 and student_id.is_absent == True:
                            val = {'two_0':False}
                                            
                        elif date.day == 30 and student_id.is_absent == False: 
                            val = {'two_0':True}
        
                        elif date.day == 31 and student_id.is_absent == True:
                            val = {'three_1':False}
                                            
                        elif date.day == 31 and student_id.is_absent == False: 
                            val = {'three_1':True}
                        else:
                            val = {}
                            
                        attendance_sheet_line_obj.write(cr, uid, search_id, val, context=context)
                
        self.write(cr, uid, ids, {'state' : 'validate'}, context=context)
        return True

class daily_attendance_line(osv.Model):
    
    ''' Defining Daily Attendance Sheet Line Information '''
    _description ='Daily Attendance Line'
    _name = 'daily.attendance.line'
    _order = 'roll_no'
    _rec_name= 'roll_no'

    _columns = {
        'roll_no':fields.integer('Roll No.', required=True, help='Roll Number'), 
        'standard_id': fields.many2one('daily.attendance', 'Standard'), 
        'stud_id': fields.many2one('student.student','Name', required=True), 
        'is_present': fields.boolean('Present'), 
        'is_absent': fields.boolean('Absent'), 
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: