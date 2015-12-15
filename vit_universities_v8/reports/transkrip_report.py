import time
from openerp.report import report_sxw 

class transkrip_report(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(transkrip_report, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.transkrip_report', 'operasional.transkrip', 'addons/vit_universities_v8/reports/vit_transkrip.rml', parser=transkrip_report) 