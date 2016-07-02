import time
from openerp.report import report_sxw 

class vit_customer(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(vit_arus_kas, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.vit_arus_kas', 'vit.arus.kas', 'addons/vit_arus_kas/report/arus_kas.rml', parser=vit_arus_kas) 