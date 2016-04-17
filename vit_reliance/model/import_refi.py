from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)

####################################################################
# partner data
# from refi-customer csv file
####################################################################
class import_refi(osv.osv): 
	_name 		= "reliance.import_refi"
	_columns 	= {


		'is_imported' 		: 	fields.boolean("Imported to Partner?", select=1),
		"notes"				:	fields.char("Notes"),
	}

	def action_import_partner(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner(self, cr, uid, context=None):
		_logger.warning('running cron import_refi')
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=100, context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		for import_refi in self.browse(cr, uid, ids, context=context):

			pemegang_data = {
				'name'				: import_refi.nama_pemegang,
				'policy_no'			: import_refi.policy_no,
				'is_company'		: True,
				'comment' 			: 'REFI'
			}
			
			########################## check exiting partner partner 
			pid = partner.search(cr, uid, [('policy_no','=',import_refi.policy_no)],context=context)
			if not pid:
				pid = partner.create(cr, uid, pemegang_data, context=context)	
				i = i + 1
			else:
				pid = pid[0]
				_logger.warning('Partner exist with policy_no %s' % import_refi.policy_no)
				ex = ex + 1

			pemegang_old = import_refi.nama_pemegang

			#commit per record
			cr.execute("update reliance_import_refi set is_imported='t' where id=%s" % import_refi.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )


