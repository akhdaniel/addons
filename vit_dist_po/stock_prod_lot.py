from openerp.osv import fields, osv
from datetime import timedelta, date, datetime
from openerp.tools.translate import _

class stock_production_lot(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'life_date'], context)
        # reads = self.read(cr, uid, ids, ['name', 'prefix', 'ref', 'life_date'], context)
        res = []
        for record in reads:
            name = record['name']
            # prefix = record['prefix']
            # if prefix:
            #     name = prefix + '/' + name
            # if record['ref']:
            #     name = '%s [%s]' % (name, record['ref'])
            if record['life_date']:
                name = '%s [E.D.: %s]' % (name, record['life_date'][:10])
            res.append((record['id'], name))
        return res

    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'
    _order = 'life_date'

    _columns = {
        'is_bad': fields.boolean('Is Bad?'),
        'reason': fields.char('Deskripsi/Alasan'),
        }

    def create(self, cr, uid, vals, context=None):
        if vals['life_date']:
            dat  =datetime.strptime(vals['life_date'], '%Y-%m-%d %H:%M:%S')-timedelta(days=3*365/12)
            datemin3 = dat.strftime('%Y-%m-%d %H:%M:%S')
            vals['use_date']=datemin3
            vals['removal_date']=datemin3
            vals['alert_date']=datemin3
        return super(stock_production_lot, self).create(cr, uid, vals, context=context)

stock_production_lot()


class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"
    _order = 'is_bad'

    _columns = {
        'is_bad': fields.boolean('Is Bad?'),
        'reason': fields.char('Alasan'),
        'barcode' : fields.related('product_id','barcode',type="char",relation="product.product",string="Barcode",store=True),
        'default_code' : fields.related('product_id','default_code',type="char",relation="product.product",string="Code",store=True),
    }

    _default = {
        'is_bad':False,
    }

class stock_move_split_lines_exist(osv.osv_memory):
    _inherit = "stock.move.split.lines"
    _name = "stock.move.split.lines"

    _columns = {
        'expire': fields.datetime('Expire Date'),
        'reason': fields.char('Alasan'),
        'is_bad': fields.boolean('Is Bad?'),
    }

    _default = {
        'is_bad':False,
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
                            'life_date': line.expire,
                            'is_bad':line.is_bad,
                            'reason':line.reason or ''},
                        context=context)

                    # is bad = True : move to bad stock
                    move_datas = {'prodlot_id': prodlot_id, 'state':move.state, 'is_bad':line.is_bad, 'reason':line.reason or ''}
                    if line.is_bad:
                        [bad_stock] = self.pool.get('stock.location').search(cr,uid,[('location_id','=',move.location_dest_id.location_id.id),('bad_location','=',True)],limit=1)
                        move_datas.update({'location_dest_id':bad_stock})
                    move_obj.write(cr, uid, [current_move], move_datas)

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        update_val['product_uos_qty'] = uos_qty_rest
                        update_val['state'] = move.state
                        # update_val['product_qty_nett'] = quantity_rest
                        move_obj.write(cr, uid, [move.id], update_val)

        return new_move

split_in_production_lot()

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

# class stock_partial_picking_line(osv.TransientModel):

#     _name = "stock.partial.picking.line"
#     _inherit = "stock.partial.picking.line"

# Enable jika ingin create serial no. pada wizard receiving (fungsi dan fields)
#     def on_change_ed(self, cr, uid, ids, ed_date,prodlot_id2,product_id, context=None):
#         if ed_date and product_id and prodlot_id2:
#             prod_lot = self.pool.get('stock.production.lot').create(cr,uid,{'name':prodlot_id2,'product_id':product_id,'life_date': ed_date}, context=context)
#             return {'value':{'prodlot_id':prod_lot}}
#         return True

#     _columns = {
#         'ed_date' : fields.datetime("Expire Date", required=False),
#         'prodlot_id2' : fields.char(string='Serial Number', size=64, required=False,),
#     }

# stock_partial_picking_line()

# class stock_partial_picking_line(osv.osv_memory):
#     _name = "stock.partial.picking.line"
#     _inherit = "stock.partial.picking.line"


# INI UDAH DIREPLACE SAMA product_fifo_lifo
#     def do_partial(self, cr, uid, ids, context=None):
#         assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
#         stock_picking = self.pool.get('stock.picking')
#         stock_move = self.pool.get('stock.move')
#         uom_obj = self.pool.get('product.uom')
#         partial = self.browse(cr, uid, ids[0], context=context)
#         partial_data = {
#             'delivery_date' : partial.date
#         }
#         picking_type = partial.picking_id.type
#         for wizard_line in partial.move_ids:
#             line_uom = wizard_line.product_uom
#             move_id = wizard_line.move_id.id

#             #Quantiny must be Positive
#             if wizard_line.quantity < 0:
#                 raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))

#             #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
#             qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

#             if line_uom.factor and line_uom.factor <> 0:
#                 if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
#                     raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
#             if move_id:
#                 #Check rounding Quantity.ex.
#                 #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
#                 #partial delivery: 253g
#                 #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
#                 initial_uom = wizard_line.move_id.product_uom
#                 #Compute the quantity for respective wizard_line in the initial uom
#                 qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
#                 without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
#                 if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
#                     raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
#             else:
#                 seq_obj_name =  'stock.picking.' + picking_type
#                 move_id = stock_move.create(cr,uid,{'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
#                                                     'product_id': wizard_line.product_id.id,
#                                                     'product_qty': wizard_line.quantity,
#                                                     'product_uom': wizard_line.product_uom.id,
#                                                     'prodlot_id': wizard_line.prodlot_id.id,
#                                                     'location_id' : wizard_line.location_id.id,
#                                                     'location_dest_id' : wizard_line.location_dest_id.id,
#                                                     'picking_id': partial.picking_id.id
#                                                     },context=context)
#                 stock_move.action_confirm(cr, uid, [move_id], context)
#             partial_data['move%s' % (move_id)] = {
#                 'product_id': wizard_line.product_id.id,
#                 'product_qty': wizard_line.quantity,
#                 'product_uom': wizard_line.product_uom.id,
#                 'prodlot_id': wizard_line.prodlot_id.id,
#             }
#             if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
#                 partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
#                                                                   product_currency=wizard_line.currency.id)
            
#             import pdb;pdb.set_trace()
#             self.pool.get('stock.production.lot').write(cr,uid,wizard_line.prodlot_id.id,{'life_date': ''}, context=context)
#         stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)
#         return {'type': 'ir.actions.act_window_close'}

# stock_partial_picking_line()
