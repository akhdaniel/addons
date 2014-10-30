import time 
from report import report_sxw 
class incoming_shipment(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(incoming_shipment, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.incoming_shipment', 'stock.picking.in', 'addons/vit_print_shipment/report/incoming_shipment.rml', parser=incoming_shipment) 