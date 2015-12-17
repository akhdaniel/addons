from openerp import models, fields, api

class policy_fee_details(models.TransientModel):
	_name = 'policy_fee_details'

	_columns = {
		'membership' 	: fields.char('Membership'),
		'fee' 			: fields.float('Fee'),
		'total_member' 	: fields.float('Total Member'),
		'total_fee' 	: fields.float('Total Fee Per Membership'),
	}