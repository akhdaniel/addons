import os
import re
import time
import tempfile
from openerp.report import report_sxw
import datetime
from pytz import timezone
        

class ReportStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'urut': self.urut,
            'koma': self.koma,
            'pencetak': self.pencetak,
            'get_dp':self.get_dp,
            'get_basedon': self.get_basedon,
        })
        
        self.re_digits_nondigits = re.compile(r'\d+|\D+')
        

    def get_dp(self, o):
        dp = 0
        for x in o.payment_ids:
            dp += x.credit
        return dp
                                       
    def urut(self, list, value):
        return list.index(value) + 1
                                       
    def get_basedon(self, form):
        data = self.pool.get(form['model']).browse(self.cr, self.uid, [form['form']['id']])
        return data

    def pencetak(self):
        date = datetime.now(timezone('Asia/Jakarta')).strftime("%d/%m/%Y at %H:%M:%S")
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        
        return date, user.name
    
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


report_sxw.report_sxw('report.invoice.customer', 'account.invoice', 'addons/siu_sale_order/report/invoice_customer.rml', parser=ReportStatus, header=False)
report_sxw.report_sxw('report.invoice.rekanan', 'account.invoice', 'addons/siu_sale_order/report/invoice_rekanan.rml', parser=ReportStatus, header=False)

