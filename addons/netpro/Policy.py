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
# Generated by the OpenERP plugin for Dia !
from openerp.osv import fields,osv
class netpro_policy(osv.osv):
    _name = 'netpro.policy'
    _columns = {
        'PolicyNo': fields.char('Policy No'),
        'ReferenceNo': fields.char('Reference No'),
        'QuotationNo': fields.char('Quotation No'),
        'CI': fields.char('C/I'),
        'CorporateID': fields.char('Corporate ID'),
        'policy_category': fields.many2one('netpro.policy_category','Policy Category'),
        'policy_type': fields.many2one('netpro.policy_type', 'Policy Type'),
        'branch': fields.many2one('netpro.branch', 'Branch'),
        'MarketingOfficer': fields.many2one('res.partner', 'Marketing Officer'),
        'PolicyHolder': fields.many2one('res.partner', 'Policy Holder'),
        'group': fields.many2one('netpro.policy_group', 'Group'),
        'InsurancePeriodStart': fields.date('Insurance Period Start'),
        'InsurancePeriodEnd': fields.date('Insurance Period End'),
        'ExclusivePeriod': fields.boolean('Exclusive Period'),
        'toc': fields.many2one('netpro.tocTOC'),
        'Ujroh': fields.float('Ujroh'),
        'Currency': fields.many2one('res.currency', 'Currency'),
        'PolicyPayor': fields.many2one('res.partner', 'Policy Payor'),
        'InsuranceSource': fields.many2one('res.partner', 'Insurance Source'),
        'segment': fields.many2one('netpro.segment', 'Segment'),
        'PIC': fields.many2one('res.partner', 'PIC'),
        'PolicyDate': fields.date('Policy Date'),
        'BusinessSource': fields.many2one('res.partner', 'Business Source'),
        'lob': fields.many2one('netpro.lob', 'LOB'),
        'occupation': fields.many2one('netpro.occupation', 'Occupation'),
        'ExistingPolicyNo': fields.many2one('res.partner', 'Existing Policy No'),
        'region': fields.many2one('netpro.province', 'Region'),
        'Remarks': fields.text('Remarks'),
        'payment_option_mode': fields.many2one('netpro.payment_option_mode', 'Payment Option Mode'),
        'payment_option_installment': fields.many2one('netpro.payment_option_installment', 'Payment Option Installment'),
        'RefundAdj': fields.float('Refund Adj.'),
        'RefundwithClaimDeduction': fields.boolean('Refund with Claim Deduction'),
        'EndorsementFee': fields.float('Endorsement Fee'),
        'EndorsementwithInstallment': fields.boolean('Endorsement with Installment'),
        'refund_type': fields.many2one('netpro.refund_type', 'Add / Refund Type'),
        'Norefundchangingpremiumdifference': fields.boolean('No refund changing premium difference'),
        'PrintCardName': fields.char('Print Name'),
        'print_card_order': fields.many2one('netpro.print_card_order', 'Print Order'),
        'PrintCardBirthdate': fields.boolean('Print Birthdate'),
        'PrintCardSex': fields.boolean('Print Sex'),
        'PrintCardPlan': fields.boolean('Print Plan'),
        'tpa': fields.many2one('netpro.tpa', 'TPA'),
        'calculation_method': fields.many2one('netpro.calculation_method', 'Calculation Method'),
        'prorate_calc_method': fields.many2one('netpro.prorate_calc_method', 'Prorate Calc Method'),
        'expired_claim_receipt': fields.many2one('netpro.expired_claim_receipt', 'Expired Claim Receipt'),
        'PaymentDueDays': fields.integer('Payment Due Days'),
        'payment_due_interval': fields.many2one('netpro.payment_due_interval', 'Payment Due Interval'),
        'MaxAgeChildren': fields.integer('Max Age Children'),
        'max_children': fields.many2one('netpro.max_children', 'Max Children'),
        'max_children_maternity': fields.many2one('netpro.max_children_maternity', 'Max Children Maternity'),
        'card_type': fields.many2one('netpro.card_type', 'Card Type'),
        'pre_existing_condition': fields.many2one('netpro.pre_existing_condition', 'Pre Existing Condition'),
        'ToleranceUpRoomPercent': fields.integer('Tolerance Up Room Percent'),
        'ToleranceUpRoomAmount': fields.float('ToleranceUpRoomAmount'),
        'up_room_class': fields.many2one('netpro.up_room_class', 'Up Room Class'),
        'UpRoomClassDays': fields.integer('Up Room Class Days'),
        'ProrateAfterToleranceAddition': fields.boolean('Prorate After Tolerance Addition'),
        'AllowAdultChildPremium': fields.boolean('Allow Adult Child Premium'),
        'HaveSubCompany': fields.boolean('Have Sub Company'),
        'FemaleSpouseOnly': fields.boolean('Female Spouse Only'),
        'ProfitSharing': fields.boolean('Profit Sharing'),
        'UseInHouseClinic': fields.boolean('Use In House Clinic'),
        'AllowPlanSharing': fields.boolean('Allow Plan Sharing'),
        'RenewalwithOldCard': fields.boolean('Renewal with Old Card'),
        'RenewalManual': fields.boolean('Renewal Manual (TPA)'),
        'CommissionbyGrossPremium': fields.boolean('Commission by Gross Premium'),
        'AllowExcessonReimbursement': fields.boolean('Allow Excess on Reimbursement'),
        'ASODeposit': fields.float('ASO Deposit'),
        'Bank': fields.many2one('res.partner.bank', 'Bank'),
        'VAccountNo': fields.char('V Account No'),
        'BankOptional': fields.many2one('res.partner.bank', 'Bank Optional', help='Relasi ke Partner Bank'),
        'VAccountNoOptional': fields.char('V Account No Optional'),
        'policy_status': fields.many2one('netpro.policy_status', 'Policy Status'),
        'EndorsementDate': fields.date('Endorsement Date'),
        'EmailDate': fields.date('EmailDate'),
        'IntEndorsementNo': fields.integer('Int. Endorsement No'),
        'ExtEndorsementNo': fields.integer('Ext. Endorsement No'),
        'PNO': fields.integer('PNO'),
        'PPNO': fields.integer('PPNO'),
        'CancelPolicy': fields.boolean('Cancel Policy'),
        'ProfitSharingEndorsement': fields.boolean('Profit Sharing Endorsement'),
        'CreatedBy': fields.many2one('res.partner', 'Created By'),
        'CreatedByDate': fields.datetime('Created By Date'),
        'LastEditedBy': fields.many2one('res.partner', 'Last Edited By'),
        'LastEditedByDate': fields.datetime('Last Edited By Date'),
        'ApprovedBy': fields.many2one('res.partner', 'Approved By'),
        'ApprovedByDate': fields.datetime('Approved By Date'),
        'claim_rule_reimbursement_payee': fields.many2one('netpro.claim_rule', 'Reimbursement Payee'),
        'claim_rule_excess_payor': fields.many2one('netpro.claim_rule', 'Excess Payor'),
        'claim_rule_refund_payee': fields.many2one('netpro.claim_rule', 'Refund Payee'),
        'correspondence_rule_premium': fields.many2one('netpro.correspondence_rule', 'Premium'),
        'correspondence_rule_claim': fields.many2one('netpro.correspondence_rule', 'Claim'),
        'DiscountSpecialDiscount': fields.float('Special Discount'),
        'DiscountDirectDiscount': fields.float('Direct Discount'),
        'DiscountDiscountAmount': fields.float('Discount Amount'),
        'DiscountDiscountOnlyApplyOnPolicy': fields.boolean('Discount Only Apply On Policy'),
        'LoadingCCLoading': fields.float('CC Loading'),
        'DepositDepositRecovery': fields.float('Deposit Recovery'),
        'ClaimReimbursementTransferFee': fields.float('Fee (per employee)'),
        'OtherSettingsAdminCost': fields.float('Admin Cost'),
        'OtherSettingsCardFee': fields.float('@Card Fee'),
        'OtherSettingsTotalCardFee': fields.float('Total Card Fee'),
        'OtherSettingsTotalAdminCost': fields.float('Total Admin Cost'),
        'OtherSettingsStampDuty': fields.float('Stamp Duty'),
        'OtherSettingsInterest': fields.float('Interest'),
        'PoolFundInfoPoolFund': fields.float('Pool Fund'),
        'PoolFundInfoMaxPoolFundMember': fields.integer('Max Pool Fund Member'),
        'PoolFundInfoMaxMemberPoolFund': fields.float('@Max Member Pool Fund'),
        'PoolFundInfoRemarks': fields.text('Remarks'),
        'EDCApplyProrate': fields.boolean('Apply Prorate'),
        'EDCShowExcessAmount': fields.boolean('Show Excess Amount'),
        'EDCShowExcessRemarks': fields.boolean('Show Excess Remarks'),
        'EDCExcessRemarks': fields.text('Excess Remarks'),
        'EDCDisableEDCForInpatient': fields.boolean('Disable EDC For Inpatient'),
        'EDCDisableEDCForOutpatient': fields.boolean('Disable EDC For Outpatient'),
        'EDCDisableEDCForMaternity': fields.boolean('Disable EDC For Maternity'),
        'EDCDisableEDCForDental': fields.boolean('Disable EDC For Dental'),
        'EDCDisableSwipeForExcessedLimit': fields.boolean('Disable Swipe For Excessed Limit'),
        'EDCIgnoreClaimOverBelowSettings': fields.boolean('Ignore Claim Over Below Settings'),
        'EDCInpatient': fields.integer('Inpatient'),
        'EDCOutpatient': fields.integer('Outpatient'),
        'EDCMaternity': fields.integer('Maternity'),
        'EDCDental': fields.integer('Dental'),
        'ProfitSharingSharingRemarks': fields.text('Sharing Remarks'),
        'ProfitSharingGrossPremium': fields.float('Gross Premium'),
        'ProfitSharingClaimPaid': fields.float('Claim Paid'),
        'ProfitSharingClaimRatio': fields.float('Claim Ratio'),
        'ProfitSharingFormula': fields.text('Formula'),
        'ProfitSharingProfitSharing': fields.float('Profit Sharing'),
        'ProfitSharingAdjustment': fields.float('Adjustment'),
        'ProfitSharingProfitSharingAmt': fields.float('Profit Sharing Amt'),
        'Coverage_ids': fields.one2many('netpro.coverage', 'Policy_id', 'Coverages', ondelete='cascade'),
        'Class_ids': fields.one2many('netpro.class', 'Policy_id', 'Classes', ondelete='cascade'),
        'Plan_schedule_ids': fields.one2many('netpro.plan_schedule', 'Policy_id', 'Plan Schedules', ondelete='cascade'),
        'Business_source_ids': fields.one2many('netpro.business_source', 'Policy_id', 'Business Sources', ondelete='cascade'),
    }
netpro_policy()

class netpro_policy_category(osv.osv):
    _name = 'netpro.policy_category'
    _columns = {
        'Name': fields.char('Name'),
        'Code': fields.char('Code'),
        'Notes': fields.text('Notes'),
    }
netpro_policy_category()

class netpro_policy_type(osv.osv):
    _name = 'netpro.policy_type'
    _columns = {
        'Name': fields.char('Name'),
        'Code': fields.char('Code'),
        'Notes': fields.text('Notes'),
    }
netpro_policy_type()

class netpro_policy_group(osv.osv):
    _name = 'netpro.policy_group'
    _columns = {
        'Name': fields.char('Name'),
        'Code': fields.char('Code'),
        'Notes': fields.text('Notes'),
    }
netpro_policy_group()

class netpro_toc(osv.osv):
    _name = 'netpro.toc'
    _columns = {
        'TOC': fields.char('TOC'),
        'Description': fields.text('Description'),
        'Ujroh': fields.float('Ujroh'),
    }
netpro_toc()

class netpro_segment(osv.osv):
    _name = 'netpro.segment'
    _columns = {
        'Segment': fields.char('Segment'),
        'Description': fields.text('Description'),
    }
netpro_segment()

class netpro_lob(osv.osv):
    _name = 'netpro.lob'
    _columns = {
        'LOB': fields.char('LOB'),
        'Description': fields.text('Description'),
    }
netpro_lob()

class netpro_occupation(osv.osv):
    _name = 'netpro.occupation'
    _columns = {
        'Occupation': fields.char('Occupation'),
        'Description': fields.text('Description'),
    }
netpro_occupation()

class netpro_province(osv.osv):
    _name = 'netpro.province'
    _columns = {
        'Name': fields.char('Name'),
        'Country': fields.many2one('res.country', 'Country'),
    }
netpro_province()

class netpro_payment_option_mode(osv.osv):
    _name = 'netpro.payment_option_mode'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_payment_option_mode()

class netpro_payment_option_installment(osv.osv):
    _name = 'netpro.payment_option_installment'
    _columns = {
        'Name': fields.char('Name'),
        'Point': fields.integer('Point'),
        'Description': fields.text('Description'),
    }
netpro_payment_option_installment()

class netpro_refund_type(osv.osv):
    _name = 'netpro.refund_type'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_refund_type()

class netpro_print_card_order(osv.osv):
    _name = 'netpro.print_card_order'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_print_card_order()

class netpro_calculation_method(osv.osv):
    _name = 'netpro.calculation_method'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_calculation_method()

class netpro_prorate_calc_method(osv.osv):
    _name = 'netpro.prorate_calc_method'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_prorate_calc_method()

class netpro_expired_claim_receipt(osv.osv):
    _name = 'netpro.expired_claim_receipt'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_expired_claim_receipt()

class netpro_payment_due_interval(osv.osv):
    _name = 'netpro.payment_due_interval'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_payment_due_interval()

class netpro_max_children(osv.osv):
    _name = 'netpro.max_children'
    _columns = {
        'Name': fields.char('Name'),
        'Point': fields.integer('Point'),
        'Description': fields.text('Description'),
    }
netpro_max_children()

class netpro_max_children_maternity(osv.osv):
    _name = 'netpro.max_children_maternity'
    _columns = {
        'Name': fields.char('Name'),
        'Point': fields.integer('Point'),
        'Description': fields.text('Description'),
    }
netpro_max_children_maternity()

class netpro_card_type(osv.osv):
    _name = 'netpro.card_type'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_card_type()

class netpro_pre_existing_condition(osv.osv):
    _name = 'netpro.pre_existing_condition'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_pre_existing_condition()

class netpro_up_room_class(osv.osv):
    _name = 'netpro.up_room_class'
    _columns = {
        'Name': fields.char('Name'),
        'Point': fields.integer('Point'),
    }
netpro_up_room_class()

class netpro_policy_status(osv.osv):
    _name = 'netpro.policy_status'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_policy_status()

class netpro_coverage(osv.osv):
    _name = 'netpro.coverage'
    _columns = {
        'PdiructType': fields.many2one('netpro.product_type', 'Product Type'),
        'ProductId': fields.many2one('netpro.product_id', 'Product ID'),
        'Reimbursement': fields.float('Reimbursement'),
        'Provider': fields.float('Provider'),
        'ExcessPayontheSpot': fields.boolean('Excess Pay on the Spot'),
        'SwipeCard': fields.boolean('Swipe Card'),
        'ShowCard': fields.boolean('ShowCard'),
        'ReimbursementBoolean': fields.boolean('Reimbursement'),
        'NoPlan': fields.integer('No Plan'),
        'NoOfBenefit': fields.integer('No Of Benefit'),
        'DefaultLimit': fields.many2one('netpro.default_limit', 'Default Limit'),
        'AnnualLimitPerDisability': fields.boolean('Annual Limit Per Disability'),
        'FamilyLimit': fields.boolean('Family Limit'),
        'FamilyPremium': fields.boolean('Family Premium'),
        'UseChildPremium': fields.boolean('Use Child Premium'),
        'ASOCoverage': fields.boolean('ASO Coverage'),
        'HiPlan': fields.boolean('Hi Plan'),
        'MaximumAgeEmployee': fields.integer('Maximum Age Employee'),
        'MaximumAgeSpouse': fields.integer('Maximum Age Spouse'),
        'MaximumAgeChildren': fields.integer('Maximum Age Children'),
        'ASOFeePerMember': fields.float('ASO Fee Per Member'),
        'ASOCommission': fields.float('ASO Commission'),
        'ASOCommissionInPercent': fields.float('ASO Commission In Percent'),
        'ASOFeePerClaim': fields.float('ASO Fee Per Claim'),
        'ASOFeePerClaimAmount': fields.float('ASO Fee Per Claim Amount'),
        'NotProcessExcessonDeposit': fields.boolean('Not Process Excess on Deposit'),
        'PrintOptionSeqNo': fields.integer('Seq No.'),
        'PrintOptionPrintTextOnCard': fields.char('Print Text (On Card)'),
        'PrintCardwithPlanAmount': fields.boolean('Print Card with Plan Amount'),
        'MembershipOptionNotAllowedforEmployee': fields.boolean('Not Allowed for Employee'),
        'MembershipOptionNotAllowedforSpouse': fields.boolean('Not Allowed for Spouse'),
        'MembershipOptionNotAllowedforChild': fields.boolean('Not Allowed for Child'),
        'Policy_id': fields.many2one('netpro.policy', 'Policy'),
    }
netpro_coverage()

class netpro_class(osv.osv):
    _name = 'netpro.class'
    _columns = {
        'ClassNo': fields.integer('Class No'),
        'ShortDesc': fields.char('Short Desc'),
        'Description': fields.text('Description'),
        'Policy_id': fields.many2one('netpro.policy', 'Policy'),
        'Membership_plan_ids': fields.one2many('netpro.membership_plan', 'class_id', 'Membership Plans', ondelete='cascade'),
    }
netpro_class()

class netpro_plan_schedule(osv.osv):
    _name = 'netpro.plan_schedule'
    _columns = {
        'Product_plan': fields.many2one('netpro.product_plan', 'Product Plan'),
        'BAmount': fields.float('BAmount'),
        'Reimbursement': fields.float('Reimbursement'),
        'ReimbursementAffectToBenefit': fields.boolean('Reimbursement Affect To Benefit'),
        'IndividualOverallLimitAmountPoint': fields.integer('Individual Overall Limit Amount'),
        'IndividualOverallLimitAmountInterval': fields.integer('Individual Overall Limit Amount Interval'),
        'FamilyOverallLimitAmountPoint': fields.integer('Family Overall Limit Amount'),
        'FamilyOverallLimitAmountInterval': fields.integer('Family Overall Limit Amount Inteval'),
        'DependantLimit': fields.integer('Dependant Limit'),
        'SpouseLimit': fields.integer('Spouse Limit'),
        'ChildLimit': fields.integer('@Child Limit'),
        '1Dependant': fields.char('+1 Dependant'),
        '2Dependant': fields.char('+2 Dependant'),
        '3Dependant': fields.char('+3 Dependant'),
        '4Dependant': fields.char('+4 Dependant'),
        '5Dependant': fields.char('+5 Dependant'),
        '6Dependant': fields.char('+6 Dependant'),
        '7Dependant': fields.char('+7 Dependant'),
        '8Dependant': fields.char('+8 Dependant'),
        '9Dependant': fields.char('+9 Dependant'),
        'AggregateLimit': fields.integer('Aggregate Limit'),
        'GroupDiscount': fields.float('Group Discount'),
        'PremiumDiscount': fields.float('Premium Discount'),
        'Loading': fields.float('Loading'),
        'Deductible': fields.float('Deductible'),
        'NoRefund': fields.boolean('No Refund'),
        'NoRefundIfAnyClaim': fields.boolean('No Refund If Any Claim'),
        'HiPlan': fields.boolean('Hi Plan (Apply As Charge if R&B Same or Lower than Taken Benefit)'),
        'ASOPlan': fields.boolean('ASO Plan'),
        'MaximumAgeEmployee': fields.integer('For Employee'),
        'MaximumAgeSpouse': fields.integer('For Spouse'),
        'MaximumAgeChildren': fields.integer('For Children'),
        'SequenceNo': fields.integer('Sequence No'),
        'Provider_level': fields.many2one('netpro.provider_level', 'Provider Level'),
        'Plan_schedule_detail_benefit_schedule_ids': fields.one2many('netpro.plan_schedule_detail_benefit_schedule', 'plan_schedule_id', 'Plan Schedule', ondelete='cascade'),
        'Policy_id': fields.many2one('netpro.policy', 'Policy'),
    }
netpro_plan_schedule()

class netpro_business_source(osv.osv):
    _name = 'netpro.business_source'
    _columns = {
        'Agent': fields.many2one('netpro.agent', 'Agent'),
        'Type': fields.many2one('netpro.business_source_type', 'Type'),
        'Commission': fields.float('Commission'),
        'CommissionOnlyApplyOnNewBusiness': fields.boolean('Commission Only Apply On New Business'),
        'ASOCommission': fields.boolean('ASO Commission'),
        'ASOCommissiononlyapplyonNewBusiness': fields.boolean('ASO Commission only apply on New Business'),
        'ASORemarksbySystem': fields.text('ASO Remarks by System'),
        'Policy_id': fields.many2one('netpro.policy', 'Policy'),
    }
netpro_business_source()

class netpro_product_type(osv.osv):
    _name = 'netpro.product_type'
    _columns = {
        'ProductType': fields.char('Product Type'),
        'Description': fields.text('Description'),
    }
netpro_product_type()

class netpro_product_id(osv.osv):
    _name = 'netpro.product_id'
    _columns = {
        'ProductID': fields.char('Product ID'),
        'Description': fields.text('Description'),
    }
netpro_product_id()

class netpro_default_limit(osv.osv):
    _name = 'netpro.default_limit'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_default_limit()

class netpro_product_plan(osv.osv):
    _name = 'netpro.product_plan'
    _columns = {
        'pplan': fields.char('PPlan'),
        'Name': fields.char('Name'),
    }
netpro_product_plan()

class netpro_provider_level(osv.osv):
    _name = 'netpro.provider_level'
    _columns = {
        'PLevel': fields.char('PLevel'),
        'Description': fields.text('Description'),
    }
netpro_provider_level()

class netpro_agent(osv.osv):
    _name = 'netpro.agent'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_agent()

class netpro_business_source_type(osv.osv):
    _name = 'netpro.business_source_type'
    _columns = {
        'Name': fields.char('Name'),
        'Description': fields.text('Description'),
    }
netpro_business_source_type()

class netpro_membership_plan(osv.osv):
    _name = 'netpro.membership_plan'
    _columns = {
        'class_id': fields.many2one('netpro.class', 'Class'),
        'as_employee': fields.boolean('Employee'),
        'as_spouse': fields.boolean('Spouse'),
        'as_child': fields.boolean('Child'),
        'product_plan': fields.many2one('netpro.product_plan', 'Product Plan'),
        'male_female_bamount': fields.float('Male / Female BAmount'),
        'occur_in_other_membership': fields.boolean('Occur in Other Membership'),
    }
netpro_membership_plan()

class netpro_plan_schedule_detail_benefit_schedule(osv.osv):
    _name = 'netpro.plan_schedule_detail_benefit_schedule'
    _columns = {
        'plan_schedule_id': fields.many2one('netpro.plan_schedule', 'Plan Schedule'),
        'product_plan': fields.many2one('netpro.product_plan', 'Product Plan'),
        'bamount': fields.float('BAmount'),
        'benefit_id': fields.many2one('netpro.benefit', 'Benefit ID'),
        'parent_benefit_id': fields.many2one('netpro.benefit', 'Parent Benefit'),
        'pre': fields.char('Pre'),
        'post': fields.char('Post'),
        'min_allowed': fields.float('Min Allowed'),
        'max_allowed': fields.float('Max Allowed'),
        'difference _provider_non_provider': fields.boolean('Difference Provider & Non Provider'),
        'not_affect_to_overall_limit': fields.boolean('Not Affect to Overall Limit'),
        'occurance_inner_limit': fields.boolean('Occurance Inner Limit'),
        'occurance_inner_limit_limit': fields.float('Limit'),
        'occurance_inner_limit_max': fields.float('Max'),
        'occurance_inner_limit_std': fields.float('Std.'),
        'confinement_inner_limit': fields.boolean('Confinement Inner Limit'),
        'confinement_inner_limit_limit': fields.float('Limit'),
        'confinement_inner_limit_max': fields.float('Max'),
        'confinement_inner_limit_std': fields.float('Std.'),
        'annual_inner_limit': fields.boolean('Annual Inner Limit'),
        'annual_inner_limit_limit': fields.float('Limit'),
        'annual_inner_limit_max': fields.float('Max'),
        'annual_inner_limit_std': fields.float('Std.'),
        'annual_inner_limit_family': fields.float('Family'),
        'annual_inner_limit_max_family': fields.float('Family Max'),
        'annual_inner_limit_std_family': fields.float('Family Std.'),
        'company_inner_limit': fields.boolean('Company Inner Limit'),
        'company_inner_limit_limit': fields.float('Limit'),
        'company_inner_limit_max': fields.float('Max'),
        'company_inner_limit_std': fields.float('Std.'),
        'company_inner_limit_reimbursement': fields.float('Reimbursement'),
        'company_inner_limit_seq_no': fields.integer('Seq. No.'),
        'non_provider_occurance_inner_limit': fields.boolean('Occurance Inner Limit'),
        'non_provider_occurance_inner_limit_limit': fields.float('Limit'),
        'non_provider_occurance_inner_limit_max': fields.float('Max'),
        'non_provider_occurance_inner_limit_std': fields.float('Std.'),
        'non_provider_confinement_inner_limit': fields.boolean('Confinement Inner Limit'),
        'non_provider_confinement_inner_limit_limit': fields.float('Limit'),
        'non_provider_confinement_inner_limit_max': fields.float('Max'),
        'non_provider_confinement_inner_limit_std': fields.float('Std.'),
        'non_provider_annual_inner_limit': fields.boolean('Annual Inner Limit'),
        'non_provider_annual_inner_limit_limit': fields.float('Limit'),
        'non_provider_annual_inner_limit_max': fields.float('Max'),
        'non_provider_annual_inner_limit_std': fields.float('Std.'),
        'non_provider_annual_inner_limit_family_limit': fields.float('Family'),
        'non_provider_annual_inner_limit_family_max': fields.float('Family Max'),
        'non_provider_annual_inner_limit_family_std': fields.float('Family Std.'),
        'non_provider_company_inner_limit': fields.boolean('Company Inner Limit'),
        'non_provider_company_inner_limit_limit': fields.float('Limit'),
        'non_provider_company_inner_limit_max': fields.float('Max'),
        'non_provider_company_inner_limit_std': fields.float('Std.'),
    }
netpro_plan_schedule_detail_benefit_schedule()

class netpro_plan_schedule_detail_diagnosis_exclusion(osv.osv):
    _name = 'netpro.plan_schedule_detail_diagnosis_exclusion'
    _columns = {
        'plan_schedule_id': fields.many2one('netpro.plan_schedule', 'Plan Schedule'),
        'master_diagnosis_exclusion_id': fields.many2one('netpro.master_diagnosis_exclusion', 'Master Diagnosis Exclusion'),
        'Description': fields.text('Description'),
    }
netpro_plan_schedule_detail_diagnosis_exclusion()

class netpro_plan_schedule_detail_diagnosis_exclusion_exception(osv.osv):
    _name = 'netpro.plan_schedule_detail_diagnosis_exclusion_exception'
    _columns = {
        'plan_schedule_id': fields.many2one('netpro.plan_schedule', 'Plan Schedule'),
        'master_diagnosis_exclusion_id': fields.many2one('netpro.master_diagnosis_exclusion', 'Master Diagnosis Exclusion'),
        'Description': fields.text('Description'),
    }
netpro_plan_schedule_detail_diagnosis_exclusion_exception()

class netpro_benefit(osv.osv):
    _name = 'netpro.benefit'
    _columns = {
        'BenefitId': fields.char('Benefit ID'),
        'Name': fields.char('Name'),
        'As_parent': fields.boolean('As Parent'),
    }
netpro_benefit()

class netpro_master_diagnosis_exclusion(osv.osv):
    _name = 'netpro.master_diagnosis_exclusion'
    _columns = {
        'DiagnosisId': fields.char('Diagnosis ID'),
        'DiagnosisDescription': fields.text('Diagnosis Description'),
        'Poly': fields.char('Poly'),
        'As_exception': fields.boolean('As Exception'),
    }
netpro_master_diagnosis_exclusion()

