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
	}



	def get_health_all_member(self, cr, uid, nomor_polis, context=None):
		members = False
		pid = self.search(cr, uid, [('health_nomor_polis','=',nomor_polis)], context=context)
		_logger.warning('health_nomor_polis=%s' % nomor_polis)

		if pid:
			members = self.search_read(cr,uid,[('health_parent_id','=',pid[0])],context=context)
		else:
			_logger.error('no partner with health_nomor_polis=%s' % nomor_polis)
		return members 

	def get_health_member(self, cr, uid, reliance_id, context=None):
		member = self.search_read(cr,uid,[('reliance_id','=',reliance_id)],context=context)
		return member

	def get_health_member_by_member_id(self, cr, uid, member_id, context=None):
		member = self.search_read(cr,uid,[('health_member_id','=',member_id)],context=context)
		return member

	def get_health_holder(self, cr, uid, reliance_id, context=None):
		holder = False
		pid = self.search(cr, uid, [('reliance_id','=',reliance_id)], context=context)

		if pid:
			if not pid[0].health_parent_id:
				raise osv.except_osv(_('error'),_("not linked to any health_parent_id") ) 
			holder = self.search_read(cr,uid,[('id','=',pid[0].health_parent_id.id)],context=context)
		else:
			raise osv.except_osv(_('error'),'no partner with reliance_id=%s' % reliance_id) 
		return holder

