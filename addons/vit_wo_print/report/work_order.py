import time 
from report import report_sxw 
class work_order(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(work_order, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.mrp.production.workcenter.line', 'mrp.production.workcenter.line', 'addons/vit_wo_print/report/work_order.rml', parser=work_order) 
