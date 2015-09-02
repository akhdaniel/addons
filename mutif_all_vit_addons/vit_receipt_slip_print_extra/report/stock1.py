import time 
from report import report_sxw 
class stock1(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(stock1, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.stock1', 'stock.picking.in', 'addons/vit_receipt_slip_print_extra/report/stock1.rml', parser=stock1) 
