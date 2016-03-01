from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class benefit(osv.osv):
	_name 		= "netpro.benefit"
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
		'allowed_benefit_from' 		: fields.float("allowed Benefit From", help="%"),
		'allowed_benefit_to' 		: fields.float("Allowed Benefit To", help="%"),
		'limit_from_parent_benefit' : fields.float("Limit From Parent Benefit", help="%"),
		'benefit_category_id' 		: fields.many2one("netpro.benefit_category", "Benefit Category"),
		'benefit_type' 		 		: fields.related('benefit_category_id', 'type' , type="char", relation="netpro.benefit_category", string="Benefit Type", store=False),

		'accumulated_for_one_day'	: fields.boolean("Accumulated for One Day"),
		'reinstateable_benefit' 	: fields.boolean("Reinstateable Benefit"),
		'surgery_benefit' 			: fields.boolean("Surgery Benefit"),
		'group_term_life_benefit' 	: fields.boolean("Group Term Life Benefit (PA)"),
		'claimable_benefit' 		: fields.boolean("Claimable Benefit"),
		'hide_on_printing' 			: fields.boolean("Hide on Printing"),
		'pre_post_maternity_benefit': fields.boolean("Pre & Post Maternity Benefit"),
		'pool_fund_benefit' 		: fields.boolean("Pool Fund Benefit"),

		'external_benefit_code'		: fields.char('External Benefit Code'),
		'show_benefit_on_receipt'	: fields.boolean('Show Benefit On Receipt'),
		'show_benefit_limit_on_receipt'	: fields.boolean('Show Benefit Limit On Receipt'),

		'benefit_external_map_ids'	: fields.one2many('netpro.benefit_external_map','benefit_id','External Maps', ondelete="cascade"),
		'benefit_diagnosis_ids'		: fields.one2many('netpro.benefit_diagnosis','benefit_id','Diagnosis', ondelete="cascade"),
		'benefit_edc_map_ids'		: fields.one2many('netpro.benefit_edc_map','benefit_id','EDC Map', ondelete="cascade"),
		'benefit_rate_ids'			: fields.one2many('netpro.benefit_rate','benefit_id','Rate', ondelete="cascade"),
		'created_by_id' 			: fields.many2one('res.users', 'Creator'),
		'tpa_id' 					: fields.many2one('netpro.tpa', 'TPA'),
	}

	_sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Code must be Unique!'),
    ]

	def create(self, cr, uid, vals, context=None):

		external_benefit_code_val = False

		if 'benefit_edc_map_ids' in vals.keys():
			if len(vals['benefit_edc_map_ids']) > 1:
				raise osv.except_orm(('Warning!'),("Cannot add EDC Map more than 1 record"))
			elif vals['benefit_edc_map_ids'] and len(vals['benefit_edc_map_ids']) == 1:
				if vals['benefit_edc_map_ids'][0][2]:
					benefit_map_id = vals['benefit_edc_map_ids'][0][2].values()[0]
					benefit_map_obj = self.pool.get('netpro.benefit_map').browse(cr, uid, benefit_map_id, context=None)
					external_benefit_code_val = benefit_map_obj.code

		cur_user = self.pool.get('res.users').browse(cr, uid, uid, context=None)
		tpa_val = False
		if cur_user.tpa_id:
			tpa_val = cur_user.tpa_id.id
			pass
		vals.update({
			'created_by_id':uid,
			'external_benefit_code': external_benefit_code_val,
			'tpa_id':tpa_val,
		})

		new_record = super(benefit, self).create(cr, uid, vals, context=context)
		return new_record

	def write(self, cr, uid, ids, vals, context=None):
		external_benefit_code_val = False

		if 'benefit_edc_map_ids' in vals.keys():
			if len(vals['benefit_edc_map_ids']) > 1:
				raise osv.except_orm(('Warning!'),("Cannot add EDC Map more than 1 record"))
			elif vals['benefit_edc_map_ids'] and len(vals['benefit_edc_map_ids']) == 1:
				if vals['benefit_edc_map_ids'][0][2]:
					benefit_map_id = vals['benefit_edc_map_ids'][0][2].values()[0]
					benefit_map_obj = self.pool.get('netpro.benefit_map').browse(cr, uid, benefit_map_id, context=None)
					external_benefit_code_val = benefit_map_obj.code

		vals.update({
			'external_benefit_code': external_benefit_code_val
		})

		return super(benefit, self).write(cr, uid, ids, vals, context=context)

	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		res = []
		for r in self.browse(cr, uid, ids, context=context):
			if r.code and r.name:
				name = "[%s] %s" % (r.code, r.name)
				res.append((r.id,name))
			else :
				res.append((r.id,r.code))

		return res

	def onchange_ben_cat(self, cr, uid, ids, ben_cat_id):
		res = {}
		if not ben_cat_id:
			return res
		data = self.pool.get('netpro.benefit_category').browse(cr, uid, ben_cat_id, context=None)
		res = {
			'value' : {
				'benefit_type' : data.type,
			}
		}
		return res
        

class benefit_diagnosis(osv.osv):
	_name 		= "netpro.benefit_diagnosis"
	_rec_name 	= "diagnosis_id"
	_columns 	= {
		'diagnosis_id'	: fields.many2one('netpro.diagnosis', 'Diagnosis'),
		'benefit_id' 	: fields.many2one('netpro.benefit', 'Benefit'),
	}

class benefit_edc_map(osv.osv):
	_name 		= "netpro.benefit_edc_map"
	_rec_name 	= "benefit_map_id"
	_columns 	= {
		'category' 			: fields.char('Category'),
		'benefit_map_id' 	: fields.many2one('netpro.benefit_map', 'Benefit Map'),
		'benefit_id'		: fields.many2one('netpro.benefit', 'Benefit'),
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

class benefit_category(osv.osv):
	_name 		= "netpro.benefit_category"
	_columns 	= {
		'name'			: fields.char("Name"),
		'type'			: fields.char("Type"),
		'description' 	: fields.text('Description'),
	}
