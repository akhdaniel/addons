import time 
from report import report_sxw 
class stock_picking(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context):
        super(stock_picking, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time,
        'get_product_desc': self.get_product_desc,
        'get_product_asc': self.get_product_asc,
        })

    def get_product_desc(self, move_line):
        # import pdb;pdb.set_trace()
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            # desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
            desc = desc
        return desc

    def get_product_asc(self, cr, uid, move_line, context):
        # import pdb;pdb.set_trace()
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
            # desc = desc
        return desc


for suffix in ['', '.in', '.out']:
    report_sxw.report_sxw('report.stock_picking' + suffix,
                          'stock.picking' + suffix,
                          'addons/vit_DO_print_sign/report/stock_picking.rml',
                          parser=stock_picking)
# for suffix in ['', '.in', '.out']:        
# report_sxw.report_sxw('report.stock_picking', 'stock.picking.out', 'addons/vit_DO_print_sign/report/stock_picking.rml', parser=stock_picking) 
