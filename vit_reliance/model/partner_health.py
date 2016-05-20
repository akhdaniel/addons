from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class partner(osv.osv):
	_name 		= "res.partner"
	_inherit 	= "res.partner"
	_columns = {
		"health_nomor_polis"	: fields.char("Health Nomor Polis", select=1),
		"health_member_id"		: fields.char("Health Member ID", select=1),
		"health_parent_id"		: fields.many2one('res.partner', 'Health Polis Holder' , select=1),

		"health_status"			: fields.char("Health Status", select=1),
		"health_relationship"	: fields.char("Health Relationship"),
		"health_product"		: fields.char("Health Product", select=1),
		"health_effdt"			: fields.date("Health Eff. Date"),
		"health_expdt"			: fields.date("Health Exp. Date"),

		"health_limit_ids"		: fields.one2many('reliance.partner_health_limit','partner_id','Health Limit', ondelete="cascade"),
	}

	#####################################################################
	# mengambil data semua member suatu polis
	#####################################################################
	def get_health_all_member(self, cr, uid, nomor_polis, context=None):
		members = False
		pid = self.search(cr, uid, [('health_nomor_polis','=',nomor_polis)], context=context)
		_logger.warning('health_nomor_polis=%s' % nomor_polis)

		if pid:
			members = self.search_read(cr,uid,[('health_parent_id','=',pid[0])],context=context)
		else:
			_logger.error('no partner with health_nomor_polis=%s' % nomor_polis)
		return members 

	#####################################################################
	# mengambil data member health  berdasarkan nomor RelianceID
	#####################################################################
	def get_health_member(self, cr, uid, reliance_id, context=None):
		member = self.search_read(cr,uid,[('reliance_id','=',reliance_id)],context=context)
		return member

	#####################################################################
	# mengambil data member health  berdasarkan nomor Member ID
	#####################################################################
	def get_health_member_by_member_id(self, cr, uid, member_id, context=None):
		member = self.search_read(cr,uid,[('health_member_id','=',member_id)],context=context)
		return member

	#####################################################################
	# mengambil data Polis Holder seorang member
	#####################################################################
	def get_health_holder(self, cr, uid, reliance_id, context=None):
		holder = False
		pid = self.search_read(cr, uid, [('reliance_id','=',reliance_id)], context=context)

		if pid:
			if not pid[0]['health_parent_id']:
				raise osv.except_osv(_('error'),_("not linked to any health_parent_id") ) 
			holder = self.search_read(cr,uid,[('id','=',pid[0]['health_parent_id'][0])],context=context)
		else:
			raise osv.except_osv(_('error'),'no partner with reliance_id=%s' % reliance_id) 
		return holder

	#####################################################################
	# mengabmbil data benefit limit suatu member berdasarkan Reliance ID
	#####################################################################
	def get_health_limit(self, cr, uid, reliance_id, context=None):
		pid = self.search(cr, uid, [('reliance_id','=',reliance_id)], context=context)

		if not pid:
			raise osv.except_osv(_('error'), 'no partner with reliance_id=%s' % reliance_id ) 

		limit = self.pool.get('reliance.partner_health_limit')

		limits = limit.search_read(cr, uid, [('partner_id','=',pid[0])], context=context)

		return limits 

	#####################################################################
	# mengabmbil data benefit limit suatu member berdasarkan 
	# Policy Number dan Member ID
	#####################################################################
	def get_health_limit_by_member_id(self, cr, uid, policy_no, member_id, context=None):
		pid = self.search(cr, uid, [
			('health_nomor_polis','=',policy_no),
			('health_member_id','=',member_id),
			('is_company','=',False)
			], context=context)

		if not pid:
			raise osv.except_osv(_('error'), 'no partner with member_id=%s and policyno=%s' % (member_id,policy_no) ) 

		limit = self.pool.get('reliance.partner_health_limit')
		limits = limit.search_read(cr, uid, [('partner_id','=',pid[0])], context=context)

		return limits 

class partner_health_limit(osv.osv):
	_name 		= "reliance.partner_health_limit"
	_rec_name  	= "manfaat"
	_columns = {
		"partner_id"	: fields.many2one('res.partner', 'Partner', select=1),
		"policyno"		: fields.char("Policy No", select=1),
		"membid"		: fields.char("Member ID", select=1),
		"manfaat"		: fields.char("Manfaat", select=1),
		"limit"			: fields.float("Limit"),
	}
