import re
import xlwt
import time
import datetime
from pytz import timezone
from openerp.report import report_sxw
from report_engine_xls import report_xls

class ReportStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'koma': self.koma,
            'get_order': self.get_order,
            'get_no': self.get_no,
            'get_qty': self.get_qty,
            'get_name': self.get_name,
            'get_shop': self.get_shop,
            'pencetak': self.pencetak,
            'get_filter': self.get_filter,
            'get_invoice': self.get_invoice,
            'get_setoran': self.get_setoran,
            'get_rincian': self.get_rincian,
            'get_grandtotal': self.get_grandtotal   
        })

        self.no = 0
                
    def get_no(self):
        self.no = self.no + 1
        return self.no
     
    def get_name(self, i):
        name = '-'
        try:
            name = i.order_id.name 
        except:
            pass
        
        try:
            name = i.stock_id.name 
        except:
            pass
        
        return name

    def get_qty(self, i):
        qty = 0
        try:
            qty = i.product_uom_qty 
        except:
            pass
        
        try:
            qty = i.product_qty 
        except:
            pass
        
        try:
            qty = i.qty 
        except:
            pass
        
        return int(qty)

    def get_shop(self, i):
        shop = '-'
        try:
            shop = i.order_id.shop_id.name 
        except:
            pass
        
        try:
            shop = i.stock_id.shop_id.name 
        except:
            pass
        
        return shop
    
    def get_filter(self, o):
        data = ('Rasa', o.rasa)
        if o.name == 'ukuran':
            data = ('Ukuran', o.ukuran)
        elif o.name == 'delivery':
            data = ('', '')
        elif o.name == 'shop':
            data = ('Shop', o.shop_id.name)
        return data 


    def pencetak(self):
        date = datetime.now(timezone('Asia/Jakarta')).strftime("%d/%m/%Y at %H:%M:%S")
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        
        return date, user.name


    def get_setoran(self, o):
        
        obj_shop = self.pool.get('wtc.shop')
        obj_voucher = self.pool.get('account.voucher')
        obj_journal = self.pool.get('account.journal')
        obj_pos = self.pool.get('pos.order')
        obj_pos_line = self.pool.get('pos.order.line')
            
        hid = obj_shop.search(self.cr, self.uid, [])
        had = obj_shop.browse(self.cr, self.uid, hid)
                                 
        data = []; tot_total = 0; tot_cash = 0; tot_bank = 0; tot_transfer = 0; n = 0
        for x in had:
            total = 0; cash = 0; bank = 0; transfer = 0
            n += 1

            pid = obj_pos.search(self.cr, self.uid, [('shop_id', '=', x.id), ('date_order', '>=', o.date_from), ('date_order', '<=', o.date_from), ('state', 'not in', ('draft', 'cancel'))])
            pad = obj_pos_line.search(self.cr, self.uid, [('order_id','in', pid)])
            if pad:
                for k in obj_pos_line.browse(self.cr, self.uid, pad):
                    cash += k.price_subtotal

            jid = obj_journal.search(self.cr, self.uid, [('shop_id', '=', x.id)])
            if jid:
                vid = obj_voucher.search(self.cr, self.uid, [('journal_id', 'in', jid), ('setor_date', '>=', o.date_from), ('setor_date', '<=', o.date_from), ('state', '=', 'posted')])
                if vid :   
                    vad = obj_voucher.browse(self.cr, self.uid, vid)
                    for i in vad:
                        if i.journal_id.type == 'cash':
                            cash += i.amount
                        elif i.journal_id.type == 'bank':
                            bank += i.amount
                        else:
                            transfer += i.amount
                                                            
                    total = cash+bank+transfer
                    tot_total += total; tot_cash += cash; tot_bank += bank; tot_transfer += transfer
                    
            data.append({
                         'no': n, 
                         'shop': x.name, 
                         'total': self.koma('%.0f', total), 
                         'cash': self.koma('%.0f', cash), 
                         'bank': self.koma('%.0f', bank), 
                         'transfer': self.koma('%.0f', transfer)
                         })


        return data, self.koma('%.0f', tot_total), self.koma('%.0f', tot_cash), self.koma('%.0f', tot_bank), self.koma('%.0f', tot_transfer)


    def get_rincian(self, o):
        obj_shop = self.pool.get('wtc.shop')
        obj_voucher = self.pool.get('account.voucher')
        obj_journal = self.pool.get('account.journal')
        obj_pos = self.pool.get('pos.order')
        obj_pos_line = self.pool.get('pos.order.line')
            
        hid = obj_shop.search(self.cr, self.uid, [])
        had = obj_shop.browse(self.cr, self.uid, hid)
                                 
        data = []; n = 0
        for x in had:
            n += 1
            total = 0.0
            
            pid = obj_pos.search(self.cr, self.uid, [('shop_id', '=', x.id), ('date_order', '>=', o.date_from), ('date_order', '<=', o.date_from), ('state', 'not in', ('draft', 'cancel'))])
            pad = obj_pos_line.search(self.cr, self.uid, [('order_id','in', pid)])
            if pad:
                for k in obj_pos_line.browse(self.cr, self.uid, pad):
                    total += k.price_subtotal
                    
            data.append({
                         'no': n, 
                         'shop': x.name, 
                         'order': 'Rekapan POS Cabang', 
                         'price': self.koma('%.0f', total), 
                         'date': '-'
            })
            
            jid = obj_journal.search(self.cr, self.uid, [('shop_id', '=', x.id)])
            if jid:
                vid = obj_voucher.search(self.cr, self.uid, [('journal_id', 'in', jid), ('setor_date', '>=', o.date_from), ('setor_date', '<=', o.date_from), ('state', '=', 'posted')])
                if vid :
                    vad = obj_voucher.browse(self.cr, self.uid, vid)        
                    for i in vad:
                        data.append({
                                     'no': n, 
                                     'shop': x.name, 
                                     'order': i.line_cr_ids[0].move_line_id.invoice.number + ' (' + i.line_cr_ids[0].move_line_id.invoice.origin + ')', 
                                     'price': self.koma('%.0f', i.amount), 
                                     'date': time.strftime('%d %B %Y', time.strptime(i.setor_date,'%Y-%m-%d'))
                                     })

        return data
    
    def get_invoice(self, pid, o):
        data = []; total = 0
        
        obj_invoice = self.pool.get('account.invoice')
        sid = obj_invoice.search(self.cr, self.uid, [('partner_id', '=', pid), ('party_datetime', '>=', o.dari), ('party_datetime', '<=', o.sampai), ('state', '=', 'open')])
        if sid:
            sad = obj_invoice.browse(self.cr, self.uid, sid)
            for x in sad:
                for i in x.invoice_line:
                    total += i.price_subtotal
                    data.append({
                                 'number': i.invoice_id.number, 
                                 'date': time.strftime('%d %B %Y', time.strptime(i.invoice_id.party_datetime,'%Y-%m-%d %H:%M:%S')), 
                                 'ucapan': i.ucapan, 
                                 'harga': self.koma('%.0f', i.price_subtotal)
                                 })
        else:
            data.append({'number': '-', 'date': '-', 'ucapan': '-', 'harga': ''})
                
        return data, self.koma('%.0f', total)
    

    def get_grandtotal(self, o):
        grandtotal = 0.0
        obj_invoice = self.pool.get('account.invoice')
        for x in o.partner_ids:
            sid = obj_invoice.search(self.cr, self.uid, [('partner_id', '=', x.id), ('party_datetime', '>=', o.dari), ('party_datetime', '<=', o.sampai), ('state', '=', 'open')])
            if sid:
                sad = obj_invoice.browse(self.cr, self.uid, sid)
                for x in sad:
                    for i in x.invoice_line:
                        grandtotal += i.price_subtotal
            
        return self.koma('%.0f', grandtotal)
    
    def get_order(self, o):
        data = []; lid = []; mid = []; pad = []
        obj_order_line = self.pool.get('sale.order.line')
        obj_stock_line = self.pool.get('stock.order.line')
        obj_pos_line = self.pool.get('pos.order.line')
        
        sid = self.pool.get('sale.order').search(self.cr, self.uid, [('date_order', '>=', o.dari), ('date_order', '<=', o.sampai), ('state', 'not in', ('draft', 'cancel', 'shipping_except', 'invoice_except'))])
        oid = self.pool.get('stock.order').search(self.cr, self.uid, [('date', '>=', o.dari), ('date', '<=', o.sampai), ('state', '!=', 'draft')])
        pid = self.pool.get('pos.order').search(self.cr, self.uid, [('date_order', '>=', o.dari), ('date_order', '<=', o.sampai), ('state', 'not in', ('draft', 'cancel'))])
        
        if o.name == "rasa":
            lid = obj_order_line.search(self.cr, self.uid, [('order_id','in', sid), ('name', 'like', o.rasa)])
            mid = obj_stock_line.search(self.cr, self.uid, [('stock_id','in', oid), ('name', 'like', o.rasa)])
        elif o.name == "ukuran":
            lid = obj_order_line.search(self.cr, self.uid, [('order_id','in', sid), ('name', 'like', o.ukuran)])
            mid = obj_stock_line.search(self.cr, self.uid, [('stock_id','in', oid), ('name', 'like', o.ukuran)])
        elif o.name == "delivery":
            sid = self.pool.get('sale.order').search(self.cr, self.uid, [('delivery_date', '>=', o.dari), ('delivery_date', '<=', o.sampai), ('state', 'not in', ('draft', 'cancel', 'shipping_except', 'invoice_except'))])
            pad = obj_pos_line.search(self.cr, self.uid, [('order_id','in', pid)])
            lid = obj_order_line.search(self.cr, self.uid, [('order_id','in', sid)])
            mid = obj_stock_line.search(self.cr, self.uid, [('stock_id','in', oid)])
            
        if lid :    
            data += obj_order_line.browse(self.cr, self.uid, lid)
        if mid :
            data += obj_stock_line.browse(self.cr, self.uid, mid)
        if pad :
            data += obj_pos_line.browse(self.cr, self.uid, pad)
        return data
          
    def koma(self, format, value):
        if type(value) == type(1.0) or type(value) == type(1):
            parts = re.compile(r'\d+|\D+').findall(format % (value,))
            for i in xrange(len(parts)):
                s = parts[i]
                if s.isdigit():
                    parts[i] = self.commafy(s)
                    break
            return ''.join(parts)
        else :
            return value
            
    def commafy(self, s):
        r = []
        for i, c in enumerate(reversed(s)):
            if i and (not (i % 3)):
                r.insert(0, ',')
            r.insert(0, c)
        return ''.join(r)


report_sxw.report_sxw('report.rekap.invoice', 'consolidate.invoice', 'addons/siu_report/report/rekap_invoice.rml', parser=ReportStatus, header=False)        
report_sxw.report_sxw('report.sale.varian', 'sale.varian.report', 'addons/siu_report/report/sale_varian.rml', parser=ReportStatus, header=False)        
report_sxw.report_sxw('report.rekap.setoran', 'many.report', 'addons/siu_report/report/rekap_setoran.rml', parser=ReportStatus, header=False)        
report_sxw.report_sxw('report.rincian.setoran', 'many.report', 'addons/siu_report/report/rincian_setoran.rml', parser=ReportStatus, header=False)        
report_sxw.report_sxw('report.wtc.shop.pdf', 'sale.varian.report', 'addons/siu_report/report/sale_shop_pdf.rml', parser=ReportStatus, header=False)        
report_sxw.report_sxw('report.sale.stock.pdf', 'sale.varian.report', 'addons/siu_report/report/sale_stock_pdf.rml', parser=ReportStatus, header=False)        
    

class shop_order_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Sales Report'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1

        cols_specs = [
                      ('Reference', 1, 100, 'text', lambda x, d, p: x[0]),
                      ('Shop', 1, 120, 'text', lambda x, d, p: x[1]),
                      ('Product', 1, 150, 'text', lambda x, d, p: x[2]),
                      ('Quantity', 1, 100, 'text', lambda x, d, p: x[3]),
                      ('Price Unit', 1, 100, 'text', lambda x, d, p: x[4]),
                      ('Customer', 1, 100, 'text', lambda x, d, p: x[5]),
                      ('Total Order', 1, 100, 'text', lambda x, d, p: x[6]),
                      ('Invoice', 1, 100, 'text', lambda x, d, p: x[7]),
                      ('Sisa', 1, 100, 'text', lambda x, d, p: x[8]),
                      ('Voucher', 1, 100, 'text', lambda x, d, p: x[9]),
                      ('Date', 1, 100, 'text', lambda x, d, p: x[10]),
                      ('Payment', 1, 100, 'text', lambda x, d, p: x[11]),
                      ('Setoran', 1, 100, 'text', lambda x, d, p: x[12]),
        ]
       
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        title = self.xls_row_template(cols_specs, ['Reference', 'Shop', 'Product', 'Quantity', 'Price Unit', 'Customer', 'Total Order', 'Invoice', 'Sisa', 'Voucher', 'Date', 'Payment', 'Setoran'])
        self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
        
        
        row_count = 1
        for x in data['csv']:
            ws.write(row_count, 0, x[0])
            ws.write(row_count, 1, x[1])
            ws.write(row_count, 2, str(x[2]))
            ws.write(row_count, 3, x[3])
            ws.write(row_count, 4, x[4])
            ws.write(row_count, 5, x[5])
            ws.write(row_count, 6, x[6])
            ws.write(row_count, 7, x[7])
            ws.write(row_count, 8, x[8])
            ws.write(row_count, 9, x[9])
            ws.write(row_count, 10, x[10])
            ws.write(row_count, 11, x[11])
            ws.write(row_count, 12, x[12])
            row_count += 1
            
        pass

shop_order_xls('report.wtc.shop.excel', 'sale.varian.report', 'addons/siu_report/report/sale_varian.rml', parser=ReportStatus, header=False)
