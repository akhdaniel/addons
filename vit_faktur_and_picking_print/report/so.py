import time 
from report import report_sxw 
class so(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(so, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.so', 'sale.order', 'addons/vit_faktur_and_picking_print/report/so.rml', parser=so,)
