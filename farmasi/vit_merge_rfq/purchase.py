from openerp.tools.translate import _
from openerp.osv import fields, osv


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

purchase_order()