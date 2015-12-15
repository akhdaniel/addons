import time
from openerp.report import report_sxw 

class kelas_report(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(kelas_report, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.kelas_report', 'master.kelas', 'addons/vit_universities_v8/reports/vit_kelas.rml', parser=kelas_report) 