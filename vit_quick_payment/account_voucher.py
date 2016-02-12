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
from lxml import etree

from openerp import netsvc
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw

class account_voucher(osv.osv):
    _inherit = "account.voucher"

    def button_create_voucher(self, cr, uid, ids, context=None):
        import pdb; pdb.set_trace()
        # create account voucher utk invoice ybs
        voucher = self.browse(cr, uid, ids, context)
        vid = self.create_payment(cr, uid, inv, partner_id, amount, journal, company_id, context)
        self.payment_confirm(cr, uid, vid, context)
        return 

    ####################################################################################
    #create payment 
    #invoice_id: yang mau dibayar
    #journal_id: payment method
    ####################################################################################
    def create_payment(self, cr, uid, inv, partner_id, amount, journal, company_id, context=None):
        voucher_lines = []

        #cari invoice
        # inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        
        #cari move_line yang move_id nya = invoice.move_id
        move_line_id = self.pool.get('account.move.line').search( cr, uid, [('move_id.id','=', inv.move_id.id)] );
        move_lines = self.pool.get('account.move.line').browse(cr, uid, move_line_id)
        move_line = move_lines[0] # yang AR saja

        voucher_lines.append((0,0,{
            'move_line_id':         move_line.id,
            'account_id':           move_line.account_id.id,
            'amount_original':      move_line.debit,
            'amount_unreconciled':  move_line.debit,
            'reconcile':            True,
            'amount':               move_line.debit,
            'type':                 'cr',
            'name':                 move_line.name,
            'company_id':           company_id
        }))
        

        voucher_id = self.pool.get('account.voucher').create(cr,uid,{
            'partner_id'    : partner_id,
            'amount'        : amount,
            'account_id'    : journal.default_debit_account_id.id,
            'journal_id'    : journal.id,
            'reference'     : 'payment #',
            'name'          : 'payment #',
            'company_id'    : company_id,
            'type'          : 'receipt',
            'line_ids'      : voucher_lines
            })
        _logger.info("   created payment id:%d" % (voucher_id) )
        return voucher_id

    ####################################################################################
    #set done
    ####################################################################################
    def payment_confirm(self, cr, uid, vid, context=None):
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
        _logger.info("   confirmed payment id:%d" % (vid) ) 
        return True


    def onchange_journal(self, cr, uid, ids, journal_id, company_id, context=None):

        if context is None:
            context = {}
        if not journal_id:
            return False

        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id

        vals = {'value':{ 'account_id' : account_id.id} }

        currency_id = False

        if journal.currency:
            currency_id = journal.currency.id
        else:
            currency_id = journal.company_id.currency_id.id

        vals['value'].update({'currency_id': currency_id})

        if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
            vals['value']['amount'] = 0
            amount = 0

        return vals


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
