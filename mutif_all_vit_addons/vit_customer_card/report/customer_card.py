import time 
from report import report_sxw 

class vit_customer(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(vit_customer, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.vit_customer', 'vit.customer', 'addons/vit_customer_card/report/customer_card.rml', parser=vit_customer) 