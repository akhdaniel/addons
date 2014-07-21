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
        '''def was_on_tugas(employee_id, datetime_day, context=None):
            ress = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','luar'),('date_from','<=',day),('date_to','>=',day)])
            if holiday_ids:
                ress = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].tugas_luar
            return ress    
        ress = []
        '''
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
            luar ={}
            leaves = {}
            leave={}
            #import pdb;pdb.set_trace()
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
                    if leave_type == "Cuti Tahunan" :
                        ###### cuti	
                        #if he was on leave, fill the leaves dict
                        
                        if leave_type in leaves:
                            if employee.cuti_tahunan >= 0 :
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
                                    leaves[leave_type]['number_of_hours'] = working_hours_on_day * alok_cuti
                                else :
                                    if totals <= alok_cuti :
                                        fff= alok_cuti - totals
                                        leaves[leave_type]['number_of_days'] = fff 
                                        leaves[leave_type]['number_of_hours'] = working_hours_on_day * fff
                                    else : 
                                        leaves[leave_type]['number_of_days'] = 0.0 
                                        leaves[leave_type]['number_of_hours'] = 0.0
                        else:
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
                            }
                    if leave_type != "Cuti Tahunan" and leave_type :
                        if leave_type in leave:
                            leave[leave_type]['number_of_days'] += 1.0
                            leave[leave_type]['number_of_hours'] += working_hours_on_day
                        else :
                            leave[leave_type] = {
                                    'name': leave_type,
                                    'sequence': 5,
                                    'code': leave_type,
                                    'number_of_days': 1.0,
                                    'number_of_hours': working_hours_on_day,
                                    'contract_id': contract.id,
                                    }
                    '''tugas_luar = was_on_tugas(contract.employee_id.id, day_from + timedelta(days=day), context=context)                
                    if tugas_luar :
                        if tugas_luar in luar:
                            luar[tugas_luar]['number_of_days'] += 1.0
                            luar[tugas_luar]['number_of_hours'] += working_hours_on_day
                        else :
                            luar[tugas_luar] = {
                                    'name': tugas_luar,
                                    'sequence': 5,
                                    'code': tugas_luar,
                                    'number_of_days': 1.0,
                                    'number_of_hours': working_hours_on_day,
                                    'contract_id': contract.id,
                                    }
                    '''
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
                    #leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    isNonWorkingDay = date.isoweekday()==6 or date.isoweekday()==7
                    if isNonWorkingDay == False :
                        if leave_type == False or leave_type == "Cuti Tahunan":                       
                            attendances['number_of_days'] += 1.0
                            attendances['number_of_hours'] += working_hours_on_day
                        ### tidak cuti, cek apakah dia masuk absen?
                    if real_working_hours_on_day >= 0.000000000000000001 and not isNonWorkingDay and leave_type == False :
                        presences['number_of_days'] += 1.0
                        presences['number_of_hours'] += working_hours_on_day
            leaves = [value for key,value in leaves.items()]
            leave = [value for key,value in leave.items()]
            luar = [value for key,value in luar.items()]
            if leaves == [] :
                attendances['number_of_days'] = attendances['number_of_days'] - 0
            else :    
                attendances['number_of_days'] = attendances['number_of_days'] - leaves[0]['number_of_days']
            res += [attendances] + leaves + leave + luar + [presences] 
        coos = self.line2(cr, uid, contract_ids,date_to,date_from,context=None) 
        return res + coos 
        
    def line2(self, cr, uid, contract_ids,date_to,date_from, context=None):
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
        #if date.isoweekday() == 5 :   
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
            
            overtime_proyek_biasa = {
                'name' : _("Overtime Proyek hari Biasa"),
                'sequence': 2,
                'code': 'OVERTIME_PROYEK_BIASA',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id':contract.id,
            }

            overtime_proyek_libur = {
                'name' : _("Overtime Proyek Hari Libur"),
                'sequence': 2,
                'code': 'OVERTIME_PROYEK_LIBUR',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id':contract.id,
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
            
            uang_makan_proyek = {
                 'name': _("Uang Makan Proyek"),
                 'sequence': 2,
                 'code': 'UANG_MAKAN_PROY',
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

            uang_makan_lembur_proyek = {
                 'name': _("Uang Makan Lembur"),
                 'sequence': 2,
                 'code': 'UANG_MAKAN_LEMBUR_PROY',
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
            xxx=date_to
            ccc=date_from
            year_from=str(datetime.strptime(ccc,"%Y-%m-%d").year)
            month_f=datetime.strptime(ccc,"%Y-%m-%d").month
            month_from=str(month_f-1)
            day_from = str(16)
            if month_f != 1 :
                dates_from=year_from+"-"+month_from+"-"+day_from
            else :
                year=datetime.strptime(ccc,"%Y-%m-%d").year
                year_from = str(year -1)
                dates_from = year_from+"-"+"12"+"-"+day_from
            day_from = datetime.strptime(dates_from,"%Y-%m-%d")
            year_to=str(datetime.strptime(xxx,"%Y-%m-%d").year)
            month_to=str(datetime.strptime(xxx,"%Y-%m-%d").month)
            day_to = str(15)
            dates_to=year_to+"-"+month_to+"-"+day_to
            day_to = datetime.strptime(dates_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1  
            jumlah_biasa = 0 
            jumlah_libur = 0
            tot_semua = 0    
            incentives = 0
            for day in range(0, nb_of_days):
            	# cek dari jadwal kerja, berapa jam sehari employee bekerja            	
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                #working_hours_on_day = 8.00
                date = (day_from + timedelta(days=day))
                if working_hours_on_day >= 0:
                    #the employee had to work
                    employee_id = contract.employee_id.id
                    #employee info
                    emp_obj = self.pool.get('hr.employee')
                    employee = emp_obj.browse(cr, uid, employee_id, context=context)
                    real_working_hours_on_day = self.pool.get('hr.attendance').real_working_hours_on_day(cr,uid, contract.employee_id.id, day_from + timedelta(days=day),context)
                    tanggal = day_from + timedelta(days=day)
                    proyek_many = contract.proyek
                    if proyek_many == [] :
                        if real_working_hours_on_day >= 4 :    
                            uang_makan_proyek['number_of_days'] += 1.0
                        if real_working_hours_on_day >= 0.000000000000001 : 
                            transport['number_of_days'] += 1.0
                    else :
                        for kon in proyek_many :
                            tgl_sampai = kon.sampai
                            tgl_mulai = kon.mulai
                            tgl_mulai = datetime.strptime(tgl_mulai,"%Y-%m-%d") 
                            tgl_asli = datetime.strptime(tgl_sampai,"%Y-%m-%d")
                            if tanggal <= tgl_asli and tanggal >= tgl_mulai:
                                if real_working_hours_on_day >= 4 :    
                                    uang_makan_proyek['number_of_days'] += 1.0
                                if real_working_hours_on_day >= 14 :
                                    #import pdb;pdb.set_trace() 
                                    #yr = day_from + timedelta(days=day)
                                    #obj_att = self.pool.get('hr.attendance')
                                    #src_att = obj_att.search(cr,uid,[('employee_id','=',employee_id)])
                                    #for xxx in obj_att.browse(cr,uid,src_att) :
                                    uang_makan_lembur_proyek['number_of_days'] += 1.0  
                            elif real_working_hours_on_day >= 0.1 :
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
                   # import pdb;pdb.set_trace()
                    if real_working_hours_on_day > 0:
                        if contract.jenis_lembur == 'overtime' or no_urut < 100 :
                            datas = day_from + timedelta(days=day)
                            yr = datas.year
                            bln = datas.month
                            hr = datas.day
                            tanggal = str(yr) + "-" + str(bln) + "-" + str(hr)
                            obj_over = self.pool.get('hr.overtime')
                            src_over = obj_over.search(cr,uid,[('employee_id','=',employee_id),('tanggal','=',tanggal),('state','=','validate')])
                            for overt in obj_over.browse(cr,uid,src_over) :
                                if overt.overtime_type_id.name == 'Lembur' :
                                    jumlah = overt.total_jam1
                                    jumlah_ril = overt.jam_lembur
                                    overtimes['number_of_hours'] += jumlah
                                    if jumlah_ril >= 4 :
                                        uang_makan_lembur['number_of_days'] += 1
                                elif overt.overtime_type_id.name == 'Lembur Proyek' :
                                    #import pdb;pdb.set_trace()
                                    if date.isoweekday() != 7 and leave_type == False :
                                        jumlah_biasa += overt.jam_lembur
                                    else :   
                                        jumlah_libur += overt.jam_lembur
                                    tot_semua = jumlah_biasa + jumlah_libur
                        elif contract.jenis_lembur == 'incentive' or no_urut >= 200 : 
                            if isNonWorkingDay and real_working_hours_on_day > 4 and no_urut <= 399 :
                                incentives += 1
                                if incentives <= 2 and lave_type != 'Cuti Masal' : #and leave_type !=:
                                    incentives['number_of_days'] += 1.0
                                    incentive =  real_working_hours_on_day - working_hours_on_day
                                    if incentive >= 4 :
                                        incentives_meal['number_of_days'] += 1.0
                                elif leave_type == 'Cuti Masal' :
                                    incentives['number_of_days'] += 1.0
                                    incentive =  real_working_hours_on_day - working_hours_on_day
                                    if incentive >= 4 :
                                        incentives_meal['number_of_days'] += 1.0

                                #elif leave_type ==
                        """ title = kolom sortir
                        else if employee.title_id > 100 : #operator ke atas:
                            employee.gol_id.urutan > 1 and  employee.gol_id.urutan < 3 :
                              xml rule =  incentive: contract.wage/12 * worked_days.INCENTIVE.number_of_days
                                 if isNonWorkingDay && real_working_hours_on_day > 4:
                                    incentives['number_of_days'] += 1.0
                                 

                                else :employee.gol_id.urutan > 4:
                                    nol
                            """  
                date = (day_from + timedelta(days=day))
                if date.isoweekday() == 7 and jumlah_biasa < 25 and tot_semua <= 25:
                    #import pdb;pdb.set_trace()
                    overtime_proyek_biasa['number_of_hours'] += jumlah_biasa
                    overtime_proyek_libur['number_of_hours'] += jumlah_libur
                    jumlah_biasa = 0
                    jumlah_libur = 0
                elif date.isoweekday() == 7 and jumlah_biasa > 25 :
                    #import pdb;pdb.set_trace()
                    overtime_proyek_biasa['number_of_hours'] += 25
                    overtime_proyek_libur['number_of_hours'] += 0
                    jumlah_biasa = 0
                    jumlah_libur = 0
                elif date.isoweekday() == 7 and jumlah_biasa < 25 and tot_semua > 25 :
                    #import pdb;pdb.set_trace()
                    overtime_proyek_biasa['number_of_hours'] += jumlah_biasa
                    overtime_proyek_libur['number_of_hours'] += 25 - jumlah_biasa
                    jumlah_biasa = 0
                    jumlah_libur = 0
            res += [overtimes] + [incentives] + [transport] + [uang_makan] + [uang_makan_lembur] + [incentives_meal] + [uang_makan_proyek] + [uang_makan_lembur_proyek] + [overtime_proyek_biasa] + [overtime_proyek_libur]       
        return res
        
    def compute_sheet(self, cr, uid, ids, context=None):         
        slip_line_pool = self.pool.get('hr.payslip.line')
        sequence_obj = self.pool.get('ir.sequence')
        contract_obj = self.pool.get("hr.contract")
        #contract_src = contract_obj.search()
        tunj_proyek = self.tunjangan(cr,uid,ids,context=None)
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
            # overwrite field in payslip for tunjangan pajak and pajak
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
                if cod == "BASIC" :      
                    coo =line['amount']  
                    self.write(cr, uid, [payslip.id], {'basic':coo}, context=context)
                if cod == "OVERTIME" :
                    coo =line['amount']
                    self.write(cr,uid, [payslip.id], {'overtime': coo}, context=context)
                if cod == "INCENTIVES" :
                    coo =line['amount']
                    self.write(cr,uid, [payslip.id], {'incentive': coo}, context=context)
                if cod == "BONUS" :
                    coo =line['amount']
                    self.write(cr,uid, [payslip.id], {'bonus': coo}, context=context)
                if cod == "THR" :
                    coo =line['amount']
                    self.write(cr,uid, [payslip.id], {'thr': coo}, context=context)   
                if cod == "RAPEL" :
                    coo = line['amount']
                    self.write(cr,uid, [payslip.id], {'rapel' : coo}, context=context)
                if cod == "RO" :
                    coo = line['amount']
                    self.write(cr,uid, [payslip.id], {'rapel_over' : coo}, context=context)
                if cod =="TPAJ" :   
                    tunj=line['amount']
                    if tunj == 0 :
                        for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                            cod= line['code']
                            if cod == "GROSS" :
                                tj =line['amount']
                                self.write(cr, uid, [payslip.id], {'gros_sebelum':tj}, context=context)   
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                cod= line['code']   
                if cod == 'OVERTIME' :
                    coo =line['amount']
                    self.write(cr,uid, [payslip.id], {'overtime': coo}, context=context)                      
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                cod= line['code']   
                if cod == "GROSS":
                    coo = line['amount']
                    self.write(cr, uid, [payslip.id], {'gros':coo}, context=context)     
                    coos = self.funct(cr,uid,ids,context=None)    
                    self.write(cr, uid, [payslip.id], {'total':coos}, context=context)
                    coos = self.tunj_pajak(cr,uid,ids,context=None)    
                    self.write(cr, uid, [payslip.id], {'tunj_pajak':coos}, context=context)        
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                cod= line['code']   
                if cod == "GROSS":
                    coo = line['amount']
                    self.write(cr, uid, [payslip.id], {'gros':coo}, context=context)     
                if cod == "NET":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'net':coo}, context=context)   
            coos = self.funct(cr,uid,ids,context=None)    
            self.write(cr, uid, [payslip.id], {'total':coos}, context=context)
            coos = self.pkp(cr,uid,ids,context=None)  
            #coos = self.check_tunj_pajak(cr,uid,ids,context=None) 
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                cod= line['code']   
                if cod == "GROSS":
                    self.write(cr, uid, [payslip.id], {'gros':coo}, context=context)     
                if cod == "NET":
                    coo =line['amount']      
                    self.write(cr, uid, [payslip.id], {'net':coo}, context=context)                         
            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number})
            ccc =self.libur(cr,uid,ids,context=None)
            self.write(cr,uid,ids,{'libur':ccc},context=context)
        return True     
        
    def tunjangan(self,cr,uid,ids,context=None):
        pay = self.browse(cr,uid,ids)[0]
        worked = pay.worked_days_line_ids
        for work in worked :
            cod = work.code
            if cod == 'UANG_MAKAN_PROY' :
                jum = work.number_of_days  
            if cod == 'OVERTIME_PROYEK_BIASA' :
                jum_over = work.number_of_hours
            if cod == 'OVERTIME_PROYEK_LIBUR' :
                jum_libur = work.number_of_hours
        kontrak = pay.contract_id.id
        date_from = pay.date_from
        date_to = pay.date_to
        day_from = datetime.strptime(date_from,"%Y-%m-%d")
        day_to = datetime.strptime(date_to,"%Y-%m-%d")
        obj = self.pool.get('hr.contract')
        obj_src = obj.search(cr,uid,[('id','=', kontrak)])
        for kont in obj.browse(cr,uid,obj_src):
            tunjangan = kont.proyek
            for kontrak in tunjangan :
                tgl_sampai = kontrak.sampai
                tgl_mulai = kontrak.mulai
                tgl_mulai = datetime.strptime(tgl_mulai,"%Y-%m-%d") 
                tgl_asli = datetime.strptime(tgl_sampai,"%Y-%m-%d")
                if day_from <= tgl_asli and day_from >= tgl_mulai:
                    tunjangan = kontrak.tunjangan_proyek
                    umak = kontrak.tunjangan_lain.umak
                    over_biasa = kontrak.tunjangan_lain.lembur1
                    over_libur = kontrak.tunjangan_lain.lembur2
        jum_umak = umak * jum
        total_over = (jum_over * over_biasa) + (jum_libur * over_libur)
        return self.write(cr,uid,ids,{'tunj_proyek':tunjangan,'uang_makan_proyek': jum_umak,'lembur_proyek':total_over})

    def funct(self,cr,uid,ids,context=None) :
        xxx=self.browse(cr,uid,ids)[0]
        xyz=xxx.employee_id.name
        ccc=xxx.date_to
        pot_jab = (xxx.gros * xxx.contract_id.type_id.biaya_jabatan)/100 
        tht = (xxx.basic * xxx.contract_id.type_id.tht)/100 
        ptkp = xxx.employee_id.ptkp_id.nominal_bulan
        kena_pajak = xxx.gros - pot_jab - tht - ptkp
        if kena_pajak >= 0 :
            self.write(cr,uid,ids,{'kena_pajak' : kena_pajak}, context=context)
        yyy=datetime.strptime(ccc,"%Y-%m-%d").year
        yy=datetime.strptime(ccc,"%Y-%m-%d").month
        zzz=datetime.strptime(ccc,"%Y-%m-%d")
        self_obj=self.pool.get('hr.payslip')
        src_obj=self_obj.search(cr,uid,[('employee_id','=',xyz)])
        obj=self_obj.browse(cr,uid,src_obj)
        totals = 0.0
        total = 0.0
        for xyc in obj :
            ttt=xyc.date_to
            ttx=datetime.strptime(ttt,"%Y-%m-%d").year
            ttz=datetime.strptime(ttt,"%Y-%m-%d")
            tt=datetime.strptime(ttt,"%Y-%m-%d").month
            if yyy == ttx :
                if yy > tt :             
                    total += xyc.kena_pajak
            if yyy == ttx :
                if yy >= tt :         
                    totals += xyc.kena_pajak
        self.write(cr,uid,ids,{'totals' : total}, context=context)
        return totals

    def tunj_pajak(self,cr,uid,ids,context=None) :
        obj =self.browse(cr,uid,ids)[0]
        employee = obj.employee_id.id
        basic = obj.basic
        inc = obj.incentive
        ovr = obj.overtime
        rap = obj.rapel
        rap_ovr = obj.rapel_over
        thr = obj.thr
        bonus = obj.bonus
        year =datetime.now().year
        date = obj.date_from
        bulan = datetime.strptime(date,"%Y-%m-%d").month
        bln = bulan - 1
        gros = obj.gros_sebelum 
        grs =obj.gros
        #hitung pajak tanpa alw
        obj_psl = self.pool.get('hr.payslip')
        obj_src = obj_psl.search(cr,uid,[('employee_id','=',employee)])
        obj_brw = obj_psl.browse(cr,uid,obj_src)
        pjk_tnp_alw = (basic * 13) + inc + ovr + rap + rap_ovr + thr + bonus
        gross = inc + ovr + rap + rap_ovr + thr + bonus
        for xxx in obj_brw :
            dates= xxx.date_from
            data = datetime.strptime(dates,"%Y-%m-%d").year
            mon = datetime.strptime(dates,"%Y-%m-%d").month
            if data == year :
                if bln == mon :
                    pjk_tnp_alw = xxx.tampung1 + gross
        self.write(cr,uid,ids,{'tampung1': pjk_tnp_alw},context=context)
        pot_jab = (pjk_tnp_alw * obj.contract_id.type_id.biaya_jabatan)/100   
        tht = ((basic * 13) * (obj.contract_id.type_id.tht +  obj.contract_id.type_id.ttht))/100       
        ptkp = obj.employee_id.ptkp_id.nominal_tahun
        pkp = pjk_tnp_alw - (pot_jab + ptkp +tht )
        hpkp = pkp
        self_obj=self.pool.get('hr.pkp')
        src_obj=self_obj.search(cr,uid,[])
        objk = self_obj.browse(cr,uid,src_obj)
        tj_pjk = 0
        if pkp <= 0 :
            tj_pjk = 0
        elif pkp > 0 :
            for hitung in objk :
                minimal = hitung.nominal_min
                mak = hitung.nominal_max
                pajak = hitung.pajak   
                if hpkp <= mak :
                    tj_pjk = (( pkp * pajak )/100) + tj_pjk
                    pkp = 0
                elif hpkp >= mak :
                    tj_pjk = ( mak * pajak )/100 + tj_pjk
                    pkp = pkp - mak
        self.write(cr,uid,ids,{'tj_pjk':tj_pjk},context=context)
        #hitung pajak dengan alw
        pajak_alw = (grs - basic - obj.tunj_pajak) + (basic * 13)
        alw = grs - basic - obj.tunj_pajak
        for xxx in obj_brw :
            dates = xxx.date_from
            waktu = datetime.strptime(dates,"%Y-%m-%d").year
            mont = datetime.strptime(dates,"%Y-%m-%d").month
            if waktu == year :
                if mont == bln :
                    pajak_alw = xxx.tampung2 + alw
        self.write(cr,uid,ids,{'tampung2':pajak_alw},context=context)
        pot_jab = (pajak_alw * obj.contract_id.type_id.biaya_jabatan)/100 
        tht = ((basic * 13) * (obj.contract_id.type_id.tht +  obj.contract_id.type_id.ttht))/100    
        ptkp = obj.employee_id.ptkp_id.nominal_tahun
        pkp = pajak_alw - (pot_jab + ptkp + tht )
        hpkp = pkp
        self_obj=self.pool.get('hr.pkp')
        src_obj=self_obj.search(cr,uid,[])
        objk = self_obj.browse(cr,uid,src_obj)
        tj_pjk_alw = 0
        if pkp <= 0 :
            tj_pjk_alw = 0
        elif pkp > 0 :
            for hitung in objk :
                minimal = hitung.nominal_min
                mak = hitung.nominal_max
                pajak = hitung.pajak   
                if hpkp <= mak :
                    tj_pjk_alw = (( pkp * pajak )/100) + tj_pjk_alw                 
                    if pkp != 0 :
                        pembagi = pajak
                    pkp = 0
                elif hpkp >= mak :
                    tj_pjk_alw = ( mak * pajak )/100 + tj_pjk_alw
                    pkp = pkp - mak
        #hitung tunjangan pajak
        tunjangan_pajak = ((tj_pjk_alw - tj_pjk) * 100) / (100 - pembagi) 
        tunjangan_pajak = tunjangan_pajak / 13
        return tunjangan_pajak

    def pkp(self,cr,uid,ids,context=None) :
        #import pdb;pdb.set_trace()
        obj=self.browse(cr,uid,ids)[0]
        gros = obj.gros - obj.basic
        basic = obj.basic * 13
        year =datetime.now().year
        date = obj.date_from
        bulan = datetime.strptime(date,"%Y-%m-%d").month
        bln = bulan - 1
        pjk = basic + gros
        employee = obj.employee_id.id
        obj_psl = self.pool.get('hr.payslip')
        obj_src = obj_psl.search(cr,uid,[('employee_id','=',employee)])
        obj_brw = obj_psl.browse(cr,uid,obj_src)
        for xxx in obj_brw :
            dates= xxx.date_from
            data = datetime.strptime(dates,"%Y-%m-%d").year
            mon = datetime.strptime(dates,"%Y-%m-%d").month
            if data == year :
                if bln == mon :
                   pjk = xxx.tampung_pajak + gros
        self.write(cr,uid,ids,{'tampung_pajak':pjk},context=context)
        pjkp = pjk
        pot_jab = (pjk * obj.contract_id.type_id.biaya_jabatan)/100 
        tht = (basic * (obj.contract_id.type_id.tht +  obj.contract_id.type_id.ttht))/100    
        ptkp = obj.employee_id.ptkp_id.nominal_tahun  
        pajak = 0
        pkp = pjk - (pot_jab + tht + ptkp)
        self_obj=self.pool.get('hr.pkp')
        src_obj=self_obj.search(cr,uid,[])
        objk = self_obj.browse(cr,uid,src_obj)
        if pkp <= 0 :
            pajak = 0
        elif pkp > 0 :
            #import pdb;pdb.set_trace()
            for hitung in objk :
                minimal = hitung.nominal_min
                mak = hitung.nominal_max
                persen = hitung.pajak   
                if pkp <= mak :
                    pajak = (( pkp * persen )/100) + pajak
                    pkp = 0
                    pajak = pajak / 13
                    return self.write(cr, uid,ids, {'pkp':pajak}, context=context)
                elif pkp >= mak :
                    pajak = ( mak * persen )/100 + pajak
                    pkp = pkp - mak
        return True

    def check_tunj_pajak (self,cr,uid,ids,context=None) :
        #untuk cek tunjangan pajak dan fungsi nilai up
        obj = self.browse(cr,uid,ids)[0]
        pajak = obj.pkp
        tunj_pajak = obj.tunj_pajak
        pjk_no_alw = obj.tampung1
        cek = pajak - tunj_pajak
        while cek < pjk_no_alw :
            tpj = tunj_pajak
            tunj_pajak = obj.tunj_pajak * 1.5
            self.write(cr,uid,ids,{'tunj_pajak': tunj_pajak},context=context)
            coo = self.pkp(cr,uid,ids,context=None) 
            cek2 = obj.pkp - obj.tunj_pajak
            if cek2 > pjk_no_alw :
                self.write(cr,uid,ids,{'tunj_pajak': tunj_pajak},context=context)
                coo = self.pkp(cr,uid,ids,context=None) 
            cek = obj.pkp - obj.tunj_pajak
        return True
        
    def libur (self,cr,uid,ids,context=None):
        xxx=self.browse(cr,uid,ids)[0]
        aaa=xxx.name
        date_from_16 =str(datetime.now() + relativedelta.relativedelta(months=+0, day=1))[:10]
        day_from = datetime.strptime(date_from_16,"%Y-%m-%d").year
        cuti = "Cuti Tahunan"
        obj=self.pool.get('hr.payslip.worked_days')
        src=obj.search(cr,uid,[('payslip_id','=',aaa)])
        pay_obj=obj.browse(cr,uid,src,context=context)
        ccc= 0.0
        for xyz in pay_obj :
            if xyz.code == cuti :
                ccc = xyz.number_of_days
        return ccc
         

    _columns = {
        'net' : fields.float("Net"),
        'komisi': fields.float("komisi"),
        'reimburse_obat':fields.float('Total Reimburse Obat'),
        'reimburse_rawat':fields.float('Total Reimburse Rawat'),
        'pot_absen':fields.float('Potongan Absen'),
        'gros':fields.float('gros'),
        'gros_sebelum' :fields.float('gros sebelum kena pajak'),
        'total':fields.float('total kena pajak'), 
        'pkp' :fields.float('pkp'),
        'pot_koperasi':fields.float('potongan koperasi'),
        'pot_telepon' :fields.float('potongan telepon'),
        'pot_spsi' : fields.float('potongan spsi'),
        'umak' : fields.float('uang makan'),
        'ut' : fields.float('uang transport'),
        'uml' : fields.float('uang makan lembur'),
        'libur' : fields.float('libur'),
        'totals' :fields.float('kena pajak sebelum'),
        'kena_pajak' :fields.float('kena Pajak'),
        'tunj_pajak' :fields.float('tunjangan pajak'),
        #basic alw
        'basic' : fields.float('basic'),
        'overtime' : fields.float('overtime'),
        'incentive' : fields.float('incentive'),
        'bonus' :fields.float('Bonus'),
        'rapel' : fields.float('rapel'),
        'rapel_over' : fields.float('rapel overtime'),
        'thr' : fields.float('THR'),
        'tampung1' : fields.float('tampung1'),
        'tampung2' :fields.float('tampung2'),
        'tampung_pajak' :fields.float('tampung_pajak'),
        'tj_pjk' :fields.float('Tunjangan Pajak Tanda alw'),
        'tunj_proyek' : fields.integer('tunjangan proyek'),
        'uang_makan_proyek' : fields.integer('uang makan proyek'),
        'lembur_proyek' : fields.integer('Lembur Proyek'),
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
        date_from_16 =str(datetime.now() + relativedelta.relativedelta(months=+0, day=1))[:10]
        days = datetime.strptime(date_from_16,"%Y-%m-%d").month
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        for record in self.browse(cr, uid, ids):
            if record.holiday_type == 'employee' and record.type == 'remove':
                if record.employee_id and not record.holiday_status_id.limit:
                    leaves_rest = holi_status_obj.get_days( cr, uid, [record.holiday_status_id.id], record.employee_id.id, False)[record.holiday_status_id.id]['remaining_leaves']
                    day_too= record.date_to
                    day_took = datetime.strptime(day_too, DATETIME_FORMAT ).month
                    if days != day_took :
                        x=5
                        #raise osv.except_osv(_('Warning!'),_('Pengajuan Cuti Harus Pada Bulan Yang Sama.')) 
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
    
    def _aaa(self, cr, uid, ids, name, args, context=None):
        result = {}
        date_from_16 =str(datetime.now() + relativedelta.relativedelta(months=+0, day=1))[:10]
        dates = datetime.strptime(date_from_16,"%Y-%m-%d").year
        date = str(dates)
        for hol in self.browse(cr, uid, ids, context=context):
            if hol.type!='remove' and hol.tahun == date :
                result[hol.id] = 0.0
            else:
                result[hol.id] = -hol.number_of_days_temp
        return result
        
    _columns = {
        'temp' : fields.function(_aac, "blabla"),
        'tempp' :fields.function(_aaa),
        'tahun': fields.char('Tahun',readonly=True),
        'tugas_luar':fields.selection([('luar','luar')],'allokasi'),
        'holiday_status_id': fields.many2one("hr.holidays.status", "Leave Type", required=False,readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'type': fields.selection([('remove','Leave Request'),('add','Allocation Request'),('luar','Luar Kota')], 'Request Type', required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, help="Choose 'Leave Request' if someone wants to take an off-day. \nChoose 'Allocation Request' if you want to increase the number of leaves available for someone", select=True),
        'ket' : fields.boolean('Tugas Luar Kota'),
     }
      
    _defaults = { 
        'tahun' : lambda *a : time.strftime('%Y'),   
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
                ccc=hol.holiday_status_id.name
                stt = hol.state
                if stt == 'validate' and ccc == 'Cuti Tahunan':
                    yyy  += xyz   
                    zz += xxx                
            result[reim.id] =zz
        return result   
    
    def _cuti(self, cr, uid, ids, name, args, context=None):
        holiday_obj = self.pool.get("hr.holidays")
        yyy=0.0
        result={}
        zz=0.0
        for reim in self.browse(cr,uid,ids):
            xxx=reim.name
            search_obj=holiday_obj.search(cr,uid,[('employee_id','=',xxx)])
            holi=holiday_obj.browse(cr,uid,search_obj,context=context)
            for hol in holi :   
                xyz=hol.tempp
                xxx=hol.temp
                ccc=hol.holiday_status_id.name
                stt = hol.state
                if stt == 'validate' and ccc == 'Cuti Tahunan':
                    yyy  += xyz   
                    zz += xxx               
            result[reim.id] =zz + yyy
        return result      
         
    def lembur(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'status_lembur':'lembur'},context=context)
        return True

    def tidak_lembur(self,cr,uid,ids,status_lembur,context=None):
        self.write(cr,uid,ids,{'status_lembur':'tidak_lembur'},context=context)
        return True   

    _columns = {
        'alokasi' : fields.function(_aloc,string='Alokasi Cuti Tahunan'),
        'cuti_tahunan': fields.function(_cuti, string='Jatah Cuti Tahunan'),
        'status_lembur' : fields.selection([('lembur','Lembur'),('tidak_lembur','Tidak Lembur')],'Status Lembur'),
    }

    _defaults = {
        'status_lembur' : 'tidak_lembur'
    }
    
hr_employee()
