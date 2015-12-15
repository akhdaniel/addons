import time
from openerp.report import report_sxw 

class krs_report(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(krs_report, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.krs_report', 'operasional.krs', 'addons/vit_universities_v8/reports/vit_krs.rml', parser=krs_report) 