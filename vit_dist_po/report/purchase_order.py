import time
from report import report_sxw
from osv import osv

class purchase_webkit(report_sxw.rml_parse):
  def __init__(self, cr, uid, name, context):
    super(purchase_webkit, self).__init__(cr, uid, name, context=context)
    self.localcontext.update({
        'time': time,
        'cr':cr,
        'uid': uid,
    })        

report_sxw.report_sxw('report.webkit.purchase.order',
                      'purchase.order', 
                      'vit_dist_po/report/purchase_order.mako',
                      parser=purchase_webkit)


class plan_purchase_webkit(report_sxw.rml_parse):
  def __init__(self, cr, uid, name, context):
    super(plan_purchase_webkit, self).__init__(cr, uid, name, context=context)
    self.localcontext.update({
        'time': time,
        'cr':cr,
        'uid': uid,
    })        

report_sxw.report_sxw('report.webkit.plan.purchase.order',
                      'purchase.order', 
                      'vit_dist_po/report/plan_purchase_order.mako',
                      parser=plan_purchase_webkit)


class supplier_invo(report_sxw.rml_parse):
  def __init__(self, cr, uid, name, context):
    super(supplier_invo, self).__init__(cr, uid, name, context=context)
    self.localcontext.update({
        'time': time,
        'cr':cr,
        'uid': uid,
    })        

report_sxw.report_sxw('report.webkit.po.supplier.invo',
                      'account.invoice', 
                      'vit_dist_po/report/po_invo.mako',
                      parser=supplier_invo)


class inship_fisik(report_sxw.rml_parse):
  def __init__(self, cr, uid, name, context):
    super(inship_fisik, self).__init__(cr, uid, name, context=context)
    self.localcontext.update({
        'time': time,
        'cr':cr,
        'uid': uid,
    })        

report_sxw.report_sxw('report.webkit.inship.fisik',
                      'stock.picking.in', 
                      'vit_dist_po/report/inship_fisik.mako',
                      parser=inship_fisik)