from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_contact_mgt(osv.osv):
	_name = 'netpro.contact_mgt'

	# def create(self, cr, uid, vals, context=None):

 #        vals.update({
 #        	'created_by_id':uid,
 #        	'created_date':time.strftime("%Y-%m-%d %H:%M:%S"),
 #        })

 #        new_id = super(netpro_contact_mgt, self).create(cr, uid, vals, context=context)

 #        return new_id

	_columns = {
		'member_id' : fields.many2one('netpro.member', 'Member'),
		'provider_id' : fields.many2one('netpro.provider', 'Provider'),
		'caller_name' : fields.char('Caller Name'),
		'card_no' : fields.related('member_id', 'card_no' , type="char", relation="netpro.member", string="Card No", store=False),
		'employee_id' : fields.related('member_id', 'employee_id' , type="integer", relation="netpro.member", string="Employee ID", store=False),
		'employee_name' : fields.related('member_id', 'employee_id', type="many2one", relation="netpro.employee", string="Employee Name", store=False),
		'birth_date' : fields.related('member_id', 'date_of_birth',type="char", relation="netpro.member", string="Birth Date", store=False),
		'birth_place' : fields.related('member_id', 'birth_place',type="char", relation="netpro.member", string="Birth Date", store=False),
		'email' : fields.related('member_id', 'partner_id', 'email', type="char", relation="res.partner", string="Email", store=False),
		'address' : fields.related('member_id', 'partner_id', 'street', type="char", relation="res.partner", string="Address", store=False),
		'mobile' : fields.related('member_id', 'partner_id', 'mobile', type="char", relation="res.partner", string="Mobile Phone", store=False),
		'fax' : fields.related('member_id', 'partner_id', 'fax', type="char", relation="res.partner", string="Fax", store=False),
		'call_number' : fields.integer('Call Number'),
		'call_date' : fields.date('Call Date'),
		'relation_with_member' : fields.char('Relation With Member'),
		'membership' : fields.related('member_id', 'membership' , type="char", relation="netpro.membership", string="Membership", store=False),
		'census_no' : fields.related('member_id', 'census_no' , type="char", relation="netpro.member", string="Census No", store=False),
		'gender_id' : fields.related('member_id', 'gender_id' , type="char", relation="netpro.gender", string="Sex", store=False),
		'company_name' : fields.related('member_id', 'policy_id', 'policy_holder_id', type="many2one", relation="res.partner", string="Company Name", store=False),
		'company_address' : fields.related('member_id', 'policy_id', 'policy_holder_id', 'street', type="char", relation="res.partner", string="Company Address", store=False),
		'company_phone' : fields.related('member_id', 'policy_id', 'policy_holder_id', 'phone', type="char", relation="res.partner", string="Company Phone", store=False),
		'company_fax' : fields.related('member_id', 'policy_id', 'policy_holder_id', 'fax', type="char", relation="res.partner", string="Company Fax", store=False),
		'created_by_id' : fields.many2one('res.users', 'Created By'),
		'created_date' : fields.date('Created Date'),
		'updated_by_id' : fields.many2one('res.users', 'Updated By'),
		'updated_date' : fields.date('Updated Date'),
	}

	_defaults = {
		'call_date' : lambda*a : time.strftime("%Y-%m-%d")
	}

	def onchange_member(self, cr, uid, ids, member_id, context=None):
		results = {}
		
		if not member_id:
			return results

		member_obj = self.pool.get('netpro.member').browse(cr, uid, member_id, context=None)

		results = {
			'value' : {
				'card_no' : member_obj.card_no,
				'employee_id' : member_obj.employee_id.id,
				'employee_name' : member_obj.employee_id.name,
				'birth_date' : member_obj.date_of_birth,
				'birth_place' : member_obj.birth_place,
				'email' : member_obj.partner_id.email,
				'address' : member_obj.partner_id.street,
				'mobile' : member_obj.partner_id.mobile,
				'fax' : member_obj.partner_id.fax,
			}
		}

		return results