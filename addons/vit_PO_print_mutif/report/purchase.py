import time 
from report import report_sxw 
class purchase(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(purchase, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.purchase', 'purchase.order', 'addons/vit_PO_print_mutif/report/purchase.rml', parser=purchase) 
