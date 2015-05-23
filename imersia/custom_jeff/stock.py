import time

from openerp.osv import fields
from openerp.osv import osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class StockMove(osv.osv):
    _inherit = 'stock.move'
    
    
        
    def _src_id_default(self, cr, uid, ids, context=None):
        try:
            location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'location_production')
            self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
        except (orm.except_orm, ValueError):
            location_id = False
        return location_id
    
    
    def _dest_id_default(self, cr, uid, ids, context=None):
        try:
            location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
            self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
        except (orm.except_orm, ValueError):
            location_id = False
        return location_id

    _columns = {
        'custom_production_id': fields.many2one('mrp.production.custom', 'Production Order for Produced Products', select=True, copy=False),
#        'waste_qty':fields.float('Waste (%)')
#       'raw_material_production_id': fields.many2one('mrp.production', 'Production Order for Raw Materials', select=True),
#        'consumed_for': fields.many2one('stock.move', 'Consumed for', help='Technical field used to make the traceability of produced products'),
    }
    
    def action_consume_custom(self, cr, uid, ids, product_qty, location_id=False, restrict_lot_id=False, restrict_partner_id=False,
                       consumed_for=False, context=None):
        """ Consumed product with specific quantity from specific source location.
        @param product_qty: Consumed/produced product quantity (= in quantity of UoM of product)
        @param location_id: Source location
        @param restrict_lot_id: optionnal parameter that allows to restrict the choice of quants on this specific lot
        @param restrict_partner_id: optionnal parameter that allows to restrict the choice of quants to this specific partner
        @param consumed_for: optionnal parameter given to this function to make the link between raw material consumed and produced product, for a better traceability
        @return: New lines created if not everything was consumed for this line
        """
        if context is None:
            context = {}
        res = []
        production_obj = self.pool.get('mrp.production.custom')

        if product_qty <= 0:
            raise osv.except_osv(_('Warning!'), _('Please provide proper quantity.'))
        #because of the action_confirm that can create extra moves in case of phantom bom, we need to make 2 loops
        ids2 = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state == 'draft':
                ids2.extend(self.action_confirm(cr, uid, [move.id], context=context))
            else:
                ids2.append(move.id)

        prod_orders = set()
        for move in self.browse(cr, uid, ids2, context=context):
            prod_orders.add(move.custom_production_id.id)
            print"Total Qty>>>",product_qty
            move_qty = product_qty
            if move_qty <= 0.00:
                raise osv.except_osv(_('Error!'), _('Cannot consume a move with negative or zero quantity.'))
            
            quantity_rest = move_qty - product_qty
            print"Rest Qty>>>",quantity_rest
            # Compare with numbers of move uom as we want to avoid a split with 0 qty
            quantity_rest_uom = move.product_uom_qty - self.pool.get("product.uom")._compute_qty_obj(cr, uid, move.product_id.uom_id, product_qty, move.product_uom)
            if float_compare(quantity_rest_uom, 0, precision_rounding=move.product_uom.rounding) != 0:
                new_mov = self.split(cr, uid, move, quantity_rest, context=context)
                print"New Move>>>",new_mov
                res.append(new_mov)
            vals = {'restrict_lot_id': restrict_lot_id,
                    'restrict_partner_id': restrict_partner_id,
                    'consumed_for': consumed_for}
            if location_id:
                vals.update({'location_id': location_id})
            self.write(cr, uid, [move.id], vals, context=context)
        # Original moves will be the quantities consumed, so they need to be done
        self.action_done(cr, uid, ids2, context=context)
        if res:
            self.action_assign(cr, uid, res, context=context)
        if prod_orders:
            
            production_obj.action_in_production(cr, uid, list(prod_orders), context=None)
            #production_obj.signal_workflow(cr, uid, list(prod_orders), 'button_produce')
        return res
    
    
    
    _defaults = {
        'location_id': _src_id_default,
        'location_dest_id': _dest_id_default
    }