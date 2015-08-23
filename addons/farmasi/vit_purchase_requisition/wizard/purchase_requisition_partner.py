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

import time
from openerp.osv import fields, osv
from openerp.osv.orm import browse_record, browse_null
from openerp.tools.translate import _
from lxml import etree


class PowerDict(dict):
    # http://stackoverflow.com/a/3405143/190597 (gnibbler)
    def __init__(self, parent=None, key=None):
        self.parent = parent
        self.key = key

    def __missing__(self, key):
        self[key] = PowerDict(self, key)
        return self[key]

    def append(self, item):
        self.parent[self.key] = [item]

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        try:
            val.parent = self
            val.key = key
        except AttributeError:
            pass


class purchase_requisition_partner(osv.osv_memory):

    _inherit = 'purchase.requisition.partner'
    _columns = {
        'group_flag': fields.boolean(string='Grouping'),
        'overwrite': fields.boolean(string='Overwrite Supplier'),
        'all_supplier_flag': fields.boolean(string='Show All Suppliers'),
        'partner_id': fields.many2one('res.partner', 'Supplier', required=False, domain=[('supplier', '=', True)]),
    }
    _defaults = {
                 'all_supplier_flag': False,
    }

    #Overriding from purchase_requisition_partner Class
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}

        active_ids = context and context.get('active_ids', False)

        result = super(purchase_requisition_partner, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                            context=context, toolbar=toolbar, submenu=submenu)
        if not context:
            context = {}
        partner_ids = []
        if active_ids:
            for requisition in self.pool.get('purchase.requisition').browse(cr, uid, active_ids, context=context):
                for line in requisition.line_ids:
                    for partner in line.product_id.seller_ids:
                        partner_ids.append(partner.name.id)

            ttype = set(partner_ids)

            lv = list(ttype)
            if len(lv) > 0:
                doc = etree.XML(result['arch'])
                for node in doc.xpath("//form[@string='Purchase Requisition']/group/field[@name='partner_id']"):
                    #Set Domain color if QTY of product less than reorder point
                    node.set('domain', "[('id', 'in', [%s])]" % ','.join(str(x) for x in lv))

                result['arch'] = etree.tostring(doc)
        return result

    def onchange_related_flag(self, cr, uid, ids, all_supplier_flag, context=None):
        res = {}
        active_ids = context and context.get('active_ids', False)

        if not context:
            context = {}

        partner_ids = []
        if active_ids and not all_supplier_flag:
            for requisition in self.pool.get('purchase.requisition').browse(cr, uid, active_ids, context=context):
                for line in requisition.line_ids:
                    for partner in line.product_id.seller_ids:
                        partner_ids.append(partner.name.id)
            ttype = set(partner_ids)

            lv = list(ttype)
            if len(lv) > 0:
                res.update({'domain': {'partner_id': [('id', '=', lv)]}})
            else:
                res.update({'domain': {'partner_id': False}})
        else:
            res.update({'domain': {'partner_id': False}})
        return res

    def overwrite_onchange(self, cr, uid, ids, overwrite, context=None):
        res = {}
        return res

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(purchase_requisition_partner, self).view_init(cr, uid, fields_list, context=context)
        if not res:
            res = {}
        res.update({'domain': {'partner_id': [('id', '=', 1)]}})
        return res

    def _create_po(self, cr, uid, requisition, supplier_id, context=None):
        res_partner = self.pool.get('res.partner')
        purchase_order = self.pool.get('purchase.order')

        supplier = res_partner.browse(cr, uid, supplier_id, context=context)
        supplier_pricelist = supplier.property_product_pricelist_purchase or False
        location_id = requisition.warehouse_id.lot_input_id.id
        purchase_id = purchase_order.create(cr, uid, {
                    'origin': requisition.name,
                    'partner_id': supplier.id,
                    'pricelist_id': supplier_pricelist.id,
                    'location_id': location_id,
                    'company_id': requisition.company_id.id,
                    'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
                    'requisition_id': requisition.id,
                    'notes': requisition.description,
                    'warehouse_id': requisition.warehouse_id.id,
                    }, context=context)
        return purchase_id

    def _create_po_line(self, cr, uid, purchase_id, supplier_id, pr_line, context=None):
        purchase_requisition = self.pool.get('purchase.requisition')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')

        supplier = res_partner.browse(cr, uid, supplier_id, context=context)
        line = self.pool.get('purchase.requisition.line').browse(cr, uid, pr_line['pr_line_ids'][0], context=context)
        seller_price, qty, default_uom_po_id, date_planned = purchase_requisition._seller_details(cr, uid, line, supplier, context=context)
        val = {
            'order_id': purchase_id,
            'name': pr_line['partner_ref'],
            'product_qty': pr_line['product_qty'],
            'product_id': pr_line['product_id'],
            'product_uom': pr_line['product_uom'],
            'price_unit': seller_price,
            'date_planned': date_planned,
            'taxes_id': [(6, 0, pr_line['taxes_id'])],
            'pr_line_ids': [(6, False, pr_line['pr_line_ids'])],
        }
        purchase_order_line.create(cr, uid, val, context=context)
        return

    def _create_grouping_po(self, cr, uid, pr_grouping, context=None):

        purchase_requisition = self.pool.get('purchase.requisition')
        purchase_ids =[]
        for pr_id in pr_grouping:
            requisition = purchase_requisition.browse(cr, uid, pr_id, context=context)
            for partner_itm in pr_grouping[pr_id]:
                purchase_id = self._create_po(cr, uid, requisition, partner_itm, context)
                for product_itm in pr_grouping[pr_id][partner_itm]:
                    for uom_itm in pr_grouping[pr_id][partner_itm][product_itm]:
                        pr_line = pr_grouping[pr_id][partner_itm][product_itm][uom_itm]
                        pr_line.update({'product_id': product_itm, 'product_uom': uom_itm})
                        self._create_po_line(cr, uid, purchase_id, partner_itm, pr_line, context=None)
                purchase_ids.append(purchase_id)

        return purchase_ids

    def _create_po_per_line(self, cr, uid, pr_grouping, context=None):
        purchase_requisition = self.pool.get('purchase.requisition')
        purchase_ids = []
        for pr_id in pr_grouping:
            requisition = purchase_requisition.browse(cr, uid, pr_id, context=context)
            for partner_itm in pr_grouping[pr_id]:
                for product_itm in pr_grouping[pr_id][partner_itm]:
                    for uom_itm in pr_grouping[pr_id][partner_itm][product_itm]:
                        pr_line = pr_grouping[pr_id][partner_itm][product_itm][uom_itm]
                        pr_line.update({'product_id': product_itm, 'product_uom': uom_itm})
                        purchase_id = self._create_po(cr, uid, requisition, partner_itm, context)
                        self._create_po_line(cr, uid, purchase_id, partner_itm, pr_line, context=None)
                purchase_ids.append(purchase_id)
        return purchase_ids

    def _pr_grouping(self, cr, uid, pr_ids, supplier_id, context=None):
        res = PowerDict()
        product_uom = self.pool.get('product.uom')
        pr_data = self.pool.get('purchase.requisition').browse(cr, uid, pr_ids, context=context)
        fiscal_position = self.pool.get('account.fiscal.position')
        for rec in pr_data:
            for line in rec.line_ids:
                if line.selected_flag:
                    if supplier_id:
                        suppliers = self.pool.get('res.partner').browse(cr, uid, [supplier_id], context=context)
                    else:
                        suppliers = line.partner_ids

                    if not suppliers:
                        raise osv.except_osv(_('Warning!'), _('Please select the supplier'))
                    #assert suppliers, 'Supplier should be specified'
                    for partner_id in suppliers:
                        if partner_id.id in filter(lambda x: x, [rfq.state != 'cancel' and rfq.partner_id.id or None for rfq in rec.purchase_ids]):
                            raise osv.except_osv(_('Warning!'), _('You have already one %s purchase order for this partner, you must cancel this purchase order to create a new quotation.') % rfq.state)

                        default_uom_po_id = line.product_id.uom_po_id.id
                        qty = product_uom._compute_qty(cr, uid, line.product_uom_id.id, line.product_qty, default_uom_po_id)
                        if res[rec.id][partner_id.id][line.product_id.id][default_uom_po_id]:
                            po_line = res[rec.id][partner_id.id][line.product_id.id][default_uom_po_id]
                            po_line['product_qty'] = po_line['product_qty'] + qty
                            po_line['pr_line_ids'].append(line.id)
                        else:
                            po_line = {'requisition_id': rec.id,
                                     'pr_line_ids': [line.id],
                                     'pr_names': rec.name,
                                     'product_qty': qty,
                                     'taxes_id': fiscal_position.map_tax(cr, uid, partner_id.property_account_position, line.product_id.supplier_taxes_id) ,
                                     'partner_ref': line.product_id.partner_ref
                                     }
                        res[rec.id][partner_id.id][line.product_id.id][default_uom_po_id] = po_line
        if res == {}:
            raise osv.except_osv(_('Warning!'), _('Please select Product(s)'))
        return res

    def create_order(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', [])
        data = self.browse(cr, uid, ids, context=context)[0]

        po_ids = False
        if data.overwrite:
            res = self._pr_grouping(cr, uid, active_ids, data.partner_id.id, context)
            if data.group_flag:
                self._create_grouping_po(cr, uid, res, context)
            else:
                self._create_po_per_line(cr, uid, res, context)
        else:
            res = self._pr_grouping(cr, uid, active_ids, None, context)
            if data.group_flag:
                self._create_grouping_po(cr, uid, res, context)
            else:
                self._create_po_per_line(cr, uid, res, context)

        return {'type': 'ir.actions.act_window_close'}

purchase_requisition_partner()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
