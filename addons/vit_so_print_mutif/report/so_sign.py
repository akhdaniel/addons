import time 
from report import report_sxw 
class so_sign(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(so_sign, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.so_sign', 'sale.order', 'addons/vit_so_print_mutif/report/so_sign.rml', parser=so_sign,) 