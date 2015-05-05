import os
import re
import time
import tempfile
import datetime
from openerp.report import report_sxw
from pytz import timezone


class ReportStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'urut': self.urut,
            'nourut': self.nourut,
            'koma': self.koma,
            'datetime': datetime,
            'get_label': self.get_label,
            'pencetak': self.pencetak,
            'get_order': self.get_order,
        })
        
        self.re_digits_nondigits = re.compile(r'\d+|\D+')
        self.no = 0
                       
    def nourut(self):
        self.no = self.no + 1
        return self.no
                                       
    def urut(self, list, value):
        return list.index(value) + 1

    def pencetak(self):
        date = datetime.now(timezone('Asia/Jakarta')).strftime("%d/%m/%Y at %H:%M:%S")
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        
        return date, user.name

    def get_label(self, o):
        res = []; val = []
        
        for x in o.plan_id.order_ids:
            for i in x.order_line:
                if i.product_uom_qty > 1:
                    for a in range(0, int(i.product_uom_qty)):
                        res.append([x.name, i.product_id.name])
                else:
                    res.append([x.name, i.product_id.name])
                    
        for x in o.plan_id.stock_ids:
            for i in x.stock_line:
                if i.product_qty > 1:
                    for a in range(0, int(i.product_qty)):
                        res.append([x.name, i.product_id.name])
                else:
                    res.append([x.name, i.product_id.name])
                    
        if len(res) % 2 :
            res.append(['-', '-'])
            
        for x in range(0, len(res), 2):
            val.append([res[x], res[x+1]])
            
        return val


    def get_order(self, o):
        res = []
        for x in o.plan_id.order_ids:
            for i in x.order_line:
                res.append({
                            'name': x.name,
                            'shop': x.shop_id.name,
                            'partner': x.partner_id.name,
                            'product': i.product_id.partner_ref,
                            'ucapan': i.ucapan,
                            'qty': self.koma('%.0f', i.product_uom_qty)
                            })
                
        for x in o.plan_id.stock_ids:
            for i in x.stock_line:
                res.append({
                            'name': x.name,
                            'shop': x.shop_id.name,
                            'partner': '-',
                            'product': i.product_id.partner_ref,
                            'ucapan': '-',
                            'qty': self.koma('%.0f', i.product_qty)
                            })
                            
        return res
    
                     
    def koma(self, format, value):
        parts = self.re_digits_nondigits.findall(format % (value,))
        for i in xrange(len(parts)):
            s = parts[i]
            if s.isdigit():
                parts[i] = self.commafy(s)
                break
        return ''.join(parts)
        
    def commafy(self, s):
        r = []
        for i, c in enumerate(reversed(s)):
            if i and (not (i % 3)):
                r.insert(0, ',')
            r.insert(0, c)
        return ''.join(r)


report_sxw.report_sxw('report.print.rekap', 'material.requirement', 'addons/siu_mrp/report/print_rekap_produksi.rml', parser=ReportStatus, header=False)
report_sxw.report_sxw('report.print.produksi', 'mrp.production', 'addons/siu_mrp/report/print_produksi.rml', parser=ReportStatus, header=False)
report_sxw.report_sxw('report.print.order', 'material.requirement', 'addons/siu_mrp/report/print_order.rml', parser=ReportStatus, header=False)
report_sxw.report_sxw('report.print.label', 'material.requirement', 'addons/siu_mrp/report/print_label.rml', parser=ReportStatus, header=False)

