from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_benefit_map(osv.osv):
	_name = 'netpro.benefit_map'

	_columns = {
		'name' : fields.char('Name'),
		'category' : fields.char('Category'),
		'code' : fields.char('Code'),
	}

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