import time 
from report import report_sxw 

class move(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(move, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.move', 'stock.picking', 'addons/vit_internal_move_print/report/move.rml', parser=move) 
