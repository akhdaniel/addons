import time 
from report import report_sxw 
class supplier_card(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(supplier_card, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.supplie.card', 'supplier.card', 'addons/vit_supplier_card/report/supplier_card.rml', parser=supplier_card) 
