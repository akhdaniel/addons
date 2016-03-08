import time 
from openerp.report import report_sxw 
class hr_training(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(hr_training, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.hr_training', 'hr_training.analisa', 'addons/hrd_ppi_training/report/hr_training.rml', parser=hr_training,) 
