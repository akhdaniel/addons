from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class payslip(osv.osv):
	_name 		= "hr.payslip"
	_inherit 	= "hr.payslip"

	def _calc_total(self, cr, uid, ids, field, arg, context=None):
		results = {}
		# return harus berupa dictionary dengan key id session
		# contoh kalau 3 records:
		# {
		#      1 : 50.8,
		#      2 : 25.5,
		#      3 : 10.0
		# }
		for p in self.browse(cr, uid, ids, context=context):
			results[p.id]  = 0.0 
			for line in p.line_ids:
				if line.code == 'NET':
					results[p.id] += line.amount
		return results	

	_columns 	= {
		'total' : fields.function(_calc_total, type='float', string="Total", store=True),
	}