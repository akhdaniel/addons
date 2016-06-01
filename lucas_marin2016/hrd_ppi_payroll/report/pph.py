import time 
from report import report_sxw 
class pph(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(pph, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, })
        
report_sxw.report_sxw('report.pph', 'hr.payslip','addons/hrd_ppi_payroll/report/pph.rml', parser=pph,) 
