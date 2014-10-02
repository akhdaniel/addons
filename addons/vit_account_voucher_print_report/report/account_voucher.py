import time 
from report import report_sxw 
class account_voucher(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(account_voucher, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.account_voucher', 'account.voucher', 'addons/vit_account_voucher_print_report/report/account_voucher.rml', parser=account_voucher,) 
