import os
import re
import time
import tempfile
from openerp.osv import fields
import datetime
from openerp.report import report_sxw

class ReportStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'urut': self.urut,
            'koma': self.koma,
            'total': self.total,
            'datetime': datetime,
            'pencetak': self.pencetak,
            'get_lines': self.get_lines,
            'get_invoice': self.get_invoice,
            'get_basedon': self.get_basedon,
        })
        
        self.re_digits_nondigits = re.compile(r'\d+|\D+')
                                               
    def urut(self, list, value):
        return list.index(value) + 1

    def pencetak(self):
        from pytz import timezone
        date = datetime.now(timezone('Asia/Jakarta')).strftime("%d/%m/%Y at %H:%M:%S")
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        
        return date, user.name
                                
    def total(self, o):
        n = 0
        for x in o.order_ids:
            for i in x.move_lines:
                n += i.product_qty
                
        for x in o.stock_ids:
            for i in x.move_lines:
                n += i.product_qty
                
        return int(n)
                                                
    def get_lines(self, o):
        n = 1; data = []
        for x in o.order_ids:
            for i in x.move_lines:
                data.append({
                             'no': n,
                             'customer': x.partner_id.name,
                             'shop': x.shop_id.name,
                             'party_date': time.strftime('%d %B %Y %H:%M:%S', time.strptime(x.party_datetime,'%Y-%m-%d %H:%M:%S')),
                             'product': i.product_id.partner_ref,
                             'quantity': i.product_qty,
                             'ucapan': i.sale_line_id.ucapan,
                             'ref': x.origin
                             })
                n += 1
                
        for x in o.stock_ids:
            for i in x.move_lines:
                data.append({
                             'no': n,
                             'customer': x.partner_id.name,
                             'shop': x.shop_id.name,
                             'party_date': '-',
                             'product': i.product_id.partner_ref,
                             'quantity': i.product_qty,
                             'ucapan': '-',
                             'ref': x.origin
                             })
                n += 1
                
        return data
                
    
    def get_invoice(self, ori):
        obj_invoice = self.pool.get('account.invoice')
        data = obj_invoice.search(self.cr, self.uid, [('origin', '=', ori)])
        if data:
            val =obj_invoice.browse(self.cr, self.uid, data[0]).number
            return val 
        return '-'
             
    def get_basedon(self, form):
        data = self.pool.get(form['model']).browse(self.cr, self.uid, [form['form']['id']])
        return data
    
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


report_sxw.report_sxw('report.print.stock', 'stock.picking', 'addons/siu_manifest_delivery/report/print_stock.rml', parser=ReportStatus, header=False)
report_sxw.report_sxw('report.print.deliver', 'stock.picking', 'addons/siu_manifest_delivery/report/print_delivery.rml', parser=ReportStatus, header=False)
report_sxw.report_sxw('report.manifest.deliver', 'manifest.delivery', 'addons/siu_manifest_delivery/report/manifest_delivery.rml', parser=ReportStatus, header=False)

