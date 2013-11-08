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

            leaves = {}
           # import pdb;pdb.set_trace()
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
                    #import pdb;pdb.set_trace()
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    if leave_type:
                        ###### cuti	
                        #if he was on leave, fill the leaves dict
                        
                        if leave_type in leaves:
                           # xis += 1.0 
                            if employee.remaining_leaves >= 0 :
                                leaves[leave_type]['number_of_days'] += 1.0
                                leaves[leave_type]['number_of_hours'] += working_hours_on_day
                            else : 
                                xyz=employee.name
                                ccc=date_to
                                yyy=datetime.strptime(ccc,"%Y-%m-%d").year
                                zzz=datetime.strptime(ccc,"%Y-%m-%d")
                                self_obj=self.pool.get('hr.payslip')
                                src_obj=self_obj.search(cr,uid,[('employee_id','=',xyz)])
                                obj=self_obj.browse(cr,uid,src_obj)
                                totals = 0.0
                                alok_cuti = employee.alokasi
                                for xyc in obj :
                                    ttt=xyc.date_to
                                    ttx=datetime.strptime(ttt,"%Y-%m-%d").year
                                    ttz=datetime.strptime(ttt,"%Y-%m-%d")
                                    if yyy == ttx :
                                            totals += xyc.libur
                                if totals == 0.0 :
                                    leaves[leave_type]['number_of_days'] = alok_cuti
                                else :
                                    if totals >= alok_cuti :
                                        leaves[leave_type]['number_of_days'] = 0.0       
                           # xo += working_hours_on_day
                        else:
                            #import pdb;pdb.set_trace()
                            if employee.remaining_leaves >= 0 :
                                leaves[leave_type] = {
                                    'name': leave_type,
                                    'sequence': 5,
                                    'code': leave_type,
                                    'number_of_days': 1.0,
                                    'number_of_hours': working_hours_on_day,
                                    'contract_id': contract.id,
                                    }
                            else : 
                                xyz=employee.name
                                ccc=date_to
                                yyy=datetime.strptime(ccc,"%Y-%m-%d").year
                                zzz=datetime.strptime(ccc,"%Y-%m-%d")
                                self_obj=self.pool.get('hr.payslip')
                                src_obj=self_obj.search(cr,uid,[('employee_id','=',xyz)])
                                obj=self_obj.browse(cr,uid,src_obj)
                                totals = 0.0
                                alok_cuti = employee.alokasi
                                for xyc in obj :
                                    ttt=xyc.date_to
                                    ttx=datetime.strptime(ttt,"%Y-%m-%d").year
                                    ttz=datetime.strptime(ttt,"%Y-%m-%d")
                                    if yyy == ttx :
                                            totals += xyc.libur
                                if totals == 0.0 :
                                    leaves[leave_type] = {
                                    'name': leave_type,
                                    'sequence': 5,
                                    'code': leave_type,
                                    'number_of_days': alok_cuti,
                                    'number_of_hours': working_hours_on_day,
                                    'contract_id': contract.id,
                                    }
                                else :
                                    if totals >= alok_cuti :
                                        leaves[leave_type] = {
                                        'name': leave_type,
                                        'sequence': 5,
                                        'code': leave_type,
                                        'number_of_days': 0.0,
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
                    if real_working_hours_on_day >= 0.000000000000000001 and not isNonWorkingDay:
                        presences['number_of_days'] += 1.0
                        presences['number_of_hours'] += working_hours_on_day
                    #no_urut = employee.gol_id.no
                    #urut_title = employee.title_id.urutan
                    #pprint.pprint(no_urut)
                    #pprint.pprint(urut_title)
                    #no_urut=float(no_urut)
                    #urut_title=float(urut_title)
            import pdb;pdb.set_trace()       
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves + [presences]
        coos = self.line2(cr, uid, contract_ids,context=None) 
        return res + coos
        
    def line2(self, cr, uid, contract_ids, context=None):
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
  
            overtimes = {
                 'name': _("Overtime"),
                 'sequence': 2,
                 'code': 'OVERTIME',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            
            transport = {
                 'name': _("Transport"),
                 'sequence': 2,
                 'code': 'TRANSPORT',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            
            uang_makan = {
                 'name': _("Uang Makan"),
                 'sequence': 2,
                 'code': 'UANG_MAKAN',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            
            uang_makan_lembur = {
                 'name': _("Uang Makan Lembur"),
                 'sequence': 2,
                 'code': 'UANG_MAKAN_LEMBUR',
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
            incentives_meal = {
                 'name': _("Incentives Meal"),
                 'sequence': 3,
                 'code': 'INC_MEAL',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            leaves = {}
            #import pdb;pdb.set_trace()
            date_from_16 =str(datetime.now() + relativedelta.relativedelta(months=+0, day=1, days=-15))[:10]
            date_to_15 =str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-17))[:10]
            day_from = datetime.strptime(date_from_16,"%Y-%m-%d")
            day_to = datetime.strptime(date_to_15,"%Y-%m-%d")
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
                    #import pdb;pdb.set_trace()
                    real_working_hours_on_day = self.pool.get('hr.attendance').real_working_hours_on_day(cr,uid, contract.employee_id.id, day_from + timedelta(days=day),context)
                    if real_working_hours_on_day >= 0.000000000000001 : 
                        transport['number_of_days'] += 1.0
                    if real_working_hours_on_day >= 4 :    
                        uang_makan['number_of_days'] += 1.0
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
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    isNonWorkingDay = date.isoweekday()==6 or date.isoweekday()==7 or leave_type 
                    no_urut = employee.gol_id.no
                    urut_title = employee.title_id.urutan
                    pprint.pprint(no_urut)
                    pprint.pprint(urut_title)
                    no_urut=float(no_urut)
                    urut_title=float(urut_title)
                    if real_working_hours_on_day >= working_hours_on_day :
                        if contract.jenis_lembur == 'overtime' or no_urut < 100 :
                            #add the input vals to tmp (increment if existing)
                            # number_of_days = hari masuk dalam sebulan sesuai absensi

                            ### hitung overtime: masukkan di field number_of_hours
                            overtime =  real_working_hours_on_day - working_hours_on_day
                            if overtime >= 4 :
                                overtimes['number_of_days'] += 1.0
                                uang_makan_lembur['number_of_days'] += 1.0

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
                        elif contract.jenis_lembur == 'incentive' or no_urut >= 200 : 
                            if isNonWorkingDay and real_working_hours_on_day > 4 and no_urut <= 399 :
                                incentives['number_of_days'] += 1.0
                                incentive =  real_working_hours_on_day - working_hours_on_day
                                if incentive >= 4 :
                                    incentives_meal['number_of_days'] += 1.0
                        """ title = kolom sortir
                        else if employee.title_id > 100 : #operator ke atas:
                            employee.gol_id.urutan > 1 and  employee.gol_id.urutan < 3 :
                              xml rule =  incentive: contract.wage/12 * worked_days.INCENTIVE.number_of_days
                                 if isNonWorkingDay && real_working_hours_on_day > 4:
                                    incentives['number_of_days'] += 1.0
                                 

                                else :employee.gol_id.urutan > 4:
                                    nol
                            """     
            res += [overtimes] + [incentives] + [transport] + [uang_makan] + [uang_makan_lembur] + [incentives_meal]                            
        return res
        
    def compute_sheet(self, cr, uid, ids, context=None):         
        slip_line_pool = self.pool.get('hr.payslip.line')
        sequence_obj = self.pool.get('ir.sequence')
        contract_obj = self.pool.get("hr.contract")
        #contract_src = contract_obj.search()
        for payslip in self.browse(cr, uid, ids, context=context):

            date_contract=payslip.contract_id.date_start
            date_to = payslip.date_to
            date_cont = datetime.strptime(date_contract,"%Y-%m-%d").year
            date_pays = datetime.strptime(date_to,"%Y-%m-%d").year
            year =(date_pays - date_cont) / 5
            date_cont = datetime.strptime(date_contract,"%Y-%m-%d").month
            date_pays = datetime.strptime(date_to,"%Y-%m-%d").month
            if year == 1 or year == 2 or year == 3 or year == 4 or year == 5 or year == 6 or year == 7 or year ==8 or year == 9 or year == 10 :
                if date_cont == date_pays :
                    nilai=1
                    self.write(cr, uid,ids, {'komisi': nilai}, context=context)
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
                cod= line['code']
                if cod == "NET":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'net':coo}, context=context)     
                if cod == "POT_ABSEN":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'pot_absen':coo}, context=context)  
                if cod == "POTO_KOPERASI":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'pot_koperasi':coo}, context=context)
                if cod == "POT_SPSI":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'pot_spsi':coo}, context=context)
                if cod == "POT_TELEPON":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'pot_telepon':coo}, context=context)
                if cod == "MEAL":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'umak':coo}, context=context)
                if cod == "TRANSPORT":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'ut':coo}, context=context)  
                if cod == "OT_MEAL":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'uml':coo}, context=context)     
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                cod= line['code']   
                if cod == "GROSS":
                    coo = line['amount']
                    self.write(cr, uid, [payslip.id], {'gros':coo}, context=context)     
                    coos = self.funct(cr,uid,ids,context=None)    
                    self.write(cr, uid, [payslip.id], {'total':coos}, context=context)
                    coos = self.pkp(cr,uid,ids,context=None)  
                    self.write(cr, uid, [payslip.id], {'pkp':coos}, context=context)
            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number})
            ccc =self.libur(cr,uid,ids,context=None)
            self.write(cr,uid,ids,{'libur':ccc},context=context)
        return True     

    def funct(self,cr,uid,ids,context=None) :
        xxx=self.browse(cr,uid,ids)[0]
        xyz=xxx.employee_id.name
        ccc=xxx.date_to
        yyy=datetime.strptime(ccc,"%Y-%m-%d").year
        yy=datetime.strptime(ccc,"%Y-%m-%d").month
        zzz=datetime.strptime(ccc,"%Y-%m-%d")
        self_obj=self.pool.get('hr.payslip')
        src_obj=self_obj.search(cr,uid,[('employee_id','=',xyz)])
        obj=self_obj.browse(cr,uid,src_obj)
        totals = 0.0
        for xyc in obj :
            ttt=xyc.date_to
            ttx=datetime.strptime(ttt,"%Y-%m-%d").year
            ttz=datetime.strptime(ttt,"%Y-%m-%d")
            tt=datetime.strptime(ttt,"%Y-%m-%d").month
            if yyy == ttx :
                if zzz != ttz : 
                    gtot= xyc.gros + xyc.pot_absen
                    total = totals + gtot
            if yyy == ttx :
                if yy >= tt :         
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
        
    def libur (self,cr,uid,ids,context=None):
        #import pdb;pdb.set_trace()
        xxx=self.browse(cr,uid,ids)[0]
        aaa=xxx.name
        date_from_16 =str(datetime.now() + relativedelta.relativedelta(months=+0, day=1))[:10]
        day_from = datetime.strptime(date_from_16,"%Y-%m-%d").year
        cuti = "Cuti Tahunan"
        obj=self.pool.get('hr.payslip.worked_days')
        src=obj.search(cr,uid,[('payslip_id','=',aaa)])
        pay_obj=obj.browse(cr,uid,src,context=context)
        for xyz in pay_obj :
            if xyz.code == cuti :
                ccc = xyz.number_of_days
        return ccc
         

    _columns = {
        'net' : fields.integer("Net"),
        'komisi': fields.integer("komisi"),
        'reimburse_obat':fields.float('Total Reimburse Obat'),
        'reimburse_rawat':fields.float('Total Reimburse Rawat'),
        'pot_absen':fields.float('Potongan Absen'),
        'gros':fields.float('gros'),
        'total':fields.float('total'), 
        'pkp' :fields.float('pkp'),
        'pot_koperasi':fields.float('potongan koperasi'),
        'pot_telepon' :fields.float('potongan telepon'),
        'pot_spsi' : fields.float('potongan spsi'),
        'umak' : fields.float('uang makan'),
        'ut' : fields.float('uang transport'),
        'uml' : fields.float('uang makan lembur'),
        'libur' : fields.float('libur'),
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
        'amount_python_compute':fields.text('Python Code'),
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


class hr_holidays(osv.osv):
    _name = "hr.holidays"
    _description = "Leave"
    _inherit = "hr.holidays"
    
    def check_holidays(self, cr, uid, ids, context=None):
        holi_status_obj = self.pool.get('hr.holidays.status')
        for record in self.browse(cr, uid, ids):
            if record.holiday_type == 'employee' and record.type == 'remove':
                if record.employee_id and not record.holiday_status_id.limit:
                    leaves_rest = holi_status_obj.get_days( cr, uid, [record.holiday_status_id.id], record.employee_id.id, False)[record.holiday_status_id.id]['remaining_leaves']
                    if leaves_rest > record.number_of_days_temp :
                        raise osv.except_osv(_('Warning!'), _('There are not enough %s allocated for employee %s; please create an allocation request for this leave type.') % (record.holiday_status_id.name, record.employee_id.name))            
        return True
    def _aac(self, cr, uid, ids, name, args, context=None):
        result = {}
        date_from_16 =str(datetime.now() + relativedelta.relativedelta(months=+0, day=1))[:10]
        dates = datetime.strptime(date_from_16,"%Y-%m-%d").year
        date = str(dates)
        for hol in self.browse(cr, uid, ids, context=context):
            if hol.type!='remove' and hol.tahun == date :
                result[hol.id] = hol.number_of_days_temp
            else:
                result[hol.id] = 0.0
        return result
        
    _columns = {
        'temp' : fields.function(_aac, "blabla"),
        'tahun': fields.char('tahun',readonly=True),
     }
      
    _defaults = { 
        'tahun' : lambda *a : time.strftime('%Y')    
        }   
         
hr_holidays()  

class hr_employee(osv.osv):
    _inherit="hr.employee"
    
    def _aloc(self, cr, uid, ids, name, args, context=None):
        holiday_obj = self.pool.get("hr.holidays")
        yyy=0.0
        result={}
        zz=0.0
        for reim in self.browse(cr,uid,ids):
            xxx=reim.name
            search_obj=holiday_obj.search(cr,uid,[('employee_id','=',xxx)])
            holi=holiday_obj.browse(cr,uid,search_obj,context=context)
            for hol in holi :   
                xyz=hol.number_of_days
                xxx=hol.temp
                stt = hol.state
                if stt == 'validate':
                    yyy  += xyz   
                    zz += xxx                
            result[reim.id] =zz
        return result   
    
    _columns = {
        'alokasi' : fields.function(_aloc)
    }
    
hr_employee()
