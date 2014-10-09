import time 
from report import report_sxw 
class picking(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(picking, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.picking', 'surat.jalan', 'addons/vit_faktur_and_picking_print/report/picking.rml', parser=picking,) 
