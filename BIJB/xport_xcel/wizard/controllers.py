# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.web.controllers.main import ExcelExport
import openerp.addons.web.http as openerpweb
from openerp.http import request
try:
    import xlwt
except ImportError:
    xlwt = None
try:
    import json
except ImportError:
    import simplejson as json
from cStringIO import StringIO

class XportXcel(ExcelExport):
    _cp_path = '/xport_xcel/xport_xcel'

    def create_xls(self, fields, rows):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        Payslip = pool['hr.payslip']
        style0 = xlwt.easyxf('font: name Times New Roman, color-index black, bold on',num_format_str='#,##0.00')
        style1 = xlwt.easyxf(num_format_str='D-MMM-YY')
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Sheet 1')
        heads = fields[0]['data'] #['Acc. No.','Trans. Amount','emp.Number','emp.Name','Dept','Trans. Date']
        x=0
        data=''
        for head in heads:
            ws.write(0,x,head,style0)
            x+=1
        for row in rows:
            slip_ids = Payslip.search(cr,uid,[('state','=','done'),('date_from','>=',row['datefrom']),('date_to','<=',row['dateto'])], context=context)
            payslips = Payslip.browse(cr, uid, slip_ids, context=context)
            payslip=[]
            for p in payslips:
                paid = 0.0;x=0;data=''
                payslip.append(p.id)
                amount=[line[0].total for line in p.details_by_salary_rule_category if line.category_id.name == 'Net']
                if amount:
                    paid=amount[0]
                ws.write(len(payslip),0,str(p.employee_id.name))
                ws.write(len(payslip),1,str(p.employee_id.job_id.name))
                ws.write(len(payslip),2,str(paid))
                ws.write(len(payslip),3,str(p.employee_id.bank_account_id.bank_name))
                ws.write(len(payslip),4,str(p.employee_id.bank_account_id.acc_number))
                ws.write(len(payslip),5,str(p.employee_id.bank_account_id.bank_bic))
                #ws.write(len(payslip),5,str(row['datetrf']))
        
        fp = StringIO()
        wb.save(fp)
        fp.seek(0)
        xlsdata = fp.read()
        fp.close()
        return xlsdata
        
    @openerpweb.httprequest
    def index(self, req, data, token):
        data = json.loads(data)
        return req.make_response(
            self.create_xls(data.get('headers', []), data.get('rows', [])),
                           headers=[
                                    ('Content-Disposition', 'attachment; filename="%s"'
                                        % data.get('model', 'export.xls')),
                                    ('Content-Type', self.content_type)
                                    ],
                                 cookies={'fileToken': token}
                                 )