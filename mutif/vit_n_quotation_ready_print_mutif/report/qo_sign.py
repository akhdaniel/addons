import time 
from report import report_sxw 
class qo_sign(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(qo_sign, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.qo_sign', 'sale.order', 'addons/vit_n_quotation_ready_print_mutif/report/qo_sign.rml', parser=qo_sign,) 