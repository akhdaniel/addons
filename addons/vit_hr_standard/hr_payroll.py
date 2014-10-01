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
    Tiket Pay Slip
    '''

    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    _description = 'Pay Slip Inheriteed tiket'
    
    
    # _defaults = {
    #     'date_from': lambda *a: time.strftime('%Y-%m-25'),
    #     'date_to': lambda *a: time.strftime('%Y-%m+1 -25'),

    # }
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

            att = {
                 'name': _("Attendance"),
                 'sequence': 2,
                 'code': 'ATT',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            } 

            ovt = {
                 'name': _("Overtime"),
                 'sequence': 3,
                 'code': 'OVT',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }                       
            leaves = {}
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
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
                    else:
                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + [att] + [ovt] + leaves
        return res     



    def compute_sheet(self, cr, uid, ids, context=None):         
        slip_line_pool = self.pool.get('hr.payslip.line')
        sequence_obj = self.pool.get('ir.sequence')
        contract_obj = self.pool.get("hr.contract")
        employ = self.pool.get("hr.employee")

        for payslip in self.browse(cr, uid, ids, context=context):

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

            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
               
                sud= line['code']

                if sud =="BASIC":
                    amn = line['amount']
                    self.write(cr, uid, [payslip.id], {'basic':amn}, context=context)
                elif sud =="GROSS":
                    amn = line['amount']
                    self.write(cr, uid, [payslip.id], {'gross':amn}, context=context)  
                elif sud == "MLNS":
                    amn == line['amount'] 
                    self.write(cr, uid, [payslip.id], {'um':amn}, context=context)
                elif sud == "MLS":
                    amn == line['amount'] 
                    self.write(cr, uid, [payslip.id], {'um':amn}, context=context)                    
                elif sud == "UL":
                    amn = line['amount']
                    self.write(cr, uid, [payslip.id], {'ul':amn}, context=context)
                elif sud =="BNS":
                    amn = line['amount']
                    self.write(cr, uid, [payslip.id], {'bns':amn}, context=context)
                elif sud =="THR":
                    amn = line['amount']
                    self.write(cr, uid, [payslip.id], {'thr':amn}, context=context)                    
                elif sud =="TRP":
                    amn = line['amount']
                    self.write(cr, uid, [payslip.id], {'transport':amn}, context=context)
                elif sud =="NET":
                    amn = line['amount']
                    self.write(cr, uid, [payslip.id], {'net':amn}, context=context)
                elif sud =="JHTTK":
                    amn = line['amount']
                    self.write(cr, uid, [payslip.id], {'jms':amn}, context=context)

                elif sud =="OTS":
                    #import pdb;pdb.set_trace()
                    amn = line['amount']
                    self.write(cr, uid, [payslip.id], {'total_lembur':amn}, context=context)
                elif sud =="OTNS":
                    amn = line['amount']
                    self.write(cr, uid, [payslip.id], {'lembur_non_staff':amn}, context=context)                    
         
            
                    
                                                
            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number})

        return True     

 
    _columns = {
        'total_lembur' : fields.float("Total Lembur"),
        'um': fields.float("Uang Makan"),
        'transport': fields.float("Transport"),
        'ul': fields.float("Unpaid Leave"),
        'jms' : fields.float('Jamsostek 2%'),
        'basic' : fields.float('GaPok'),
        'gross' : fields.float('Gross'),
        'net' : fields.float('Net'),
        'thr' : fields.float('THR'),
        'bns' : fields.float('Bonus'),
    } 
