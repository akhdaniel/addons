from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class benefit(osv.osv):
	_name 		= "netpro.benefit"
	_rec_name = 'code'
	_columns 	= {
		'code'						: fields.char("Benefit ID"),
		'name'						: fields.char("Name"),
		'name_alt'					: fields.char("Name (alt language)"),
		'description' 				: fields.char("Description"),
		'description_alt' 			: fields.char("Description (alt language)"),
		'short_name'				: fields.char("Short Name"),
		'level'						: fields.selection([('benefit', 'Benefit'), ('sub_benefit', 'Sub Benefit'), ('item', 'Item')], "Level"),
		'unit_id'					: fields.many2one('netpro.benefit_unit', 'Unit'),
		'unit_alt'					: fields.many2one('netpro.benefit_unit', 'Unit (alt language)'),
		'claim_type_id'				: fields.many2one('netpro.product_type', 'Claim Type') ,
		'max_frequency'				: fields.float("Max Frequency"),
		'max_frequency_interval'	: fields.selection([('day', 'Per Day'), ('confinement', 'Per Disabiliy / Confinement'), ('year', 'Per Year')], " "),

		'reinstate_in' 				: fields.float("Reinstate in", help="Day(s)"),
		'pre_hospitalization'		: fields.float("Pre Hospitalization", help="Day(s)"),
		'post_hospitalization' 		: fields.float("Post Hospitalization", help="Day(s)"),
		'limit_from_surgery'  		: fields.float("limit from Surgery", help="% (eg. Anesthesy Benefit)"),
		'limit_from_parent_benefit' : fields.float("Limit From Parent Benefit", help="%"),
		'allowed_benefit_from' 		: fields.float("allowed Benefit From", help="%"),
		'allowed_benefit_to' 		: fields.float("Allowed Benefit To", help="%"),

		'accumulated_for_one_day'	: fields.boolean("Accumulated for One Day"),
		'reinstateable_benefit' 	: fields.boolean("Reinstateable Benefit"),
		'surgery_benefit' 			: fields.boolean("Surgery Benefit"),
		'group_term_life_benefit' 	: fields.boolean("Group Term Life Benefit (PA)"),
		'claimable_benefit' 		: fields.boolean("Claimable Benefit"),
		'hide_on_printing' 			: fields.boolean("Hide on Printing"),
		'pre_post_maternity_benefit': fields.boolean("Pre & Post Maternity Benefit"),
		'benefit_category' 			: fields.boolean("Benefit Category"),
		'pool_fund_benefit' 		: fields.boolean("Pool Fund Benefit"),

		'benefit_external_map_ids'	: fields.one2many('netpro.benefit_external_map','benefit_id','External Maps', ondelete="cascade"),
		'benefit_diagnosis_ids'		: fields.one2many('netpro.benefit_diagnosis','benefit_id','Diagnosis', ondelete="cascade"),
		'benefit_edc_map_ids'		: fields.one2many('netpro.benefit_edc_map','benefit_id','EDC Maps', ondelete="cascade"),
		'benefit_rate_ids'			: fields.one2many('netpro.benefit_rate','benefit_id','Rate', ondelete="cascade"),
		'created_by_id' 			: fields.many2one('res.users', 'Creator'),
		'tpa_id' 					: fields.many2one('netpro.tpa', 'TPA'),
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

		new_record = super(benefit, self).create(cr, uid, vals, context=context)
		return new_record

class benefit_diagnosis(osv.osv):
	_name 		= "netpro.benefit_diagnosis"
	_columns 	= {
		'name'			: fields.char("Name"),
		'benefit_id' 	: fields.many2one('netpro.benefit', 'Benefit'),
		'diagnosis_id'	: fields.many2one('netpro.diagnosis', 'Diagnosis'),
	}

class benefit_edc_map(osv.osv):
	_name 		= "netpro.benefit_edc_map"
	_columns 	= {
		'name'			: fields.char("Name"),
		'benefit_id' 	: fields.many2one('netpro.benefit', 'Benefit'),
	}

class benefit_external_map(osv.osv):
	_name 		= "netpro.benefit_external_map"
	_columns 	= {
		'name'			: fields.char("Name"),
		'benefit_id' 	: fields.many2one('netpro.benefit', 'Benefit'),
	}

class benefit_rate(osv.osv):
	_name 		= "netpro.benefit_rate"
	_columns 	= {
		'name'			: fields.char("Name"),
		'benefit_id' 	: fields.many2one('netpro.benefit', 'Benefit'),
	}
