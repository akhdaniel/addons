import time
from report import report_sxw
from osv import osv

class ppn_webkit(report_sxw.rml_parse):
  def __init__(self, cr, uid, name, context):
    super(ppn_webkit, self).__init__(cr, uid, name, context=context)
    self.localcontext.update({
        'time': time,
        'cr':cr,
        'uid': uid,
    })        

report_sxw.report_sxw('report.webkit.account.invoice',
                      'account.invoice', 
                      'vit_dist_ppn/reports/ppn.mako',
                      parser=ppn_webkit)