from openerp.osv import fields,osv
from openerp import tools
import itertools

class stock_moves_summary(osv.osv):
    _name = "stock.moves.summary"
    
    _columns = {
        'pick_in_id' : fields.many2one('stock.picking.in',"Picking",ondelete='cascade'),
        'product_qty' : fields.float("Good Quantity"),
        'bad_product_qty' : fields.float("Bad Quantity"),
        'product_id' : fields.many2one('product.product',"Products"),
        'barcode' : fields.related('product_id','barcode',type="char",relation="product.product",string="Barcode",store=True),
        'default_code' : fields.related('product_id','default_code',type="char",relation="product.product",string="Code",store=True),
    }

stock_moves_summary()

class stock_picking_in(osv.osv):
    _name = "stock.picking.in"
    _inherit = "stock.picking.in"

    _columns = {
        'move_summary_ids' : fields.one2many('stock.moves.summary','pick_in_id',"Stock move(s)"),
    }

    def query_summarize_stock_move(self,cr, uid,ids, context=None): 
        inship =self.browse(cr,uid,ids,context)[0] 
        mids   =[]
        sum_move=[];data=[]
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
                            AND is_bad is null or is_bad = false
                        GROUP BY product_id
                        )
                ) as CUMUL
                GROUP BY product_id
                """)
            data = cr.fetchall()
            for x in data:
                sum_move.append((0,0,{'product_qty':int(x[0]),'bad_product_qty':int(x[1]),'product_id':x[2]}))
        if inship.move_summary_ids:
            self.pool.get('stock.moves.summary').unlink(cr, uid, [x.id for x in inship.move_summary_ids], context=None)
        self.write(cr,uid,ids[0],{'move_summary_ids':sum_move})
        return True

    def summarize_stock_move(self,cr, uid,ids, context=None): 
        inship =self.browse(cr,uid,ids,context)[0] 
        sum_move=[];data=[];li=[]
        if inship.move_lines:
            for l in sorted(inship.move_lines, key=lambda sku_order: (sku_order.product_id.id,sku_order.is_bad), reverse=False):
                li.append({'product_id':l.product_id.id,'product_qty':l.product_qty,'is_bad':l.is_bad})
            for key, group in itertools.groupby(li, lambda item: (item["product_id"],item['is_bad'])):
                data.append({
                    'product_id':key[0],
                    'product_qty':not key[1] and sum([item['product_qty'] for item in group]) ,
                    'bad_product_qty':key[1] and sum([item['product_qty'] for item in group]) ,
                    })
            for dat in data:
                sum_move.append((0,0,{
                    'product_qty':dat['product_qty'],
                    'bad_product_qty':dat['bad_product_qty'],
                    'product_id':dat['product_id']
                    }))
        if inship.move_summary_ids:
            self.pool.get('stock.moves.summary').unlink(cr, uid, [x.id for x in inship.move_summary_ids], context=None)
        self.write(cr,uid,ids[0],{'move_summary_ids':sum_move})
        return True

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    _columns = {
        'move_summary_ids' : fields.one2many('stock.moves.summary','pick_in_id',"Stock move(s)"),
    }