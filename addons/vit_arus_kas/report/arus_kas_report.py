import time
from openerp.report import report_sxw 

class arus_kas(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(arus_kas, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.vit_arus_kas', 'arus.kas', 'addons/vit_arus_kas/report/arus_kas.rml', parser=arus_kas)