import time 
from report import report_sxw 
from openerp.tools import amount_to_text_en

class pph(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(PPH21_report, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, })
        
report_sxw.report_sxw('report.pph', 'hr.payslip',  'hrd_ppi_payroll/report/pph/pph.rml', parser=PPH21_report) 
