from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class stock_summary(osv.osv):
    _name    = "vit.stock_summary"
    _inherit = "vit.stock_summary"

    def action_calculate(self, cr, uid, ids, context=None):
        super(stock_summary, self).action_calculate(cr, uid, ids, context=context)

        qobj = self.pool.get('stock.quant')
        for sc in self.browse(cr, uid, ids, context=context):
            for line in sc.line_ids:
                qty = 0.0
                lot_id = line.lot_id.id if line.lot_id else False
                product_id = line.product_id.id
                qids = qobj.search(cr,uid,[
                    ('location_id.complete_name','=','Physical Locations / GBA / Input'),
                    ('lot_id','=',lot_id),
                    ('qty','>',0),
                    ('product_id','=',product_id)],context=context)

                # if line.product_id.default_code == 'AGS0020101':
                #     print 'ok'

                for q in qobj.read(cr,uid,qids):
                    qty += q['qty']

                lot_id = "=%s" % (line.lot_id.id) if line.lot_id else "is null"
                sql = "update vit_stock_summary_line set qty_input = %s where product_id=%s and lot_id %s" % (qty,product_id, lot_id)
                cr.execute(sql)

                sql = "update vit_stock_summary_line set qty_total = qty_balance + qty_input where product_id=%s and lot_id %s" % (
                product_id, lot_id)
                cr.execute(sql)

        return




class stock_summary_line(osv.osv):
    _name 		= "vit.stock_summary_line"
    _inherit 	= "vit.stock_summary_line"

    _columns = {
        'qty_input' : fields.float("Qty Karantina"),
        'qty_total' : fields.float("Total"),
    }
