from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.osv import fields, osv


class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"


    def sum_qty_quant(self, cr, uid, ids, location_id, context = None):
        sql = """select sum(qty) from stock_quant WHERE location_id =' %s'"""%(location_id)
        cr.execute(sql)
        qty = cr.fetchone()
        qty = qty[0]
        return qty

    def action_confirm(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            if move.location_dest_id.id in self.loc_dest_id_rack(cr,uid,ids,context):
                """ Check Isi Rack """
                qty_loc = self.sum_qty_quant(cr,uid,ids, move.location_dest_id.id, context)
                if qty_loc > 0:
                    raise osv.except_osv( 'Peringatan!' , 'Lokasi Destinasi Sudah Terisi Lakukan Edit Ulang Pilih Gudang Rak Yang Available')
 
        res = super(stock_move, self).action_confirm(cr, uid, ids, context=context)
        return res

    def loc_dest_id_rack (self, cr, uid, ids, context=None):
        loc_ids = self.pool.get('stock.location').search(cr, uid, [('name', 'ilike', 'rak')])
        return loc_ids

