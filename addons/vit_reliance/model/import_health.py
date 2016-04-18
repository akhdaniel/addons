from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)

CUST_MAPPING = {
}

COMPANY_MAPPING = {
}

AGENT_MAPPING = {
}

####################################################################
# partner data
# from health_peserta-peserta csv file
####################################################################
class import_health_peserta(osv.osv): 
	_name 		= "reliance.import_health_peserta"
	_columns 	= {
		"policyno"			:	fields.char("POLICYNO"),
		"memberid"			:	fields.char("MEMBERID"),
		"membername"		:	fields.char("MEMBERNAME"),
		"sex"				:	fields.char("SEX"),
		"birthdate"			:	fields.char("BIRTHDATE"),
		"status"			:	fields.char("STATUS"),
		"relationship"		:	fields.char("RELATIONSHIP"),

		'is_imported' 		: 	fields.boolean("Imported to Partner?", select=1),
		"notes"				:	fields.char("Notes"),
	}

	def action_import_peserta(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_peserta(self, cr, uid, context=None):
		_logger.warning('running cron import_health_peserta')
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=100, context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no peserta to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')

		for import_health_peserta in self.browse(cr, uid, ids, context=context):

			cust_data = {}

			#commit per record
			cr.execute("update reliance_import_health_peserta set is_imported='t' where id=%s" % import_health_peserta.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )





####################################################################
# partner data
# from health_polis csv file
####################################################################
class import_health_polis(osv.osv): 
	_name 		= "reliance.import_health_polis"
	_columns 	= {
		"policyno"		:	fields.char("POLICYNO"),
		"clientname"	:	fields.char("CLIENTNAME"),
		"phone"			:	fields.char("PHONE"),
		"fax"			:	fields.char("FAX"),
		"email"			:	fields.char("EMAIL"),
		"product"		:	fields.char("PRODUCT"),
		"effdt"			:	fields.char("EFFDT"),
		"expdt"			:	fields.char("EXPDT"),

		'is_imported' 		: 	fields.boolean("Imported to Partner?", select=1),
		"notes"				:	fields.char("Notes"),
	}

	def action_import_polis(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_polis(self, cr, uid, context=None):
		_logger.warning('running cron import_health_polis')
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=100, context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no polis to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')

		for import_health_polis in self.browse(cr, uid, ids, context=context):

			#commit per record
			cr.execute("update reliance_import_health_polis set is_imported='t' where id=%s" % import_health_polis.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )





####################################################################
# partner data
# from health_limit csv file
####################################################################
class import_health_limit(osv.osv): 
	_name 		= "reliance.import_health_limit"
	_columns 	= {
		"policyno"		:	fields.char("POLICYNO"),
		"membid"		:	fields.char("MEMBID"),
		"manfaat"		:	fields.char("MANFAAT"),
		"limit"			:	fields.char("LIMIT"),

		'is_imported' 		: 	fields.boolean("Imported to Partner?", select=1),
		"notes"				:	fields.char("Notes"),
	}

	def action_import_limit(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_limit(self, cr, uid, context=None):
		_logger.warning('running cron import_health_limit')
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=100, context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no limit to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')

		for import_health_limit in self.browse(cr, uid, ids, context=context):

			#commit per record
			cr.execute("update reliance_import_health_limit set is_imported='t' where id=%s" % import_health_limit.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )


