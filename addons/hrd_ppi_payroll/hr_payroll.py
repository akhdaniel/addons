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
                 'name': _("Transport Hari Libur"),
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
                    working_hours=int(real_working_hours_on_day)
                    working_minutes=real_working_hours_on_day - working_hours
                    work_minutes = working_minutes / 1.66666667
                    if working_minutes > 0.15 and working_minutes <= 0.45 :
                        real_working_hours_on_day= working_hours + (0.30 * 1.66666667)
                    elif working_minutes >= 0.45 :    
                        real_working_hours_on_day= working_hours + 1
                    elif working_minutes < 15 :
                        real_working_hours_on_day= working_hours  						
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
                            elif real_working_hours_on_day>=9:
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
        
    def compute_sheet(self, cr, uid, ids,employee_id, context=None):    
        #import pdb;pdb.set_trace()     
        slip_line_pool = self.pool.get('hr.payslip.line')
        sequence_obj = self.pool.get('ir.sequence')
        contract_obj = self.pool.get("hr.contract")
        reimburse_obj = self.pool.get("reimburse")

        for payslip in self.browse(cr, uid, ids, context=context):   
            emp=payslip.employee_id.name
            emp_id=reimburse_obj.search(cr, uid, [('employee_id', '=', emp)], context=context)           
            date_contract=payslip.contract_id.date_start
            date_from=payslip.date_from
            date_to = payslip.date_to
            date_cont = datetime.strptime(date_contract,"%Y-%m-%d").year
            date_pays = datetime.strptime(date_to,"%Y-%m-%d").year
            year =(date_pays - date_cont) / 5
            date_cont = datetime.strptime(date_contract,"%Y-%m-%d").month
            date_pays = datetime.strptime(date_to,"%Y-%m-%d").month
            nom=0.00
            nam=0.00
            if year == 1 or year == 2 or year == 3 or year == 4 or year == 5 or year == 6 or year == 7 or year ==8 or year == 9 or year == 10 :
                if date_cont == date_pays :
                    nilai=1
                    self.write(cr, uid,ids, {'komisi': nilai}, context=context)
            for su in reimburse_obj.browse(cr, uid, emp_id, context=context):
                tgl=su.tanggal
                jn=su.jenis
                st=su.state               
                if tgl >= date_from and tgl <= date_to and st == 'approve2' and jn == 'obat' :    
                    nom=su.nomin+nom
                    self.write(cr, uid,ids, {'reimburse_obat': nom}, context=context)
                if tgl >= date_from and tgl <= date_to and st == 'approve2' and jn == 'rawat' :    
                    nam=su.nomin+nam
                    self.write(cr, uid,ids, {'reimburse_rawat': nam}, context=context)                    
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
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                cod= line['code']
                if cod == "NET":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'net':coo}, context=context)     
                if cod == "POT_ABSEN":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'pot_absen':coo}, context=context) 
                if cod == "GROSS":
                    coo = line['amount']
                    self.write(cr, uid, [payslip.id], {'gros':coo}, context=context)     
                    coos = self.funct(cr,uid,ids,context=None)    
                    self.write(cr, uid, [payslip.id], {'total':coos}, context=context)
                    coos = self.pkp(cr,uid,ids,context=None)  
                    self.write(cr, uid, [payslip.id], {'pkp':coos}, context=context)
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number}, context=context)
        return True
		
    def funct(self,cr,uid,ids,context=None) :
        xxx=self.browse(cr,uid,ids)[0]
        xyz=xxx.employee_id.name
        ccc=xxx.date_to
        yyy=datetime.strptime(ccc,"%Y-%m-%d").year
        self_obj=self.pool.get('hr.payslip')
        src_obj=self_obj.search(cr,uid,[('employee_id','=',xyz)])
        obj=self_obj.browse(cr,uid,src_obj)
        totals = 0.0
        for xyc in obj :
            ttt=xyc.date_to
            ttx=datetime.strptime(ttt,"%Y-%m-%d").year
            if yyy == ttx :
                gtot= xyc.gros + xyc.pot_absen
                totals = totals + gtot
        return totals

    def pkp(self,cr,uid,ids,context=None) :
        xxx=self.browse(cr,uid,ids)[0]
        xcz=xxx.total
        self_obj=self.pool.get('hr.pkp')
        src_obj=self_obj.search(cr,uid,[])
        obj = self_obj.browse(cr,uid,src_obj)
        for ccc in obj :
            ocd = ccc.nominal_min
            occ = ccc.nominal_max
            if xcz >= ocd and xcz <= occ :
                pkp = ccc.pajak
        return pkp    	
    
    _columns = {
        'net' : fields.integer("Net"),
        'komisi': fields.integer("komisi"),
        'reimburse_obat':fields.float('Total Reimburse Obat'),
        'reimburse_rawat':fields.float('Total Reimburse Rawat'),
        'pot_absen':fields.float('Potongan Absen'),
        'gros':fields.float('gros'),
        'total':fields.float('total'), 
        'pkp' :fields.float('pkp'),
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

class hr_salary_rule(osv.osv):
    _name = 'hr.salary.rule'
    _inherit = 'hr.salary.rule'     
    
    _columns={
        'amount_python_compute':fields.text('Python Code',readonly=True),
        'condition_range':fields.selection([('contract.wage','Gaji Pokok'),('employee.children','Jumlah Anak'),('emoployee.remaining_leaves','Sisa Cuti'),('employee.vehicle_distance','Jarak dari Rumah ke Kantor'),('employee.job_id.urutan','Jabatan/Title'),('employee.gol_id.no','Golongan'),('worked_days.PRESENCES.number_of_days','Jumlah Kehadiran Perbulan'),('inputs.THR.amount','Jumlah THR'),('inputs.TUNJANGAN_PAJAK.amount','Tunjangan Pajak'),('inputs.MEDICAL_REFUND.amount','Medical Refund'),('inputs.MEDICAL_REFUND.amount','Medical Allowance'),('inputs.BONUS.amount','Jumlah Bonus'),('inputs.RAPEL.amount','Jumlah Rapel'),('inputs.HOUSING.amount','Housing Allowance'),('inputs.LUAR_KOTA.amount','Tunjangan Luar Kota'),('inputs.PULSA.amount','Tunjangan Pulsa')],'Range Based on', readonly=False, help='This will be used to compute the % fields values; in general it is on basic, but you can also use categories code fields in lowercase as a variable names (hra, ma, lta, etc.) and the variable basic.'),
            }
    
    _defaults={
        'condition_range':'contract.wage',
            }
   
    def _check_crange(self, cr, uid, ids):
        for crange in self.browse(cr, uid, ids):
            crange_id = self.search(cr, uid, [('condition_range_min', '>', crange.condition_range_max), ('condition_range_max', '<', crange.condition_range_min)])
            if crange_id:
                return False
        return True      
            
    _constraints = [
        (_check_crange, 'range max tidak boleh lebih kecil dari range min!', ['condition_range_min','condition_range_max']),
                    ]
hr_salary_rule()

class hr_payslip_worked_days(osv.osv):
    '''
    Payslip Worked Days
    '''

    _name = 'hr.payslip.worked_days'
    _inherit = 'hr.payslip.worked_days'
    _description = 'Payslip Worked Days'
    _columns = {
        'name': fields.char('Description', size=256, required=True,readonly=True),
        'payslip_id': fields.many2one('hr.payslip', 'Pay Slip', required=True, ondelete='cascade', select=True),
        'sequence': fields.integer('Sequence', required=True, select=True),
        'code': fields.char('Code', size=52, required=True, help="The code that can be used in the salary rules",readonly=True),
        'number_of_days': fields.float('Number of Days',readonly=True),
        'number_of_hours': fields.float('Number of Hours',readonly=True),
        'contract_id': fields.many2one('hr.contract', 'Contract', required=True, help="The contract for which applied this input",readonly=True),
    }
    _order = 'payslip_id, sequence'
    _defaults = {
        'sequence': 10,
    }
hr_payslip_worked_days()

class hr_payslip_run(osv.osv):

    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'
        
    def approve (self, cr, uid, ids, context=None):
        data = self.browse(cr,uid,ids)[0]
        payslip_obj = self.pool.get('hr.payslip')       
        return payslip_obj.write(cr, uid, [x.id for x in data.slip_ids], {'state':"done"})

hr_payslip_run()

class hr_salary_rule(osv.osv):
    _name = 'hr.salary.rule'
    _inherit = 'hr.salary.rule'     
    
    _columns={
        'condition_range':fields.selection([('contract.wage','Gaji Pokok'),('employee.children','Jumlah Anak'),('emoployee.remaining_leaves','Sisa Cuti'),('employee.vehicle_distance','Jarak dari Rumah ke Kantor'),('employee.job_id.urutan','Jabatan/Title'),('employee.gol_id.no','Golongan'),('worked_days.PRESENCES.number_of_days','Jumlah Kehadiran Perbulan'),('inputs.THR.amount','Jumlah THR'),('inputs.TUNJANGAN_PAJAK.amount','Tunjangan Pajak'),('inputs.MEDICAL_REFUND.amount','Medical Refund'),('inputs.MEDICAL_REFUND.amount','Medical Allowance'),('inputs.BONUS.amount','Jumlah Bonus'),('inputs.RAPEL.amount','Jumlah Rapel'),('inputs.HOUSING.amount','Housing Allowance'),('inputs.LUAR_KOTA.amount','Tunjangan Luar Kota'),('inputs.PULSA.amount','Tunjangan Pulsa')],'Range Based on', readonly=False, help='This will be used to compute the % fields values; in general it is on basic, but you can also use categories code fields in lowercase as a variable names (hra, ma, lta, etc.) and the variable basic.'),
            }
    
    _defaults={
        'condition_range':'contract.wage',
            }
   
    def _check_crange(self, cr, uid, ids):
        for crange in self.browse(cr, uid, ids):
            crange_id = self.search(cr, uid, [('condition_range_min', '>', crange.condition_range_max), ('condition_range_max', '<', crange.condition_range_min)])
            if crange_id:
                return False
        return True      
            
    _constraints = [
        (_check_crange, 'range max tidak boleh lebih kecil dari range min!', ['condition_range_min','condition_range_max']),
                    ]
                    
hr_salary_rule()