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
import  logging
_logger = logging.getLogger(__name__)

class hr_payslip(osv.osv):
    '''
    PPI Pay Slip
    '''

    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    _description = 'Pay Slip Inheriteed Lucas Marin'

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
        empolyee_obj    = self.pool.get('hr.employee')
        contract_obj    = self.pool.get('hr.contract')
        worked_days_obj = self.pool.get('hr.payslip.worked_days')
        input_obj       = self.pool.get('hr.payslip.input')

        if context is None:
            context = {}

        ######################################################################
        #delete old worked days lines
        ######################################################################
        old_worked_days_ids = ids and worked_days_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_worked_days_ids:
            worked_days_obj.unlink(cr, uid, old_worked_days_ids, context=context)

        ######################################################################
        #delete old input lines
        ######################################################################
        old_input_ids = ids and input_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_input_ids:
            input_obj.unlink(cr, uid, old_input_ids, context=context)

        ######################################################################
        #defaults
        ######################################################################
        res = {'value':{
                      'line_ids':[],
                      'input_line_ids': [],
                      'worked_days_line_ids': [],
                      #'details_by_salary_head':[], TODO put me back
                      'name':'',
                      'contract_id': False,
                      'struct_id': False,
                      'lokasi_kerja':'',
                      }
            }
        if (not employee_id) or (not date_from) or (not date_to):
            return res

        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
        res['value'].update({
                    'name': _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
                    'company_id': employee_id.company_id.id
        })

        if not context.get('contract', False):
            ######################################################################
            #fill with the first contract of the employee
            ######################################################################
            contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)
        else:
            if contract_id:
                ######################################################################
                #set the list of contract for which the input have to be filled
                ######################################################################
                contract_ids = [contract_id]
            else:
                ######################################################################
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                ######################################################################
                contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)

        if not contract_ids:
            return res


        contract_record = contract_obj.browse(cr, uid, contract_ids[0], context=context)
        res['value'].update({
                    'contract_id': contract_record and contract_record.id or False,
                    'lokasi_kerja': contract_record.employee_id.address_id2.name,
                    'status_karyawan': contract_record.employee_id.status_karyawan.name
        })
        struct_record = contract_record and contract_record.struct_id or False

        if not struct_record:
            return res

        res['value'].update({
                'struct_id': struct_record.id,
        })

        ######################################################################
        #computation of the salary input
        # moved to reload input
        ######################################################################
        # worked_days_line_ids = self.get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context=context)
        # input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
        # res['value'].update({
        #             'worked_days_line_ids': worked_days_line_ids,
        #             'input_line_ids': input_line_ids,
        # })
        return res

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
        din = 0 # index record hr_attendance
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):

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
            Bonus_Shift_3 = {
                 'name': _("Bonus Shift 3"),
                 'sequence': 3,
                 'code': 'BONUSSHIFT3',
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
            potongan_tunjangan = {
                 'name': _("Potongan Tunjangan"),
                 'sequence': 2,
                 'code': 'POT_TUNJANGAN',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            denda_keterlambatan = {
                 'name': _("Denda Keterlambatan"),
                 'sequence': 5,
                 'code': 'DENDA_KETERLAMBATAN',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            denda_ketidakhadiran = {
                 'name': _("Denda Ketidakhadiran"),
                 'sequence': 6,
                 'code': 'DENDA_KETIDAKHADIRAN',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            luar ={}
            leaves = {}
            leave={}
            employee_id = contract.employee_id.id

            #################################################################################
            # jumlah hari dalam range period payslip
            # start from dimunduri utk handle shift malam
            #################################################################################
            day_from = datetime.strptime(date_from,"%Y-%m-%d") -timedelta(hours=12)
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1

            #################################################################################
            # search attendance
            # x = jumlah records attendance
            #################################################################################
            x= -1
            attid = self.pool.get('hr.attendance').search(cr, uid, [
                ('employee_id', '=', contract.employee_id.id),
                ('name_date', '>=', date_from),
                ('name_date', '<=',  date_to)], order="name asc")
            x = len(attid)-1

            #################################################################################
            # loop dari hari ke-0 sd jumlah hari period payslip
            #################################################################################
            for day in range(0, nb_of_days):

                #################################################################################
                # cek dari jadwal kerja, berapa jam sehari employee bekerja
                #################################################################################
                working_hours_on_day    = False
                date                    = day_from + timedelta(days=day)
                _logger.warning(date)
                datess                  = str(date)[:10]
              
                #################################################################################
                # mencari worked hours utk tanggal date
                # dari shift atau dari calendar kerja, tergantung dari
                # Working Schedule = field working_hours
                #################################################################################
                if not contract.working_hours: # cari dari shift
                    obj_shift = self.pool.get('hr.shift_karyawan')
                    src_shift = obj_shift.search(cr,uid,[
                        ('contract_id','=',contract.id),
                        ('date_from','<=',datess),
                        ('date_to','>=',datess)])
                    for shift in obj_shift.browse(cr,uid,src_shift):
                        working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(
                            cr, uid, shift.schedule_id, date, context)
                else: # cari dari Working Schedule
                    working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(
                        cr, uid, contract.working_hours, date, context)

                #################################################################################
                # ada jadwal untuk tanggal=date ?
                #################################################################################
                if working_hours_on_day != False :

                    #################################################################################
                    # apakah dia date ini ada ambil cuti ?
                    #################################################################################
                    emp_obj = self.pool.get('hr.employee')
                    employee = emp_obj.browse(cr, uid, employee_id, context=context)
                    leave_type = was_on_leave(contract.employee_id.id, date, context=context)

                    if leave_type == "Cuti Tahunan" :
                        #################################################################################
                        ###### cuti	: if he was on leave, fill the leaves dict
                        #################################################################################
                        
                        if leave_type in leaves:
                            if employee.cuti_tahunan >= 0 :
                                leaves[leave_type]['number_of_days'] += 1.0
                                leaves[leave_type]['number_of_hours'] += working_hours_on_day
                            else : 
                                xyz=employee.name
                                ccc=date_to
                                yyy=datetime.strptime(ccc,"%Y-%m-%d").year
                                zzz=datetime.strptime(ccc,"%Y-%m-%d")
                                pay_objk=self.pool.get('hr.payslip')
                                src_obj=pay_objk.search(cr,uid,[('employee_id','=',xyz)])
                                obj=pay_objk.browse(cr,uid,src_obj)
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
                                pay_objk=self.pool.get('hr.payslip')
                                src_obj=pay_objk.search(cr,uid,[('employee_id','=',xyz)])
                                obj=pay_objk.browse(cr,uid,src_obj)
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
                        #leaves0 += 1 


                    #################################################################################
                    # real_working_hours_on_day
                    #################################################################################
                    real_working_hours_on_day = 0
                    if x > din :
                        attout = self.pool.get('hr.attendance').browse(cr,uid,attid[din+1],context=context)
                        attin = self.pool.get('hr.attendance').browse(cr,uid,attid[din],context=context)
                        attout_date = attout.name #dapat GMT
                        attin_date = attin.name #data GMT
                        din = din+2

                        # jika ketemu record att login - login: maka
                        # dianggap tdk hadir, din mundurin 1 record
                        if attout.action == 'sign_in' :
                            din = din - 1
                            real_working_hours_on_day = 0
                        else:
                            real_working_hours_on_day = (datetime.strptime(attout_date,"%Y-%m-%d %H:%M:%S") -
                                datetime.strptime(attin_date, "%Y-%m-%d %H:%M:%S")).seconds / 3600

                    #################################################################################
                    # menghitung denda keterlambatan
                    #################################################################################
                    date_attendance = time.strftime('%Y-%m-%d', time.strptime(str(date), '%Y-%m-%d %H:%M:%S'))
                    attendance_obj  = self.pool.get('hr.attendance')
                    attendance_src  = attendance_obj.search(cr,uid,[
                        ('fingerprint_code','=',contract.employee_id.fingerprint_code),
                        ('day','=',date_attendance),
                        ('binary_action','=','1')])

                    for atendances in attendance_obj.browse(cr,uid,attendance_src) :
                        if atendances.keterlambatan != False :
                            _logger.warning("************ %s", float(atendances.keterlambatan) )
                            if float(atendances.keterlambatan) <= 0.15 and float(atendances.keterlambatan) > 0.0 : 
                                denda_keterlambatan['number_of_days'] += 1.0
                            elif float(atendances.keterlambatan) > 0.15 :
                                denda_ketidakhadiran['number_of_days'] += 1.0

                    #################################################################################
                    # menghitung tunjangan Shift 3
                    #################################################################################

                    if attendance_src != [] :
                        shift_obj   = self.pool.get('hr.shift_karyawan')
                        shift_src   = shift_obj.search(cr,uid,[
                            ('contract_id','=',contract.id),
                            ('date_from','<=',date_attendance),
                            ('date_to','>=',date_attendance),
                            ('urutan_shift','=','3')])
                        for shift in shift_obj.browse(cr,uid,shift_src) :
                            Bonus_Shift_3['number_of_days'] += 1.0

                    #################################################################################
                    # hitung working hours
                    #################################################################################
                    working_hours=int(real_working_hours_on_day)
                    working_minutes=real_working_hours_on_day - working_hours
                    work_minutes = working_minutes / 1.66666667
                    if working_minutes > 0.15 and working_minutes <= 0.45 :
                        real_working_hours_on_day= working_hours + (0.30 * 1.66666667)
                    elif working_minutes >= 0.45 :    
                        real_working_hours_on_day= working_hours + 1
                    elif working_minutes < 15 :
                        real_working_hours_on_day= working_hours  						
                    # date = (day_from + timedelta(days=day))

                    # isNonWorkingDay = date.isoweekday()==6 or date.isoweekday()==7

                    if working_hours_on_day > 0:
                        if not contract.working_hours:
                            if shift.schedule_id.shift_gt_hr == False :
                                if leave_type == False or leave_type == "Cuti Tahunan":                      
                                    attendances['number_of_days'] += 1.0
                                    attendances['number_of_hours'] += working_hours_on_day
                                    ### tidak cuti, cek apakah dia masuk absen?
                            elif shift.schedule_id.shift_gt_hr == True and date.isoweekday() < 6 :
                                if leave_type == False or leave_type == "Cuti Tahunan":                      
                                    attendances['number_of_days'] += 1.0
                                    attendances['number_of_hours'] += working_hours_on_day
                        else :
                                attendances['number_of_days'] += 1.0
                                attendances['number_of_hours'] += working_hours_on_day
                                ### tidak cuti, cek apakah dia masuk absen?
                    else:
                        _logger.warning("date=%s working_hours_on_day=%s"% (date, working_hours_on_day))

                    #################################################################################
                    # jika real_working_hours_on_day>0, hitung sebagai kehadiran
                    #################################################################################
                    if real_working_hours_on_day >= 0.000000000000000001 :
                        presences['number_of_days'] += 1.0
                        presences['number_of_hours'] += working_hours_on_day
                        _logger.warning("date=%s working_hours_on_day=%s"% (date, working_hours_on_day))

                else:
                    _logger.warning("date=%s working_hours_on_day=%s"% (date, working_hours_on_day))

                #################################################################################
                # menghitung lembur
                #################################################################################
                tanggal = date.strftime("%Y-%m-%d")
                obj_over = self.pool.get('hr.overtime')

                src_over = obj_over.search(cr,uid,[
                    ('employee_id','=',employee_id),
                    ('tanggal','=',tanggal),
                    ('state','=','validate')])
                for overt in obj_over.browse(cr,uid,src_over) :
                    if overt.overtime_type_id.name == 'Lembur' :
                        jumlah = overt.total_jam1
                        jumlah_ril = overt.jam_lembur
                        lembur['number_of_hours'] += jumlah

            leaves = [value for key,value in leaves.items()]
            leave = [value for key,value in leave.items()]
            luar = [value for key,value in luar.items()]


            if leaves == [] :
		_logger.info("leaves")
		_logger.info(leaves)
                attendances['number_of_days'] = attendances['number_of_days'] - 0
                #################################################################################
                # menhitung potongan tunjangan
                #################################################################################
                potongan_tunjangan['number_of_days'] = attendances['number_of_days'] - presences['number_of_days']

            else :
                attendances['number_of_days'] = attendances['number_of_days'] - leaves[0]['number_of_days']
                #################################################################################
                # menhitung potongan tunjangan
                #################################################################################
                potongan_tunjangan['number_of_days'] = attendances['number_of_days'] - presences['number_of_days']- leaves[0]['number_of_days']


            #################################################################################
            # denda ketidak hadiran
            #################################################################################
            denda_ketidakhadiran['number_of_days'] = potongan_tunjangan['number_of_days']
            res += [attendances] + leaves + leave + luar + [presences] + [Bonus_Shift_3] + [lembur] + [potongan_tunjangan] + [denda_keterlambatan] + [denda_ketidakhadiran]

        return res

    def reload_input(self, cr, uid, ids, context=None):
        payslip         = self.browse(cr,uid,ids)[0]
        contract_ids    = [payslip.contract_id.id]
        date_from       = payslip.date_from
        date_to         = payslip.date_to

        #clear dulu
        cr.execute('delete from hr_payslip_worked_days where payslip_id=%s' % (ids[0]))
        cr.execute('delete from hr_payslip_input where payslip_id=%s' % (ids[0]))

        worked_days_line_ids = self.get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context=context)
        input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)

        self.write(cr, uid, ids, {
                'worked_days_line_ids'  : [(0,0,data) for data in worked_days_line_ids],
                'input_line_ids'        : [(0,0,data) for data in input_line_ids]
            }, context=context)

        return True

    def compute_sheet(self, cr, uid, ids, context=None):   
        pay_objk 		= self.browse(cr,uid,ids)[0]
        slip_line_pool 	= self.pool.get('hr.payslip.line')
        sequence_obj 	= self.pool.get('ir.sequence')
        contract_obj 	= self.pool.get("hr.contract")
        worked 			= pay_objk.worked_days_line_ids

        ################################################################################
        ### Tunjangan Hari Raya
        ################################################################################
        for work in worked :
            cod = work.code
            if cod 	== 'UANG_MAKAN_PROY' :
                jum = work.number_of_days  
            if cod 	== 'OVERTIME_PROYEK_BIASA' :
                jum_over = work.number_of_hours
            if cod == 'OVERTIME_PROYEK_LIBUR' :
                jum_libur = work.number_of_hours
        date_from 		= pay_objk.date_from
        date_to 		= pay_objk.date_to
        day_from 		= datetime.strptime(date_from,"%Y-%m-%d")
        day_to 			= datetime.strptime(date_to,"%Y-%m-%d")

        contract_id 	= contract_obj.search(cr,uid,[('id','=', pay_objk.contract_id.id)])

        tunjangan 		= 0
        jum_umak 		= 0
        total_over 		= 0

        ################################################################################
        # uang makan proyek
        ################################################################################
        for kont in contract_obj.browse(cr,uid,contract_id):
            tunjangan = kont.proyek
            for kontrak in tunjangan :
                tgl_sampai 	= kontrak.sampai
                tgl_mulai 	= kontrak.mulai
                tgl_mulai 	= datetime.strptime(tgl_mulai,"%Y-%m-%d") 
                tgl_asli 	= datetime.strptime(tgl_sampai,"%Y-%m-%d")
                if day_from <= tgl_asli and day_from >= tgl_mulai:
                    tunjangan 	= kontrak.tunjangan_proyek
                    umak 		= kontrak.tunjangan_lain.umak
                    over_biasa 	= kontrak.tunjangan_lain.lembur1
                    over_libur 	= kontrak.tunjangan_lain.lembur2
                    jum_umak 	= umak * jum
                    total_over 	= (jum_over * over_biasa) + (jum_libur * over_libur)
                    self.write(cr,uid,[pay_objk.id],{'uang_makan_proyek': jum_umak,'lembur_proyek':total_over})

        for payslip in self.browse(cr, uid, ids, context=context):
            ################################################################################
            #menghitung hutang koperasi dan hutang perusahaan
            ################################################################################
            if payslip.employee_id.sisa_tunggakan > 0 :
                pembayaran      = payslip.employee_id.hutang_koperasi / float(payslip.employee_id.pembayaran)
                self.write(cr,uid,[payslip.id],{'hutang_koperasi': pembayaran})
            if payslip.employee_id.sisa_tunggakan2 > 0 :
                pembayaran      = payslip.employee_id.hutang_perusahaan / payslip.employee_id.pembayaran2
                self.write(cr,uid,[payslip.id],{'hutang_perusahaan': pembayaran})
            if payslip.employee_id.sisa_denda > 0 :
                pembayaran      = payslip.employee_id.denda_kelalaian / float(payslip.employee_id.cicilan)
                self.write(cr,uid,[payslip.id],{'denda_kelalaian' : pembayaran})
            date_contract	=payslip.contract_id.date_start
            date_to 		= payslip.date_to
            date_cont 		= datetime.strptime(date_contract,"%Y-%m-%d").year
            date_pays 		= datetime.strptime(date_to,"%Y-%m-%d").year
            year 			=(date_pays - date_cont) / 5
            date_cont 		= datetime.strptime(date_contract,"%Y-%m-%d").month
            date_pays 		= datetime.strptime(date_to,"%Y-%m-%d").month

            ################################################################################
            #menghitung tunjangan kinerja
            ################################################################################
            kinerja_obj = self.pool.get("hr.tk.gol")
            kinerja_src = kinerja_obj.search(cr,uid,[('master_tunjangan','=',payslip.contract_id.jenis_tunjangan.id)])
            for kinerja in kinerja_obj.browse(cr,uid,kinerja_src) :
	       		if pay_objk.employee_id.gol_id.id == kinerja.gol_id.id :
	       			self.write(cr,uid,[payslip.id],{'tunjangan_kinerja' : kinerja.nominal})

	        #menghitung tunjangan hari raya
			# date_now 	= datetime.now().year
			# thr_obj		= self.pool.get('thr')
			# thr_src		= thr_obj.search(cr,uid,[('tahun','=',date_now)])
			# for thr in thr_obj.browse(cr,uid,thr_src) :
			# 	month_date	= thr.date
			# 	month 		= datetime.strptime(month_date,"%Y-%m-%d").month
			# 	if date_pays == month :
			# 		self.write(cr,uid,ids,{'tunjangan_hariraya' : pay_objk.contract_id.wage})
            # if year == 1 or year == 2 or year == 3 or year == 4 or year == 5 or year == 6 or year == 7 or year ==8 or year == 9 or year == 10 :
            #    if date_cont == date_pays :
            #        nilai	=1
            #        self.write(cr, uid,ids, {'komisi': nilai}, context=context)
          
            if pay_objk.thr == True :
                # cari tanggal masuk kerja di dalam kontrak
                tgl_masuk = pay_objk.contract_id.date_start
                tgl_masuk_str = datetime.strptime(tgl_masuk,"%Y-%m-%d")
                tgl_masuk_y = datetime.strptime(tgl_masuk,"%Y-%m-%d").year
                tgl_masuk_m = datetime.strptime(tgl_masuk,"%Y-%m-%d").month
                
                # cari tanggal gajian
                tgl_gaji = pay_objk.date_from
                tgl_gaji_str = datetime.strptime(tgl_gaji,"%Y-%m-%d")
                tgl_gaji_y = datetime.strptime(tgl_gaji,"%Y-%m-%d").year
                tgl_gaji_m = datetime.strptime(tgl_gaji,"%Y-%m-%d").month
                
                if tgl_masuk_y < tgl_gaji_y :
                    self.write(cr,uid,[pay_objk.id],{'tunjangan_hariraya' : pay_objk.contract_id.wage})
                else :
                    pembagi = tgl_gaji_m - (tgl_masuk_m - 1)
                    terima_thr = pay_objk.contract_id.wage/pembagi
                    self.write(cr,uid,[pay_objk.id],{'tunjangan_hariraya' : pembagi})  

            number          = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')
            #date_d = datetime.strptime(date,"%Y-%m-%d %H:%M:%S").day

            ################################################################################
            #delete old payslip lines
            ################################################################################
            old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
            if old_slipline_ids:
                slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)

            if payslip.contract_id:
                ################################################################################
                #set the list of contract for which the rules have to be applied
                ################################################################################
                contract_ids 	= [payslip.contract_id.id]
            else:
                ################################################################################
                #if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                ################################################################################
                contract_ids 	= self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)


            ################################################################################
            # overwrite field in payslip for tunjangan pajak and pajak
            ################################################################################
            gross = 0.0
            cat_obj	=self.pool.get('hr.salary.rule.category')
            cat_src			=cat_obj.search(cr,uid,[('name','=','Net')])
            for categoriess in cat_obj.browse(cr,uid,cat_src) :
                cat_id 		= categoriess.id 
            salary_obj		=self.pool.get('hr.salary.rule')
            if pay_objk.contract_id.type_id.type_perhitungan_pajak == "mix" :
                total_gross_tetap = 0.0
                total_gross_ttetap = 0.0
                potongan 	= 0.0
                for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                    # import pdb;pdb.set_trace()
                    rule 	= line['salary_rule_id']
                    brw_rule = salary_obj.browse(cr,uid,[rule])[0]
                    if brw_rule.bonus == 'bonus_tetap' and brw_rule.category_id.name == "Gross" :
                        total_gross_tetap += line['amount']
                    elif brw_rule.bonus == 'bonus_tidak_tetap' and brw_rule.category_id.name == "Gross" :
                        total_gross_ttetap += line['amount']
                    cod =line['code'] 
                    if cod == 'POT_ABSEN' :
                        self.write(cr,uid,[pay_objk.id],{'pot_absen':line['amount']},context=context)    
                    if cod == "BASIC" and brw_rule.category_id.name == "Gross" :
                        potongan = pay_objk.pot_absen
                gross = total_gross_tetap + potongan      
                self.write(cr,uid,[pay_objk.id],{'gross_tetap': gross ,'gross_ttetap' : total_gross_ttetap})     
                tunjangan_pajak = self.tunjangan(cr,uid,ids,context=None)    


            total_bonus_tetap = 0.0
            total_bonus_ttetap = 0.0
            basic = 0.0
            makan = 0.0
            jabatan = 0.0
            tunj = 0.0
            bpjs_ket = 0.0
            bpjs_ket2 = 0.0
            total = 0.0
            tunj_THR = 0.0 
            bpjs_kes = 0.0
            tunj_Adlk = 0.0
            tunj_shift3 = 0.0
            # tunj_kinerja = 0.0
            tunj_trans = 0.0
            basic = 0.0
            tunj_makan = 0.0
            tunj_jab = 0.0
            tunj_kom = 0.0
            tunj_fung = 0.0
            bpjs_ket  = 0.0
            bpjs_ket2 = 0.0
            denda_terlambat = 0.0
            denda_tidakhadir = 0.0
            pot_komunikasi = 0.0 
            pot_fungsional = 0.0
            pot_transport  = 0.0
            pot_kinerja    = 0.0
            pot_bpjs_kes = 0.0
            pinjaman_koperasi = 0.0
            pinjaman_perusahaan = 0.0
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                rule = line['salary_rule_id']
                brw_rule = salary_obj.browse(cr,uid,[rule])[0]
                if brw_rule.bonus == 'bonus_tetap' and brw_rule.category_id.name != "Deduction" :
                    total_bonus_tetap += line['amount']
                elif brw_rule.bonus == 'bonus_tidak_tetap' and brw_rule.category_id.name != "Deduction" :
                    total_bonus_ttetap += line['amount']

                ##### menghitung upah tetap #####                
                cod = line['code'] 
                if cod == 'BASIC' :
                    basic = line['amount']
                if cod == 'tunjangan_makan' :
                    makan = line['amount']
                if cod == 'tunjangan_jabatan' :
                    jabatan = line['amount']

                ##### menghitung bpjs etenagakerjaan ######
                if cod == 'BPJS_KETENAGAKERJAAN' :
                    bpjs_ket = line['amount']
                if cod == 'POT_BPJS_KETENAGAKERJAAN':
                    bpjs_ket2 = line['amount']*-1
                if cod == 'POT_ABSEN' :
                    self.write(cr,uid,[pay_objk.id],{'pot_absen':line['amount']},context=context)   
                if cod == 'TPAJ' and brw_rule.category_id.name == "Gross" :
                    self.write(cr,uid,[pay_objk.id],{'tunj_pajak_code':'Gross'},context=context) 
                if cod == 'TPAJ' :
                    tunj = line['amount']
                if cod == "BASIC" :
                    basic = line['amount']
                if cod == 'tunjangan_makan' :
                    tunj_makan =line['amount']
                if cod == 'tunjangan_jabatan' :
                    tunj_jab = line['amount']
                if cod == 'tunjangan_komunikasi' :
                    tunj_kom = line['amount']
                if cod == 'tunjangan_fungsional' :
                    tunj_fung = line['amount']
                if cod == 'tunjangan_transport' :
                    tunj_trans = line['amount']
                if cod == 'tunjangan_shift_3' :
                    tunj_shift3 = line['amount']
                if cod == 'Adlk' :
                    tunj_Adlk = line['amount']
                if cod == 'THR' :
                    tunj_THR = line['amount'] 
                if cod == 'BPJS_KESEHATAN' :
                    bpjs_kes = line['amount']
                if cod == 'Total' :
                    total = line['amount']
                if cod == 'LEMBUR' :
                    lembur = line['amount']
                if cod == 'denda_ketidakhadiran' :
                    denda_tidakhadir = line['amount']
                if cod == 'denda_terlambat' :
                    denda_terlambat = line['amount']
                if cod == "pot_tunjangan_komunikasi" :
                    pot_komunikasi = line['amount']
                if cod == 'pot_tunjangan_fungsional' :
                    pot_fungsional = line['amount']
                if cod == 'pot_tunjangan_transport' :
                    pot_transport = line['amount']
                if cod == 'pot_tunjangan_kinerja' :
                    pot_kinerja = line['amount']
                if cod == 'POT_BPJS_KESEHATAN' :
                    pot_bpjs_kes = line['amount']
                if cod == 'hutang_kop' :
                    pinjaman_koperasi = line['amount']
                if cod == 'hutang_per' :
                    pinjaman_perusahaan = line['amount']

            ################################################################################
            # denda ketidak hadiran
            ################################################################################
            dendatdkhdrall = denda_tidakhadir + pot_komunikasi + pot_fungsional + pot_transport + pot_kinerja    
            self.write(cr,uid,[payslip.id],{
                'status_karyawan':payslip.employee_id.status_karyawan.name,
                'pinjaman_koperasi':pinjaman_koperasi,
                'pinjaman_perusahaan':pinjaman_perusahaan,
                'bpjs_kes_pot':pot_bpjs_kes,
                'denda_ketidakhadiran':dendatdkhdrall,
                'denda_keterlambatan':denda_terlambat,
                'lembur':lembur,
                'job_id':payslip.employee_id.job_id.name,
                'department_id':payslip.employee_id.department_id.name,
                'class_id':payslip.employee_id.clas_id.name,
                'gol_id':payslip.employee_id.gol_id.name,
                'lokasi_kerja':payslip.employee_id.address_id2.name,
                'net':total,
                'tunjangan_hariraya':tunj_THR,
                'bpjs_kes':bpjs_kes,
                'tunj_luarkt':tunj_Adlk,
                'tunj_shift3':tunj_shift3,
                'tunj_trans':tunj_trans,
                'gapok':basic,
                'tunj_makan':tunj_makan,
                'tunj_jab':tunj_jab,
                'tunj_kom':tunj_kom,
                'tunj_fungsional':tunj_fung,
                'bpjs_ket':bpjs_ket,
                'bpjs_ket_pot' : bpjs_ket2 ,
                'total_tp': total_bonus_tetap ,
                'total_ttp' : total_bonus_ttetap})

            if payslip.employee_id.ptkp_id.id != False :
                pajak = self.pajak(cr,uid,ids,context=None)              
            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number})
            ccc =self.libur(cr,uid,ids,context=None)
            date_pays2 = datetime.strptime(date_to,"%Y-%m-%d").year
            self.write(cr,uid,ids,{'libur':ccc,'year':date_pays2},context=context)
        return True     

    def tunjangan(self,cr,uid,ids,context=None) :
        obj = self.browse(cr,uid,ids)[0]
        date = obj.date_to
        employee = obj.employee_id.id
        years = datetime.strptime(date,"%Y-%m-%d").year 
        months = datetime.strptime(date,"%Y-%m-%d").month
        date_contract = obj.contract_id.date_start
        year_contract = datetime.strptime(date_contract,"%Y-%m-%d").year
        month_contract = datetime.strptime(date_contract,"%Y-%m-%d").month
        date_now = datetime.now().year
        status_pjk = obj.employee_id.ptkp_id.nominal_tahun
        cek = True
        xx = 0
        tunj_pajak = 0.0
        recursive =1.0
        if year_contract == date_now :
            pengali = 13 - int(month_contract) 
        else :
            pengali = 12
        if months != 12 :
            while cek == True and xx <= 100 :
                total1 = obj.gross_tetap + tunj_pajak
                total2 = obj.gross_ttetap
                basic = obj.contract_id.wage
                pjk12 = (total1 * pengali) + total2 # total allowance di setahunkan
                #potongan jabatan
                pot_jab = (obj.contract_id.type_id.biaya_jabatan * pjk12)/100
                if pot_jab >= obj.contract_id.type_id.max_biaya_jabatan :
                    pot_jab = obj.contract_id.type_id.max_biaya_jabatan
                #tunjangan hari tua
                tht_alw = (obj.contract_id.type_id.ttht * (obj.contract_id.wage * pengali))/100
                if tht_alw >= obj.contract_id.type_id.max_tht :
                    tht_alw = obj.contract_id.type_id.max_tht
                # pengurang pajak
                total_ptkp = pot_jab + status_pjk + tht_alw
                # total PKP
                pkp = pjk12 - total_ptkp
                obj_ptkp = self.pool.get('hr.pkp')
                src_ptkp = obj_ptkp.search(cr,uid,[])
                pajjak = 0.0
                for ptkp in obj_ptkp.browse(cr,uid,src_ptkp):
                    pajak = 0.0
                    percent = ptkp.pajak
                    if pkp > ptkp.nominal_max :
                        total_ptkp = ptkp.nominal_max - ptkp.nominal_min
                        pajak = (total_ptkp * percent)/100 
                    elif pkp <= ptkp.nominal_max and pkp >= ptkp.nominal_min :
                        pjk = pkp - ptkp.nominal_min
                        pajak = (pjk *percent)/100
                    pajjak = pajjak + pajak 
                pajak2 = pajjak / pengali
                if obj.contract_id.type_id.type_perhitungan_pajak == 'net' : 
                    self.write(cr,uid,ids,{'pkp':pajak2})
                    cek = False
                else :
                    xx += 1
                    if pajak2 >= tunj_pajak :
                        recursive = recursive + 0.001
                        if xx == 1 :
                            tp = pajak2
                        tunj_pajak = tp * recursive
                    else :
                        cek = False
                    if pajak2 >= tunj_pajak :  
                        self.write(cr,uid,ids,{'pkp':pajak2, 'tunj_pajak' : pajak2})       
        else :
            pay_obj = self.pool.get('hr.payslip')
            pay_src = pay_obj.search(cr,uid,[('employee_id','=',employee),('state','=','done'),('year','=',years)])
            x = 0.0
            total_gross = 0.0
            total_gross1 = 0.0
            pajak_total = 0.0
            tunj_pajak = 0.0
            tunj_pajak1 = 0.0
            jum_gross = 0.0
            jum_gross1 = 0.0
            for pajak_year in pay_obj.browse(cr,uid,pay_src):
                jum_gross += pajak_year.gross_tetap + pajak_year.gross_ttetap 
                x += 1
                tunj_pajak1 += pajak_year.tunj_pajak
            jum_gross1 = jum_gross
            jum_gross = jum_gross + obj.gross_tetap + obj.gross_ttetap
            #potongan jabatan
            while cek == True and xx <= 100 :
                total_gross1 = jum_gross + tunj_pajak
                pot_jab = (obj.contract_id.type_id.biaya_jabatan * total_gross1)/100
                if pot_jab >= obj.contract_id.type_id.max_biaya_jabatan :
                    pot_jab = obj.contract_id.type_id.max_biaya_jabatan 
                tht_alw = (obj.contract_id.type_id.ttht * (obj.contract_id.wage * x))/100
                if tht_alw >= obj.contract_id.type_id.max_tht :
                    tht_alw = obj.contract_id.type_id.max_tht
                total_ptkp = pot_jab + status_pjk + tht_alw
                pkp = total_gross1 - total_ptkp
                obj_ptkp = self.pool.get('hr.pkp')
                src_ptkp = obj_ptkp.search(cr,uid,[])
                pajjak = 0.0
                for ptkp in obj_ptkp.browse(cr,uid,src_ptkp):
                    pajak = 0.0
                    percent = ptkp.pajak
                    if pkp > ptkp.nominal_max :
                        total_ptkp = ptkp.nominal_max - ptkp.nominal_min
                        pajak = (total_ptkp * percent)/100 
                    elif pkp <= ptkp.nominal_max and pkp >= ptkp.nominal_min :
                        pjk = pkp - ptkp.nominal_min
                        pajak = (pjk *percent)/100
                    pajjak = pajjak + pajak 
                if obj.contract_id.type_id.type_perhitungan_pajak == 'net': 
                    self.write(cr,uid,ids,{'pkp':pajak2})
                    cek = False
                else :
                    xx += 1
                    if pajjak >= tunj_pajak :
                        recursive = recursive + 0.001
                        if xx == 1 :
                            tp = pajjak
                        tunj_pajak = tp * recursive
                    else :
                        cek = False
                    if pajjak >= tunj_pajak :
                        pajjak1 = pajjak 
            pajak2 = pajjak1 - tunj_pajak1
            self.write(cr,uid,ids,{'pkp':0.0, 'tunj_pajak' : pajak2,'tunj_pajak_tahun' : pajjak1})
        return True

    def pajak(self,cr,uid,ids,context=None) :
        obj = self.browse(cr,uid,ids)[0]
        date = obj.date_to
        npwp = obj.contract_id.employee_id.npwp
        employee = obj.employee_id.id
        years = datetime.strptime(date,"%Y-%m-%d").year 
        months = datetime.strptime(date,"%Y-%m-%d").month
        date_contract = obj.contract_id.date_start
        year_contract = datetime.strptime(date_contract,"%Y-%m-%d").year
        month_contract = datetime.strptime(date_contract,"%Y-%m-%d").month
        date_now = datetime.now().year
        status_pjk = obj.employee_id.ptkp_id.nominal_tahun
        cek = True
        xx = 0
        tunj_pajak = 0.0
        recursive =1.0
        if year_contract == date_now :
            pengali = 13 - int(month_contract) 
        else :
            pengali = 12
        if months != 12 :
            while cek == True and xx <= 100 :
                if obj.contract_id.type_id.type_perhitungan_pajak != 'mix':
                    total1 = obj.total_tp + obj.pot_absen + tunj_pajak 
                else :
                    total1 = obj.total_tp + obj.pot_absen  + obj.tunj_pajak  
                total2 = obj.total_ttp
                basic = obj.contract_id.wage
                #import pdb;pdb.set_trace()
                pjk12 =  (((obj.total_tp-obj.bpjs_ket)+(obj.bpjs_ket/6.89*1.19))*12)+(obj.contract_id.wage+obj.contract_id.jenis_tunjangan.tunj_makan+obj.contract_id.jenis_tunjangan.tunj_jabatan)
                #pjk12 = (total1 * pengali) + total2 # total allowance di setahunkan
                #potongan jabatan
                pot_jab = (obj.contract_id.type_id.biaya_jabatan * pjk12)/100
                if pot_jab >= obj.contract_id.type_id.max_biaya_jabatan :
                    pot_jab = obj.contract_id.type_id.max_biaya_jabatan
                #tunjangan hari tua
                tht_alw = (obj.contract_id.type_id.ttht * (obj.contract_id.wage * pengali))/100
                if tht_alw >= obj.contract_id.type_id.max_tht :
                    tht_alw = obj.contract_id.type_id.max_tht
                # pengurang pajak
                total_ptkp = pot_jab + status_pjk #+ tht_alw
                # total PKP
                pkp = (pjk12 - pot_jab - (obj.bpjs_ket_pot/9.89*3)*12)-status_pjk
                #pkp = (pjk12 - pot_jab - status_pjk)
                obj_ptkp = self.pool.get('hr.pkp')
                src_ptkp = obj_ptkp.search(cr,uid,[])
                pajjak = 0.0
                for ptkp in obj_ptkp.browse(cr,uid,src_ptkp):
                    pajak = 0.0
                    percent = ptkp.pajak
                    if pkp > ptkp.nominal_max :
                        total_ptkp = ptkp.nominal_max - ptkp.nominal_min
                        pajak = (total_ptkp * percent)/100 
                    elif pkp <= ptkp.nominal_max and pkp >= ptkp.nominal_min :
                        pjk = pkp - ptkp.nominal_min
                        pajak = (pjk *percent)/100
                    pajjak = pajjak + pajak
                #import pdb;pdb.set_trace() 
                if npwp == False :
                    pajak2 = int((pajjak+((pajjak*20)/100))/12)
                else :
                    pajak2 = int(pajjak / 12)
                if obj.contract_id.type_id.type_perhitungan_pajak == 'net'  or obj.contract_id.type_id.type_perhitungan_pajak == 'mix'  : 
                    self.write(cr,uid,ids,{'pkp':pajak2})
                    cek = False
                else :
                    xx += 1
                    if pajak2 >= tunj_pajak :
                        recursive = recursive + 0.001
                        if xx == 1 :
                            tp = pajak2
                        tunj_pajak = tp * recursive
                    else :
                        cek = False
                    if pajak2 >= tunj_pajak :
                        self.write(cr,uid,ids,{'pkp':pajak2, 'tunj_pajak' : pajak2})          
        else :
            pay_obj = self.pool.get('hr.payslip')
            pay_src = pay_obj.search(cr,uid,[('employee_id','=',employee),('state','=','done'),('year','=',years)])
            x = 1.0
            total_alw = 0.0
            pajak_total = 0.0
            tot_Sementara = 0.0
            pajjak1 = 0.0
            for pajak_year in pay_obj.browse(cr,uid,pay_src):
                jum_alw = pajak_year.total_tp + pajak_year.total_ttp + pajak_year.pot_absen 
                total_alw += jum_alw
                pajak_total += pajak_year.pkp
                x += 1
            tot_sementara = total_alw
            total_alw = tot_sementara + obj.total_tp + obj.total_ttp + obj.pot_absen
            if  obj.contract_id.type_id.type_perhitungan_pajak == 'mix' :
                total_alw = tot_sementara + obj.total_tp + obj.total_ttp + obj.pot_absen + obj.tunj_pajak_tahun
            #potongan jabatan
            while cek == True and xx <= 100 :
                pot_jab = (obj.contract_id.type_id.biaya_jabatan * total_alw)/100
                if pot_jab >= obj.contract_id.type_id.max_biaya_jabatan :
                    pot_jab = obj.contract_id.type_id.max_biaya_jabatan 
                tht_alw = (obj.contract_id.type_id.ttht * (obj.contract_id.wage * x))/100
                if tht_alw >= obj.contract_id.type_id.max_tht :
                    tht_alw = obj.contract_id.type_id.max_tht
                total_ptkp = pot_jab + status_pjk + tht_alw
                pkp = (total_alw + tunj_pajak) - total_ptkp
                obj_ptkp = self.pool.get('hr.pkp')
                src_ptkp = obj_ptkp.search(cr,uid,[])
                pajjak = 0.0
                for ptkp in obj_ptkp.browse(cr,uid,src_ptkp):
                    pajak = 0.0
                    percent = ptkp.pajak
                    if pkp > ptkp.nominal_max :
                        total_ptkp = ptkp.nominal_max - ptkp.nominal_min
                        pajak = (total_ptkp * percent)/100 
                    elif pkp <= ptkp.nominal_max and pkp >= ptkp.nominal_min :
                        pjk = pkp - ptkp.nominal_min
                        pajak = (pjk *percent)/100
                    pajjak = pajjak + pajak 
                if obj.contract_id.type_id.type_perhitungan_pajak == 'net' or obj.contract_id.type_id.type_perhitungan_pajak == 'mix' : 
                    pajak2 = pajjak - pajak_total
                    self.write(cr,uid,ids,{'pkp':pajak2})
                    cek = False
                elif obj.contract_id.type_id.type_perhitungan_pajak == 'gross_up':
                    xx += 1
                    if pajjak >= tunj_pajak :
                        recursive = recursive + 0.001
                        if xx == 1 :
                            tp = pajjak
                        tunj_pajak = tp * recursive
                    else :
                        cek = False
                    if pajjak >= tunj_pajak :
                        pajjak1 = pajjak 
            if obj.contract_id.type_id.type_perhitungan_pajak == 'gross_up' :
                pajak2 = pajjak1 - pajak_total
                self.write(cr,uid,ids,{'pkp':pajak2, 'tunj_pajak' : pajak2})
        return True

    def process_sheet(self, cr, uid, ids, context=None):
    	obj 			= self.browse(cr,uid,ids)[0]
    	employee_obj	= self.pool.get('hr.employee')
        sisa_tunggakan	= obj.employee_id.sisa_tunggakan - obj.hutang_koperasi 
        sisa_tunggakan2	= obj.employee_id.sisa_tunggakan2 - obj.hutang_perusahaan 
        sisa_denda 		= obj.employee_id.sisa_denda - obj.denda_kelalaian
       	employee_obj.write(cr,uid,[obj.employee_id.id],{'sisa_tunggakan' : sisa_tunggakan, 'sisa_tunggakan2' : sisa_tunggakan2,'sisa_denda' : sisa_denda})
        return self.write(cr, uid, ids, {'paid': True, 'state': 'done'}, context=context)

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
        #view report
        'gapok'                     : fields.float('Gaji Pokok'),
        'tunj_makan'                : fields.float('Tunjangan Makan'),
        'tunj_jab'                  : fields.float('Tunjangan Jabatan'),
        'tunj_kom'                  : fields.float('Tunjangan komunikasi'),
        'tunj_fungsional'           : fields.float('Tunjangan Fungsional'),
        'tunj_trans'                : fields.float('Tunjangan Transportasi'),
		'tunjangan_kinerja'			: fields.float('Tunjangan Kinerja'),
        'tunj_shift3'               : fields.float('Tunjangan Shift 3'),
        'tunj_luarkt'               : fields.float('Tunjangan Luar Kota'),
        'lembur'                    : fields.float('Lembur'),
        'tunjangan_hariraya'        : fields.float('Tunjangan Hari Raya'),
        'bpjs_ket'                  : fields.float('Tunjangan bpjs ket'),
        'bpjs_kes'                  : fields.float('Tunjangan bpjs kes'),

        #DENDA
        'denda_keterlambatan'       : fields.float('Denda Keterlambatan'),
        'denda_ketidakhadiran'      : fields.float('Denda Ketidakhadiran'),
        'bpjs_ket_pot'              : fields.float('pot bpjs ket'),
        'bpjs_kes_pot'              : fields.float('pot bpjs kes'),
		'hutang_koperasi'			: fields.float('hutang ke koperasi'),
		'hutang_perusahaan'			: fields.float('hutang Ke perusahaan'),
		'denda_kelalaian'			: fields.float('Denda Kelalaian'),
        'pinjaman_koperasi'         : fields.float('Pinjaman Koperasi'),
        'pinjaman_perusahaan'         : fields.float('Pinjaman Perusahaan'),
        
    	'thr'                       : fields.boolean('THR',help='Centang Jika Bulan Ini THR'),
        'lokasi_kerja'              : fields.char('Lokasi Kerja'),
        'job_id'                    : fields.char('Jabatan'),
        'department_id'             : fields.char('Department'),
        'class_id'                  : fields.char('Kelas'),
        'gol_id'                    : fields.char('Golongan'),
        'status_karyawan'           : fields.char('Status Karyawan'),
        }
hr_payslip()

class master_tunjangan(osv.osv):
	
	_name			= 'hr.master.tunjangan'
	_description	= 'master tunjangan'

	_columns		={
		'name'				: fields.char('Code'),
		'name_jabatan'		: fields.selection([('pejabat','Pejabat'),('penjabat','Penjabat')],'Nama Jabatan'),
		'kelas'				: fields.many2one('hr.kelas.jabatan','class'),   
		'tunj_jabatan'		: fields.integer('Tunjangan Jabatan'),
		'tunj_makan'		: fields.integer('Tunjangan Makan'), 
		'tunj_komunikasi'	: fields.integer('Tunjangan Komunikasi'),
		'tunj_fungsional'	: fields.integer('Tunjangan Fungsional'),
		'tunj_transportasi'	: fields.integer('Tunjangan Transportasi'),
		'tunj_kinerja'		: fields.one2many('hr.tk.gol','master_tunjangan','Tunjangan Kinerja'),
        #'tunj_lainlain'     : fields.integer('Tunjangan Lain-Lain'),


	}
master_tunjangan()

class tunjangan_kinerja(osv.osv):

	_name			= 'hr.tk.gol'
	_description	= 'tunjangan kinerja'

	_columns		= {
		'master_tunjangan'	: fields.many2one('hr.master.tunjangan','master tunjangan'),
		'gol_id'			: fields.many2one('hr_employs.gol','Golongan'),
		'nominal'			: fields.integer('Nominal'),
	}

class tunjangan_hari_raya(osv.osv):

	_name			= "thr"
	_description	= 'tunjangan hari raya'

	def create(self, cr, uid, vals, context=None):
		#import pdb;pdb.set_trace()
		date = vals['date']
		year = int(datetime.strptime(date,"%Y-%m-%d").year)
		vals['tahun'] =year
		return super(tunjangan_hari_raya, self).create(cr, uid, vals, context=context)

	_columns		= {
		'name'				: fields.char('Nama Tunjangan Hari raya'),
		'date'				: fields.date('Jatuh Tempo Tunjangan Hari Raya'),
		'tahun'				: fields.integer('Tahun')
	}
tunjangan_hari_raya()

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
        #date_from_16 =str(datetime.now() + relativedelta.relativedelta(months=+0, day=1))[:10]
        date_from_16 =str(datetime.now())[:10]
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
