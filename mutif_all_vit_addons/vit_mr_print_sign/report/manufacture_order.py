import time 
from report import report_sxw 
class manufacture_order(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(manufacture_order, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.mrp.production', 'mrp.production', 'addons/vit_mr_print_sign/report/manufacture_order.rml', parser=manufacture_order) 
