import time
from openerp.report import report_sxw 

class spmb_report(report_sxw.rml_parse): 
	def __init__(self, cr, uid, name, context): 
		super(spmb_report, self).__init__(cr, uid, name, context) 
		self.localcontext.update({ 'time': time, }) 
		
report_sxw.report_sxw('report.spmb_report', 'spmb.mahasiswa', 'addons/vit_universities_v8/reports/vit_spmb.rml', parser=spmb_report) 