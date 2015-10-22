from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_product_plan(osv.osv):
    _name = 'netpro.product_plan'
    _columns = {
        'code': fields.char('Product Plan Code'),
        'name': fields.char('Name'),
        'short_name': fields.char('Short Name'),
        'description': fields.text('Description'),
        'product_id': fields.many2one('netpro.product', 'Product Code'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'product_plan_base_id': fields.many2one('netpro.product_plan_base', 'Product Plan'),
        'overall_limit': fields.float('Overall Limit'),
        'family_overall_limit': fields.float('Family Overall Limit'),
        'remarks_ind': fields.text('Remarks (Ind)'),
        'remarks_eng': fields.text('Remarks (Eng)'),
        'no_refund': fields.boolean('No Refund'),
        'no_refund_if_already_claim': fields.boolean('No Refund If Already Claim'),
        'by_premium_table': fields.boolean('By Premium Table'),
        'by_membership_classification': fields.boolean('By Membership Classification'),
        'benefit_limit_affect_to_calculation': fields.boolean('Benefit Limit Affect to Calculation'),
        'rate_calculation_after_loading': fields.boolean('Rate Calculation After Loading'),
        'reimbusement_affect_to_premium': fields.boolean('Reimbursement Affect To Premium'),
        'card_fee': fields.float('Card Fee'),
        'inner_limit_apply_card_fee': fields.boolean('Apply Card Fee'),
        'inner_limit_dependant_rate_base_on_male': fields.boolean('Dependant Rate base on Male'),
        'inner_limit_limit_rate': fields.float('Limit Rate'),
        'inner_limit_claim_rate': fields.float('Claim Rate'),
        'inner_limit_annual_rate': fields.float('Annual Rate'),
        'inner_limit_overall_limit_loading': fields.float('Overall Limit Loading'),
        'as_charge_apply_card_fee': fields.boolean('Apply Card Fee'),
        'as_charge_dependant_rate_base_on_male': fields.boolean('Dependant Rate base on Male'),
        'as_charge_limit_rate': fields.float('Limit Rate'),
        'as_charge_claim_rate': fields.float('Claim Rate'),
        'as_charge_annual_rate': fields.float('Annual Rate'),
        'as_charge_overall_limit_loading': fields.float('Overall Limit Loading'),
        'sub_as_charge_apply_card_fee': fields.boolean('Apply Card Fee'),
        'sub_as_charge_dependant_rate_base_on_male': fields.boolean('Dependant Rate base on Male'),
        'sub_as_charge_limit_rate': fields.float('Limit Rate'),
        'sub_as_charge_claim_rate': fields.float('Claim Rate'),
        'sub_as_charge_annual_rate': fields.float('Annual Rate'),
        'sub_as_charge_overall_limit_loading': fields.float('Overall Limit Loading'),
        'benefit_ids': fields.one2many('netpro.product_plan_benefit', 'product_plan_id', 'Benefits', ondelete='cascade'),
        'membership_ids': fields.one2many('netpro.product_plan_membership', 'product_plan_id', 'Memberships', ondelete='cascade'),
        'premium_type_ids': fields.one2many('netpro.product_plan_premium_type', 'product_plan_id', 'Premium Type', ondelete='cascade'),
        'created_by_id' : fields.many2one('res.users', 'Creator', readonly=True),
        'tpa_id' : fields.many2one('netpro.tpa', 'TPA'),

        'co_share' : fields.boolean('Co Share'),
        'co_share_value' : fields.float('Co Share (%)'),
    }

    def create(self, cr, uid, vals, context=None):
        cur_user = self.pool.get('res.users').browse(cr, uid, uid, context=None)
        tpa_val = False
        if cur_user.tpa_id:
            tpa_val = cur_user.tpa_id.id
            pass
        vals.update({
            'created_by_id':uid,
            'tpa_id':tpa_val,
        })
        
        new_record = super(netpro_product_plan, self).create(cr, uid, vals, context=context)
        return new_record
netpro_product_plan()

class netpro_product_plan_benefit(osv.osv):
    _name = 'netpro.product_plan_benefit'
    _columns = {
        'product_plan_id': fields.many2one('netpro.product_plan', 'Product Plan'),
        'benefit_id': fields.many2one('netpro.benefit', 'Benefit'),
        'benefit_limit_start': fields.float('Benefit Limit Start'),
        'benefit_limit_end': fields.float('Benefit Limit End'),
        'parent_benefit_id': fields.many2one('netpro.benefit', 'Parent Benefit'),
        'reimbursement': fields.float('Reimbursement'),
        'benefit_seq_no': fields.integer('Benefit Seq No.'),
        'limit_from_main_benefit_start': fields.float('Limit From Main Benefit Start'),
        'limit_from_main_benefit_end': fields.float('Limit From Main Benefit End'),
        'limit_from_annual_start': fields.float('Limit From Annual Start'),
        'limit_from_annual_end': fields.float('Limit From Annual End'),
        'annual_limit_after_loading': fields.boolean('Annual Limit After Loading'),
        'average_benefit_rate_and_annual_rate': fields.boolean('Average Benefit Rate And Annual Rate'),
        'not_effect_to_overall_limit': fields.boolean('Not Effect To Overall Limit'),
        'default_benefit': fields.boolean('Default Benefit'),
        'provider_per_occurance': fields.boolean('Per Occurance'),
        'provider_per_occurance_amount_limit_1': fields.float('Amount Limit 1'),
        'provider_per_occurance_amount_limit_2': fields.float('Amount Limit 2'),
        'provider_per_occurance_amount_limit_3': fields.integer('Amount Limit 3'),
        'provider_per_occurance_freq_limit': fields.integer('Freq Limit'),
        'provider_per_confinement': fields.boolean('Per Confinement'),
        'provider_per_confinement_amount_limit_1': fields.float('Amount Limit 1'),
        'provider_per_confinement_amount_limit_2': fields.float('Amount Limit 2'),
        'provider_per_confinement_amount_limit_3': fields.integer('Amount Limit 3'),
        'provider_per_confinement_freq_limit': fields.integer('Freq Limit'),
        'provider_per_year': fields.boolean('Per Year'),
        'provider_per_year_amount_limit_1': fields.float('Amount Limit 1'),
        'provider_per_year_amount_limit_2': fields.float('Amount Limit 2'),
        'provider_per_year_amount_limit_3': fields.integer('Amount Limit 3'),
        'provider_per_year_freq_limit': fields.integer('Freq Limit'),
        'provider_per_year_family_amt_limit_1': fields.float('Family Amt. Limit'),
        'provider_per_year_family_amt_limit_2': fields.float('Family Amt. Limit 2'),
        'provider_per_year_family_amt_limit_3': fields.integer('Family Amt. Limit 3'),
        'provider_per_year_family_freq_limit': fields.integer('Family Freq Limit'),
        'provider_per_company': fields.boolean('Per Company'),
        'provider_per_company_amount_limit_1': fields.float('Amount Limit 1'),
        'provider_per_company_amount_limit_2': fields.float('Amount Limit 2'),
        'provider_per_company_amount_limit_3': fields.integer('Amount Limit 3'),
        'provider_per_company_freq_limit': fields.integer('Freq Limit'),
        'non_provider_per_occurance': fields.boolean('Per Occurance'),
        'non_provider_per_occurance_amount_limit_1': fields.float('Amount Limit 1'),
        'non_provider_per_occurance_amount_limit_2': fields.float('Amount Limit 2'),
        'non_provider_per_occurance_amount_limit_3': fields.integer('Amount Limit 3'),
        'non_provider_per_occurance_freq_limit': fields.integer('Freq Limit'),
        'non_provider_per_confinement': fields.boolean('Per Confinement'),
        'non_provider_per_confinement_amount_limit_1': fields.float('Amount Limit 1'),
        'non_provider_per_confinement_amount_limit_2': fields.float('Amount Limit 2'),
        'non_provider_per_confinement_amount_limit_3': fields.integer('Amount Limit 3'),
        'non_provider_per_confinement_freq_limit': fields.integer('Freq Limit'),
        'non_provider_per_year': fields.boolean('Per Year'),
        'non_provider_per_year_amount_limit_1': fields.float('Amount Limit 1'),
        'non_provider_per_year_amount_limit_2': fields.float('Amount Limit 2'),
        'non_provider_per_year_amount_limit_3': fields.integer('Amount Limit 3'),
        'non_provider_per_year_family_amt_limit_1': fields.float('Family Amt. Limit 1'),
        'non_provider_per_year_family_amt_limit_2': fields.float('Family Amt. Limit 2'),
        'non_provider_per_year_family_amt_limit_3': fields.integer('Family Amt. Limit 3'),
        'non_provider_per_year_family_freq_limit': fields.integer('Family Freq Limit'),
        'non_provider_per_company': fields.boolean('Per Company'),
        'non_provider_per_company_amount_limit_1': fields.float('Amount Limit 1'),
        'non_provider_per_company_amount_limit_2': fields.float('Amount Limit 2'),
        'non_provider_per_company_amount_limit_3': fields.integer('Amount Limit 3'),
        'non_provider_per_company_freq_limit': fields.integer('Freq Limit'),
    }
netpro_product_plan_benefit()

class netpro_product_plan_membership(osv.osv):
    _name = 'netpro.product_plan_membership'
    #_rec_name = 'product_plan_id'
    _columns = {
        'product_plan_id': fields.many2one('netpro.product_plan', 'Product Plan'),
        'membership_id': fields.many2one('netpro.membership', 'Membership'),
        'gender_id': fields.many2one('netpro.gender', 'Gender'),
        'marital_status_id': fields.many2one('netpro.marital_status', 'Marital Status'),
    }
netpro_product_plan_membership()

class netpro_product_plan_premium_type(osv.osv):
    _name = 'netpro.product_plan_premium_type'
    #_rec_name = 'product_plan_id'
    _columns = {
        'product_plan_id': fields.many2one('netpro.product_plan', 'Product Plan'),
        'premium_type_id': fields.many2one('netpro.premium_type', 'Premium Type'),
        'premium_table_id': fields.many2one('netpro.premium_table', 'Premium Table'),
        'apply_to_policy_holder': fields.boolean('Apply To Policy Holder'),
        'apply_to_spouse': fields.boolean('Apply To Spouse'),
        'apply_to_children': fields.boolean('Apply To Children'),
    }
netpro_product_plan_premium_type()