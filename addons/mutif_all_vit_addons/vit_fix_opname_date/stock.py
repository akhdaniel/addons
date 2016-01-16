from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class stock_move(osv.osv):
    _inherit = "stock.move"
    _name = "stock.move"


    # def _create_product_valuation_moves(self, cr, uid, move, context=None):
    #     """
    #     Generate the appropriate accounting moves if the product being moves is subject
    #     to real_time valuation tracking, and the source or destination location is
    #     a transit location or is outside of the company.
    #     """
    #     import pdb;pdb.set_trace()
    #     if move.product_id.valuation == 'real_time': # FIXME: product valuation should perhaps be a property?
    #         if context is None:
    #             context = {}
    #         src_company_ctx = dict(context,force_company=move.location_id.company_id.id)
    #         dest_company_ctx = dict(context,force_company=move.location_dest_id.company_id.id)
    #         account_moves = []
    #         # Outgoing moves (or cross-company output part)
    #         if move.location_id.company_id \
    #             and (move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal'\
    #                  or move.location_id.company_id != move.location_dest_id.company_id):
    #             journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
    #             reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
    #             #returning goods to supplier
    #             if move.location_dest_id.usage == 'supplier':
    #                 account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_src, reference_amount, reference_currency_id, context))]
    #             else:
    #                 account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_dest, reference_amount, reference_currency_id, context))]

    #         # Incoming moves (or cross-company input part)
    #         if move.location_dest_id.company_id \
    #             and (move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal'\
    #                  or move.location_id.company_id != move.location_dest_id.company_id):
    #             journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, dest_company_ctx)
    #             reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
    #             #goods return from customer
    #             if move.location_id.usage == 'customer':
    #                 account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_dest, acc_valuation, reference_amount, reference_currency_id, context))]
    #             else:
    #                 account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_src, acc_valuation, reference_amount, reference_currency_id, context))]

    #         move_obj = self.pool.get('account.move')

    #         context.update({'account_period_prefer_normal':True})
    #         period_id   = self.pool.get('account.period').find(cr,uid, move.date, context)[0]
    #         for j_id, move_lines in account_moves:
    #             # import pdb;pdb.set_trace()
    #             move_obj.create(cr, uid,
    #                     {
    #                      'journal_id': j_id,
    #                      'date': move.date,
    #                      'line_id': move_lines,
    #                      'ref': move.name,
    #                      'period_id': period_id,
    #                      # 'ref': move.picking_id and move.picking_id.name
    #                      'ref' : move.name
    #                      })

    def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given stock move.
        """
        _logger.error(move.date)
        # import pdb;pdb.set_trace()
        # prepare default values considering that the destination accounts have the reference_currency_id as their main currency
        partner_id = (move.picking_id.partner_id and self.pool.get('res.partner')._find_accounting_partner(move.picking_id.partner_id).id) or False
        debit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id and move.product_id.id or False,
                    'quantity': move.product_qty,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': move.date,
                    'partner_id': partner_id,
                    'debit': reference_amount,
                    'account_id': dest_account_id,
        }
        credit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id and move.product_id.id or False,
                    'quantity': move.product_qty,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': move.date,
                    'partner_id': partner_id,
                    'credit': reference_amount,
                    'account_id': src_account_id,
        }
        # if we are posting to accounts in a different currency, provide correct values in both currencies correctly
        # when compatible with the optional secondary currency on the account.
        # Financial Accounts only accept amounts in secondary currencies if there's no secondary currency on the account
        # or if it's the same as that of the secondary amount being posted.
        account_obj = self.pool.get('account.account')
        src_acct, dest_acct = account_obj.browse(cr, uid, [src_account_id, dest_account_id], context=context)
        src_main_currency_id = src_acct.company_id.currency_id.id
        dest_main_currency_id = dest_acct.company_id.currency_id.id
        cur_obj = self.pool.get('res.currency')
        if reference_currency_id != src_main_currency_id:
            # fix credit line:
            credit_line_vals['credit'] = cur_obj.compute(cr, uid, reference_currency_id, src_main_currency_id, reference_amount, context=context)
            if (not src_acct.currency_id) or src_acct.currency_id.id == reference_currency_id:
                credit_line_vals.update(currency_id=reference_currency_id, amount_currency=-reference_amount)
        if reference_currency_id != dest_main_currency_id:
            # fix debit line:
            debit_line_vals['debit'] = cur_obj.compute(cr, uid, reference_currency_id, dest_main_currency_id, reference_amount, context=context)
            if (not dest_acct.currency_id) or dest_acct.currency_id.id == reference_currency_id:
                debit_line_vals.update(currency_id=reference_currency_id, amount_currency=reference_amount)

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]        
stock_move()