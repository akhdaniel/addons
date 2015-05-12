import time
from datetime import datetime

import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp import SUPERUSER_ID


class account_move_line(osv.osv):
	_name = "account.move"
	_inherit = "account.move"

	_columns = {
		'is_flagged':fields.boolean('Is Flagged ?'),
		}
