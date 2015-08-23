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

from openerp.osv import fields, osv


class purchase_order_info(osv.osv_memory):

    _name = "purchase.order.info"
    _description = "Purchase Order Info"

    _columns = {
        'pr_line_id': fields.many2one('purchase.requisition.line', 'Purchase Requisition Line', readonly=True),
        'po_info_line': fields.one2many('purchase.order.info.line', 'po_info_id', 'Purchase Order Info Lines', readonly=True)
    }
    _defaults = {
        'pr_line_id': lambda self, cr, uid, ctx: ctx.get('active_id', False)
    }

    def onchange_pr_line_id(self, cr, uid, ids, pr_line_id, context=None):
        pr_line = self.pool.get('purchase.requisition.line').browse(cr, uid, pr_line_id)
        po_info_line = []
        for line in pr_line.po_line_ids:
            po_info_line.append([0, 0, {
                'order_id': line.order_id and line.order_id.id or False,
                'partner_id': line.partner_id and line.partner_id.id or False,
                'state': line.state,
                }])
        return {'value': {
            'po_info_line': po_info_line,
        }}

purchase_order_info()


class purchase_order_info_line(osv.osv_memory):

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    _name = "purchase.order.info.line"
    _description = "Purchase Order Info Lines"

    _columns = {
        'po_info_id': fields.many2one('purchase.order.info', 'Purchase Order Info'),
        'order_id': fields.many2one('purchase.order', 'Purchase Order'),
        'partner_id': fields.many2one('res.partner', 'Supplier'),
        'state': fields.selection(STATE_SELECTION, 'Status')
    }

purchase_order_info_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
