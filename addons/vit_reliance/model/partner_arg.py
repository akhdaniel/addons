from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class partner(osv.osv):
	_name 		= "res.partner"
	_inherit 	= "res.partner"
	_columns = {
		"arg_nomor_polis"		: fields.char("ARG Nomor Polis"),
		"arg_cust_code"			: fields.char("ARG Customer Code"),
		"arg_class"				: fields.char("ARG Class"),
		"arg_subclass"			: fields.char("ARG Sub Class"),	
		"arg_eff_date"			: fields.date("ARG Eff Date"),
		"arg_exp_date"			: fields.date("ARG Exp Date"),
		"arg_qq"				: fields.char("ARG QQ"),
		"arg_cp"				: fields.char("ARG CP"),

	}



