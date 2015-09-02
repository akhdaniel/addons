import time 
from report import report_sxw 
class stock(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(stock, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.stock', 'stock.picking.in', 'addons/vit_receipt_slip_print/report/stock.rml', parser=stock) 