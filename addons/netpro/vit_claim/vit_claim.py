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
CLAIM_STATES = [('draft','Draft'),
    ('open','Open'),
    ('approved','Approved'),
    ('revised','Revised'),
    ('released','Released'),
    ('cancelled','Cancelled'),
    ('hold','Hold')]

from openerp.osv import fields,osv
import time

class netpro_claim(osv.osv):
    _name = 'netpro.claim'
    _rec_name = 'claim_no'

    def create(self, cr, uid, vals, context=None):
        # claim_status_draft = self.pool.get('netpro.claim_status').get_by_code(cr, uid, 'D', context=context)
        nomor = self.pool.get('ir.sequence').get(cr, uid, 'claim_seq') or '/'
        vals.update({
            'claim_no'  : nomor,
            # 'state'     : claim_status_draft,
        })
        new_id = super(netpro_claim, self).create(cr, uid, vals, context=context)
        return new_id

    _columns = {
        'claim_no': fields.char('Claim No.'),
        'claim_no_revision': fields.integer('Claim No Revision'),
        'ext_claim_no': fields.char('Ext Claim No'),
        'claim_date': fields.date('Claim Date'),
        'claim_received_date': fields.date('Claim Received Date'),
        'claim_loss_date_start': fields.date('Claim Loss Date Start'),
        'claim_loss_date_end': fields.date('Claim Loss Date End'),
        'policy_id': fields.many2one('netpro.policy', 'Policy'),
        'member_id': fields.many2one('netpro.member', 'Member'),
        'claim_category_id': fields.many2one('netpro.claim_category', 'Category'),
        'claim_type_id': fields.many2one('netpro.claim_type', 'Claim Type'),
        'member_plan_id': fields.many2one('netpro.member_plan', 'Claim Type (Member Plan)'),
        'diagnosis_id': fields.many2one('netpro.diagnosis', 'Diagnosis'),
        '2nd_diagnosis': fields.many2one('netpro.diagnosis', '2nd Diagnosis'),
        '3rd_diagnosis': fields.many2one('netpro.diagnosis', '3rd Diagnosis'),
        'claim_id': fields.many2one('netpro.claim', 'Main Claim No'),
        'branch_id': fields.many2one('netpro.branch', 'Branch'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'claim_rate': fields.float('Claim Rate'),
        'policy_rate': fields.float('Policy Rate'),
        'reimbursement': fields.float('Reimbursement'),
        'claim_room_id': fields.many2one('netpro.claim_room', 'Room'),
        'exgratia_claim': fields.boolean('Exgratia Claim'),
        'non_jabodetabek': fields.boolean('Non-Jabodetabek'),
        'disable_prorate': fields.boolean('Disable Prorate'),
        'country_id': fields.many2one('res.country', 'Country'),
        'remarks': fields.text('Remarks'),
        'reason_id': fields.many2one('netpro.reason', 'Reason'),
        'other_reason': fields.text('Other Reason'),
        'sys_remarks': fields.text('Sys Remarks'),
        'discount': fields.float('Discount'),
        'aso_charge': fields.float('ASO Charge'),
        'reference_no': fields.char('Reference No'),
        'ref_tpa_payment': fields.char('Ref. TPA Payment'),
        'ref_excess': fields.char('Ref. Excess'),
        'pay_to': fields.many2one('res.partner', 'Pay To'),
        'payment_id': fields.many2one('res.partner', 'ID'),
        'account_no': fields.char('Account No'),
        'account_name': fields.char('Account Name'),
        'bank_id': fields.many2one('res.partner.bank', 'Bank'),
        'bank_name': fields.char('Bank Name'),
        'bank_branch': fields.char('Bank Branch'),
        'excess_payor_id': fields.many2one('netpro.excess_payor', 'Excess Payor'),
        'excess_id': fields.many2one('res.partner', 'Excess ID'),
        'excess_tpa_id': fields.many2one('netpro.tpa', 'Excess TPA ID'),
        'refund_account_no': fields.char('Account No'),
        'refund_account_name': fields.char('Account Name'),
        'refund_bank_name': fields.char('Bank Name'),
        'edc_trc_authorization': fields.char('TRC Authorization'),
        'edc_trc_claim_payable': fields.char('TRC Claim Payable'),
        # 'state': fields.many2one('netpro.claim_status', 'Status'),
        'state' : fields.selection(CLAIM_STATES,'Status',readonly=True,required=True),
        'acceptation_status': fields.char('Acceptation Status'),
        'cno': fields.integer('CNO'),
        'pcno': fields.integer('PCNO'),
        'batch_id': fields.integer('Batch ID'),
        'glid': fields.integer('GL ID'),
        'prorate': fields.float('Prorate'),
        'payment_status_request_date': fields.date('Request Date'),
        'payment_status_payment_date': fields.date('Payment Date'),
        'payment_status_excess_payment_date': fields.date('Excess Payment Date'),
        'transaction_history_created_by_id': fields.many2one('res.users', 'Created By', readonly=True),
        'transaction_history_created_date': fields.datetime('Created Date'),
        'transaction_history_last_edited_by_id': fields.many2one('res.users', 'Last Edited By', readonly=True),
        'transaction_history_last_edited_date': fields.datetime('Last Edited By Date', readonly=True),
        'transaction_history_adjusted_by_id': fields.many2one('res.users', 'Adjusted By', readonly=True),
        'transaction_history_adjusted_date': fields.date('Adjusted Date', readonly=True),
        'transaction_history_checked_by_id': fields.many2one('res.users', 'Checked By', readonly=True),
        'transaction_history_checked_date': fields.date('Checked Date', readonly=True),
        'transaction_history_released_by_id': fields.many2one('res.users', 'Releases By', readonly=True),
        'transaction_history_released_date': fields.date('Released Date', readonly=True),
        'doctor': fields.char('Doctor'),
        'symptoms': fields.char('Symptoms'),
        'disease_history': fields.char('Disease History'),
        'phys_examination': fields.char('Phys. Examination'),
        'consultation': fields.char('Consultation'),
        'treatment_id': fields.many2one('netpro.treatment', 'Treatment'),
        'treatment_remarks': fields.text('Treatment Remarks'),
        'treatment_place': fields.char('Treatment Place'),
        'place_id': fields.many2one('netpro.place', 'Place'),
        'summary_billed': fields.float('Billed'),
        'sumary_unpaid': fields.float('Unpaid'),
        'summary_discount': fields.float('Discount'),
        'summary_cash_member': fields.float('Cash Member'),
        'summary_total_paid': fields.float('Total Paid'),
        'summary_accepted': fields.float('Accepted'),
        'summary_client_accepted': fields.float('Client Accepted'),
        'sumary_total_excess': fields.float('Total Excess'),
        'summary_cash_member_accepted': fields.float('Cash Member'),
        'summary_excess': fields.float('Excess (+)'),
        'summary_verified': fields.float('Verified'),
        'summary_adjustment': fields.float('Adjustment'),
        'summary_overall_limit': fields.float('Overall Limit'),
        'summary_usage': fields.float('Usage'),
        'summary_balance': fields.float('Balance'),
        'summary_family_limit': fields.float('Family Limit'),
        'summary_family_usage': fields.float('Family Usage'),   
        'summary_family_balance': fields.float('Family Balance'),
        'summary_claim_count': fields.float('Claim Count'),
        'claim_detail_ids': fields.one2many('netpro.claim_detail', 'claim_id', 'Claim Details', ondelete='cascade'),
        'diagnosis_ids': fields.one2many('netpro.claim_diagnosis', 'claim_id', 'Diagnosis', ondelete='cascade'),
        'claim_reason_ids': fields.one2many('netpro.claim_reason', 'claim_id', 'Reasons', ondelete='cascade'),
        'tpa_id' : fields.many2one('netpro.tpa', 'TPA'),
        'provider_id' : fields.many2one('netpro.provider', 'Provider'),
    }


    _defaults = {
        'claim_date'        : lambda *a : time.strftime("%Y-%m-%d") ,
        'state'             : CLAIM_STATES[0][0]
    }


    def action_draft(self,cr,uid,ids,context=None):
        #set to "draft" state
        # claim_status_draft = self.pool.get('netpro.claim_status').get_by_code(cr, uid, 'D', context=context)
        claim_status_draft = CLAIM_STATES[0][0]
        return self.write(cr,uid,ids,{'state':claim_status_draft},context=context)

    def action_open(self,cr,uid,ids,context=None):
        #set to "open" state
        # claim_status_open = self.pool.get('netpro.claim_status').get_by_code(cr, uid, 'O', context=context)
        claim_status_open = CLAIM_STATES[1][0]
        return self.write(cr,uid,ids,{'state':claim_status_open},context=context)

    def action_approve(self,cr,uid,ids,context=None):
        #set to "approved" state
        # claim_status_approved = self.pool.get('netpro.claim_status').get_by_code(cr, uid, 'A', context=context)
        claim_status_approved = CLAIM_STATES[2][0]
        return self.write(cr,uid,ids,{'state':claim_status_approved},context=context)

    def action_revise(self,cr,uid,ids,context=None):
        #set to "revised" state
        # claim_status_revised = self.pool.get('netpro.claim_status').get_by_code(cr, uid, 'R', context=context)
        claim_status_revised = CLAIM_STATES[3][0]
        return self.write(cr,uid,ids,{'state':claim_status_revised},context=context)

    def action_release(self,cr,uid,ids,context=None):
        #set to "revised" state
        # claim_status_revised = self.pool.get('netpro.claim_status').get_by_code(cr, uid, 'R', context=context)
        claim_status_release = CLAIM_STATES[4][0]
        return self.write(cr,uid,ids,{'state':claim_status_release},context=context)

    def action_cancel(self,cr,uid,ids,context=None):
        #set to "cancel" state
        # claim_status_cancelled = self.pool.get('netpro.claim_status').get_by_code(cr, uid, 'X', context=context)
        claim_status_cancelled = CLAIM_STATES[5][0]
        return self.write(cr,uid,ids,{'state':claim_status_cancelled},context=context)

    def action_hold(self,cr,uid,ids,context=None):
        #set to "cancel" state
        # claim_status_hold = self.pool.get('netpro.claim_status').get_by_code(cr, uid, 'H', context=context)
        claim_status_hold = CLAIM_STATES[6][0]
        return self.write(cr,uid,ids,{'state':claim_status_hold},context=context)

        

netpro_claim()

class netpro_claim_detail(osv.osv):
    _name = 'netpro.claim_detail'
    _columns = {
        'cno': fields.char('CNO'),
        'claim_id': fields.many2one('netpro.claim', 'Claim No'),
        'benefit_id': fields.many2one('netpro.benefit', 'Benefit'),
        'treatment_date_start': fields.date('Treatment Date Start'),
        'treatment_date_end': fields.date('Treatment Date End'),
        'quantity': fields.integer('Quantity'),
        'billed': fields.float('Billed'),
        'remarks': fields.text('Remarks'),
        'claim_detail_status_id': fields.many2one('netpro.claim_detail_status', 'Status'),
        'exclude': fields.boolean('Exclude'),
        'benefit_limit': fields.float('Benefit Limit'),
        'not_affectto_overall_limit': fields.boolean('Not Affect to Overall Limit'),
        'overall_limit': fields.float('Overall Limit'),
        'usage': fields.float('Usage'),
        'balance': fields.float('Balance'),
        'family_limit': fields.float('Family Limit'),
        'family_usage': fields.float('Family Usage'),
        'family_balance': fields.float('Family Balance'),
        'system_remarks': fields.text('System Remarks'),
        'verified': fields.float('Verified'),
        'excess': fields.float('Excess'),
        'accepted': fields.float('Accepted'),
        'unpaid': fields.float('Unpaid'),
        'cash_member': fields.float('Cash Member'),
        'client_accepted': fields.float('Client Accepted'),
        'quantity_verified': fields.integer('Quantity Verified'),
        'quantity_accepted': fields.integer('Quantity Accepted'),
        'reason_id': fields.many2one('netpro.reason', 'Reason'),
        'other_reason': fields.text('Other Reason'),
        'manual_verfied': fields.float('Manual Verfied'),
        'manual_excess': fields.float('Manual Excess'),
        'manual_accepted': fields.float('Manual Accepted'),
        'tolerance': fields.float('Tolerance'),
        'tolerance_days': fields.integer('Tolerance Days'),
        'claim_id': fields.many2one('netpro.claim', 'Claim'),
    }
netpro_claim_detail()

# pindah ke vit_actuary
# class netpro_diagnosis(osv.osv):
#     _name = 'netpro.diagnosis'
#     _columns = {
#         'diagnosis': fields.char('Diagnosis'),
#         'name': fields.char('Name'),
#         'exclusion_F': fields.boolean('ExclusionF'),
#         'pre_existing_f': fields.boolean('PreExistingF'),
#         'standard_fee': fields.float('StandardFee'),
#     }
# netpro_diagnosis()

class netpro_claim_category(osv.osv):
    _name = 'netpro.claim_category'
    _columns = {
        'name': fields.char('Name'),
        'description': fields.text('Description'),
    }
netpro_claim_category()

class netpro_claim_type(osv.osv):
    _name = 'netpro.claim_type'
    _columns = {
        'name': fields.char('Name'),
        'description': fields.text('Description'),
    }
netpro_claim_type()

class netpro_claim_room(osv.osv):
    _name = 'netpro.claim_room'
    _columns = {
        'name': fields.char('Name'),
        'description': fields.text('Description'),
    }
netpro_claim_room()

class netpro_claim_reason(osv.osv):
    _name = 'netpro.claim_reason'
    _columns = {
        'name': fields.char('Name'),
        'description': fields.text('Description'),
        'claim_id': fields.many2one('netpro.claim', 'Claim'),
    }
netpro_claim_reason()

class netpro_excess_payor(osv.osv):
    _name = 'netpro.excess_payor'
    _columns = {
        'name': fields.char('Name'),
        'description': fields.text('Description'),
    }
netpro_excess_payor()

class netpro_treatment(osv.osv):
    _name = 'netpro.treatment'
    _columns = {
        'treatment': fields.char('Treatment'),
        'name': fields.char('Name'),
        'treatment_category_id': fields.many2one('netpro.treatment_category', 'Treatment Category'),
        'description': fields.text('Description'),
    }
netpro_treatment()

class netpro_treatment_category(osv.osv):
    _name = 'netpro.treatment_category'
    _columns = {
        'name': fields.char('Name'),
        'description': fields.text('Description'),
    }
netpro_treatment_category()

# class netpro_benefit(osv.osv):
#     _name = 'netpro.benefit'
#     _columns = {
#         'benefit_id': fields.char('ID'),
#         'name': fields.char('Name'),
#         'reim': fields.float('Reim'),
#         'provider_limit': fields.float('Provider Limit'),
#         'non_provider_limit': fields.float('Non Provider Limit'),
#         'unit': fields.char('Unit'),
#         'usage': fields.float('Usage'),
#         'remaining': fields.float('Remaining'),
#     }
# netpro_benefit()
class netpro_claim_status(osv.osv):
    _name = 'netpro.claim_status'
    _columns = {
        'code': fields.char('Code'),
        'name': fields.char('Name'),
        'description': fields.text('Description'),
    }


    def get_by_code(self, cr, uid, code, context=None):
        state = self.search(cr, uid, [('code','=', code )], context=context)
        return state[0]

netpro_claim_status()


class netpro_claim_detail_status(osv.osv):
    _name = 'netpro.claim_detail_status'
    _columns = {
        'name': fields.char('Name'),
        'description': fields.text('Description'),
    }
netpro_claim_detail_status()

class netpro_claim_diagnosis(osv.osv):
    _name = 'netpro.claim_diagnosis'
    _columns = {
        'claim_id': fields.many2one('netpro.claim', 'Claim'),
        'diagnosis': fields.char('Diagnosis ID'),
        'diagnosis_name': fields.char('Diagnosis Name'),
        'remarks': fields.char('Remarks'),
        'standard_fee': fields.float('Standard Fee'),
    }
netpro_claim_diagnosis()


class netpro_member(osv.osv):
    _name           = "netpro.member"
    _inherit        = "netpro.member"
    _columns     = {
        'claim_ids'  : fields.one2many('netpro.claim','member_id','Claim History', ondelete="cascade")
    }
netpro_member()