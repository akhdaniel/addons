from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class ir_sequence(osv.osv):
	_inherit 		= "ir.sequence"

	_columns = {
		'is_autoreset_monthly' : fields.boolean('Is Auto Reset Monthly'),
		'is_autoreset_yearly' : fields.boolean('Is Auto Reset Yearly'),
	}

	def cron_reset(self, cr, uid, context=None):
		monthly_ids = self.search(cr, uid, [('is_autoreset_monthly','=',True)], context=context)
		if monthly_ids:
			self.write(cr, uid, monthly_ids, {'number_next_actual':1}, context=context)
			_logger.info('Next Number reset to 1 for')
			_logger.info(monthly_ids)
		else:
			_logger.info('No sequence to reset today this month')

		if time.strftime('%m-%d') == '01-01':
			yearly_ids = self.search(cr, uid, [('is_autoreset_yearly','=',True)], context=context)
			if yearly_ids:
				self.write(cr, uid, yearly_ids, {'number_next_actual':1}, context=context)
				_logger.info('Next Number reset to 1 for')
				_logger.info(yearly_ids)
		else:
			_logger.info('No sequence to reset today this year')

		return True 
