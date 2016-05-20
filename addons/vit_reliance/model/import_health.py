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
		"source"			:	fields.char("Source", select=1),
	}

	def action_import_polis(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_polis(self, cr, uid, context=None):
		health_import_polis_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'health_import_polis_limit')
		_logger.warning('running cron import_health_polis limit=%s' % health_import_polis_limit)
		
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(health_import_polis_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no polis to import"
		return True

	################################################################
	# the import process: create polis holder partner
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')
		country = self.pool.get('res.country')
		indo = country.search(cr, uid, [('name','ilike','indonesia')], context=context)

		for import_health_polis in self.browse(cr, uid, ids, context=context):

			if not import_health_polis.policyno:
				ex = ex + 1
				self.write(cr, uid, import_health_polis.id ,  {'notes':'empty line'}, context=context)
				cr.commit()
				continue

			data = {
				'health_nomor_polis' 	: import_health_polis.policyno,
				'health_product'		: import_health_polis.product,
				'health_effdt'			: import_health_polis.effdt,		
				'health_expdt'			: import_health_polis.expdt,		

				'name'			: import_health_polis.clientname,
				'phone'			: import_health_polis.phone,	
				'fax' 			: import_health_polis.fax,		
				'email' 		: import_health_polis.email,
				'country_id'	: indo[0],

				'is_company'	: True,
				'comment'		: 'HEALTH',
				'initial_bu'	: 'HEALTH',
			}


			existing = partner.search(cr, uid, [
				('health_nomor_polis','=',import_health_polis.policyno),
				('name', '=', import_health_polis.clientname)
			], context=context)

			if not existing:
				partner.create(cr, uid, data, context=context)
			else:
				ex = ex + 1

			#commit per record
			i = i + 1
			cr.execute("update reliance_import_health_polis set is_imported='t' where id=%s" % import_health_polis.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s polis holder partner and skipped %s' % (i, ex) )





####################################################################
# from health_peserta csv file
# create peserta partner of a polis holder, set the parent_id to
# polis holder
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
		"source"			:	fields.char("Source"),
	}

	def action_import_peserta(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_peserta(self, cr, uid, context=None):
		health_import_peserta_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'health_import_peserta_limit')
		_logger.warning('running cron import_health_peserta, limit=%s' % health_import_peserta_limit)
		
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(health_import_peserta_limit), context=context)
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
		country = self.pool.get('res.country')
		master_jenis_kelamin = self.pool.get('reliance.jenis_kelamin')
		indo = country.search(cr, uid, [('name','ilike','indonesia')], context=context)

		old_policyno = ''

		for import_health_peserta in self.browse(cr, uid, ids, context=context):
			if not import_health_peserta.policyno:
				ex = ex + 1
				self.write(cr, uid, import_health_peserta.id ,  {'notes':'empty line'}, context=context)
				cr.commit()
				continue

			data = {}
			data2 = {}


			polis_holder = partner.search(cr, uid, [
				('health_nomor_polis','=', import_health_peserta.policyno),
				('is_company','=', True),
			], context=context)

			if not polis_holder:
				self.write(cr, uid,import_health_peserta.id, {'notes': 'NO POLIS HOLDER'}, context=context)
				cr.commit()
				ex = ex + 1 
				continue

			########################### polis holder
			polis_holder = partner.browse(cr, uid, polis_holder[0], context=context)

			########################### cari related_partner_id (induk)
			# rule: cari yang policyno dan xxxxxx-1 
			#                              01234567

			related_partner_id = False
			# import pdb; pdb.set_trace()
			if import_health_peserta.memberid[6:] != "-1":
				sql = "select id from res_partner where health_nomor_polis='%s' and health_member_id='%s'" % (
					import_health_peserta.policyno, import_health_peserta.memberid[0:6] + "-1")
				cr.execute(sql)
				res = cr.fetchone()
				if res and res[0] != None:
					related_partner_id = res[0]


			data = {
				'health_nomor_polis' 		: import_health_peserta.policyno	,
				'health_member_id'			: import_health_peserta.memberid	,
				'name' 						: import_health_peserta.membername	,
				# 'perorangan_jenis_kelamin'	: import_health_peserta.sex			,
				'perorangan_tanggal_lahir'	: import_health_peserta.birthdate	,
				'health_status' 			: import_health_peserta.status		,
				'health_relationship' 		: import_health_peserta.relationship,	

				'health_product'			: polis_holder.health_product,
				'health_effdt'				: polis_holder.health_effdt,		
				'health_expdt'				: polis_holder.health_expdt,	
				'health_parent_id'			: polis_holder.id,	
				'country_id'				: indo[0],
				'comment'					: 'HEALTH',
			}
			existing = partner.search(cr, uid, [
				('health_member_id','=', import_health_peserta.memberid),
				('name','=', import_health_peserta.membername),
				('health_nomor_polis','=', import_health_peserta.policyno),
			], context=context)

			############################ cek master jenis_kelamin
			jenis_kelamin_id = master_jenis_kelamin.get(cr, uid, 'health', import_health_peserta.sex, context=context)
			data2.update({'perorangan_jenis_kelamin': jenis_kelamin_id})
			data2.update({'initial_bu': 'HEALTH'})
			data2.update({'related_partner_id': related_partner_id})

			if not existing:
				data.update(data2)
				partner.create(cr, uid, data, context=context)
				i = i+1
			else:
				partner.write(cr, uid, existing, data2, context=context)
				ex=ex+1


			#commit per record
			cr.execute("update reliance_import_health_peserta set is_imported='t' where id=%s" % import_health_peserta.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped/updated %s' % (i, ex) )




####################################################################
# partner data
# from health_limit csv file
####################################################################
class import_health_limit(osv.osv): 
	_name 		= "reliance.import_health_limit"
	_columns 	= {
		"policyno"		:	fields.char("POLICYNO", ),
		"membid"		:	fields.char("MEMBID"),
		"manfaat"		:	fields.char("MANFAAT"),
		"limit"			:	fields.char("LIMIT"),

		'is_imported' 		: 	fields.boolean("Imported to Partner?", select=1),
		"notes"				:	fields.char("Notes"),
		"source"			:	fields.char("Source"),
	}

	def action_import_limit(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_limit(self, cr, uid, context=None):
		health_import_limit_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'health_import_limit_limit')
		_logger.warning('running cron import_health_limit, limit=%s' % health_import_limit_limit)
		
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(health_import_limit_limit), context=context)
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
		partner_health_limit = self.pool.get('reliance.partner_health_limit')

		for import_health_limit in self.browse(cr, uid, ids, context=context):
			
			if not import_health_limit.policyno:
				ex = ex + 1
				self.write(cr, uid, import_health_limit.id ,  {'notes':'empty line'}, context=context)
				cr.commit()
				continue

			# cari member 
			partner_id = partner.search(cr, uid, [
				('is_company','=',False),
				('health_member_id','=',import_health_limit.membid),
				('health_nomor_polis','=',import_health_limit.policyno)], context=context)

			if not partner_id:
				ex= ex+1
				self.write(cr, uid, import_health_limit.id, {'notes':'NO PARTNER'}, context=context)
				cr.commit()
				continue
			else:
				partner_id = partner_id[0]


			# insert into partner_health_limit
			data = {
				"partner_id"	: partner_id,
				"policyno"		: import_health_limit.policyno,
				"membid"		: import_health_limit.membid,
				"manfaat"		: import_health_limit.manfaat,
				"limit"			: import_health_limit.limit,
			}
			phl = partner_health_limit.search(cr, uid, [
				('partner_id',	'=' , partner_id),
				('policyno',	'=' , import_health_limit.policyno),
				('membid',		'=' , import_health_limit.membid),
				('manfaat',		'=' , import_health_limit.manfaat),
				], context=context)
			
			# _logger.warning('phl')
			# _logger.warning(phl)

			if not phl:
				partner_health_limit.create(cr, uid, data, context=context)
				i = i + 1
			else:
				ex= ex+1
				_logger.warning('existing limit pid=%s policyno=%s membid=%s manfaat=%s' %(partner_id,import_health_limit.policyno,import_health_limit.membid,import_health_limit.manfaat))
				partner_health_limit.write(cr, uid, phl, data, context=context)

			#commit per record
			cr.execute("update reliance_import_health_limit set is_imported='t' where id=%s" % import_health_limit.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped/updated %s' % (i, ex) )


