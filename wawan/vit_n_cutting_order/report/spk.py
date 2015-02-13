import time 
from report import report_sxw 
class spk(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(spk, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.spk', 'vit.cutting.order', 'vit_n_cutting_order/report/spk.rml', parser=spk,) 