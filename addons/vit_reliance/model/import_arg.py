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
# from arg-customer csv file
####################################################################
class import_arg(osv.osv): 
	_name 		= "reliance.import_arg"
	_columns 	= {
		"policy_no"			:	fields.char("POLICY_NO", select=1),
		"class"				:	fields.char("CLASS"),
		"subclass"			:	fields.char("SUBCLASS"),
		"eff_date"			:	fields.char("EFF_DATE"),
		"exp_date"			:	fields.char("EXP_DATE"),
		"company_code"		:	fields.char("COMPANY_CODE"),
		"company_name"		:	fields.char("COMPANY_NAME"),
		"company_type"		:	fields.char("COMPANY_TYPE"),
		"marketing_code"	:	fields.char("MARKETING_CODE"),
		"marketing_name"	:	fields.char("MARKETING_NAME"),
		"cust_code"			:	fields.char("CUST_CODE"),
		"cust_name"			:	fields.char("CUST_NAME"),
		"cust_fullname"		:	fields.char("CUST_FULLNAME"),
		"qq"				:	fields.char("QQ"),
		"cust_cp"			:	fields.char("CUST_CP"),
		"cust_addr_1"		:	fields.char("CUST_ADDR_1"),
		"cust_addr_2"		:	fields.char("CUST_ADDR_2"),
		"cust_city"			:	fields.char("CUST_CITY"),
		"cust_postal_code"	:	fields.char("CUST_POSTAL_CODE"),
		"cust_province"		:	fields.char("CUST_PROVINCE"),
		"cust_country_name"	:	fields.char("CUST_COUNTRY_NAME"),
		'is_imported' 		: 	fields.boolean("Imported to Partner?", select=1),
		"notes"				:	fields.char("Notes"),
	}

	def action_import_partner(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner(self, cr, uid, context=None):
		_logger.warning('running cron import_arg')
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

		for import_arg in self.browse(cr, uid, ids, context=context):

			pemegang_data = {
				'name'				: import_arg.nama_pemegang,
				'policy_no'			: import_arg.policy_no,
				'is_company'		: True,
				'comment' 			: 'ARG'
			}
			
			########################## check exiting partner partner 
			pid = partner.search(cr, uid, [('policy_no','=',import_arg.policy_no)],context=context)
			if not pid:
				pid = partner.create(cr, uid, pemegang_data, context=context)	
				i = i + 1
			else:
				pid = pid[0]
				_logger.warning('Partner Pemegang exist with policy_no %s' % import_arg.policy_no)
				ex = ex + 1

			pemegang_old = import_arg.nama_pemegang

			#commit per record
			cr.execute("update reliance_import_arg set is_imported='t' where id=%s" % import_arg.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )


