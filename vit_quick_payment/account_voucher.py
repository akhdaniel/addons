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
import logging

_logger = logging.getLogger(__name__)

class account_voucher(osv.osv):
    _inherit = "account.voucher"

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        if not journal_id:
            return {}
        if context is None:
            context = {}
        #TODO: comment me and use me directly in the sales/purchases views
        res = self.basic_onchange_partner(cr, uid, ids, partner_id, journal_id, ttype, context=context)
        if ttype in ['sale', 'purchase']:
            return res
        ctx = context.copy()
        # not passing the payment_rate currency and the payment_rate in the context but it's ok because they are reset in recompute_payment_rate
        ctx.update({'date': date})
       
        return res

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': date})
        #read the voucher rate with the right date in the context
        currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
        voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        ctx.update({
            'voucher_special_currency': payment_rate_currency_id,
            'voucher_special_currency_rate': rate * voucher_rate})
        #res = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
        vals = self.onchange_rate(cr, uid, ids, rate, amount, currency_id, payment_rate_currency_id, company_id, context=ctx)
        # for key in vals.keys():
        #     res[key].update(vals[key])
        # # import pdb; pdb.set_trace()
        return vals


    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        if context is None:
            context = {}
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        if ttype in ('sale', 'receipt'):
            account_id = journal.default_debit_account_id
        elif ttype in ('purchase', 'payment'):
            account_id = journal.default_credit_account_id
        else:
            account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id

        vals = {'value':{} }
        if ttype in ('sale', 'purchase'):
            vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
            vals['value'].update({'tax_id':tax_id,'amount': amount})
        currency_id = False
        if journal.currency:
            currency_id = journal.currency.id
        else:
            currency_id = journal.company_id.currency_id.id
        vals['value'].update({'currency_id': currency_id, 'payment_rate_currency_id': currency_id})
        #in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal 
        #without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
        #this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
        if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
            vals['value']['amount'] = 0
            amount = 0
        #--------------------- update  
        if ttype in ['sale', 'purchase']:
            return res
        ctx = context.copy()
        #---------------------- end update
        if partner_id:
            res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
            #------------------------------------- update
            vals = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
            vals2 = self.recompute_payment_rate(cr, uid, ids, vals, currency_id, date, ttype, journal_id, amount, context=context)
            for key in vals.keys():
                res[key].update(vals[key])
            for key in vals2.keys():
                res[key].update(vals2[key])
            #TODO: can probably be removed now
            #TODO: onchange_partner_id() should not returns [pre_line, line_dr_ids, payment_rate...] for type sale, and not 
            # [pre_line, line_cr_ids, payment_rate...] for type purchase.
            # We should definitively split account.voucher object in two and make distinct on_change functions. In the 
            # meanwhile, bellow lines must be there because the fields aren't present in the view, what crashes if the 
            # onchange returns a value for them
            if ttype == 'sale':
                del(res['value']['line_dr_ids'])
                del(res['value']['pre_line'])
                del(res['value']['payment_rate'])
            elif ttype == 'purchase':
                del(res['value']['line_cr_ids'])
                del(res['value']['pre_line'])
                del(res['value']['payment_rate'])
            res
            #----------------------------------- end update

            for key in res.keys():
                # import pdb; pdb.set_trace()
                vals[key].update(res[key])

        return vals



    def quick_payment(self, cr, uid, ids, context=None):
        voucher = self.browse(cr, uid, ids, context)
        self.onchange_partner_id(cr, uid, ids, voucher[0].partner_id.id, voucher[0].journal_id.id, voucher[0].amount, voucher[0].currency_id.id, voucher[0].type, voucher[0].date, context=None)
        # import pdb; pdb.set_trace()
        # self.payment_confirm(cr, uid, ids, context=None)
        journal_id = voucher[0].journal_id.id
        line_ids = voucher[0].line_ids
        tax_id = voucher[0].tax_id.id
        partner_id = voucher[0].partner_id.id
        date = voucher[0].date
        amount = voucher[0].amount
        ttype = voucher[0].type 
        company_id = voucher[0].company_id.id
        # self.onchange_journal(self, cr, uid, ids, voucher[0].journal_id.id,voucher[0].line_ids, voucher[0].tax_id.id, voucher[0].partner_id.id, voucher[0].date, voucher[0].amount, voucher[0].type, voucher[0].company_id.id)
        self.onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id)
        self.button_proforma_voucher(cr, uid, ids, context=None)
        return True


    def payment_confirm(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'account.voucher', ids[0], 'proforma_voucher', cr)
        _logger.info("   confirmed payment id:%d" % (ids[0]) ) 
        self.update_voucher_entry( cr, uid, ids, context=None)
        return True

    def update_voucher_entry(self, cr, uid, ids, context=None):
    	# for journal_deb in 
    	voucher = self.browse(cr, uid, ids, context)
    	for journal_deb in voucher[0].move_ids:
    		if journal_deb.debit != 0:
    			journal_deb.debit 
    			# import pdb; pdb.set_trace()
    			voucher_lines=[]
    			voucher_lines.append((0,0,{
		            'move_line_id':         journal_deb.id,
		            'account_id':           journal_deb.account_id.id,
		            'amount_original':      journal_deb.debit,
		            'amount_unreconciled':  journal_deb.debit,
		            'reconcile':            True,
		            'amount':               journal_deb.debit,
		            'type':                 'dr',
		            'name':                 journal_deb.name,
		            'company_id':           journal_deb.company_id.id
		        }))
		       
		        voucher_id = self.write(cr,uid,ids,{
		     
		            'line_ids'      : voucher_lines
		            })

    	return



    def onchange_journal2(self, cr, uid, ids, journal_id, company_id, context=None):

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

    # def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
    #     if not journal_id:
    #         return {}
    #     if context is None:
    #         context = {}
    #     #TODO: comment me and use me directly in the sales/purchases views
    #     res = self.basic_onchange_partner(cr, uid, ids, partner_id, journal_id, ttype, context=context)
    #     if ttype in ['sale', 'purchase']:
    #         return res
    #     ctx = context.copy()
    #     # not passing the payment_rate currency and the payment_rate in the context but it's ok because they are reset in recompute_payment_rate
    #     ctx.update({'date': date})
    #     # vals = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
    #     # vals2 = self.recompute_payment_rate(cr, uid, ids, vals, currency_id, date, ttype, journal_id, amount, context=context)
    #     # for key in vals.keys():
    #     #     res[key].update(vals[key])
    #     # for key in vals2.keys():
    #     #     res[key].update(vals2[key])
    #     # #TODO: can probably be removed now
    #     # #TODO: onchange_partner_id() should not returns [pre_line, line_dr_ids, payment_rate...] for type sale, and not 
    #     # # [pre_line, line_cr_ids, payment_rate...] for type purchase.
    #     # # We should definitively split account.voucher object in two and make distinct on_change functions. In the 
    #     # # meanwhile, bellow lines must be there because the fields aren't present in the view, what crashes if the 
    #     # # onchange returns a value for them
    #     # if ttype == 'sale':
    #     #     del(res['value']['line_dr_ids'])
    #     #     del(res['value']['pre_line'])
    #     #     del(res['value']['payment_rate'])
    #     # elif ttype == 'purchase':
    #     #     del(res['value']['line_cr_ids'])
    #     #     del(res['value']['pre_line'])
    #     #     del(res['value']['payment_rate'])
    #     return res

    # def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
    #     if context is None:
    #         context = {}
    #     if not journal_id:
    #         return False
    #     journal_pool = self.pool.get('account.journal')
    #     journal = journal_pool.browse(cr, uid, journal_id, context=context)
    #     if ttype in ('sale', 'receipt'):
    #         account_id = journal.default_debit_account_id
    #     elif ttype in ('purchase', 'payment'):
    #         account_id = journal.default_credit_account_id
    #     else:
    #         account_id = journal.default_credit_account_id or journal.default_debit_account_id
    #     tax_id = False
    #     if account_id and account_id.tax_ids:
    #         tax_id = account_id.tax_ids[0].id

    #     vals = {'value':{} }
    #     if ttype in ('sale', 'purchase'):
    #         vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
    #         vals['value'].update({'tax_id':tax_id,'amount': amount})
    #     currency_id = False
    #     if journal.currency:
    #         currency_id = journal.currency.id
    #     else:
    #         currency_id = journal.company_id.currency_id.id
    #     vals['value'].update({'currency_id': currency_id, 'payment_rate_currency_id': currency_id})
    #     #in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal 
    #     #without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
    #     #this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
    #     if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
    #         vals['value']['amount'] = 0
    #         amount = 0
    #     # if partner_id:
    #     #     res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
    #     #     for key in res.keys():
    #     #         vals[key].update(res[key])
    #     return vals
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
