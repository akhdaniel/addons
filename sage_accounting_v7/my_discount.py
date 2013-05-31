# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from osv import fields, osv
import decimal_precision as dp

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    
    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        '''Call after the creation of the invoice line'''
        #import pdb; pdb.set_trace()
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_line_obj.write(cr, uid, [invoice_line_id], {'discount_nominal' : move_line.sale_line_id.discount_nominal})
        return    
        
stock_picking()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _name = 'sale.order.line'

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res=super(sale_order_line, self)._amount_line(cr, uid, ids, field_name, arg, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = res[line.id] - (line.discount_nominal * line.product_uom_qty)
        return res
    
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res=super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id, context=context)
        res['discount_nominal'] = line.discount_nominal
        return res
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):

        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        
        #return {'value': result, 'domain': domain, 'warning': warning}
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        discount=0.0
        for pd in partner.product_discount:
            if pd.product_id.id == product:
                discount = pd.discount

        res['value'].update({'discount_nominal': discount})
        return res
    
    _columns ={
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Sale Price')),
        'discount_nominal': fields.float('Discount', digits=(14,4)),
    }
    
sale_order_line()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _name = "account.invoice.line"

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        
        res=super(account_invoice_line, self)._amount_line(cr, uid, ids, prop, unknow_none, unknow_dict)

        for line in self.browse(cr, uid, ids):
            res[line.id] = res[line.id] - (line.discount_nominal * line.quantity)
        return res


    _columns ={
        'discount_nominal': fields.float('Discount', digits=(14,4)),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', type="float",
            digits_compute= dp.get_precision('Account'), store=True),
    }

account_invoice_line()

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    _columns ={
        'product_discount': fields.one2many('sage.customer.discount.line', 'partner_id', 'Product Discounts'),
    }      
res_partner()

class sage_customer_discount_line(osv.osv):
    _name = 'sage.customer.discount.line'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'discount': fields.float('Product Discount', digits=(12,4)),
    }
sage_customer_discount_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
