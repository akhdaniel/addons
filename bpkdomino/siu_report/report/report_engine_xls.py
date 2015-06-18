# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 AJM Technologies S.A. (http://www.ajm.lu)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.report import report_sxw
from openerp import tools
import xlwt
import cStringIO
import time
import datetime
from openerp import pooler

class report_xls(report_sxw.report_sxw):

    xls_types = {
        'bool': xlwt.Row.set_cell_boolean,
        'date': xlwt.Row.set_cell_date,
        'text': xlwt.Row.set_cell_text,
        'number': xlwt.Row.set_cell_number,
    }
    xls_types_default = {
        'bool': False,
        'date': None,
        'text': '',
        'number': 0,
    }

    def create(self, cr, uid, ids, data, context=None):
        pool = pooler.get_pool(cr.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        report_xml_ids = ir_obj.search(cr, uid,
                [('report_name', '=', self.name[7:])], context=context)
        if report_xml_ids:
            report_xml = ir_obj.browse(cr, uid, report_xml_ids[0], context=context)
        else:
            title = ''
            rml = tools.file_open(self.tmpl, subdir=None).read()
            report_type= data.get('report_type', 'pdf')
            class a(object):
                def __init__(self, *args, **argv):
                    for key,arg in argv.items():
                        setattr(self, key, arg)
            report_xml = a(title=title, report_type=report_type, report_rml_content=rml, name=title, attachment=False, header=self.header)
        report_type = report_xml.report_type
        ## ajm override :: begin
        report_type = 'xls'
        ## ajm override :: end
        if report_type in ['sxw','odt']:
            fnct = self.create_source_odt
        elif report_type in ['pdf','raw','html']:
            fnct = self.create_source_pdf
        elif report_type=='html2html':
            fnct = self.create_source_html2html
        ## ajm override :: begin
        elif report_type == 'xls':
            fnct = self.create_source_xls
        ## ajm override :: end
        else:
            raise 'Unknown Report Type'
        fnct_ret = fnct(cr, uid, ids, data, report_xml, context)
        if not fnct_ret:
            return (False,False)
        return fnct_ret

    def create_source_xls(self, cr, uid, ids, data, report_xml, context=None):
        print("START: "+time.strftime("%Y-%m-%d %H:%M:%S"))

        if not context:
            context = {}
        context = context.copy()
        rml_parser = self.parser(cr, uid, self.name2, context=context)
        objs = self.getObjects(cr, uid, ids, context=context)
        rml_parser.set_context(objs, data, ids, 'xls')

        n = cStringIO.StringIO()
        wb = xlwt.Workbook(encoding='utf-8')
        for i, a in enumerate(rml_parser.localcontext['objects']):
            self.generate_xls_report(rml_parser, data, a, wb)
        wb.save(n)
        n.seek(0)

        print("END: "+time.strftime("%Y-%m-%d %H:%M:%S"))

        return (n.read(), 'xls')

    def generate_xls_report(self, parser, data, obj, wb):
        raise NotImplementedError()

    def dt_to_datetime(self, date_str):
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(date_str, '%Y-%m-%d %H:%M:%S')))

    def d_to_datetime(self, date_str):
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(date_str, '%Y-%m-%d')))

    def xls_row_template(self, specs, wanted_list):
        """
        Return a row template, each column contains:
        0: Column Name
        1: Column Colspan
        2: Column Size
        3: Column Type (from report_xls.xls_types)
        4: Column data_get_function(x, d, p)
        5: Column write_cell_func
        6: Column Style
        """
        r = []
        col = 0
        for w in wanted_list:
            found = False
            for s in specs:
                if s[0] == w:
                    found = True
                    c = list(s[:])
                    c.append(report_xls.xls_types[c[3]])

                    # Set custom cell style
                    if len(s) > 5 and s[5] is not None:
                        c.append(s[5])
                    else:
                        c.append(None)

                    r.append((col, c[1], c))
                    col += c[1]
                    break
            if not found:
                print("column '%s' not found in specs" % (w))
        return r
    def xls_write_row(self, ws, x, d, p, row_count, row_template, row_style):
        r = ws.row(row_count)
        for col, size, spec in row_template:
            data = spec[4](x, d, p)
            style = spec[6] and spec[6] or row_style
            if not data:
                # if no data, use default values
                data = report_xls.xls_types_default[spec[3]]
            if size != 1:
                ws.write_merge(row_count, row_count,
                               col, col+size-1,
                               data, style)
            else:
                spec[5](r, col, data, style)

    def xls_write_row_header(self, ws, row_count, row_template, row_style=None, set_column_size=False):
        r = ws.row(row_count)
        for col, size, spec in row_template:
            data = spec[0]
            if size != 1:
                ws.write_merge(row_count, row_count,
                               col, col+size-1,
                               data, row_style)
            else:
                r.set_cell_text(col, data, row_style)
            if set_column_size:
                ws.col(col).width = spec[2] * 54


