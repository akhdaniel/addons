from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time
import logging
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import datetime

import sets

class account_move(osv.osv):
	_inherit = 'account.move'

	def execute_cancel_journal_entries(self, cr, uid, context=None):
		################################################################################
		# id yg akan diproses
		################################################################################
		active_ids 		= context['active_ids']
		#
		_logger.info('processing from menu. active_ids=%s' % (active_ids)) 
		self.actual_cancel_journal_entries(cr, uid, active_ids, context)


	def actual_cancel_journal_entries(self, cr, uid, ids, context=None):
		i = len(ids)
		#import pdb;pdb.set_trace()
		for journal in self.browse(cr,uid, ids, context):
			# if j.state == 'draft':
			# 	raise osv.except_osv(_('Error !'),_("Journal Entry %s berstatus %s, tidak bisa di cancel !")%(j.name,j.state) )
			sql = "update account_move set state = 'draft' where id = %s" % (journal.id)
			cr.execute(sql)

		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_move_tree')
		view_id = view_ref and view_ref[1] or False,	
		return {
			'warning': {'title': _('OK!'),'message': _('Done processing. %s Journal Entry(s) canceled' % (i) )}, 
			'name' : _('Journal Entries'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'account.move',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			"context":"{}",
			'nodestroy': False,
		}


	def execute_post_journal_entries(self, cr, uid, context=None):
		################################################################################
		# id yg akan diproses
		################################################################################
		active_ids 		= context['active_ids']
		#import pdb;pdb.set_trace()
		_logger.info('processing from menu. active_ids=%s' % (active_ids)) 
		self.actual_post_journal_entries(cr, uid, active_ids, context)

	def actual_post_journal_entries(self, cr, uid, ids, context=None):
		i = len(ids)
		#import pdb;pdb.set_trace()
		for journal in self.browse(cr,uid, ids, context):
			# if j.state == 'posted':
			# 	raise osv.except_osv(_('Error !'),_("Journal Entry %s berstatus %s, tidak bisa di cancel !")%(j.name,j.state) )
			sql = "update account_move set state = 'posted' where id = %s" % (journal.id)
			cr.execute(sql)

		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_move_tree')
		view_id = view_ref and view_ref[1] or False,	
		return {
			'warning': {'title': _('OK!'),'message': _('Done processing. %s Journal Entry(s) posted' % (i) )}, 
			'name' : _('Journal Entries'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'account.move',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			"context":"{}",
			'nodestroy': False,
		}		