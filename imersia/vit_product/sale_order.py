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
from datetime import datetime,time
from openerp.tools import float_compare

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

    def _get_qty_total(self, cr, uid, ids, field_name, arg, context=None):
        result = dict.fromkeys(ids, False)
        for i in self.browse(cr, uid, ids, context=context):
            qty = 0.0
            for line in i.order_line:
                qty += line.product_uom_qty
            result[i.id] = qty
        return result

    def _get_so_name(self, cr, uid, ids, field_name, arg, context=None):
        result = dict.fromkeys(ids, False)
        for i in self.browse(cr, uid, ids, context=context):
            result[i.id] = 'PO'+ i.name[2:]
        return result

    _columns = {
        'proforma_no':fields.function(_get_so_name,type='char',store=True,string='No.'),
        'state': fields.selection([
            ('draft', 'Draft Proforma Invoice'),
            ('sent', 'Proforma Invoice Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the proforma invoice or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'port_name':fields.char("Port of loading"),
        'comment':fields.text("Remarks"),
        'port_discharge':fields.char("Port of discharge"),
        'desc_goods':fields.char("Description of goods"),
        'qty_total':fields.function(_get_qty_total,type='float',digits=(12, 2),string='Quantity',help="Total products quantity"),
        'readiness_date':fields.date("Readiness",help="Order availability date"),
        'week_of_year': fields.char('Week'),
        'etd_date':fields.datetime("ETD",help="Estimated Time of Delivery"),
        }

    _defaults={
        'desc_goods': "Wooden Furniture",
        'week_of_year': "Week -" 
    }

    def readydate_change(self, cr, uid, ids,rd,):
        if rd:
            dte = "Week  " + str(datetime.strptime(rd,"%Y-%m-%d").isocalendar()[1])
            return {'value':{'week_of_year':dte}}
        return {'value':{'week_of_year':"Week -"}}

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def hitung_mm_ke_cm(self,bilangan):
        hasil = 0
        if bilangan > 0 :
            hasil =  bilangan / 10
        return hasil 

    ####################################
    #konversi mm ke cm
    ####################################
    def hitung_width_mm_ke_cm(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_larg
            hasil     = self.hitung_mm_ke_cm(bilangan)
            result[ids[0]] = hasil
        return result         

    def hitung_height_mm_ke_cm(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_height
            hasil     = self.hitung_mm_ke_cm(bilangan)
            result[ids[0]] = hasil
        return result 

    def hitung_length_mm_ke_cm(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan  = obj.product_id.product_length
            hasil     = self.hitung_mm_ke_cm(bilangan)
            result[ids[0]] = hasil
        return result   

    def hitung_total_volume_m3(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}

        for obj in self.browse(cr,uid,ids,context=context):
            bilangan1  = obj.product_id.product_length
            hasil1     = 0
            if bilangan1 > 0:
                hasil1 = bilangan1 / 1000

            bilangan2  = obj.product_id.product_height
            hasil2     = 0
            if bilangan2 > 0:
                hasil2 = bilangan2 / 1000  

            bilangan3  = obj.product_id.product_larg
            hasil3     = 0
            if bilangan1 > 0:
                hasil3 = bilangan3 / 1000                          

            qty        = obj.product_uom_qty

            hasil      = round((hasil1 * hasil2 *hasil3)*qty,4)
            result[ids[0]] = hasil
        return result 


    def _get_cust_desc(self, cr, uid, ids, field_name, arg, context=None):
        result = dict.fromkeys(ids, False)
        desc_obj       = self.pool.get('product.customers.description')

        for i in self.browse(cr, uid, ids, context=context):
            desc     = '-'
            partner  = i.order_id.partner_id.id
            produk   = i.product_id.product_tmpl_id.id
            cust_ids = desc_obj.search(cr,uid,[('produk_id','=',produk),('partner_id','=',partner)])
            if cust_ids:
                desc = desc_obj.browse(cr,uid,cust_ids[0],).name
            result[i.id] = desc
        return result

    _columns = {
        'cust_desc' : fields.function(_get_cust_desc,type='char',string='Cust. Description'),
        'colection_ids': fields.related('product_id','colection_ids',type='many2many',relation='product.collection',string='Collection',readonly=True),
        'finishing_id': fields.related('product_id','finishing_id',type='many2one',relation='product.finishing',string='Finishing',readonly=True),
        'product_weight_cm': fields.function(hitung_length_mm_ke_cm, type='char', string='Depth (cm)'),
        'product_height_cm': fields.function(hitung_height_mm_ke_cm, type='char', string='Height (cm)'),
        'product_larg_cm': fields.function(hitung_width_mm_ke_cm, type='char', string='Width (cm)'),
        'product_volume_total': fields.function(hitung_total_volume_m3, type='char', string='Total Volume (m3)'),      
        'product_unbuilt_volume12': fields.related('product_id','product_unbuilt_volume12',type='float',string='Unbuilt Volume (m3)',readonly=True),
        }