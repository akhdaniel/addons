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
import pprint

class hr_payslip(osv.osv):
    '''
    PPI Pay Slip
    '''

    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    _description = 'Pay Slip Inheriteed PPI'
    
 

    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            if holiday_ids:
                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
            return res

        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }


            presences = {
                 'name': _("Presences"),
                 'sequence': 2,
                 'code': 'PRESENCES',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }

            overtimes = {
                 'name': _("Overtime"),
                 'sequence': 2,
                 'code': 'OVERTIME',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            
            overtimes_trs = {
                 'name': _("Overtime Transport"),
                 'sequence': 2,
                 'code': 'OVERTIMETRS',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            
            incentives = {
                 'name': _("Incentives"),
                 'sequence': 3,
                 'code': 'INCENTIVES',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            leaves = {}
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
            	# cek dari jadwal kerja, berapa jam sehari employee bekerja
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                #working_hours_on_day = 8.00

                if working_hours_on_day:
                    #the employee had to work
                    employee_id = contract.employee_id.id

                    #employee info
                    emp_obj = self.pool.get('hr.employee')
                    employee = emp_obj.browse(cr, uid, employee_id, context=context)

                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)

                    if leave_type:
                        ###### cuti	
                        #if he was on leave, fill the leaves dict
                        
                        if leave_type in leaves:
                            
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                            
                           # xo += working_hours_on_day
                        else:
                            #import pdb;pdb.set_trace()
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            #xos += 1.0
                            
                           # xi += working_hours_on_day    
                            }

                    real_working_hours_on_day = self.pool.get('hr.attendance').real_working_hours_on_day(cr,uid, contract.employee_id.id, day_from + timedelta(days=day),context)

                    date = (day_from + timedelta(days=day))
                    
                    isNonWorkingDay = date.isoweekday()==6 or date.isoweekday()==7 or leave_type 
                    if isNonWorkingDay == False :
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
                        ### tidak cuti, cek apakah dia masuk absen?
                    if real_working_hours_on_day > 0 and not isNonWorkingDay:
                        presences['number_of_days'] += 1.0
                        presences['number_of_hours'] += working_hours_on_day
                    no_urut = employee.gol_id.no
                    urut_title = employee.title_id.urutan
                    pprint.pprint(no_urut)
                    pprint.pprint(urut_title)
                    no_urut=float(no_urut)
                    urut_title=float(urut_title)
                    if real_working_hours_on_day >= working_hours_on_day and urut_title < 100 :
                        #add the input vals to tmp (increment if existing)
                        # number_of_days = hari masuk dalam sebulan sesuai absensi

                        ### hitung overtime: masukkan di field number_of_hours
                        overtime =  real_working_hours_on_day - working_hours_on_day
                        if overtime >= 4 or isNonWorkingDay :
                            overtimes['number_of_days'] += 1.0

                        """
                        isNonWorkingDay : dihitung berdasarkan jam hadir
                        workingDay: dihitung berdasarkan jam lembur (jam hadir - jam kerja normal)



                        if employee.title_id.urutan < 100:

                        """


                        if isNonWorkingDay:
                            if real_working_hours_on_day < 8:
                                jam1 = 0
                                jam2 = real_working_hours_on_day
                                jam3 = 0
                                jam4 = 0
                            elif (real_working_hours_on_day >= 8 and real_working_hours_on_day<9):
                                jam1 = 0
                                jam2 = 7
                                jam3 = real_working_hours_on_day - 7
                                jam4 = 0
                            elif real_working_hours_on_day>9:
                                jam1 = 0
                                jam2 = 7
                                jam3 = 1
                                jam4 = real_working_hours_on_day - 8                            
                            overtimes_trs['number_of_days'] += 1.0
                        else:
                            if overtime <=1:
                                jam1 = overtime
                                jam2 = 0
                                jam3 = 0
                                jam4 = 0
                            elif (overtime > 1 ):
                                jam1 = 1
                                jam2 = overtime - 1
                                jam3 = 0
                                jam4 = 0

                        total_overtime = jam1*1.5 + jam2*2.0 + jam3*3.0 + jam4*4.0

                        overtimes['number_of_hours'] += total_overtime
                    elif urut_title > 100 and urut_title < 200:   
                        if no_urut < 200 :
                            if isNonWorkingDay and real_working_hours_on_day > 4:
                                incentives['number_of_days'] += 1.0
                        """ title = kolom sortir
                        else if employee.title_id > 100 : #operator ke atas:
                            employee.gol_id.urutan > 1 and  employee.gol_id.urutan < 3 :
                              xml rule =  incentive: contract.wage/12 * worked_days.INCENTIVE.number_of_days
                                 if isNonWorkingDay && real_working_hours_on_day > 4:
                                    incentives['number_of_days'] += 1.0
                                 

                                else :employee.gol_id.urutan > 4:
                                    nol
                            """                 
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves + [presences] + [overtimes] + [overtimes_trs] + [incentives]
        return res
    '''    
    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
        empolyee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        worked_days_obj = self.pool.get('hr.payslip.worked_days')
        input_obj = self.pool.get('hr.payslip.input')

        if context is None:
            context = {}
        #delete old worked days lines
        old_worked_days_ids = ids and worked_days_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_worked_days_ids:
            worked_days_obj.unlink(cr, uid, old_worked_days_ids, context=context)

        #delete old input lines
        old_input_ids = ids and input_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_input_ids:
            input_obj.unlink(cr, uid, old_input_ids, context=context)


        #defaults
        res = {'value':{
                      'line_ids':[],
                      'input_line_ids': [],
                      'worked_days_line_ids': [],
                      #'details_by_salary_head':[], TODO put me back
                      'name':'',
                      'contract_id': False,
                      'struct_id': False,
                      }
            }       
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
        employee_gol = employee_id.gol_id.name
        employee_dep = employee_id.department_id.name
        grade_obj =self.pool.get('hr_employs.gol') 
        grade_src=grade_obj.search(cr,uid,[('name','=',employee_gol)])
        grade_id=grade_obj.browse(cr,uid,grade_src,context=context)        
        dep_obj =self.pool.get('hr.department') 
        dep_src=dep_obj.search(cr,uid,[('name','=',employee_dep)])
        dep_id=dep_obj.browse(cr,uid,grade_src,context=context)
        for grade in grade_id :
            grade_pay = grade.id
            #for dep in dep_id :
             #   dep_pay = dep_id.id
            res['value'].update({
                            'name': _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
                            'company_id': employee_id.company_id.id,
                            'gol_id': grade_pay,
                           # 'department_id' : dep_pay
                })

        if not context.get('contract', False):
            #fill with the first contract of the employee
            contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)
        else:
            if contract_id:
                #set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)

        if not contract_ids:
            return res
        contract_record = contract_obj.browse(cr, uid, contract_ids[0], context=context)
        res['value'].update({
                    'contract_id': contract_record and contract_record.id or False
        })
        struct_record = contract_record and contract_record.struct_id or False
        if not struct_record:
            return res
        res['value'].update({
                    'struct_id': struct_record.id,
        })
        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context=context)
        input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
        res['value'].update({
                    'worked_days_line_ids': worked_days_line_ids,
                    'input_line_ids': input_line_ids,
        })
        return res
     '''
hr_payslip()


class hr_attendance(osv.osv):
    _name = "hr.attendance"
    _inherit = "hr.attendance"
    _description = "Attendance PPI"

    def real_working_hours_on_day(self, cr, uid, employee_id, datetime_day, context=None):
        day = datetime_day.strftime("%Y-%m-%d 00:00:00")
        day2 = datetime_day.strftime("%Y-%m-%d 24:00:00")

        pprint.pprint(day)


        #employee attendance
        atts_ids = self.search(cr, uid, [('employee_id', '=', employee_id), ('name', '>', day), ('name', '<', day2)], limit=2, order='name asc' )
        
        time1=0
        time2=0

        for att in self.browse(cr, uid, atts_ids, context=context):
            if att.action == 'sign_in':
            	pprint.pprint('sign_in')
            	pprint.pprint(att.name)
                time1 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
            else:
            	pprint.pprint('sign_out')
            	pprint.pprint(att.name)
                time2 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
        
        if time2 and time1:
	        delta = (time2 - time1).seconds / 3600.00
        else:
            delta = 0

        pprint.pprint(delta)        
        return delta

    def _altern_si_so(self, cr, uid, ids, context=None):
        """ Alternance sign_in/sign_out check.
            Previous (if exists) must be of opposite action.
            Next (if exists) must be of opposite action.

            PPI: skip _constraints supaya bisa import dari CSV
        """
        return True

hr_attendance()

class hr_salary_rule(osv.osv):
    _name = 'hr.salary.rule'
    _inherit = 'hr.salary.rule'
    
    _columns = {
        'amount_python_compute':fields.text('Python Code',readonly=True),
            }
hr_salary_rule()