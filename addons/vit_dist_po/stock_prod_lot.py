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

# class stock_partial_picking_line(osv.TransientModel):
#     _name = "stock.partial.picking.line"
#     _inherit = "stock.partial.picking.line"

#     # def onchange_prodlot_id(self, cr, uid, ids, prodlot_id, context=None):
#     #     datex = self.pool.get('stock.production.lot').browse(cr,uid,prodlot_id,).life_date or False
#     #     return {'value': {'expired': datex}}

#     _columns = {
#         'expired': fields.datetime('Expire Date'),
#         }

#     # def _get_prodlot_lifetime(self, cr, uid, ids, context=None):  
#     #     import pdb;pdb.set_trace()
#     #     if context is None:
#     #         context = {}
#     #     prodlot_obj = self.pool.get('stock.production.lot').browse(cr,uid,prodlot_id.id,)
#     #     if not prodlot_obj:
#     #         return {}
#     #     lifedate = prodlot_obj.life_date
#     #     return lifedate

#     # _default =  {
#     #     'expired' : _get_prodlot_lifetime
#     # }

# stock_partial_picking_line()

class stock_move_split_lines_exist(osv.osv_memory):
    _inherit = "stock.move.split.lines"
    _name = "stock.move.split.lines"
    #TODO:MOVE TO WIZARD

    _columns = {
        'expire': fields.datetime('Expire Date'),
        }

stock_move_split_lines_exist()

class split_in_production_lot(osv.osv_memory):
    _name = "stock.move.split"
    _inherit = "stock.move.split"

    def split(self, cr, uid, ids, move_ids, context=None):
        """ To split stock moves into serial numbers

        :param move_ids: the ID or list of IDs of stock move we want to split
        """
        if context is None:
            context = {}
        assert context.get('active_model') == 'stock.move',\
             'Incorrect use of the stock move split wizard'
        inventory_id = context.get('inventory_id', False)
        prodlot_obj = self.pool.get('stock.production.lot')
        inventory_obj = self.pool.get('stock.inventory')
        move_obj = self.pool.get('stock.move')
        new_move = []
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                move_qty = move.product_qty
                quantity_rest = move.product_qty
                uos_qty_rest = move.product_uos_qty
                new_move = []
                if data.use_exist:
                    lines = [l for l in data.line_exist_ids if l]
                else:
                    lines = [l for l in data.line_ids if l]
                total_move_qty = 0.0
                for line in lines:
                    quantity = line.quantity
                    total_move_qty += quantity
                    if total_move_qty > move_qty:
                        raise osv.except_osv(_('Processing Error!'), _('Serial number quantity %d of %s is larger than available quantity (%d)!') \
                                % (total_move_qty, move.product_id.name, move_qty))
                    if quantity <= 0 or move_qty == 0:
                        continue
                    quantity_rest -= quantity
                    uos_qty = quantity / move_qty * move.product_uos_qty
                    uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
                    if quantity_rest < 0:
                        quantity_rest = quantity
                        self.pool.get('stock.move').log(cr, uid, move.id, _('Unable to assign all lots to this move!'))
                        return False
                    default_val = {
                        'product_qty': quantity,
                        'product_uos_qty': uos_qty,
                        'state': move.state
                    }
                    if quantity_rest > 0:
                        current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
                        if inventory_id and current_move:
                            inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)
                        new_move.append(current_move)

                    if quantity_rest == 0:
                        current_move = move.id
                    prodlot_id = False
                    if data.use_exist:
                        prodlot_id = line.prodlot_id.id
                    if not prodlot_id:
                        prodlot_id = prodlot_obj.create(cr, uid, {
                            'name': line.name,
                            'product_id': move.product_id.id,
                            'life_date': line.expire},
                        context=context)

                    move_obj.write(cr, uid, [current_move], {'prodlot_id': prodlot_id, 'state':move.state})

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        update_val['product_uos_qty'] = uos_qty_rest
                        update_val['state'] = move.state
                        move_obj.write(cr, uid, [move.id], update_val)

        return new_move

split_in_production_lot()