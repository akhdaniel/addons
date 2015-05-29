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

import openerp
from openerp.osv import fields, osv
import re
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import html2plaintext


# class sale_order(osv.osv):
#     """ Helpdesk Cases """
#     _inherit = 'sale.order'


#     _columns = {
#         'email_from': fields.char('Customer Email'),
#         }


#     # -------------------------------------------------------
#     # Mail gateway
#     # -------------------------------------------------------

#     def message_new(self, cr, uid, msg, custom_values=None, context=None):
#         """ Overrides mail_thread message_new that is called by the mailgateway
#             through message_process.
#             This override updates the document according to the email.
#         """
        
#         print'Partner Name>>>>>>>>',msg.get('from')
#         partner_ids = None
#         desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
#         defaults = {
#             'name': '/',
#             'note': desc,
#             'user_id': uid,
#         }
#         if msg.get('author_id', False) == False:
#             index = str(msg.get('from')).find('<')
#             partner_name = str(msg.get('from'))[:index-1].strip()
#             print'Partner Name With ..>>>>>>>>',partner_name
#             partner_ids = self.pool.get('res.partner').search(cr,uid,[('name','=',partner_name)],context=context)
#             client_mail = re.search(r'[\w\.-]+@[\w\.-]+', msg.get('from')).group(0)
#             partner_id = None
#             if not partner_ids:
#                 partner_id = self.pool.get('res.partner').create(cr,uid,{'name':partner_name, 'email':client_mail},context=context)
#                 defaults.update({'partner_id':partner_id})
#             else:
#                 defaults.update({'partner_id':partner_ids[0]})
        
#         else:
#             defaults.update({'partner_id':msg.get('author_id')})
#         if custom_values is None:
#             custom_values = {}
        
#         #partner_ids = self.pool.get('res.partner').search(cr,uid,[('customer','=',Ture)],context=context)
#         defaults.update(custom_values)
#         return super(sale_order, self).message_new(cr, uid, msg, custom_values=defaults, context=context)


class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    _columns = {
        'state': fields.selection([
            ('draft', 'Draft Proforma Invoice'),
            ('sent', 'Proforma Invoice Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Orderrrrrrrr'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the proforma invoice or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'port_name':fields.char("Port of loading"),
        'port_discharge':fields.char("Port of discharge"),
        'desc_goods':fields.text("Description of goods"),
        'qty_total':fields.float("Quantity",help="total products quantity"),
        'readiness_date':fields.datetime("Readiness",help="order availability date"),
        'etd_date':fields.datetime("ETD",help="Estimated Time of Delivery"),
        }

    _defaults={
        'desc_goods': "wooden furniture",
    }
sale_order()

# class sale_order_line(osv.osv):
#     _inherit = 'sale.order.line'
#     _columns = {
#         # 'colection_ids': fields.related('product_id','colection_ids',type='many2many',relation='product_collection_rel',string='Collection'),
#         'colection_ids': fields.Char(related='product_id.colection_ids', store=False),
#         'description_ids': fields.related('product_id','description_ids',type='one2many',relation='product.collection',string='Customer Description'),
#         }

# • Customer description (the new field we built in the product form)
# • Description (the normal description of the product)
# • Finishing (the new field too)
# • W (cm), (the width of the product)
# • L (cm), (the length of the product)
# • H (cm), (the height of the product)
# • Volume (this is the new disassemble volume)
# • Unit price
# • Quantity
# • Total amount
# • Total vol
#         }