import time 
from report import report_sxw 

class invoice1(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(invoice1, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.invoice1', 'account.invoice', 'addons/vit_invoice_print_extra/report/invoice1.rml', parser=invoice1) 

class invoice1_sign(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(invoice1_sign, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.invoice1_sign', 'account.invoice', 'addons/vit_invoice_print_extra/report/invoice1_sign.rml', parser=invoice1_sign)
