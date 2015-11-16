import time 
from report import report_sxw 
class makloon_card(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(makloon_card, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.makloon.card', 'makloon.card', 'addons/vit_makloon_card/report/makloon_card.rml', parser=makloon_card) 

class makloon_card(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(makloon_card, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.makloon.card.manu', 'makloon.card', 'addons/vit_makloon_card/report/makloon_card_manu.rml', parser=makloon_card) 