from openerp.osv import fields,osv
from openerp import tools

class stock_moves_summary(osv.osv):
    _name = "stock.moves.summary"
    
    _columns = {
        'pick_in_id' : fields.many2one('stock.picking.in',"Picking",ondelete='cascade'),
        'product_qty' : fields.float("Qty Gudang"),
        'bad_product_qty' : fields.float("Loss"),
        'product_id' : fields.many2one('product.product',"Products"),
        'barcode' : fields.related('product_id','barcode',type="char",relation="product.product",string="Barcode",store=True),
        'default_code' : fields.related('product_id','default_code',type="char",relation="product.product",string="Code",store=True),
        'po_qty': fields.float("Qty DO"),
        'office_qty': fields.float("Qty Office",required=True),
        'gap_qty' : fields.float("Gap"),
    }

    def onchange_office_qty(self, cr, uid, ids, po_qty, product_qty, office_qty, context=None):
        do = product_qty or 0.00
        of = office_qty or 0.00
        self.write(cr,uid,ids,{'gap_qty':of-do})
        return {'value':{'gap_qty':of-do}}

stock_moves_summary()

class stock_moves_loss_summary(osv.osv):
    _name = "stock.moves.loss.summary"
    _order = 'product_id'
    
    _columns = {
        'pick_in_id' : fields.many2one('stock.picking.in',"Picking",ondelete='cascade'),
        'bad_product_qty' : fields.float("Loss"),
        'product_id' : fields.many2one('product.product',"Products"),
        'barcode' : fields.related('product_id','barcode',type="char",relation="product.product",string="Barcode",store=True),
        'default_code' : fields.related('product_id','default_code',type="char",relation="product.product",string="Code",store=True),
        'reason': fields.char('Alasan'),
    }

stock_moves_loss_summary()

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    _columns = {
        'move_summary_ids' : fields.one2many('stock.moves.summary','pick_in_id',"Stock move(s)"),
        'move_loss_summary_ids' : fields.one2many('stock.moves.loss.summary','pick_in_id',"Stock move(s) Loss"),
    }

class stock_picking_in(osv.osv):
    _name = "stock.picking.in"
    _inherit = "stock.picking.in"

    _columns = {
        'move_summary_ids' : fields.one2many('stock.moves.summary','pick_in_id',"Stock move(s)"),
        'move_loss_summary_ids' : fields.one2many('stock.moves.loss.summary','pick_in_id',"Stock move(s) Loss"),
        'state': fields.selection(
            [('draft', 'Draft'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('in2logistik', 'Ready to Receive'),     
            ('assigned', 'Ready to Confirm'),
            ('2binvoiced', 'Ready to Approve'),
            ('done', 'Received'),
            ('cancel', 'Cancelled'),],
            'Status', readonly=True, select=True,
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Receive: products reserved, waiting for confirmation in logistics.\n
                 * Ready to Confirm: products confirmed in warehouse, waiting for confirmation in office logistics.\n
                 * Ready to Approve: products confirmed in warehouse, noted, waiting for confirmation in Accounting.\n
                 * Received: has been processed, can't be modified or cancelled anymore\n
                 * Cancelled: has been cancelled, can't be confirmed anymore"""),
    }

    def query_summarize_stock_move(self,cr, uid,ids, context=None): 
        inship =self.browse(cr,uid,ids,context)[0] 
        mids   =[]
        sum_move=[];sum_loss=[];data=[]
        if inship.move_lines:
            mids    =[x.id for x in inship.move_lines]
            mids    =str(mids)[1:-1]
            cr.execute("""
                SELECT 
                    SUM(product_qty) as product_qty, 
                    SUM(bad_qty) as bad_qty,
                    product_id
                FROM (
                    SELECT product_qty, bad_qty, product_id FROM(
                        SELECT 
                            0 as product_qty,
                            SUM(product_qty) as bad_qty,
                            product_id 
                        FROM stock_move 
                        WHERE 
                            id in ("""+mids+""")
                            AND picking_id = """+str(ids[0])+"""
                            AND is_bad = true
                        GROUP BY product_id) A
                        union all (
                        SELECT 
                            SUM(product_qty) as product_qty,
                            0 as bad_qty,
                            product_id
                        FROM stock_move 
                        WHERE 
                            id in ("""+mids+""")
                            AND picking_id = """+str(ids[0])+"""
                            AND (is_bad is null or is_bad = false)
                        GROUP BY product_id
                        )
                ) as CUMUL
                GROUP BY product_id
                """)
            data = cr.fetchall()
            po_line = str([l.id for l in inship.purchase_id.order_line])[1:-1]
            cr.execute("SELECT SUM(product_qty) qty,product_id from purchase_order_line where id in ("+po_line+") group by product_id")
            po = cr.fetchall()
            for x in data:
                po_qty = 0.00
                for p in po:
                    if p[1]==x[2] : po_qty = p[0]
                sum_move.append((0,0,{'product_qty':int(x[0]),'bad_product_qty':int(x[1]),'product_id':x[2] or False, 'po_qty':po_qty, 'office_qty':int(x[0]) }))
            cr.execute("""
                        SELECT 
                            product_qty,
                            product_id,
                            reason
                        FROM stock_move 
                        WHERE 
                            id in ("""+mids+""")
                            AND picking_id = """+str(ids[0])+"""
                            AND is_bad = true
                """)
            data2 = cr.fetchall()
            # grouping by product_id
            #                 SUM(product_qty) as bad_qty,
            #             GROUP BY product_id,reason
            for x in data2:
                sum_loss.append((0,0,{'reason':x[2] or '', 'bad_product_qty':int(x[0]),'product_id':x[1]}))
            
        if inship.move_summary_ids:
            self.pool.get('stock.moves.summary').unlink(cr, uid, [x.id for x in inship.move_summary_ids], context=None)
        if inship.move_loss_summary_ids:
            self.pool.get('stock.moves.loss.summary').unlink(cr, uid, [x.id for x in inship.move_loss_summary_ids], context=None)
        self.write(cr,uid,ids[0],{'move_summary_ids':sum_move,'move_loss_summary_ids':sum_loss})
        return True

    # def summarize_stock_move(self,cr, uid,ids, context=None): 
    #     inship =self.browse(cr,uid,ids,context)[0] 
    #     sum_move=[];data=[];li=[]
    #     import itertools
    #     if inship.move_lines:
    #         for l in sorted(inship.move_lines, key=lambda sku_order: (sku_order.product_id.id,sku_order.is_bad), reverse=False):
    #             li.append({'product_id':l.product_id.id,'product_qty':l.product_qty,'is_bad':l.is_bad})
    #         for key, group in itertools.groupby(li, lambda item: (item["product_id"],item['is_bad'])):
    #             data.append({
    #                 'product_id':key[0],
    #                 'product_qty':not key[1] and sum([item['product_qty'] for item in group]) ,
    #                 'bad_product_qty':key[1] and sum([item['product_qty'] for item in group]) ,
    #                 })
    #         for dat in data:
    #             sum_move.append((0,0,{
    #                 'product_qty':dat['product_qty'],
    #                 'bad_product_qty':dat['bad_product_qty'],
    #                 'product_id':dat['product_id']
    #                 }))
    #     if inship.move_summary_ids:
    #         self.pool.get('stock.moves.summary').unlink(cr, uid, [x.id for x in inship.move_summary_ids], context=None)
    #     self.write(cr,uid,ids[0],{'move_summary_ids':sum_move})
    #     return True