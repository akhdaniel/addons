# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
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


import openerp.netsvc
from openerp.osv import osv, fields
from openerp.tools.translate import _


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def _get_requistion(self, cr, uid, ids, context=None):
        orders = self.browse(cr, uid, ids, context=context)
        pr_ids = []
        for order in orders:
            for order_line in order.order_line:
                for pr_line in order_line.pr_line_ids:
                    pr_ids.append(pr_line.requisition_id.id)
        return pr_ids

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)

        pr_ids = self._get_requistion(cr, uid, ids, context)
        self.pool.get('purchase.requisition').update_done(cr, uid, pr_ids, context=context)
        return res

    def action_cancel_draft(self, cr, uid, ids, context=None):
        po_line = self.pool.get('purchase.order.line')
        super(purchase_order, self).action_cancel_draft(cr, uid, ids, context)
        line_ids = po_line.search(cr, uid, [('order_id', 'in', ids)])
        po_line.write(cr, uid, line_ids, {'state': 'draft'})
        return True

    def purchase_cancel(self, cr, uid, ids, context=None):
        po_line = self.pool.get('purchase.order.line')

        self.write(cr, uid, ids, {'state': 'cancel'})
        line_ids = po_line.search(cr, uid, [('order_id', 'in', ids)])
        po_line.write(cr, uid, line_ids, {'state': 'cancel'})

        pr_ids = self._get_requistion(cr, uid, ids, context)
        self.pool.get('purchase.requisition').update_done(cr, uid, pr_ids, context=context)

        return True

    def do_merge(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).do_merge(cr, uid, ids, context)
        po_line = self.pool.get('purchase.order.line')

        for key, value in res.iteritems():
            line_ids = po_line.search(cr, uid, [('order_id', '=', key)])
            for line_id in po_line.browse(cr, uid, line_ids, context=context):
                old_line_ids = po_line.search(cr, uid, [('order_id', 'in', value), ('product_id', '=', line_id.product_id.id)])
                pr_line_ids = []
                for old_line in po_line.browse(cr, uid, old_line_ids, context=context):
                    pr_line_ids.extend([pr_id.id for pr_id in old_line.pr_line_ids])
                po_line.write(cr, uid, [line_id.id], {'pr_line_ids': [(6, 0, pr_line_ids)]})

        return res


class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    _columns = {
         'pr_line_ids': fields.many2many('purchase.requisition.line', 'pr_rel_po', 'po_id', 'pr_id', 'Purchase requisition Lines', ondelete='cascade' ),
    }