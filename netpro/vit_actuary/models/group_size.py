from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class group_size(osv.osv):
    _name = 'netpro.group_size'
    _columns = {
        'name'			: fields.char('Group Size'),
		'description' 	:	fields.char("Description"),
		'lower' 		: fields.float('Lower'),
		'upper' 		: fields.float('Upper'),
    }
group_size()