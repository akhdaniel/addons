from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class transfer_bonus(osv.osv):
	_name 		= "mlm.transfer_bonus"
	_columns 	= {
		'member_id' 		: fields.many2one('res.partner', 'Member'),
		'bonus_id' 			: fields.many2one('mlm.bonus', 'Bonus Type'),

		'bank_no'			: fields.related('member_id', 'bank_no' , type="char", relation="res.partner", string="Bank No", readonly=True),
		'bank_account_name'	: fields.related('member_id', 'bank_account_name' , type="char", relation="res.partner", string="Bank Account Name", readonly=True),
		'bank_name'			: fields.related('member_id', 'bank_name' , type="char", relation="res.partner", string="Bank Name", readonly=True),
		'bank_branch'		: fields.related('member_id', 'bank_branch' , type="char", relation="res.partner", string="Bank Branch", readonly=True),

		'amount'			: fields.float('Bonus Amount'),
		'trans_date'		: fields.datetime('Transaction Date'),
		'description' 		: fields.char('Description'),
		'detail_ids' 		: fields.one2many('mlm.transfer_bonus_detail','transfer_bonus_id','Details', ondelete="cascade"),
	}

class transfer_bonus_detail(osv.osv):
	_name 		= "mlm.transfer_bonus_detail"
	_columns 	= {
		'transfer_bonus_id' : fields.many2one('mlm.transfer_bonus', 'Transfer Bonus ID'),
		'member_bonus_id'   : fields.many2one('mlm.member_bonus', 'Member Bonus ID'),
		'amount'			: fields.float('Bonus Amount'),
	}
