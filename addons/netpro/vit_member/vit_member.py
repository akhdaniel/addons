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
import time
from datetime import date


class netpro_member(osv.osv):
    _name = 'netpro.member'
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'name'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', select=True, ondelete='cascade'),
        'policy_id': fields.many2one('netpro.policy', 'Policy', domain='[("state","=","approved"),]'),
        'policy_holder': fields.related('policy_id', 'policy_holder_id', 
            relation='res.partner', type='many2one', store=True, string='Policy Holder'),
        'policy_category': fields.related('policy_id', 'policy_category_id', 
            relation='netpro.policy_category', type='many2one', store=False, string='Policy Category'),
        'insurance_period_start': fields.date('Insurance Period Start'),
        'insurance_period_end': fields.date('Insurance Period End'),
        'member_no': fields.char('Member No.',help="Kosongkan untuk diisi oleh sistem"),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'census_no': fields.selection([('0','0 = Employee'),('1','1 = Spouse'),('2','2 = 1st Child')],'Census No.'),
        'gender_id': fields.many2one('netpro.gender', 'Sex'),
        'marital_status': fields.many2one('netpro.marital_status', 'Marital Status'),
        'member_email': fields.char('Member Email'),
        'mobile_phone': fields.char('Mobile Phone'),
        'date_of_birth': fields.date('DoB'),
        'age': fields.integer('Age'),
        'birth_place': fields.char('Birth Place'),
        'salary': fields.float('Salary'),
        'vip': fields.boolean('VIP'),
        'black_listed': fields.boolean('Black Listed '),
        'hold_car_swipe_claim': fields.boolean('Hold Card Swipe And Claim'),
        'remarks': fields.text('Remarks'),
        'class_id': fields.many2one('netpro.class', 'Class'),
        'membership_id': fields.many2one('netpro.membership', 'Membership'),
        'card_no': fields.char('Card No'),
        'register_no': fields.char('Register No.'),
        'period_start': fields.date('Period Start'),
        'period_end': fields.date('Period End'),
        'stnc': fields.date('STNC'),
        'group_id': fields.char('Group ID'),
        'payor_id': fields.many2one('res.partner', 'Payor'),
        'premium_type_id': fields.many2one('netpro.premium_type', 'Premium Type'),
        'area_id': fields.many2one('res.country.state', 'Area'),
        'pre_existing_waived': fields.boolean('Pre Existing Waived'),
        'exclude_this_member': fields.boolean('Exclude this Member'),
        'dummy_member': fields.boolean('Dummy Member'),
        'mno': fields.float('MNO', readonly=True),
        'pmno': fields.integer('PMNO', readonly=True),
        'state': fields.selection([('draft','Draft'), ('actived','Actived'), ('nonactive', 'Non Active')],'Status'),
        #'status': fields.selection([('draft','Draft'), ('actived','Actived'), ('nonactive', 'Non Active')],'Policy Status'),
        'trans_type': fields.char('Trans. Type', readonly=True),
        'suspend_tpa': fields.boolean('Suspend TPA', readonly=True),
        'account_no': fields.char('Account No'),
        'account_name': fields.char('Account Name'),
        'bank': fields.char('Bank'),
        'bank_name': fields.char('Bank Name'),
        'bank_branch': fields.char('Bank Branch'),
        'company_address': fields.text('Address'),
        'title': fields.char('Title'),
        'division': fields.char('Division'),
        'branch': fields.char('Branch'),
        'occupation': fields.char('Occupation'),
        'id_no': fields.char('ID No'),
        'province': fields.char('Province'),
        'height': fields.integer('Height'),
        'weight': fields.integer('Weight'),
        'member_plan_ids': fields.one2many('netpro.member_plan', 'member_id', 'Plans', ondelete='cascade'),
        'family_ids': fields.one2many('netpro.member', 'parent_id', 'Families', ondelete='cascade'),
        'claim_history_ids': fields.one2many('netpro.member_claim_history', 'member_id', 'Claim Histories', ondelete='cascade'),
        'parent_id': fields.many2one('netpro.member', 'Parent'),
        'created_by_id': fields.many2one('res.users', 'Created By', readonly=True),
        'upd_code' : fields.selection([('C','C'),('N','N'),('M','M'),('R','R')], 'Update Code'),
        'upd_date' : fields.date('Update Date'),
        'masa_tunggu': fields.boolean('Masa Tunggu'),
        'masa_tunggu_value': fields.integer('Lama Masa Tunggu'),
        'grace_period': fields.boolean('Grace Period'),
        'grace_period_value': fields.integer('Grace Period Days'),
        'member_policy_exception_check' : fields.boolean('Policy Exception'),
        'member_policy_exception_ids' : fields.one2many('netpro.member_policy_exception','member_id','Policy Exception', ondelete="cascade"),
        'limit_member_excessed' : fields.boolean('Limit Member Excessed'),
    }

    _defaults = {
        'state'                     : 'draft',
        'insurance_period_start'    : lambda *a : time.strftime("%Y-%m-%d"),
        'insurance_period_end'      : lambda *a : time.strftime("%Y-%m-%d"),
        'created_by_id'             : lambda obj, cr, uid, context: uid,
        'upd_date'                  : lambda *a : time.strftime("%Y-%m-%d"),
    }

    _sql_constraints = [
        ('member_no_unique', 'UNIQUE(member_no)', 'Member No. Must be Unique!'),
    ]

    def create(self, cr, uid, vals, context=None):

        if vals['parent_id']:
            this = self.browse(cr, uid, vals['parent_id'], context=None)
            policy_obj = this.policy_id
            vals.update({
                'policy_id' : policy_obj.id,
                'insurance_period_start' : policy_obj.insurance_period_start,
                'insurance_period_end' : policy_obj.insurance_period_end,
            })

            if policy_obj.policy_category_id.name == 'Individual':
                #import pdb;pdb.set_trace()
                if policy_obj.individual_member_limit > 0:
                    if len(this.family_ids) == policy_obj.individual_member_limit-1:
                        raise osv.except_orm(('Warning!'),("Member limit excessed. Cannot add more than "+ str(policy_obj.individual_member_limit) +" member(s) to this Policy."))

        if not vals['member_no']:
            vals.update({
                'member_no' : self.pool.get('ir.sequence').get(cr, uid, 'member_seq') or '/',
            })
        return super(netpro_member, self).create(cr, uid, vals, context=context)

    def action_confirm(self,cr,uid,ids,context=None):
        # create schedule plan
        self.create_plan_schedule(cr,uid,ids,context=context)
        #set to "actived" state
        self.write(cr,uid,ids,{'state':'actived'},context=context)
        return
    
    def action_cancel(self,cr,uid,ids,context=None):
        #set to "draft" state
        return self.write(cr,uid,ids,{'state':'draft'},context=context)
    
    def action_nonactive(self,cr,uid,ids,context=None):
        #set to "nonactive" state
        return self.write(cr,uid,ids,{'state':'nonactive'},context=context) 

    def create_plan_schedule(self, cr, uid, ids, context=None):
        #import pdb;pdb.set_trace()
        pplan_bnft_obj      = self.pool.get('netpro.product_plan_benefit')
        member_plan_obj     = self.pool.get('netpro.member_plan')
        member_plan_det_obj = self.pool.get('netpro.member_plan_detail')
        self_obj            = self.browse(cr,uid,ids[0],context=context)
        # jika belum ada schedule
        if not self_obj.member_plan_ids:
            if self_obj.policy_id:
                #jika policy ny sdh aproved
                if self_obj.policy_id.state in ['approved','endorsed']:
                    #import pdb;pdb.set_trace()
                    plan_schedule_ids = self_obj.policy_id.plan_schedule_ids
                    if plan_schedule_ids:
                        for schedule in plan_schedule_ids:
                            #jika plan for sama dan classnya sama
                            if schedule.class_id.id == self_obj.class_id.id :
                                #create schedule
                                plan_schedule_id = member_plan_obj.create(cr,uid,{'member_id': ids[0],
                                                                                'product_plan_id': schedule.product_plan_id.id,
                                                                                'bamount' : schedule.bamount,
                                                                                'plan_limit' : schedule.overall_limit,
                                                                                'family_limit' : schedule.family_overall_limit_amount_point,
                                                                                'plan_for':self_obj.membership_id.name})  
                                # jika ada detail benefitnya maka di create juga benefit yang sama
                                if schedule.plan_schedule_detail_benefit_schedule_ids :
                                    for benefit in schedule.plan_schedule_detail_benefit_schedule_ids:
                                        prov_limit = 999999999
                                        non_prov_limit = 999999999
                                        unit = False
                                        pembeda = benefit.difference_provider_non_provider                                            

                                        # PER TAHUN
                                        if benefit.annual_inner_limit:
                                            unit = 'Annual'
                                            if benefit.annual_inner_limit_max != 0:
                                                unit = str(benefit.annual_inner_limit_max) + ', ' + unit

                                            if benefit.annual_inner_limit_limit != 0:
                                                prov_limit = benefit.annual_inner_limit_limit
                                                if pembeda:
                                                    non_prov_limit = benefit.non_provider_annual_inner_limit_limit
                                                else :
                                                    non_prov_limit = benefit.annual_inner_limit_limit

                                        # PER HARI
                                        if benefit.occurance_inner_limit:

                                            if benefit.occurance_inner_limit_max != 0:
                                                if not unit:
                                                    unit = str(benefit.occurance_inner_limit_max) + ', ' + 'Occurance'
                                                else :
                                                    unit += ', ' + str(benefit.occurance_inner_limit_max) + ', ' + 'Occurance'
                                            else :
                                                if not unit:
                                                    unit = '0, Occurance'
                                                else :
                                                    unit += '0, Occurance'

                                            if benefit.occurance_inner_limit_limit != 0:
                                                prov_limit = benefit.occurance_inner_limit_limit
                                                if pembeda:
                                                    non_prov_limit = benefit.non_provider_occurance_inner_limit_limit
                                                else :
                                                    non_prov_limit = benefit.occurance_inner_limit_limit

                                        # PER KEJADIAN
                                        if benefit.confinement_inner_limit:

                                            if benefit.confinement_inner_limit_max != 0:
                                                if not unit:
                                                    unit = str(benefit.confinement_inner_limit_max) + ', ' + 'Confinement'
                                                else :
                                                    unit += ', ' + str(benefit.confinement_inner_limit_max) + ', ' + 'Confinement'
                                            else :
                                                if not unit:
                                                    unit = '0, Confinement'
                                                else :
                                                    unit += '0, Confinement'

                                            if benefit.confinement_inner_limit_limit != 0:
                                                prov_limit = benefit.confinement_inner_limit_limit
                                                if pembeda:
                                                    non_prov_limit = benefit.non_provider_confinement_inner_limit_limit
                                                else :
                                                    non_prov_limit = benefit.confinement_inner_limit_limit


                                        member_plan_det_obj.create(cr,uid,{'member_plan_id':plan_schedule_id,
                                                                           'benefit_id': benefit.benefit_id.id,
                                                                           'unit':unit,
                                                                           'provider_limit':prov_limit,
                                                                           'non_provider_limit':non_prov_limit,
                                                                           'remaining':prov_limit,
                                                                           })                                    

        return  True

    def onchange_class(self, cr, uid, ids, parent_id, context=None):

        results = {}
        if not parent_id:
            return results 
        member_obj = self.pool.get('netpro.member') 
        parent_class = member_obj.browse(cr,uid,parent_id)

        results = {
            'value' : {
                'class_id' : parent_class.class_id.id
            }
        }
        return results

    def onchange_policy_member(self, cr, uid, ids, policy_id, context=None):
        results = {}
        if not policy_id:
            return results

        policy_obj = self.pool.get('netpro.policy')
        policy_data = policy_obj.browse(cr,uid,policy_id)

        results = {
            'value' : {
                'insurance_period_start'    : policy_data.insurance_period_start,
                'insurance_period_end'      : policy_data.insurance_period_end,
                'policy_holder'             : policy_data.policy_holder_id.id,
                'policy_category'           : policy_data.policy_category_id.id,
            }
        }
        return results

    def onchange_DoB(self, cr, uid, ids, date_of_birth):
        result = {}
        if date_of_birth:
            d = time.strptime(date_of_birth,"%Y-%m-%d")
            delta = date.today() - date(d[0], d[1], d[2])
            usia = delta.days / 365.2425
            result = int(usia)
        return {'value':{'age':result}}

netpro_member()

class netpro_member_policy_exception(osv.osv):
    _name = 'netpro.member_policy_exception'
    _columns = {
        'member_id' : fields.many2one('netpro.member', 'Member'),
        'diagnosis_id' : fields.many2one('netpro.diagnosis', 'List of Policy Exception', widget="many2many"),
    }
netpro_member_policy_exception()


class netpro_member_plan(osv.osv):
    _name = 'netpro.member_plan'
    _rec_name = 'product_plan_id'
    _columns = {
        'member_id': fields.many2one('netpro.member', 'Member'),
        # 'plan_schedule_id': fields.many2one('netpro.plan_schedule', 'PPlan'),
        # 'product_plan': fields.related('plan_schedule_id','product_plan_id', 'product_plan_base_id', 
        #     relation="netpro.product_plan_base",
        #     type='many2one', string='Product Plan', store=True, readonly=True),
        'product_plan_id':  fields.many2one('netpro.product_plan', 'Product Plan'),
        'bamount': fields.float('BAmount'),
        'plan_limit': fields.float('Plan Limit'),
        'remaining_limit': fields.float('Remaining Limit'),
        'family_limit': fields.float('Family Limit'),
        'family_remaining_limit': fields.float('Family Remaining Limit'),
        'hi_plan': fields.boolean('Hi Plan'),
        'aso': fields.boolean('ASO'),
        'excess': fields.char('Excess'),
        'per_disability': fields.boolean('Per Disability'),
        'member_plan_detail_ids': fields.one2many('netpro.member_plan_detail', 'member_plan_id', 'Member Plan Details', ondelete='cascade'),
        'plan_for': fields.char('Plan For',readonly="True"),
    }
netpro_member_plan()

class netpro_member_plan_detail(osv.osv):
    _name = 'netpro.member_plan_detail'
    _rec_name = 'benefit_id'
    _columns = {
        'member_plan_id': fields.many2one('netpro.member_plan', 'Member Plan'),
        'benefit_id' : fields.many2one('netpro.benefit', 'Benefit'),
        'benefit_code' : fields.related('benefit_id', 'code' , type="char", 
            relation="netpro.benefit", string="Benefit Code", store=True),
        'reim': fields.float('Reim'),
        'provider_limit': fields.float('Provider Limit'),
        'non_provider_limit': fields.float('Non Provider Limit'),
        'unit': fields.char('Unit'),
        'usage': fields.float('Usage'),
        'remaining': fields.float('Remaining'),
    }
netpro_member_plan_detail()

class netpro_member_claim_history(osv.osv):
    _name = 'netpro.member_claim_history'
    _rec_name = 'claim_id'
    _columns = {
        'member_id': fields.many2one('netpro.member', 'Member'),
        'claim_id': fields.many2one('netpro.claim', 'Claim'),
    }
netpro_member_claim_history()

class netpro_policy(osv.osv):
    _name = 'netpro.policy'
    _inherit = 'netpro.policy'
    _columns = {
        'member_ids' : fields.one2many('netpro.member','policy_id','Member', ondelete="cascade")
    }
netpro_policy()

class netpro_area(osv.osv):
    _name = 'netpro.area'
    _columns={
    'name':fields.char("Name"),
    'code':fields.char("Code"),
    }
netpro_area()

class netpro_import_member_new(osv.osv):
    _name = 'netpro.import_member_new'

    def _dict_search(self,datalist, keyword):
        ret = False
        for k,v in datalist:
            if k == keyword:
                ret = v
                break
        return ret

    def create(self,cr,uid,vals,context=None):
        if vals['NOPOL']:                    

            policy = self.pool.get('netpro.policy').search(cr,uid,[('policy_no','=',vals['NOPOL'])])
            class_data = self.pool.get('netpro.class').search(cr,uid,[('class_no','=',vals['CLASSNO']),('policy_id','=',policy[0])])

            # buat class di policy jika data class blm ada
            if not class_data:
                class_obj = self.pool.get('netpro.class').create(cr,uid,{'policy_id':policy[0],
                                                                         'class_no':vals['CLASSNO'],
                                                                         'short_desc':'Kelas '+vals['CLASSNO'],
                                                                         })

                class_data = class_obj

            if isinstance(class_data, int) :
                class_data = class_data
            else :
                class_data = class_data[0]

            gender = self.pool.get('netpro.gender').search(cr,uid,[('name','=',vals['SEX'])])
            membership = self.pool.get('netpro.membership').search(cr,uid,[('membership_id','=',vals['MEMBERSHIP'])])
            marital = self.pool.get('netpro.marital_status').search(cr,uid,[('short_desc','=',vals['MARITALSTATUS'])])
            premium_type = self.pool.get('netpro.premium_type').search(cr,uid,[('name','=',vals['PREMIUMTYPE'])])
            member = self.pool.get('netpro.member')
            member_plan = self.pool.get('netpro.member_plan')
            policy_data = self.pool.get('netpro.policy').browse(cr,uid,policy)
            
            mememp = self.pool.get('netpro.membership_plan_employee')
            memspo = self.pool.get('netpro.membership_plan_spouse')
            memchi = self.pool.get('netpro.membership_plan_child')
            member_id = member.create(cr, uid, {'name':vals['NAME'],
                                                'policy_id':policy[0],
                                                'class_id':class_data,
                                                'membership_id':membership[0],
                                                'marital_status':marital[0],
                                                'premium_type_id':premium_type[0],
                                                'census_no':vals['CENSUSNO'],
                                                'gender_id':gender[0],
                                                'date_of_birth':vals['BIRTHDATE'],
                                                'birth_place':vals['BIRTHPLACE'],
                                                'member_no':vals['MEMBERNO'],
                                                'age':vals['AGE'],
                                                'account_name':vals['ACCOUNTNAME'],
                                                'account_no':vals['ACCOUNTNO'],
                                                'bank_name':vals['BANKNAME'],
                                                'upd_code':'N',
                                                'parent_id':'',
                                                'insurance_period_start':policy_data.insurance_period_start,
                                                'insurance_period_end':policy_data.insurance_period_end,
                                                })
            
            for k,v in vals.items():
                if v and k.startswith('PLAN'):
                    plan_obj = self.pool.get('netpro.product_plan').search(cr,uid,[('code','=',v)])
                    mfbamount = self._dict_search(vals.items(), 'MFBAMOUNT'+k[-1:])
                    ffbamount = self._dict_search(vals.items(), 'FFBAMOUNT'+k[-1:])

                    # insert ke class -> membership
                    if vals['MEMBERSHIP'] == '1. EMP':
                        check = mememp.search(cr,uid,[('product_plan_id','=',plan_obj[0]),('male_female_bamount','=',mfbamount)])
                        if not check:
                            mememp.create(cr,uid,{'class_id': class_data,
                                                  'product_plan_id': plan_obj[0],
                                                  'male_female_bamount': mfbamount,
                                                  })

                    if vals['MEMBERSHIP'] == '2. SPO':
                        check = memspo.search(cr,uid,[('product_plan_id','=',plan_obj[0]),('male_female_bamount','=',mfbamount)])
                        if not check:
                            memspo.create(cr,uid,{'class_id': class_data,
                                                  'product_plan_id': plan_obj[0],
                                                  'male_female_bamount': mfbamount,
                                                  })

                    if vals['MEMBERSHIP'] == '3. CHI':
                        check = memchi.search(cr,uid,[('product_plan_id','=',plan_obj[0]),('male_female_bamount','=',mfbamount)])
                        if not check:
                            memchi.create(cr,uid,{'class_id': class_data,
                                              'product_plan_id': plan_obj[0],
                                              'male_female_bamount': mfbamount,
                                              })

                    check = member_plan.search(cr,uid,[('member_id','=',member_id),('product_plan_id','=',plan_obj[0]),('bamount','=',mfbamount)])
                    if not check:
                        member_plan.create(cr,uid, {'member_id':member_id,
                                                    'product_plan_id':plan_obj[0],
                                                    'bamount':mfbamount,
                                                    })

        return True

    _columns = {
        'CLASSNO' : fields.char('Class No'),
        'MEMBERSHIP' : fields.char('Membership'),
        'EMPID' : fields.char('Employee ID'),
        'CENSUSNO' : fields.char('Census No'),
        'AREA' : fields.char('Area'),
        'NAME' : fields.char('Name'),
        'SEX' : fields.char('Sex'),
        'BIRTHDATE' : fields.date('Birthdate'),
        'BIRTHPLACE' : fields.char('Birthplace'),
        'MEMBERNO' : fields.char('Member No'),
        'PAYORID' : fields.char('Payor ID'),
        'MARITALSTATUS' : fields.char('Marital Status'),
        'ENTRYDATE' : fields.date('Entry Date'),
        'AGE' : fields.char('Age'),
        'NOP' : fields.char('NOP'),
        'PREMIUMTYPE' : fields.char('Preimun Type'),
        'PLAN1' : fields.char('Plan 1'),
        'MFBAMOUNT1' : fields.float('MF BAmount1'),
        'FFBAMOUNT1' : fields.float('FF BAmount1'),
        'PLAN2' : fields.char('Plan 2'),
        'MFBAMOUNT2' : fields.float('MF BAmount2'),
        'FFBAMOUNT2' : fields.float('FF BAmount2'),
        'PLAN3' : fields.char('Plan 3'),
        'MFBAMOUNT3' : fields.float('MF BAmount3'),
        'FFBAMOUNT3' : fields.float('FF BAmount3'),
        'PLAN3' : fields.char('Plan 3'),
        'MFBAMOUNT3' : fields.float('MF BAmount3'),
        'FFBAMOUNT3' : fields.float('FF BAmount3'),
        'PLAN4' : fields.char('Plan 4'),
        'MFBAMOUNT4' : fields.float('MF BAmount4'),
        'FFBAMOUNT4' : fields.float('FF BAmount4'),
        'PLAN5' : fields.char('Plan 5'),
        'MFBAMOUNT5' : fields.float('MF BAmount5'),
        'FFBAMOUNT5' : fields.float('FF BAmount5'),
        'PLAN6' : fields.char('Plan 6'),
        'MFBAMOUNT6' : fields.float('MF BAmount6'),
        'FFBAMOUNT6' : fields.float('FF BAmount6'),
        'PLAN7' : fields.char('Plan 7'),
        'MFBAMOUNT7' : fields.float('MF BAmount7'),
        'FFBAMOUNT7' : fields.float('FF BAmount7'),
        'PLAN8' : fields.char('Plan 8'),
        'MFBAMOUNT8' : fields.float('MF BAmount8'),
        'FFBAMOUNT8' : fields.float('FF BAmount8'),
        'PLAN9' : fields.char('Plan 9'),
        'MFBAMOUNT9' : fields.float('MF BAmount9'),
        'FFBAMOUNT9' : fields.float('FF BAmount9'),
        'PLAN10' : fields.char('Plan 10'),
        'MFBAMOUNT10' : fields.float('MF BAmount10'),
        'FFBAMOUNT10' : fields.float('FF BAmount10'),
        'ACCOUNTNAME' : fields.char('Account Name'),
        'ACCOUNTNO' : fields.char('Account No'),
        'BANKNAME' : fields.char('Bank Name'),
        'BANKADDRESS' : fields.char('Bank Address'),
        'CARDNO' : fields.char('Card No'),
        'COUNTRY' : fields.char('Country'),
        'BRANCHVC' : fields.char('Branchvc'),
        'NOPOL' : fields.char('No Pol'),
        'POLICY_HOLDER' : fields.char('Policy Holder'),
        'NIK' : fields.char('NIK'),
    }

class netpro_import_member_endorse(osv.osv):
    _name = 'netpro.import_member_endorse'

    def create(self,cr,uid,vals,context=None):
        if vals['MEMBERNO'] and vals['TTYPE']:
            # member baru
            if vals['TTYPE'] == 'N':
                policy = self.pool.get('netpro.policy').search(cr,uid,[('policy_no','=',vals['POL'])])
                class_data = self.pool.get('netpro.class').search(cr,uid,[('class_no','=',vals['NEWCLASSNO']),('policy_id','=',policy[0])])

                # buat class di policy jika data class blm ada
                if not class_data:
                    class_obj = self.pool.get('netpro.class').create(cr,uid,{'policy_id':policy[0],
                                                                             'class_no':vals['NEWCLASSNO'],
                                                                             'short_desc':'Kelas '+vals['NEWCLASSNO'],
                                                                             })

                    class_data = class_obj

                if isinstance(class_data, int) :
                    class_data = class_data
                else :
                    class_data = class_data[0]

                gender = self.pool.get('netpro.gender').search(cr,uid,[('name','=',vals['SEX'])])
                membership = self.pool.get('netpro.membership').search(cr,uid,[('membership_id','=',vals['MEMBERSHIP'])])
                marital = self.pool.get('netpro.marital_status').search(cr,uid,[('short_desc','=',vals['MARITALSTATUS'])])
                premium_type = self.pool.get('netpro.premium_type').search(cr,uid,[('name','=',vals['PREMIUMTYPE'])])
                member = self.pool.get('netpro.member')
                member_plan = self.pool.get('netpro.member_plan')
                policy_data = self.pool.get('netpro.policy').browse(cr,uid,policy)
                
                mememp = self.pool.get('netpro.membership_plan_employee')
                memspo = self.pool.get('netpro.membership_plan_spouse')
                memchi = self.pool.get('netpro.membership_plan_child')
                member_id = member.create(cr, uid, {'name':vals['NAME'],
                                                    'policy_id':policy[0],
                                                    'class_id':class_data,
                                                    'membership_id':membership[0],
                                                    'marital_status':marital[0],
                                                    'premium_type_id':premium_type[0],
                                                    'census_no':vals['CENSUSNO'],
                                                    'gender_id':gender[0],
                                                    'date_of_birth':vals['BIRTHDATE'],
                                                    'birth_place':vals['BIRTHPLACE'],
                                                    'member_no':vals['MEMBERNO'],
                                                    'age':vals['AGE'],
                                                    'account_name':vals['ACCOUNTNAME'],
                                                    'account_no':vals['ACCOUNTNO'],
                                                    'bank_name':vals['BANKNAME'],
                                                    'upd_code':'N',
                                                    'insurance_period_start':policy_data.insurance_period_start,
                                                    'insurance_period_end':policy_data.insurance_period_end,
                                                    'parent_id':'',
                                                    })
                
                for k,v in vals.items():
                    if v and k.startswith('PLAN'):
                        plan_obj = self.pool.get('netpro.product_plan').search(cr,uid,[('code','=',v)])
                        mfbamount = self._dict_search(vals.items(), 'MFBAMOUNT'+k[-1:])
                        ffbamount = self._dict_search(vals.items(), 'FFBAMOUNT'+k[-1:])

                        # insert ke class -> membership
                        if vals['MEMBERSHIP'] == '1. EMP':
                            check = mememp.search(cr,uid,[('product_plan_id','=',plan_obj[0]),('male_female_bamount','=',mfbamount)])
                            if not check:
                                mememp.create(cr,uid,{'class_id': class_data,
                                                      'product_plan_id': plan_obj[0],
                                                      'male_female_bamount': mfbamount,
                                                      })

                        if vals['MEMBERSHIP'] == '2. SPO':
                            check = memspo.search(cr,uid,[('product_plan_id','=',plan_obj[0]),('male_female_bamount','=',mfbamount)])
                            if not check:
                                memspo.create(cr,uid,{'class_id': class_data,
                                                      'product_plan_id': plan_obj[0],
                                                      'male_female_bamount': mfbamount,
                                                      })

                        if vals['MEMBERSHIP'] == '3. CHI':
                            check = memchi.search(cr,uid,[('product_plan_id','=',plan_obj[0]),('male_female_bamount','=',mfbamount)])
                            if not check:
                                memchi.create(cr,uid,{'class_id': class_data,
                                                  'product_plan_id': plan_obj[0],
                                                  'male_female_bamount': mfbamount,
                                                  })

                        check = member_plan.search(cr,uid,[('member_id','=',member_id),('product_plan_id','=',plan_obj[0]),('bamount','=',mfbamount)])
                        if not check:
                            member_plan.create(cr,uid, {'member_id':member_id,
                                                        'product_plan_id':plan_obj[0],
                                                        'bamount':mfbamount,
                                                        })

            # member resign
            if vals['TTYPE'] == 'R':
                member_obj = self.pool.get('netpro.member').search(cr,uid,[('member_no','=',vals['MEMBERNO'])])
                return self.pool.get('netpro.member').write(cr,uid,member_obj,{'upd_code':'R'},context=context)

            # member ubah class
            if vals['TTYPE'] == 'C':
                member_obj = self.pool.get('netpro.member').search(cr,uid,[('member_no','=',vals['MEMBERNO'])])
                member_data = self.pool.get('netpro.member').browse(cr,uid,member_obj)
                if member_data.class_id != vals['CLASSNO']:
                    self.pool.get('netpro.member').write(cr,uid,{'class_id':int(vals['CLASSNO']),'upd_code':'C'}, context=context)
                return True

            # member ubah data selain class
            # if vals['TTYPE'] == 'M':
            #     member_obj = self.pool.get('netpro.member').search(cr,uid,[('member_no','=',vals['MEMBERNO']))
            #     member_data = self.pool.get('netpro.member').browse(cr,uid,member_obj)
            #     data = []
                

        return True
    _columns = {
        'OLDCLASSNO' : fields.char('Old Class No'),
        'NEWCLASSNO' : fields.char('New Class No'),
        'TTYPE' : fields.char('Transaction Type'),
        'MEMBERNO' : fields.char('Member No'),
        'MEMBERSHIP' : fields.char('Membership'),
        'EMPID' : fields.char('Employee ID'),
        'CENSUSNO' : fields.char('Census No'),
        'AREA' : fields.char('Area'),
        'NAME' : fields.char('Name'),
        'SEX' : fields.char('Sex'),
        'BIRTHDATE' : fields.date('Birthdate'),
        'BIRTHPLACE' : fields.char('Birthplace'),
        'PAYORID' : fields.char('Payor ID'),
        'MARITALSTATUS' : fields.char('Marital Status'),
        'ENTRYDATE' : fields.date('Entry Date'),
        'ENTRYDATE' : fields.date('Entry Date'),
        'AGE' : fields.integer('Age'),
        'NOP' : fields.integer('NOP'),
        'PREMIUMTYPE' : fields.char('Preimun Type'),
        'PLAN1' : fields.char('Plan 1'),
        'MFBAMOUNT1' : fields.float('MF BAmount1'),
        'FFBAMOUNT1' : fields.float('FF BAmount1'),
        'PLAN2' : fields.char('Plan 2'),
        'MFBAMOUNT2' : fields.float('MF BAmount2'),
        'FFBAMOUNT2' : fields.float('FF BAmount2'),
        'PLAN3' : fields.char('Plan 3'),
        'MFBAMOUNT3' : fields.float('MF BAmount3'),
        'FFBAMOUNT3' : fields.float('FF BAmount3'),
        'PLAN3' : fields.char('Plan 3'),
        'MFBAMOUNT3' : fields.float('MF BAmount3'),
        'FFBAMOUNT3' : fields.float('FF BAmount3'),
        'PLAN4' : fields.char('Plan 4'),
        'MFBAMOUNT4' : fields.float('MF BAmount4'),
        'FFBAMOUNT4' : fields.float('FF BAmount4'),
        'PLAN5' : fields.char('Plan 5'),
        'MFBAMOUNT5' : fields.float('MF BAmount5'),
        'FFBAMOUNT5' : fields.float('FF BAmount5'),
        'PLAN6' : fields.char('Plan 6'),
        'MFBAMOUNT6' : fields.float('MF BAmount6'),
        'FFBAMOUNT6' : fields.float('FF BAmount6'),
        'PLAN7' : fields.char('Plan 7'),
        'MFBAMOUNT7' : fields.float('MF BAmount7'),
        'FFBAMOUNT7' : fields.float('FF BAmount7'),
        'PLAN8' : fields.char('Plan 8'),
        'MFBAMOUNT8' : fields.float('MF BAmount8'),
        'FFBAMOUNT8' : fields.float('FF BAmount8'),
        'PLAN9' : fields.char('Plan 9'),
        'MFBAMOUNT9' : fields.float('MF BAmount9'),
        'FFBAMOUNT9' : fields.float('FF BAmount9'),
        'PLAN10' : fields.char('Plan 10'),
        'MFBAMOUNT10' : fields.float('MF BAmount10'),
        'FFBAMOUNT10' : fields.float('FF BAmount10'),
        'ACCOUNTNAME' : fields.char('Account Name'),
        'ACCOUNTNO' : fields.char('Account No'),
        'BANKNAME' : fields.char('Bank Name'),
        'BANKADDRESS' : fields.char('Bank Address'),
        'CARDNO' : fields.char('Card No'),
        'EFFECTIVEDATE' : fields.date('Effective Date'),
        'BRANCHVC' : fields.char('Branchvc'),
        'POL' : fields.char('Pol'),
        'POLICY_HOLDER' : fields.char('Policy Holder'),
        'ENDOR' : fields.char('Endor'),
    }