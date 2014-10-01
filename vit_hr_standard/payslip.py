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
    tiket Pay Slip PPh 21
    '''

    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    _description = 'Pay Slip Inheriteed tiket.com'
    
           
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
            jx=0
            jx2=0
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
               #import pdb;pdb.set_trace()
                emp= line['employee_id']#cari employee utk cari status pajak
                cod= line['category_id']
                sud= line['code']
                if cod == 2 and  sud != "THR": # cari yang category allowance saja dan bukan THR
                    jx += line['amount'] 
                if sud =="THR":
                    sudd = line['amount']
                    self.write(cr, uid, [payslip.id], {'thr':sudd}, context=context)
                if sud =="GROSS":
                    gro = line['amount']
                    self.write(cr, uid, [payslip.id], {'total_9':gro}, context=context)  
                if cod == 1 : # cari yang category basic
                    jx2 = line['amount']
                if sud =="JHTTK":
                    sudi = -line['amount']
                    self.write(cr, uid, [payslip.id], {'jht':sudi}, context=context)

                empp= employ.search(cr,uid,[('id','=',emp)],context=context)[0]    
                empbro = employ.browse(cr,uid,empp,context=context)
                empbro2= empbro.status_id.nominal_tahun

                self.write(cr, uid, [payslip.id], {'alw':jx}, context=context)           
            
            jx3 = jx2+jx
            self.write(cr, uid, [payslip.id], {'total_7':jx3}, context=context)   

            jx4 = jx3 * 5/100
            self.write(cr, uid, [payslip.id], {'biaya_jabatan':jx4}, context=context),

            tot13= sudi+jx4
            self.write(cr, uid, [payslip.id], {'total_13':tot13}, context=context),

            tot14= gro-tot13
            self.write(cr, uid, [payslip.id], {'total_14':tot14}, context=context),

            tot16= tot14*12
            self.write(cr, uid, [payslip.id], {'total_16':tot16}, context=context), 


            tot18= tot16-empbro2
            if tot18 > 0 :
                self.write(cr, uid, [payslip.id], {'total_18':tot18}, context=context), 

                if tot18 >= 1 and tot18 <= 25000000 :
                    pph21 = tot18 * 0.05
                    self.write(cr, uid, [payslip.id], {'pph21_1th':pph21}, context=context),   

                elif tot18 >= 25000001 and tot18 <= 50000000:
                    pph21 = tot18 * 0.1
                    self.write(cr, uid, [payslip.id], {'pph21_1th':pph21}, context=context), 

                elif tot18 <= 50000001 and tot18 <= 100000000:
                    pph21 = tot18 * 0.15
                    self.write(cr, uid, [payslip.id], {'pph21_1th':pph21}, context=context), 

                elif tot18 <= 100000001 and tot18 <= 200000000:
                    pph21 = tot18 * 0.25
                    self.write(cr, uid, [payslip.id], {'pph21_1th':pph21}, context=context), 

                else :
                    pph21 = tot18 * 0.35
                    self.write(cr, uid, [payslip.id], {'pph21_1th':pph21}, context=context),       

                tot21= pph21/12
                self.write(cr, uid, [payslip.id], {'pph21_1bln':tot21}, context=context), 
            else:
                self.write(cr, uid, [payslip.id], {'pph21_1bln':0}, context=context),  
                self.write(cr, uid, [payslip.id], {'pph21_1th':0}, context=context),                      
                                                
            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number})

        return True     

    # def _7(self, cr, uid, ids, name, args, context=None):
    #     result={}
    #     to=0.0
    #     for tot in self.browse(cr,uid,ids):
    #         xxx=reim.name
    #         search_obj=holiday_obj.search(cr,uid,[('employee_id','=',xxx)])
    #         holi=holiday_obj.browse(cr,uid,search_obj,context=context)
    #         for hol in holi :   
    #             xyz=hol.tempp
    #             xxx=hol.temp
    #             ccc=hol.holiday_status_id.name
    #             stt = hol.state
    #             if stt == 'validate' and ccc == 'Cuti Tahunan':
    #                 yyy  += xyz   
    #                 zz += xxx               
    #         result[reim.id] =zz + yyy
    #     return result  
 
    _columns = {
        'alw' : fields.float("Total Allowance"),
        'thr': fields.float("THR"),
        'total_7': fields.float("Total 7"),
        'total_9' : fields.float("Total 9"),
        'jht': fields.float("JHT"),
        'biaya_jabatan' : fields.float('Biaya Jabatan 5%'),
        'total_13' : fields.float('Total 13'),
        'total_14' : fields.float('Total 14'),
        'total_16' : fields.float('Total 16'),
        'total_18' : fields.float('Total 18'),
        'pph21_1th': fields.float('PPh21 1 Tahun'),
        'pph21_1bln' : fields.float('PPh21 1 Bulan'),
    } 
                     
hr_payslip()