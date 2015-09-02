import time 
from report import report_sxw 
class purchase_requisition_sign(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(purchase_requisition_sign, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.purchase_requisition', 'purchase.requisition', 'addons/vit_pr_print_sign/report/purchase_requisition_sign.rml', parser=purchase_requisition_sign) 
