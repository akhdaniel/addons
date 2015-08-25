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

class mrp_production_workcenter_line(osv.osv):
	_inherit = 'mrp.production.workcenter.line'

	def action_start_wo(self, cr, uid, context=None):
		################################################################################
		# id yg akan diproses
		################################################################################
		active_ids 		= context['active_ids']
		_logger.info('processing from menu. active_ids=%s' % (active_ids)) 
		self.actual_start_wo(cr, uid, active_ids, context)

	def action_finish_wo(self, cr, uid, context=None):
		################################################################################
		# id yg akan diproses
		################################################################################
		active_ids 		= context['active_ids']
		_logger.info('processing from menu. active_ids=%s' % (active_ids)) 
		self.actual_finish_wo(cr, uid, active_ids, context)


	def actual_start_wo(self, cr, uid, ids, context=None):
		i = len(ids)
		for wo in self.browse(cr,uid, ids, context):
			if wo.state not in ('draft','pause'):
				raise osv.except_osv(_('Error !'),_("Work Order %s dengan nomor produksi %s berstatus %s, tidak bisa di start !")%(wo.name,wo.production_id.name,wo.state) )
			self.write(cr,uid,wo.id,{'state':'startworking','date_start':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mrp_operations', 'mrp_production_workcenter_tree_view_inherit')
		view_id = view_ref and view_ref[1] or False,	
		return {
			'warning': {'title': _('OK!'),'message': _('Done processing. %s Work Orders started' % (i) )}, 
			'name' : _('Work Orders'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'mrp.production.workcenter.line',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			"context":"{}",
			'nodestroy': False,
		}


	def actual_finish_wo(self, cr, uid, ids, context=None):
		i = len(ids)
		#import pdb; pdb.set_trace()
		for wo in self.browse(cr,uid, ids, context):
			if wo.state != 'startworking':
				raise osv.except_osv(_('Error !'),_("Work Order %s dengan nomor produksi %s berstatus %s, tidak bisa di finish !")%(wo.name,wo.production_id.name,wo.state) )
			
			fmt = tools.DEFAULT_SERVER_DATETIME_FORMAT
			date_start = datetime.datetime.strptime(wo.date_start, fmt)
			date_end = datetime.datetime.now()
			gap_date = date_end-date_start
			waktu_bagi_rata =  gap_date/i

			waktu_hasil = date_start+waktu_bagi_rata

			delay = (waktu_bagi_rata.days*24)+(float(waktu_bagi_rata.seconds)/3600)

			self.write(cr,uid,wo.id,{'state':'done','date_finished':str(waktu_hasil),'delay':delay})
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mrp_operations', 'mrp_production_workcenter_tree_view_inherit')
		view_id = view_ref and view_ref[1] or False,	
		return {
			'warning': {'title': _('OK!'),'message': _('Done processing. %s Work Orders Finished' % (i) )}, 
			'name' : _('Work Orders'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'mrp.production.workcenter.line',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			"context":"{}",
			'nodestroy': False,
		}			