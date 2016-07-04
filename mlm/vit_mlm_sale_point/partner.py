from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
import math

_logger = logging.getLogger(__name__)

class partner(osv.osv):
	_name 		= "res.partner"
	_inherit 	= "res.partner"

	def _calc_point(self, cr, uid, ids, field, arg, context=None):
		results = {}
		pr_obj = self.pool.get('vit_sale_reward.partner_reward')
		for p in self.browse(cr, uid, ids, context=context):
			results[p.id] = 0
			pr_ids = pr_obj.search(cr, uid, [('partner_id','=',p.id)], context=context)
			for pr in pr_obj.browse(cr, uid, pr_ids, context=context):
				if pr.type == 'in':
					x = 1
				elif pr.type == 'out':
					x = -1
				else:
					x = 0
				results[p.id] = results.get(p.id,0) + pr.point*x 

		# return harus berupa dictionary dengan key id partner
		# contoh kalau 3 records:
		# {
		#      1 : 50,
		#      2 : 255,
		#      3 : 100
		# }
		return results

	_columns    = {
		'point'  : fields.function( _calc_point, type="integer", string='Point Reward'),
		'partner_reward_ids' : fields.one2many('vit_sale_reward.partner_reward',
			'partner_id','Point Reward Transactions', 
			order="date",
			ondelete="cascade"),
        'point': fields.char('Point'),
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
        'status_pelanggan': fields.char('Customer State')
	}