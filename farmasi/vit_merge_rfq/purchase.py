from openerp.tools.translate import _
from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)
from openerp.osv.orm import browse_record_list, browse_record, browse_null

class purchase_order(osv.osv):
    _inherit = "purchase.order"


    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'rfq.purchase.order', context=context) or '/'
        context = dict(context or {}, mail_create_nolog=True)
        order =  super(purchase_order, self).create(cr, uid, vals, context=context)
        self.message_post(cr, uid, [order], body=_("RFQ created"), context=context)
        return order


    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not any(line.state != 'cancel' for line in po.order_line):
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            if po.invoice_method == 'picking' and not any([l.product_id and l.product_id.type in ('product', 'consu') and l.state != 'cancel' for l in po.order_line]):
                raise osv.except_osv(
                    _('Error!'),
                    _("You cannot confirm a purchase order with Invoice Control Method 'Based on incoming shipments' that doesn't contain any stockable item."))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)        
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid,'name':self.pool.get('ir.sequence').get(cr, uid, 'purchase.order', context=context)})
        return True


    def _product_names(self, cr, uid, ids, field, arg, context=None):
        results = {}
        for po in self.browse(cr, uid, ids, context=context):
            product_names = []
            for line in po.order_line:
                product_names.append( "%s [%d %s]" % (line.product_id.name, line.product_qty, line.product_uom.name) )
            results[po.id] = ",".join(product_names)
        return results  

    _columns    = {
        'product_names' : fields.function(_product_names, type='char', string="Products",store=False),
    }



    def do_merge(self, cr, uid, ids, context=None):
        _logger.info('merge custom')
        # orders_info = super(purchase_order, self).do_merge(cr, uid, ids, context=context)
        # return orders_info


        """
        To merge similar type of purchase orders.
        Orders will only be merged if:
        * Purchase Orders are in draft
        * Purchase Orders belong to the same partner
        * Purchase Orders are have same stock location, same pricelist
        Lines will only be merged if:
        * Order lines are exactly the same except for the quantity and unit

         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: the ID or list of IDs
         @param context: A standard dictionary

         @return: new purchase order id

        """
        #TOFIX: merged order line should be unlink
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'account_analytic_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, browse_record_list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

        context = dict(context or {})

        # Compute what the new orders should contain
        new_orders = {}

        #import pdb; pdb.set_trace()
        order_lines_to_move = []
        for porder in [order for order in self.browse(cr, uid, ids, context=context) if order.state == 'draft']:
            order_key = make_key(porder, ('partner_id', 'location_id', 'pricelist_id'))
            new_order = new_orders.setdefault(order_key, ({}, []))
            new_order[1].append(porder.id)
            order_infos = new_order[0]

            if not order_infos:
                order_infos.update({
                    'origin': porder.origin,
                    'date_order': porder.date_order,
                    'partner_id': porder.partner_id.id,
                    'dest_address_id': porder.dest_address_id.id,
                    'picking_type_id': porder.picking_type_id.id,
                    'location_id': porder.location_id.id,
                    'pricelist_id': porder.pricelist_id.id,
                    'state': 'draft',
                    'order_line': {},
                    'notes': '%s' % (porder.notes or '',),
                    'fiscal_position': porder.fiscal_position and porder.fiscal_position.id or False,
                    'requisition_id': porder.requisition_id.id,

                })
            else:
                if porder.date_order < order_infos['date_order']:
                    order_infos['date_order'] = porder.date_order
                if porder.notes:
                    order_infos['notes'] = (order_infos['notes'] or '') + ('\n%s' % (porder.notes,))
                if porder.origin:
                    order_infos['origin'] = (order_infos['origin'] or '') + ' ' + porder.origin

            for order_line in porder.order_line:
                order_lines_to_move += [order_line.id]

        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.iteritems():
            # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            for key, value in order_data['order_line'].iteritems():
                del value['uom_factor']
                value.update(dict(key))
            order_data['order_line'] = [(6, 0, order_lines_to_move)]

            # create the new order
            context.update({'mail_create_nolog': True})
            neworder_id = self.create(cr, uid, order_data)
            self.message_post(cr, uid, [neworder_id], body=_("RFQ created"), context=context)
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)

            # make triggers pointing to the old orders point to the new order
            for old_id in old_ids:
                self.redirect_workflow(cr, uid, [(old_id, neworder_id)])
                self.signal_workflow(cr, uid, [old_id], 'purchase_cancel')

        return orders_info


purchase_order()
