import time 
from report import report_sxw 
class invoice2(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(invoice2, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.invoice2', 'account.invoice', 'addons/vit_faktur_and_picking_print/report/invoice2.rml', parser=invoice2,) 