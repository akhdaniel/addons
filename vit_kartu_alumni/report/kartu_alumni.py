import time
from openerp.report import report_sxw 

class res_partner(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(res_partner, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.res_partner', 'res.partner', 'addons/vit_kartu_alumni/report/kartu_alumni.rml', parser=res_partner) 