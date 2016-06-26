import time 
from openerp.report import report_sxw
class move1(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(move1, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.move1', 'account.move', 'addons/vit_account_move_print/report/move1.rml', parser=move1,) 