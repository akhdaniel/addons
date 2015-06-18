import re
import csv
import base64
import calendar
import time
import datetime
from openerp.osv import fields, osv
 


class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
        'shop_id': fields.many2one('wtc.shop', 'Shop'),
        'jenis': fields.selection((('db','Debit Card'), ('cr','Credit Card'), ('cash','Cash'), ('transfer','Transfer')), 'Jenis Pembayaran'), 
    }


class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _columns = {
        'setor': fields.boolean('Sudah Setoran ?'),
    }


class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
        'setor': fields.boolean('Sudah Setoran ?'),
        'setor_date' : fields.date('Setoran Date', readonly=True),
    }
    
    def setor(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        self.write(cr, uid, ids, {'setor': True, 'setor_date': time.strftime('%Y-%m-%d')}, context=context)
        for x in val.move_ids:
            self.pool.get('account.move.line').write(cr, uid, x.id, {'setor': True})
        return True

    def onchange_backdate(self, cr, uid, ids, date):
        if date:
            if date < str(datetime.date.today()):
                value = {'date': str(datetime.date.today())}
                warning = {'title': ('Perhatian !'), 'message' : ('Tanggal Minimal Hari Ini')}
                return {'value': value, 'warning': warning}
        return True

    def payment_batal(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        obj_move_line = self.pool.get('account.move.line')
        obj_voucher_line = self.pool.get('account.voucher.line')
        
        for x in val.move_ids:
            obj_move_line.write(cr, uid, [x.id], {'state': 'draft', 'reconcile_id': False, 'reconcile_partial_id': False})
            obj_move_line.unlink(cr, uid, [x.id])
        
        for x in val.line_ids:
            obj_voucher_line.unlink(cr, uid, [x.id])
        
        self.write(cr, uid, [val.id], {'state': 'draft'})
        self.unlink(cr, uid, [val.id])


class SaleReport(osv.osv_memory):
    _name = "sale.varian.report"
    _columns = {
                'name': fields.selection((('shop','Shop Excel'), ('shopdf','Shop PDF'), ('stock','Real Stock')), 'Filter by', required=True),
                'dari' : fields.date('Tanggal', required=True),
                'shop_id':fields.many2one('wtc.shop', 'Shop', required=True),
                'opname_id':fields.many2one('stock.inventory', 'Stock Opname'),
    }
        
    _defaults = {
        'name': 'shopdf',
        'dari': time.strftime('%Y-%m-%d'),
    }
    

    def onchange_backdate(self, cr, uid, ids, date):
        if date:
            if uid != 1:
                if date != str(datetime.date.today()):
                    value = {'dari': str(datetime.date.today())}
                    warning = {'title': ('Perhatian !'), 'message' : ('Tanggal harus sesuai dengan hari ini')}
                    return {'value': value, 'warning': warning}
        return True

    def print_report(self, cr, uid, ids, context=None):
        o = self.browse(cr, uid, ids)[0]
        if context is None:
            context = {}
        
        csv = []
        debit = 0.0; credit = 0.0; cash = 0.0; transfer = 0.0
        
        obj_product = self.pool.get('product.product')
        obj_invoice = self.pool.get('account.invoice')
        obj_order = self.pool.get('sale.order')
        obj_order_line = self.pool.get('sale.order.line')
        obj_pos = self.pool.get('pos.order')
        obj_pos_line = self.pool.get('pos.order.line')
        obj_picking = self.pool.get('stock.picking')
        obj_stock_move = self.pool.get('stock.move')
        obj_move = self.pool.get('stock.order')
        obj_move_line = self.pool.get('account.move.line')
            
        if o.name == 'stock' :
            out = False; inn = False
            no = 0
            for x in o.opname_id.inventory_line_id:
                no += 1
                out = obj_stock_move.search(cr, uid, [
                                                     ('product_id', '=', x.product_id.id),
                                                     ('location_id', '=', o.shop_id.warehouse_id.lot_stock_id.id), 
                                                     ('date', '>=', o.opname_id.date), 
                                                     ('date', '<=', o.dari), 
                                                     ('state', '=', 'done'),
                                                     ('name', 'ilike', 'INV')
                                                     ])
                inn = obj_stock_move.search(cr, uid, [
                                                     ('product_id', '=', x.product_id.id),
                                                     ('location_dest_id', '=', o.shop_id.warehouse_id.lot_stock_id.id), 
                                                     ('date', '>=', o.opname_id.date), 
                                                     ('date', '<=', o.dari), 
                                                     ('state', '=', 'done'),
                                                     ('name', 'ilike', 'INV')
                                                     ])
                
                masuk = sum([x.product_qty for x in obj_stock_move.browse(cr, uid, inn)]) 
                keluar = sum([x.product_qty for x in obj_stock_move.browse(cr, uid, out)])
                total = x.product_qty + masuk - keluar
                 
                csv.append([no, x.product_id.partner_ref, x.product_qty, masuk, keluar, total])
                    
    
        elif o.name == 'shop' or o.name == 'shopdf' :
            pid = obj_pos.search(cr, uid, [('shop_id', '=', o.shop_id.id), ('date_order', '>=', o.dari), ('date_order', '<=', o.dari), ('state', 'not in', ('draft', 'cancel'))])
            pad = obj_pos_line.search(cr, uid, [('order_id','in', pid)])
            sid = obj_order.search(cr, uid, [('shop_id', '=', o.shop_id.id), ('date_order', '>=', o.dari), ('date_order', '<=', o.dari), ('state', 'not in', ('draft', 'cancel', 'shipping_except', 'invoice_except'))])
            
            back = datetime.datetime.strptime(o.dari,'%Y-%m-%d') - datetime.timedelta(days=30)
            bid = obj_order.search(cr, uid, [('shop_id', '=', o.shop_id.id), ('date_order', '>=', str(back)), ('date_order', '<', o.dari), ('state', 'not in', ('draft', 'cancel', 'shipping_except', 'invoice_except'))])
            origin =  [x.name for x in obj_order.browse(cr, uid, bid)]
            yid = obj_invoice.search(cr, uid, [('origin', 'in', origin), ('state', '!=', 'draft')])
            number = [x.number for x in obj_invoice.browse(cr, uid, yid)]
            nid = obj_move_line.search(cr, uid, [('name', 'in', number), ('date', '>=', o.dari), ('date', '<=', o.dari)])
            
            
            if sid:
                amount_total = 0.0; tot_inv = 0.0; payment = 0.0
                for x in obj_order.browse(cr, uid, sid):
                    iid = obj_invoice.search(cr, uid, [('origin', '=', x.name), ('state', '!=', 'draft')])
                    
                    inv = '-'; sisa = 0.0
                    if iid:
                        iad = obj_invoice.browse(cr, uid, iid)[0]
                        inv = iad.number; sisa = iad.residual
                    else:
                        sisa = '-'
                    
                    amount_total += x.amount_total
                    csv.append([
                                x.name,
                                x.shop_id.name,
                                [i.product_id.partner_ref for i in x.order_line],
                                sum([i.product_uom_qty for i in x.order_line]),
                                '-',
                                x.partner_id.name, 
                                x.amount_total,
                                inv,
                                sisa,
                                '-', '-', '-', '-'
                    ])
                    
                    if iid:
                        for i in iad.payment_ids:
                            payment += i.credit
                            if i.journal_id.jenis == "db":
                                debit += i.credit
                            elif i.journal_id.jenis == "cr":
                                credit += i.credit 
                            elif i.journal_id.jenis == "cash":
                                cash += i.credit 
                            elif i.journal_id.jenis == "transfer":
                                transfer += i.credit
                            csv.append([
                                        '-', '-', '-', '-', '-', time.strftime('%d %B %Y', time.strptime(i.date,'%Y-%m-%d')), '-', '-', '-',
                                        i.ref, i.date, i.credit, i.setor
                            ])
                            
                
                if nid :
                    csv.append(['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'])
                    for i in obj_move_line.browse(cr, uid, nid):
                        so = '-'
                        cari = obj_invoice.search(cr, uid, [('number', '=', i.name)])
                        dpt = obj_invoice.browse(cr, uid, cari)
                        if dpt:
                            so = dpt[0].origin
            
                        payment += i.credit
                        if i.journal_id.jenis == "db":
                            debit += i.credit
                        elif i.journal_id.jenis == "cr":
                            credit += i.credit 
                        elif i.journal_id.jenis == "cash":
                            cash += i.credit 
                        elif i.journal_id.jenis == "transfer":
                            transfer += i.credit
                        csv.append([
                                    so, '-', 'Pelunasan Invoice ' + i.name, '-', '-', time.strftime('%d %B %Y', time.strptime(i.date,'%Y-%m-%d')), '-', '-', '-',
                                    i.ref, i.date, i.credit, i.setor
                        ])

                csv.append(['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'])
                csv.append([
                            'Total Sales Order',
                            '-',
                            '-',
                            '-',
                            '-',
                            '-', 
                            amount_total,
                            '-',
                            0.0,
                            '-', '-', payment, '-'
                ])
                csv.append(['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'])
                    
            if pad:
                pos = ''; outlet = '-'; cake = ''; harga = 0
                if o.name == 'shopdf':
                    for a in obj_pos.browse(cr, uid, pid):
                        for i in a.statement_ids: 
                            if i.journal_id.jenis == "db":
                                debit += i.amount
                            elif i.journal_id.jenis == "cr":
                                credit += i.amount 
                            elif i.journal_id.jenis == "cash":
                                cash += i.amount 
                            elif i.journal_id.jenis == "transfer":
                                transfer += i.amount
                             
                    for x in obj_pos_line.browse(cr, uid, pad):
                        pos = 'Rekapan POS'
                        outlet = x.order_id.shop_id.name
                        cake = 'Rekapan Product'
                        harga += x.price_subtotal
                        csv.append([
                                    x.order_id.name, 
                                    outlet,
                                    x.product_id.partner_ref,
                                    x.qty,
                                    '-', '-', '-', '-', '-', '-', '-', x.price_subtotal, '-'
                        ])
                         
                    csv.append([
                                pos,
                                outlet,
                                cake,
                                '-',
                                '-', '-', 0, '-', 0, '-', '-', harga, '-'
                        ])
                else: 
                    for x in obj_pos_line.browse(cr, uid, pad):
                        pos += x.order_id.name + '/'
                        outlet = x.order_id.shop_id.name
                        cake += x.product_id.partner_ref + '/'
                        harga += x.price_unit
                    csv.append([
                                pos, 
                                outlet,
                                cake,
                                '-',
                                harga,
                                '-', '-', '-', '-', '-', '-', '-', '-'
                    ])  

        
        data = self.read(cr, uid, ids)[0]
        datas = {'ids': [data['id']]}
        datas['model'] = 'sale.varian.report'
        datas['form'] = data
        datas['csv'] = csv
        datas['debit'] = debit
        datas['credit'] = credit
        datas['cash'] = cash
        datas['transfer'] = transfer
         
         
        title = 'sale.varian'
        if data['name'] == 'shop':
            title = 'wtc.shop.excel'
        elif data['name'] == 'shopdf':
            title = 'wtc.shop.pdf'
        elif data['name'] == 'stock':
            title = 'sale.stock.pdf'
         
         
        return {
            'type': 'ir.actions.report.xml',
            'report_name': title,
            'nodestroy': True,
            'datas': datas,
        }
        

class ManyReport(osv.osv_memory):
    _name = "many.report"
    _columns = {
                'date_from' : fields.date('From'),
                'data_eksport': fields.binary('File', readonly=True),
                'name': fields.char('File Name', 16),
                'location_src_id': fields.many2one('stock.location', 'Source'),
                'location_dest_id': fields.many2one('stock.location', 'Destination'),
                'report': fields.selection((('cp','Summary Payment'), ('rs','Rincian Setoran'), ('mo','Manufacture Order'), ('po','Purchase Order'), ('im','Internal Moves')), 'Report', required=True),
    }   
    
    _defaults = {
                'report': 'cp',
                'date_from': time.strftime('%Y-%m-%d')
    }   
        
    def eksport_excel(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0] 
        move_obj = self.pool.get('stock.move')
        voucher_obj = self.pool.get('account.voucher')
        picking_obj = self.pool.get('stock.picking')
        purchase_obj = self.pool.get('purchase.order')
        production_obj = self.pool.get('mrp.production')
        
        if val.report == 'im':
            title = 'internal.csv'
            data = 'sep=;\nInternal Moves;Date;Source;Destination;Product;Quantity;Price;Total'
            res = picking_obj.search(cr, uid, [('type', '=', 'internal'), ('state', '=', 'done'), ('date', '>=', val.date_from), ('date', '<=',  val.date_from)])
            if not res:
                raise osv.except_osv(('Perhatian'), ('Tidak ada mutasi stock pada lokasi terkait'))
            mid = move_obj.search(cr, uid, [('picking_id', 'in', res), ('location_id', '=', val.location_src_id.id), ('location_dest_id', '=', val.location_dest_id.id)])
            result = move_obj.browse(cr, uid, mid)
            for move in result:
                price = move.product_id.standard_price
                subtotal = move.product_qty * price
                d = [str(move.picking_id.name),
                     time.strftime('%d %B %Y', time.strptime(move.picking_id.date,'%Y-%m-%d %H:%M:%S')),
                     val.location_src_id.name,
                     val.location_dest_id.name,
                     move.product_id.partner_ref, 
                     str(move.product_qty).replace('.',','), 
                     str(price).replace('.',','), 
                     str(subtotal).replace('.',',')]
                data += '\n' + ';'.join(d)
             
        elif val.report == 'mo':
            title = 'manufacture.csv'
            data = 'sep=;\nManufacture Order;Date;Origin;Finish Goods;Quantity;Price;Total'
            fin = production_obj.search(cr, uid, [('state', '=', 'done'), ('date_planned', '>=', val.date_from), ('date_planned', '<=',  val.date_from)])
            if not fin:
                raise osv.except_osv(('Perhatian'), ('Tidak ada Manufacture Order pada tanggal terkait'))
            finish = production_obj.browse(cr, uid, fin) 
            for row in finish:
                price = row.product_id.standard_price
                subtotal = row.product_qty * price
                d = [row.name,
                     time.strftime('%d %B %Y', time.strptime(row.date_planned,'%Y-%m-%d %H:%M:%S')),
                     row.origin or '-',
                     row.product_id.partner_ref,
                     str(row.product_qty).replace('.',','),
                     str(price).replace('.',','),
                     str(subtotal).replace('.',',')]
                data += '\n' + ';'.join(d)
            
        elif val.report == 'po':
            title = 'purchase.csv'
            data = 'sep=;\nPurchase Order;Date;Supplier;Product;UoM;Quantity;Price;Total'
            pur = purchase_obj.search(cr, uid, [('state', 'not in', ('draft', 'except_picking', 'cancel')), ('date_order', '>=', val.date_from), ('date_order', '<=',  val.date_from)])
            if not pur:
                raise osv.except_osv(('Perhatian'), ('Tidak ada Purchase Order pada tanggal terkait'))
            purchase = purchase_obj.browse(cr, uid, pur)
            for x in purchase:
                for i in x.order_line:
                    d = [x.name,
                         time.strftime('%d %B %Y', time.strptime(x.date_order,'%Y-%m-%d')),
                         x.partner_id.name,
                         i.product_id.partner_ref,
                         i.product_uom.name,
                         str(i.product_qty).replace('.',','),
                         str(i.price_unit).replace('.',','),
                         str(i.price_subtotal).replace('.',',')]
                    data += '\n' + ';'.join(d)
             
        elif val.report == 'cp':

            data = self.read(cr, uid, ids)[0]
            datas = {'ids': [data['id']]}
            datas['model'] = 'many.report'
            datas['form'] = data
            title = 'rekap.setoran'
            
            return {
                'type': 'ir.actions.report.xml',
                'report_name': title,
                'nodestroy': True,
                'datas': datas,
            }

        elif val.report == 'rs':

            data = self.read(cr, uid, ids)[0]
            datas = {'ids': [data['id']]}
            datas['model'] = 'many.report'
            datas['form'] = data
            title = 'rincian.setoran'
            
            return {
                'type': 'ir.actions.report.xml',
                'report_name': title,
                'nodestroy': True,
                'datas': datas,
            }
             
                   
        out = base64.b64encode(data.encode('ascii',errors='ignore'))
        self.write(cr, uid, ids, {'data_eksport':out, 'name':title}, context=context)
        
        view_rec = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'siu_report', 'view_many_report')
        view_id = view_rec[1] or False
        
        return {
            'view_type': 'form',
            'view_id' : [view_id],
            'view_mode': 'form',
            'res_id': val.id, 
            'res_model': 'many.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }





class ConsolidateInvoice(osv.osv_memory):
    _name = "consolidate.invoice"
    _columns = {
                'name': fields.many2one('res.partner', 'Invoice Address'),
                'dari' : fields.date('Invoice From', required=True),
                'sampai' : fields.date('Invoice To', required=True),
                'partner_ids': fields.many2many('res.partner', 'partner_order_rel', 'partner_order_id', 'partner_id', 'Customer'),
    }
    
    
    _defaults = {
        'dari': time.strftime('%Y-%m-%d'),
        'sampai': time.strftime('%Y-%m-%d'),
    }
    
        
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {'ids': [data['id']]}
        datas['model'] = 'consolidate.invoice'
        datas['form'] = data
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'rekap.invoice',
            'nodestroy': True,
            'datas': datas,
        }


#             oid = obj_stock.search(cr, uid, [('shop_id', '=', o.shop_id.id), ('date', '>=', o.dari), ('date', '<=', o.dari), ('state', '!=', 'draft')])
#             mid = obj_stock_line.search(cr, uid, [('stock_id','in', oid)])
                      
            
#             if mid:
#                 for x in obj_stock_line.browse(cr, uid, mid):
#                     csv.append([
#                                 x.stock_id.name, 
#                                 x.stock_id.shop_id.name,
#                                 x.product_id.partner_ref,
#                                 x.product_qty, '-',
#                                 '-', '-', '-', '-', '-', '-', '-', '-'
#                     ])


#                         <group colspan="4" attrs="{'invisible':[('name','!=','rasa')]}">
#                             <field name="rasa"/>
#                         </group>
#                         <group colspan="4" attrs="{'invisible':[('name','!=','ukuran')]}">
#                             <field name="ukuran"/>
#                         </group>
#                         <group colspan="4" attrs="{'invisible':[('name','not in',('shop', 'shopdf'))]}">
#                             <field name="shop_id" attrs="{'required':[('name','in',('shop', 'shopdf'))]}"/>
#                         </group>
                        
#                 'ukuran': fields.selection((('25X25','25 x 25'), ('28X28','28 x 28'), ('30X30','30 x 30'), ('30X40','30 x 40'), 
#                                             ('40X40','40 x 40'), ('40X60','40 x 60'), ('50X50','50 x 50'), ('60X60','60 x 60'), 
#                                             ('80X80','80 x 80'), ('100X100','100 x 100')), 'Ukuran', required=True),
#                 'rasa': fields.selection((('LS','Lapis Surabaya'), ('BF','Black Forest'), ('CG','Chocolate Gateux'), 
#                                           ('BLUEBERRY','Blue Berry'), ('CAPPUCCINO','Cappuccino'), ('LEMON','Lemon'), ('MANGO','Mango'), 
#                                           ('MOCHA','Mocha'), ('ORANGE','Orange'), ('PANDAN','Pandan'), ('STRAWBERRY','Strawberry'), 
#                                           ('VANILLA','Vanilla'), ('TIRAMISU','Tiramisu'), ('all','All Variant')), 'Rasa', required=True),                        