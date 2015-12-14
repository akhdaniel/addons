# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv,fields
from openerp import workflow

class purchase_order_line(osv.Model):
    
    _inherit = 'purchase.order.line'

    _columns = {
        'origin': fields.char('Origin', size=1024),
        'production_lot_id': fields.many2one('stock.production.lot', 'Production Lot'),
        'customer_ref': fields.char('Customer reference', size=64),
        'origin_ref': fields.char('Origin', size=64),
    }

class purchase_order(osv.Model):
    
    _inherit = 'purchase.order'
    _order = "create_date desc"

    def action_picking_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        picking_id = False
        for order in self.browse(cr, uid, ids, context=context):
            loc_id = order.partner_id.property_stock_supplier.id,
            istate = 'none'
            if order.invoice_method == 'picking':
                istate = '2binvoiced'
            picking_id = picking_obj.create(cr, uid, {
                'origin': 'PO:%d:%s' % (order.id, order.name),
                'type': 'in',
                'address_id': order.dest_address_id.id or order.partner_id.id,
                'invoice_state': istate,
                'purchase_id': order.id,
            })
            for order_line in order.order_line:
                if not order_line.product_id:
                    continue
                if order_line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    dest = order.location_id.id
                    move_obj.create(cr, uid, {
                        'name': 'PO:' + order_line.name[:50],
                        'product_id': order_line.product_id.id,
                        'origin_ref': order.name,
                        'product_uos_qty': order_line.product_qty,
                        'product_uom': order_line.product_uom.id,
                        'date_planned': order_line.date_planned,
                        'location_id': loc_id,
                        'location_dest_id': dest,
                        'picking_id': picking_id,
                        'move_dest_id': order.location_id and order.location_id.id,
                        'state': 'assigned',
                        'prodlot_id': order_line.production_lot_id.id,
                        'customer_ref': order_line.customer_ref,
                        'purchase_line_id': order_line.id,
                    })
            purchase_order_dict = {
                'picking_ids': [(4, picking_id)]
            }
            self.write(cr, uid, [order.id], purchase_order_dict)
            workflow.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return picking_id

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        production_obj = self.pool.get('stock.production.lot')
        order_line_obj = self.pool.get('purchase.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            l_id = 0
            for line in order.order_line:
                if line.production_lot_id:
                    continue
                l_id += 1
                production_lot_dict = {
                    'product_id': line.product_id.id,
                    'name': line.order_id and (str(line.order_id.name)+'/Line'+str(l_id)) or False,
                }
                production_lot_id = production_obj.create(cr, uid, production_lot_dict )
                order_line_obj.write(cr, uid, [line.id], {'production_lot_id': production_lot_id})

        super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context)
        return True

    _defaults = {
        'invoice_method': lambda *a: 'picking',
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: