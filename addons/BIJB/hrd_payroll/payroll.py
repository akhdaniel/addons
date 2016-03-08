import time
import pprint
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval

class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''

    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'

    def compute_sheet(self, cr, uid, ids, context=None):
        slip_line_pool = self.pool.get('hr.payslip.line')
        sequence_obj = self.pool.get('ir.sequence')
        for payslip in self.browse(cr, uid, ids, context=context):
            
            # mencari jumlah izin dan sakit
            line_ids = payslip.worked_days_line_ids
            jum = 0.0
            for IS in line_ids :
                codes = IS.code
                if codes == "IZIN" or codes == "SAKIT" :
                    jum += IS.number_of_days
            self.write(cr,uid,[payslip.id],{'jum_is': jum}) 
            #################

            number = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')
            #delete old payslip lines
            old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
#            old_slipline_ids
            if old_slipline_ids:
                slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)
            if payslip.contract_id:
                #set the list of contract for which the rules have to be applied
                contract_ids = [payslip.contract_id.id]
            else:
                #if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)
            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number,}, context=context)     
        return True

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
        jum_is = 0

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
            lembur = {
                 'name': _("Lembur"),
                 'sequence': 2,
                 'code': 'LEMBUR',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            tanpa_keterangan = {
                 'name': _("Tanpa keterangan"),
                 'sequence': 2,
                 'code': 'TK',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            leaves = {}            
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1

            tanpa_keterangan1 = 0.0
            
            for day in range(0, nb_of_days):
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                
                #menghitung lembur
                employee_id = contract.employee_id.id
                datas = day_from + timedelta(days=day)
    	        tanggal = datas.strftime("%Y-%m-%d")
    	    	obj_over = self.pool.get('hr.overtime')
    	        src_over = obj_over.search(cr,uid,[('employee_id','=',employee_id),('tanggal','=',tanggal),('state','=','validate')])
                for overt in obj_over.browse(cr,uid,src_over) :
    	            if overt.overtime_type_id.name == 'Lembur' :
    	                jumlah = overt.total_jam1
    	                jumlah_ril = overt.jam_lembur
    	                lembur['number_of_hours'] += jumlah

                if working_hours_on_day:
                    #the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    if leave_type:
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

                        # attendance
                        if leave_type == "IZIN" or leave_type == "SAKIT" :
                            jum_is += 1

                    else:
                    	
                    	#kehadiran
                    	real_working_hours_on_day = self.pool.get('hr.attendance').real_working_hours_on_day(cr,uid, contract.employee_id.id, day_from + timedelta(days=day),context)
                        if real_working_hours_on_day >= 0.000000000000000001 and leave_type == False :
	                        presences['number_of_days'] += 1.0
	                        presences['number_of_hours'] += working_hours_on_day

                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day

            tanpa_keterangan['number_of_days'] = attendances['number_of_days'] - presences['number_of_days'] #- tanpa_keterangan1
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves + [presences] + [lembur] + [tanpa_keterangan]
        return res
    
    _columns = {
        'jum_is' : fields.integer("Jumlah"),
    }        


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