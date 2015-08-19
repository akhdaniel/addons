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


class tree_validation(osv.osv):
    _name = 'tree.validation'

    _columns = {
        'name' : fields.boolean('Is Tree Validation',help="Tambah Satu Approval dulu sebelum approve Quotation menjadi PO"),
        'limit_amount': fields.integer('Limit to Require a Third Approval',required=True,
            help="dihitung jika nominal lebih kecil dari amount approval ke 2"),
    }


class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def purchase_approve0(self,cr,uid,ids,context=None):         
        return self.write(cr,uid,ids,{'state':'confirmed0'},context=context)

    def _get_triple_validation(self, cr, uid, ids, field_name, arg, context=None):
        
        if context is None:
            context = {}
        result = {}
        tree_validation_obj = self.pool.get('tree.validation')
        tree_validation = False
        for obj in self.browse(cr,uid,ids,context=context):
            tree_val_exist = tree_validation_obj.search(cr,uid,[('id','=',1)])
            if tree_val_exist :
                tree_validation = tree_validation_obj.browse(cr,uid,1).name
                tree_validation_amount = tree_validation_obj.browse(cr,uid,1).limit_amount
                if tree_validation:
                    amount_total = obj.amount_total
                    #jika total nilai PO lebih besar dari settinggan triple validation
                    if amount_total <= tree_validation_amount:
                        tree_validation = False
        result[obj.id] = tree_validation
        return result

    def _get_limit_amount(self, cr, uid, ids, field_name, arg, context=None):
        
        if context is None:
            context = {}
        result = {}
        tree_validation_obj = self.pool.get('tree.validation')
        tree_validation_amount = 0
        for obj in self.browse(cr,uid,ids,context=context):
            tree_val_exist = tree_validation_obj.search(cr,uid,[('id','=',1)])
            if tree_val_exist :
                tree_validation_amount = tree_validation_obj.browse(cr,uid,1).limit_amount


        result[obj.id] = tree_validation_amount
        return result

    _columns = {
        'is_triple_validation': fields.function(_get_triple_validation, type="boolean",string='Is Triple Validation'),
        'limit_amount'        : fields.function(_get_limit_amount,type="integer",string='Limit Amount'),
        'state': fields.selection([('draft', 'Draft PO'),
                                    ('sent', 'RFQ'),
                                    ('bid', 'Bid Received'),
                                    ('confirmed', 'Waiting Approval'),
                                    ('confirmed0','Waiting Second Approval'),
                                    ('approved', 'Purchase Confirmed'),
                                    ('except_picking', 'Shipping Exception'),
                                    ('except_invoice', 'Invoice Exception'),
                                    ('done', 'Done'),
                                    ('cancel', 'Cancelled')], 'Status', readonly=True,
                                  help="The status of the purchase order or the quotation request. "
                                       "A request for quotation is a purchase order in a 'Draft' status. "
                                       "Then the order has to be confirmed by the user, the status switch "
                                       "to 'Confirmed'. Then the supplier must confirm the order to change "
                                       "the status to 'Approved'. When the purchase order is paid and "
                                       "received, the status becomes 'Done'. If a cancel action occurs in "
                                       "the invoice or in the receipt of goods, the status becomes "
                                       "in exception.",
                                  select=True, copy=False),

    }   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    