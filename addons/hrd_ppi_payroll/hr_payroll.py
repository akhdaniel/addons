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
                 'code': 'Overtime',
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
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else: 

                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
                        ### tidak cuti, cek apakah dia masuk absen?
                        real_working_hours_on_day = self.pool.get('hr.attendance').real_working_hours_on_day(cr,uid, contract.employee_id.id, day_from + timedelta(days=day),context)

                        date = (day_from + timedelta(days=day))
                        isNonWorkingDay = date.isoweekday()==6 or date.isoweekday()==7

                        if real_working_hours_on_day > 0:
                            presences['number_of_days'] += 1.0
                            presences['number_of_hours'] += working_hours_on_day

                        if real_working_hours_on_day >= working_hours_on_day:
                            #add the input vals to tmp (increment if existing)
                            # number_of_days = hari masuk dalam sebulan sesuai absensi

	                        ### hitung overtime: masukkan di field number_of_hours
                            overtime =  real_working_hours_on_day - working_hours_on_day
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

                            """
                            else if employee.title_id > 100 : #operator ke atas:
                                gol_id 1- 3 :
                                    incentive: gajipokok/12 * jlm hari hadir di NonWorkingDay
                                    incentives['number_of_days'] += 1.0 jika isNonWorkingDay && real_working_hours_on_day > 4

                                gol_id 4-7:
                                    nol
                            """

            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves + [presences] + [overtimes] 
        return res

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
