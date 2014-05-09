import time 
from report import report_sxw 
from openerp.tools import amount_to_text_en

class hierarcy(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(hierarcy, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, })
        
report_sxw.report_sxw('report.hierarcy', 'hr.employee', 'addons/hrd_ppi/report/hierarcy.rml', parser=hierarcy) 
