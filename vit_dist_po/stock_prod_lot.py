from openerp.osv import fields, osv

class stock_production_lot(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'prefix', 'ref', 'life_date'], context)
        res = []
        for record in reads:
            name = record['name']
            prefix = record['prefix']
            if prefix:
                name = prefix + '/' + name
            if record['ref']:
                name = '%s [%s]' % (name, record['ref'])
            if record['life_date']:
                name = '%s (ED: %s)' % (name, record['life_date'][:10])
            res.append((record['id'], name))
        return res

    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'
    _order = 'life_date'

stock_production_lot()

class stock_partial_picking_line(osv.TransientModel):
    _name = "stock.partial.picking.line"
    _inherit = "stock.partial.picking.line"

    def onchange_prodlot_id(self, cr, uid, ids, prodlot_id, context=None):
        datex = self.pool.get('stock.production.lot').browse(cr,uid,prodlot_id,).life_date or False
        return {'value': {'expired': datex}}

    _columns = {
        'expired': fields.date('Expire Date'),
        }

stock_partial_picking_line()

class stock_move_split_lines_exist(osv.osv_memory):
    _inherit = "stock.move.split.lines"
    _name = "stock.move.split.lines"
    #TODO:MOVE TO WIZARD

    _columns = {
        'expire': fields.date('Expire Date'),
        }

    def onchange_expire(self, cr, uid, ids, name, expire, context=None):
        # import pdb;pdb.set_trace()
        return True

stock_move_split_lines_exist()