from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_reliance(osv.osv):
    _name = 'netpro.reliance'

    _columns = {
        'RecordMode' : fields.char('Record Mode', select=1),
        'RecordType' : fields.char('Record Type', select=1),
        'PayorID' : fields.char('Payor ID', select=1),
        'MemberID' : fields.char('Member ID', select=1),
        'MappingID' : fields.char('Mapping ID', select=1),
        'AdMedikaMembID' : fields.char('AdMedika Member ID', select=1),
        'CorporateID' : fields.char('Corporate ID', select=1),
        'EmployeeID' : fields.char('Employee ID', select=1),
        'Division' : fields.char('Division', select=1),
        'BranchCode' : fields.char('Branch Code', select=1),
        'Bank' : fields.char('Bank', select=1),
        'Language' : fields.char('Language', select=1),
        'Race' : fields.char('Race', select=1),
        'PolicyNo' : fields.char('Policy No', select=1),
        'MaritalStatus' : fields.char('Marital Status', select=1),
        'Relationship' : fields.char('Relationship', select=1),
        'MemberEffDt' : fields.date('Member Effective Date', select=1),
        'MemberExpDt' : fields.date('Member Expired Date', select=1),
        'FullName' : fields.char('Fullname', select=1),
        'Address1' : fields.char('Address 1', select=1),
        'Address2' : fields.char('Address 2', select=1),
        'Address3' : fields.char('Address 3', select=1),
        'Address4' : fields.char('Address 4', select=1),
        'City' : fields.char('City', select=1),
        'State' : fields.char('State', select=1),
        'PostCode' : fields.char('Post Code', select=1),
        'Phone1' : fields.char('Phone 1', select=1),
        'Phone2' : fields.char('Phone 2', select=1),
        'Phone3' : fields.char('Phone 3', select=1),
        'NRIC' : fields.char('NRIC', select=1),
        'PassportNo' : fields.char('Passport No', select=1),
        'PassportCountry' : fields.char('Passport Country', select=1),
        'DOB' : fields.date('Date of Birth', select=1),
        'Sex' : fields.char('Sex', select=1),
        'PlanID' : fields.char('Plan ID', select=1),
        'EsSts' : fields.char('EeSts', select=1),
        'TermDt' : fields.date('Term Date', select=1),
        'PreExisting' : fields.char('Pre Existing', select=1),
        'Remarks' : fields.char('Remarks', select=1),
        'MembSince' : fields.char('Member Since', select=1),
        'PolicyIF' : fields.char('Policy IF', select=1),
        'PolicySusp' : fields.char('Policy Susp', select=1),
        'PolicySusp' : fields.char('Policy Susp', select=1),
        'InternalUse1' : fields.char('Internal Use 1', select=1),
        'InternalUse2' : fields.char('Internal Use 2', select=1),
        'InternalUse3' : fields.char('Internal Use 3', select=1),
        'InternalUse4' : fields.char('Internal Use 4', select=1),
        'InternalUse5' : fields.char('Internal Use 5', select=1),
        'InternalUse6' : fields.char('Internal Use 6', select=1),
        'InternalUse7' : fields.char('Internal Use 7', select=1),
        'InternalUse8' : fields.char('Internal Use 8', select=1),
        'InternalUse9' : fields.char('Internal Use 9', select=1),
        'InternalUse10' : fields.char('Internal Use 10', select=1),
        'InternalUse11' : fields.char('Internal Use 11', select=1),
        'InternalUse12' : fields.char('Internal Use 12', select=1),
        'InternalUse13' : fields.char('Internal Use 13', select=1),
        'InternalUse14' : fields.char('Internal Use 14', select=1),
        'InternalUse15' : fields.char('Internal Use 15', select=1),
        'InternalUse16' : fields.char('Internal Use 16', select=1),
        'InternalUse17' : fields.char('Internal Use 17', select=1),
        'InternalUse18' : fields.char('Internal Use 18', select=1),
        'InternalUse19' : fields.char('Internal Use 19', select=1),
        'InternalUse20' : fields.char('Internal Use 20', select=1),
        'InternalUse21' : fields.char('Internal Use 21', select=1),
        'InternalUse22' : fields.char('Internal Use 22', select=1),
        'is_processed' : fields.boolean('Is Processed?'),
    }

    _defaults = {
        'is_processed' : False,
    }

    def process_convert_reliance(self, cr, uid, ids, context=None):
        reliance_obj = self.pool.get('netpro.reliance')
        
        # SEDOT DATA FROM RELIANCE
        if(reliance_obj):
            reliance_ids = reliance_obj.search(cr,uid,[('is_processed', '=', False)])
            if reliance_ids:
                reliance_data = reliance_obj.browse(cr, uid, reliance_ids, context=context)
                inc = 1
                for reliance in reliance_data:

                    #####################################
                    # collect data from reliance object #
                    #####################################
                    reliance_data = {
                        'card_no' : reliance.MemberID,
                        'date_of_birth' : reliance.DOB,
                        'name' : reliance.FullName,
                        'gender_id' : self.pool.get('netpro.gender').search(cr,uid,[('name','=',reliance.Sex)])[0],
                        'insurance_period_start' : reliance.MemberEffDt,
                        'insurance_period_end' : reliance.MemberExpDt,
                        'bank_name' : reliance.Bank,
                        'remarks' : 'Reliance Data ' + str(inc),
                        'parent_id' : False,
                        'member_no' : False,
                    }

                    #################################################
                    # insert record to member object and activating #
                    #################################################
                    member_obj = self.pool.get('netpro.member')
                    member_reliance_id = member_obj.create(cr, uid, reliance_data, context)

                    ######################################
                    # get member plan from reliance data #
                    ######################################
                    member_plans = reliance.PlanID.split(',')
                    if member_plans:
                        for mplan in member_plans:
                            if mplan != '':
                                product_plan_obj = self.pool.get('netpro.product_plan').search(cr, uid, [('code', '=', mplan)])
                                if product_plan_obj:
                                    member_plan_data = {
                                        'member_id' : member_reliance_id.id,
                                        'product_plan_id' : product_plan_obj,
                                    }

                    member_reliance_id.action_confirm()

                    ###########################################
                    # add increment number for member remarks #
                    ###########################################
                    inc += 1