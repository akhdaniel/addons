import time 
from openerp.report import report_sxw 

class ktm_report(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(ktm_report, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.ktm_report', 'res.partner', 'addons/vit_universities/reporta/vit_ktm.rml', parser=ktm_report) 
