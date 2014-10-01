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

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp import netsvc

from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)
from collections import defaultdict

class purchase_requisition_line(osv.osv):

    _inherit = "purchase.requisition.line"

    ###############################################################################
    # status PR line diambil dari status PO line ygn terkait dengan PR line ini
    # relasi antara PR line dengan PO line ada di pr_rel_po table
    # secara PR line, fieldnya po_line_ids 
    ###############################################################################
    def _get_status(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 'draft')
        for line in self.browse(cr, uid, ids, context=context):
            for  po in line.po_line_ids:
                if po.state == 'draft' and res[line.id] != 'done':
                    res[line.id] = 'in_purchase'
                else:
                    if po.state == 'confirmed' or po.state == 'done':
                        res[line.id] = 'done'
                    else:
                        if po.state == 'cancel' and res[line.id] != 'done':
                                res[line.id] = 'cancel'
        return res

    ###############################################################################
    # search by state
    # harus return id sesuai state yang diminta 
    # pr_line draft : 
    #    adalah pr line yang belum ada pasangannya di po_line
    # pr_line in_purchase: 
    #    adalah pr_line yang sudah ada pasangan di po_line dan status = draft dan tidak done
    # pr_line done :
    #    adalah pr_line yang sudah ada pasangan di po_line dan status = confirmed | done
    # pr_line cancel :
    #    adalah pr_line yang sudah ada pasangan di po_line dan status = confirmed | done
    ###############################################################################
    def _search_state(self, cr, uid, obj, name, args, domain=None, context=None):
        _logger.error(obj)
        _logger.error(name)
        _logger.error(args[0][2])
        _logger.error(domain)
        
        if context is None:
            context = {}
        if not args:
            return []

        state = args[0][2]

        cr.execute('SELECT pr_id, po_id, pol.state from pr_rel_po mm \
            left join purchase_order_line pol on pol.id= mm.po_id ' )
        res = cr.fetchall()

        _logger.warning(res)

        if not res:
            return [('id', '=', '0')]

        if state == 'draft':
            return [('id', 'not in', [x[0] for x in res])]
        else:
            ids = []
            for r in res:
                _logger.warning(r)
                if state == 'in_purchase':
                    if r[2]=='draft' and r[2] != 'done' :
                        ids.append(r[0]) 
                elif state == 'done':
                    if r[2]=='confirmed' or r[2] == 'done':
                        ids.append(r[0]) 
                _logger.warning(ids)

            return [('id', 'in', ids )]


    _columns = {
        'partner_ids': fields.many2many('res.partner', 'pr_rel_partner',
                                        'pr_line_id',
                                        'partner_id', 'Suppliers', 
                                        domain=[('supplier','=',True)]
                                        ),
        'selected_flag': fields.boolean("Select"),
        'po_line_ids': fields.many2many('purchase.order.line', 'pr_rel_po',
                                        'pr_id', 'po_id',
                                        'Purchase Line Orders',
                                        ondelete='cascade'),
        'state': fields.function(_get_status, string='Status', readonly=True,
                                 type='selection',
                                 #store=True, 
                                 fnct_search=_search_state, 
                                 selection=[('draft', 'New'),
                                        ('in_purchase', 'In Progress'),
                                        ('done', 'Purchase Done'),
                                        ('cancel', 'Cancelled')]),
        'user_id': fields.related('requisition_id','user_id',
            type="many2one",
            relation="res.users",
            string="Responsible",
            ),
        'requisition_state': fields.related('requisition_id','state',
            type="text",
            relation="purchase_requisition.purchase.requisition",
            string="Requisition State"),
        'requisition_date': fields.related('requisition_id','date_start',
            type="text",
            relation="purchase_requisition.purchase.requisition",
            string="Requisition Date")        

    }
    _default = {
       'selected_flag': True,
       'po_line_ids': False,
    }


    def copy(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'po_line_ids': False,
        })
        return super(purchase_requisition_line,
                      self).copy(cr, uid, ids, default, context)

    def write(self, cr, uid, ids, vals, context=None):
        res = super(purchase_requisition_line,
                    self).write(cr, uid, ids, vals, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        # Remove po_line_ids if duplicate data
        if context.get('__copy_data_seen', False):
            vals.update({'po_line_ids': False})
        res_id = super(purchase_requisition_line, self).create(cr, uid, vals, context=context)
        return res_id

    def selected_flag_onchange(self, cr, uid, ids, selected_flag, context=None):
        res = {'value': {'all_selected': True}}
        if not selected_flag:
            res['value'].update({'all_selected': False})
        return res

    def default_get(self, cr, uid, fields, context=None):
        return super(purchase_requisition_line,
                        self).default_get(cr, uid, fields, context=context)
    
    def action_createPO(self, cr, uid, context=None):
        ##########################################################
        # id line PR yang diselect
        ##########################################################
        active_ids = context and context.get('active_ids', False)

        if not context:
            context = {}

        ##########################################################
        # untuk setiap partner , create PO dari line PR
        ##########################################################
        pos = defaultdict(list)
        for line_id in self.browse(cr, uid, active_ids, context):
            if line_id.state == 'draft':
                for partner_id in line_id.partner_ids:
                    pos[partner_id.id].append(line_id)  

        ##########################################################
        #create PO dengan per supplier dengan lines=line_id
        ##########################################################
        i = 0 
        for partner_id, line_ids in pos.items():
            self.create_po(cr, uid, partner_id, line_ids)
            i = i +1

        cr.commit()
        raise osv.except_osv( 'OK!' , 'Done creating %s Quotations(s) ' % (i) )        


    def create_po(self, cr, uid, partner_id, line_ids, context=None):
        purchase_order        = self.pool.get('purchase.order')
        purchase_order_line   = self.pool.get('purchase.order.line')
        res_partner           = self.pool.get('res.partner')
        fiscal_position       = self.pool.get('account.fiscal.position')
        supplier              = res_partner.browse(cr, uid, partner_id, context=context)
        supplier_pricelist    = supplier.property_product_pricelist_purchase or False
        purchase_requisition  = self.pool.get('purchase.requisition')


        origin          = ''
        description     = ''
        
        for line in line_ids:

            requisition         = line.requisition_id 
            origin              += line.requisition_id.name + ' '
            location_id         = requisition.warehouse_id.lot_input_id.id
            company_id          = requisition.company_id.id
            description         += (requisition.description or '') + ' '
            warehouse_id        = requisition.warehouse_id

        purchase_id = purchase_order.create(cr, uid, {
            'origin'        : origin,
            'partner_id'    : supplier.id,
            'pricelist_id'  : supplier_pricelist.id,
            'location_id'   : location_id,
            'company_id'    : company_id,
            'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
            'requisition_id': requisition.id,
            'notes'         : description,
            'warehouse_id'  : warehouse_id.id ,
        })

        for line in line_ids:
            product         = line.product_id
            seller_price, qty, default_uom_po_id, date_planned = purchase_requisition._seller_details(cr, uid, line, supplier, context=context)
            taxes_ids       = product.supplier_taxes_id
            taxes           = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
            purchase_order_line.create(cr, uid, {
                'order_id': purchase_id,
                'name': product.partner_ref,
                'product_qty': qty,
                'product_id': product.id,
                'product_uom': default_uom_po_id,
                'price_unit': seller_price,
                'date_planned': date_planned,
                'taxes_id': [(6, 0, taxes)],
                'pr_line_ids': [(6, False, [line.id] )],
            }, context=context)




purchase_requisition_line()


class purchase_requisition(osv.osv):
    _inherit = 'purchase.requisition'
    _columns = {
        'all_selected': fields.boolean("All Select(s)"),
        'state': fields.selection([('draft','New'),
            ('open','Open'),
            ('in_progress','Sent to Suppliers'),('cancel','Cancelled'),('done','Purchase Done')],
            'Status', track_visibility='onchange', required=True)
    }
    _default = {
        'all_selected': True,
    }

    def all_selected_onchange(self, cr, uid, ids, all_selected, line_ids, context=None):
        res = {'value': {'line_ids': False}}
        for index in range(len(line_ids)):
            if line_ids[index][0] in (0, 1, 4):
                if line_ids[index][2]:
                    line_ids[index][2].update({'selected_flag': all_selected})
                else:
                    if line_ids[index][0] == 4:
                        line_ids[index][0] = 1
                    line_ids[index][2] = {'selected_flag': all_selected}
        res['value']['line_ids'] = line_ids
        return res

    def update_done(self, cr, uid, ids, context=None):
        pr_recs = self.browse(cr, uid, ids, context=context)
        prs_done = []
        for rec in pr_recs:
            is_done = True
            for line in rec.line_ids:
                is_done = is_done and line.state in ('done', 'cancel')
            if is_done:
                prs_done.append(rec.id)
        self.tender_done(cr, uid, prs_done, context=None)
        return True

    def copy(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        return super(purchase_requisition,
                      self).copy(cr, uid, ids, default, context)

    def action_createPO(self, cr, uid, ids, context=None):
        selected = False
        for pr in self.browse(cr, uid, ids, context):
            for line_id in pr.line_ids:
                if line_id.selected_flag:
                    selected = True
        if not selected:
            raise osv.except_osv(_('Warning!'), _('Please select the PR Line(s) at least one line'))
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'purchase_requisition', 'action_purchase_requisition_partner')
        id = result and result[1] or False
        _logger.error(result)
        _logger.error(id)
        result = act_obj.read(cr, uid, [id], context=context)[0]
        _logger.error(result)
        return result
    def tender_open(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'open'} ,context=context)

purchase_requisition()





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
