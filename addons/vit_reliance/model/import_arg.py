from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)

CUST_MAPPING = {
	"cust_code"			: "arg_cust_code",
	"cust_fullname"		: "name",
	"cust_addr_1"		: "street",
	"cust_addr_2"		: "street2",
	"cust_city"			: "city",
	"cust_postal_code"	: "zip",
	"cust_country_name"	: "country_id",
	"cust_province"		: "state_id",
}

POLIS_MAPPING = {
	"policy_no"			: "arg_nomor_polis",
	"product_class"		: "arg_class",
	"subclass"			: "arg_subclass",
	"eff_date"			: "arg_eff_date",
	"exp_date"			: "arg_exp_date",	
	"company_code"		: "arg_company_code",
	"company_name"		: "arg_company_name",
	"company_type"		: "arg_company_type",
	"marketing_code"	: "arg_marketing_code",
	"marketing_name"	: "arg_marketing_name",
	"qq"				: "arg_qq",
	"cust_cp"			: "arg_cp",
}

POLIS_RISK_MAPPING = {
	"asset_description"			:	"asset_description",		
	"item_no"					:	"item_no",	
	"tahun"						:	"tahun",	
	"total_premi"				:	"total_premi",	
	"total_nilai_pertanggungan"	:	"total_nilai_pertanggungan",	
}

####################################################################
# partner data
# from arg-customer csv file
####################################################################
class import_arg(osv.osv): 
	_name 		= "reliance.import_arg"
	_columns 	= {
		"policy_no"			:	fields.char("POLICY_NO", select=1),
		"product_class"		:	fields.char("CLASS"),
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

		"status_policy"		:	fields.char("STATUS_POLICY"),
		"source_of_business":	fields.char("SOURCE_OF_BUSINESS"), 

		'is_imported' 		: 	fields.boolean("Imported to Partner?", select=1),
		"notes"				:	fields.char("Notes"),
		"source"			:	fields.char("Source"),
	}

	def action_import_partner(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)

	def cron_import_partner(self, cr, uid, context=None):
		arg_import_partner_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'arg_import_partner_limit')
		_logger.warning('running cron arg_import_partner, limit=%s' % arg_import_partner_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(arg_import_partner_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	##############################################################################
	# the import process
	##############################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0
		polis_created = 0

		partner = self.pool.get('res.partner')
		polis   = self.pool.get('reliance.arg_partner_polis')

		for import_arg in self.browse(cr, uid, ids, context=context):

			if not import_arg.policy_no:
				ex = ex + 1
				self.write(cr, uid, import_arg.id ,  
					{'notes':'empty line', 'is_imported': True}, context=context)
				cr.commit()
				continue



			##############################################################################   
			# creating partner from COMPANY_CODE, COMPANY_NAME, is company = True
			##############################################################################   
			# company_pid,i,ex = self.import_company(cr, uid, import_arg, partner, i,ex)


			##############################################################################   
			# creating partner from CUST_CODE, CUST_NAME, is company = True
			##############################################################################   
			# cust_pid,i,ex = self.import_cust(cr, uid, import_arg, partner, i,ex)


			############################################################################## 
			# creating partner from QQ , is company = False
			##############################################################################   
			qq_pid,i,ex = self.import_qq(cr, uid, import_arg, partner, False, i, ex)

			##############################################################################   
			# creating Polis for the above partner
			##############################################################################   
			polis_created,i,ex = self.import_polis(cr, uid, import_arg, polis, qq_pid, partner, i,ex,polis_created)

			##############################################################################   
			#commit per record
			##############################################################################   
			cr.execute("update reliance_import_arg set is_imported='t' where id=%s" % import_arg.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s , %s polis created' % (i, ex, polis_created) )

	##############################################################################   
	# import cust 
	##############################################################################   
	def import_cust(self, cr, uid, import_arg, partner, i, ex, context=None):
		country = self.pool.get('res.country')
		states_mapping = self.pool.get('reliance.states_mapping')

		cust_data = {}
		country_id = False

		for k in CUST_MAPPING.keys():
			partner_fname = CUST_MAPPING[k]
			import_ls_fname = "import_arg.%s" % k 
			cust_data.update( {partner_fname : eval(import_ls_fname)})


		if not import_arg.cust_country_name:
			cname= 'indonesia'
			self.write(cr, uid, [import_arg.id], {'notes':'EMPTY COUNTRY, ASSUME INDONESIA'}, context=context)
		else:
			cname = import_arg.cust_country_name

		country_id = country.search(cr, uid, [('name','ilike', cname)], context=context)
		country_id = country_id[0]
		cust_data.update({'country_id': country_id})

		# if import_arg.cust_province:
		# 	state_id = country.find_or_create_state(cr, uid, import_arg.cust_province, country_id, context=context)
		# 	cust_data.update({'state_id': state_id})

		state_id = states_mapping.get(cr, uid, import_arg.cust_province, context=context)
		cust_data2.update({'state_id': state_id})
		cust_data2.update({'initial_bu': 'ARG'})

		cust_data.update({'is_company': True})
		cust_data.update({'comment': 'ARG CUST_NAME'})
		
		##############################################################################   
		# check exiting partner partner by CUST_CODE
		##############################################################################   
		pid = partner.search(cr, uid, [('arg_cust_code','=',import_arg.cust_code)],context=context)
		if not pid:
			cust_data.update(cust_data2)
			pid = partner.create(cr, uid, cust_data, context=context)	
			i = i + 1
		else:
			pid = pid[0]
			partner.write(cr, uid, pid, cust_data2, context=context)	
			_logger.warning('Partner exist with arg_cust_code %s' % import_arg.cust_code)
			ex = ex + 1

		return pid,i, ex

	##############################################################################   
	# import company 
	##############################################################################   
	def import_company(self, cr, uid, import_arg, partner, i, ex, context=None):
		country = self.pool.get('res.country')
		states_mapping = self.pool.get('reliance.states_mapping')

		cust_data = {}
		country_id = False

		for k in CUST_MAPPING.keys():
			partner_fname = CUST_MAPPING[k]
			import_ls_fname = "import_arg.%s" % k 
			cust_data.update( {partner_fname : eval(import_ls_fname)})


		if not import_arg.cust_country_name:
			cname= 'indonesia'
			self.write(cr, uid, [import_arg.id], {'notes':'EMPTY COUNTRY, ASSUME INDONESIA'}, context=context)
		else:
			cname = import_arg.cust_country_name

		country_id = country.search(cr, uid, [('name','ilike', cname)], context=context)
		country_id = country_id[0]
		cust_data.update({'country_id': country_id})

		# if import_arg.cust_province:
		# 	state_id = country.find_or_create_state(cr, uid, import_arg.cust_province, country_id, context=context)
		# 	cust_data.update({'state_id': state_id})
		state_id = states_mapping.get(cr, uid, import_arg.cust_province, context=context)
		cust_data2.update({'state_id': state_id})
		cust_data2.update({'initial_bu': 'ARG'})

		cust_data.update({'is_company': True})
		cust_data.update({'comment': 'ARG COMPANY_NAME'})
		
		##############################################################################   
		# check exiting partner partner by CUST_CODE
		##############################################################################   
		pid = partner.search(cr, uid, [('arg_company_code','=',import_arg.company_code)],context=context)
		if not pid:
			cust_data.update(cust_data2)
			pid = partner.create(cr, uid, cust_data, context=context)	
			i = i + 1
		else:
			pid = pid[0]
			partner.write(cr, uid, pid, cust_data2, context=context)	
			_logger.warning('Partner exist with arg_company_code %s' % import_arg.company_code)
			ex = ex + 1

		return pid,i, ex

	##############################################################################   
	# import polis
	##############################################################################   
	def import_polis(self, cr, uid, import_arg, polis,pid, partner, i, ex, polis_created,context=None):
		

		polis_id = polis.search(cr, uid, [('arg_nomor_polis','=',import_arg.policy_no),
			('partner_id','=',pid)], context=context)

		if not polis_id:
			polis_data = {}

			for k in POLIS_MAPPING.keys():
				polis_fname = POLIS_MAPPING[k]
				import_polis_fname = "import_arg.%s" % k 
				polis_data.update( {polis_fname : eval(import_polis_fname)})

			polis_data.update({'partner_id': pid})
			polis.create(cr, uid, polis_data, context=context)
			polis_created = polis_created + 1


			#update partner's arg_nomor_polis
			qq = partner.browse(cr, uid, pid, context=context)
			if qq.arg_nomor_polis:
				nomors = qq.arg_nomor_polis + ',' 
			else:
				nomors = ''

			nomors = nomors + import_arg.policy_no
			arg_nomor_polis = nomors
			partner.write(cr, uid, pid, {'arg_nomor_polis': arg_nomor_polis}, context=context)


		else:
			polis_id = polis_id[0]
			_logger.warning('Polis exist with arg_nomor_polis %s' % import_arg.policy_no)
			ex = ex + 1

		return polis_created,i,ex

	##############################################################################   
	# import qq
	##############################################################################   
	def import_qq(self, cr, uid, import_arg, partner, parent_id, i ,ex,context=None):


		if not import_arg.qq:
			qq_name = import_arg.cust_fullname.strip()			
		else:
			qq_name = import_arg.qq.strip().replace("QQ. ", "").replace("QQ ","")

		country = self.pool.get('res.country')
		states_mapping = self.pool.get('reliance.states_mapping')

		cust_data = {}
		cust_data2 = {}
		country_id = False

		for k in CUST_MAPPING.keys():
			partner_fname = CUST_MAPPING[k]
			import_ls_fname = "import_arg.%s" % k 
			cust_data.update( {partner_fname : eval(import_ls_fname)})


		if not import_arg.cust_country_name:
			cname= 'indonesia'
			self.write(cr, uid, [import_arg.id], {'notes':'EMPTY COUNTRY, ASSUME INDONESIA'}, context=context)
		else:
			cname = import_arg.cust_country_name

		country_id = country.search(cr, uid, [('name','ilike', cname)], context=context)
		country_id = country_id[0]
		cust_data.update({'country_id': country_id})
		# import pdb; pdb.set_trace()

		# if import_arg.cust_province:
		# 	state_id = country.find_or_create_state(cr, uid, import_arg.cust_province, country_id, context=context)
		state_id = states_mapping.get(cr, uid, import_arg.cust_province, context=context)
		cust_data2.update({'state_id': state_id})
		cust_data2.update({'initial_bu' : 'ARG'})

		cust_data.update({'name': qq_name})
		cust_data.update({'arg_parent_id': parent_id})
		cust_data.update({'comment': 'ARG QQ'})
		cust_data.update({'initial_bu': 'ARG'})
		
		##############################################################################   
		# check exiting partner partner by QQ's polis no
		##############################################################################   
		pid = partner.search(cr, uid, [('arg_cust_code','=',import_arg.cust_code),
			('name','=',qq_name)],context=context)
		if not pid:
			cust_data.update(cust_data2)
			pid = partner.create(cr, uid, cust_data, context=context)	
			i = i + 1
		else:
			pid = pid[0]
			partner.write(cr, uid, pid, cust_data2, context=context)	
			_logger.warning('QQ Partner exist with name=%s cust_code=%s' % (import_arg.cust_code, qq_name))
			ex = ex + 1

		return pid,i, ex



class import_arg_polis_risk(osv.osv): 
	_name = "reliance.import_arg_polis_risk"
	_columns = {
		"policy_no"					:	fields.char("POLICY_NO"),
		"asset_description"			:	fields.char("ASSET_DESCRIPTION"),
		"item_no"					:	fields.char("ITEM_NO"),
		"tahun"						:	fields.char("TAHUN"),
		"total_premi"				:	fields.char("TOTAL_PREMI"),
		"total_nilai_pertanggungan"	:	fields.char("TOTAL_NILAI_PERTANGGUNGAN"),

		'is_imported' 		: 	fields.boolean("Imported to Polis Risk?", select=1),
		"notes"				:	fields.char("Notes"),
		"source"			:	fields.char("Source"),
	}


	def action_import(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import(self, cr, uid, context=None):
		arg_import_polis_risk_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'arg_import_polis_risk_limit')
		_logger.warning('running cron import_arg_polis_risk, limit=%s' % arg_import_polis_risk_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(arg_import_polis_risk_limit), context=context)
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
		upd = 0
		cust_data = {}

		partner = self.pool.get('res.partner')
		polis = self.pool.get('reliance.arg_partner_polis')
		risk = self.pool.get('reliance.arg_partner_polis_risk')

		for import_arg in self.browse(cr, uid, ids, context=context):	
			if not import_arg.policy_no:
				ex = ex + 1
				self.write(cr, uid, import_arg.id ,  {'notes':'empty line', 'is_imported':True}, context=context)
				cr.commit()
				continue
			

			polis_id = polis.search(cr, uid, [('arg_nomor_polis','=',import_arg.policy_no.strip())], context=context) 

			if not polis_id:
				ex = ex + 1
				self.write(cr, uid, import_arg.id ,  {'notes':'NO POLIS NO'}, context=context)
				cr.commit()
				continue
			else:
				polis_id = polis_id[0]

			for k in POLIS_RISK_MAPPING.keys():
				partner_fname = POLIS_RISK_MAPPING[k]
				import_ls_fname = "import_arg.%s" % k 
				cust_data.update( {partner_fname : eval(import_ls_fname)})


			polis_data = polis.browse(cr, uid, polis_id, context=context)

			if not polis_data.partner_id:
				ex = ex + 1
				self.write(cr, uid, import_arg.id ,  {'notes':'POLIS NO PARTNER ERROR'}, context=context)
				cr.commit()
				continue


			cust_data.update({'policy_id': polis_data.id})
			cust_data.update({'partner_id': polis_data.partner_id.id})

			exist = risk.search(cr, uid, [
				('policy_id','=',polis_id),
				('item_no','=',import_arg.item_no),
				('tahun','=',int(import_arg.tahun)),
				], context=context)
			if not exist:
				risk.create(cr, uid, cust_data, context=context)
			else:
				upd = upd + 1
				risk.write(cr, uid, exist[0], cust_data, context=context)

			#commit per record
			i = i + 1
			cr.execute("update reliance_import_arg_polis_risk set is_imported='t' where id=%s" % import_arg.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s polis risk, skipped %s, updated=%s' % (i, ex, upd) )
