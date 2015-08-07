from openerp.osv import fields, osv

class mrp_product_produce(osv.osv_memory):
    _inherit = "mrp.product.produce"

    _columns = {
        'lot_str': fields.char('Lot'),
        }

    def _get_lot_sn(self, cr, uid, context=None):
        """ To obtain MO SN
        @return: prod_lot
        """
        if context is None:
            context = {}
        prod = self.pool.get('mrp.production').browse(cr, uid,
                                context.get('active_id', False), context=context)
        sn = prod.serialno
        if not sn:
            sn = self.pool.get('ir.sequence').get(cr, uid, 'lot.sn.seq', context=None) 
        return sn

    def do_produce(self, cr, uid, ids, context=None):
        """ To create and add prod_lot in moves
        @param ids: The wizard id 
        @return: Execute production with current MO's lot_id
        """
        production_id = context.get('active_id', False)
        assert production_id, "Production Id should be specified in context as a Active ID."
        data = self.browse(cr, uid, ids[0], context=context)
        lot_id = self.pool.get('stock.production.lot').create(cr,uid,{'name':data.lot_str,'product_id':data.product_id.id})
        self.write(cr,uid,ids,{'lot_id':lot_id})
        self.pool.get('mrp.production').action_produce(cr, uid, production_id,
                            data.product_qty, data.mode, data, context=context)
        return {}

    _defaults = {
         'lot_str': _get_lot_sn,
    }
