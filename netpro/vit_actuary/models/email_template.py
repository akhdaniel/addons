from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_email_template(osv.osv):
	_name = "netpro.email_template"
	_columns = {
		'name' 		: fields.char('Name'),
		'subject' 	: fields.char('Subject'),
		'body' 		: fields.text('Body', help="Use square bracket and lowercase letters to declare a glossary. e.g. [member_no]"),
	}

	_sql_constraints = [
		('name', 'UNIQUE(name)', 'Name must be Unique!'),
	]
