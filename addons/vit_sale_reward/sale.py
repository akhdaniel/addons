from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
import math

_logger = logging.getLogger(__name__)

class sale_order(osv.osv):
	_name 		= "sale.order"
	_inherit 	= "sale.order"
	
	_columns    = {
		'point'  : fields.float('Point Reward')
	}
	
	def action_button_confirm(self, cr, uid, ids, context=None):
		res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)

		#########################################################################
		# cek SO total
		#########################################################################
		so                = self.browse(cr, uid, ids[0] , context=context)

		#########################################################################
		# skip if state = draft, misalnya gagal execption
		#########################################################################
		if so.state == 'draft':
			return res
		
		##############################################################################
		# ambil master reward
		##############################################################################
		reward_obj   = self.pool.get('vit_sale_reward.master_reward')
		reward_ids   = reward_obj.search(cr, uid, 
			[('is_active','=', True)], context=context)

		for reward_id in reward_ids:
			#########################################################################
			# the reward record
			#########################################################################
			reward            = reward_obj.browse(cr, uid, reward_id) 


			#########################################################################
			# calculate point: so.amount_total / reward.so_total , dibulatkan ke integer
			#########################################################################
			point             = math.trunc(so.amount_total / reward.so_total )

			#########################################################################
			# partner object, increment the point
			#########################################################################
			#import pdb; pdb.set_trace()
			partner_obj       = self.pool.get('res.partner')
			partner           = partner_obj.browse(cr, uid, so.partner_id.id, context=context)
			# old_point         = partner.point or 0
			# data = { 'point' : (int(old_point) + point ) }
			# partner_obj.write(cr, uid, so.partner_id.id , data , context=context)
			pr_obj            = self.pool.get('vit_sale_reward.partner_reward')
			pr_obj.point_trx(cr, uid, so.partner_id.id, point, 'in', so.name, context=context)

			#########################################################################
			# update SO point
			#########################################################################
			data = {'point' : point}
			self.write(cr, uid, ids, data, context=context)

			#########################################################################
			# create account move utk point
			#########################################################################
			am_obj            = self.pool.get('account.move')



		return res


	def action_cancel(self, cr, uid, ids, context=None):
		res = super(sale_order, self).action_cancel(cr, uid, ids, context=context)
		#########################################################################
		# cek SO total
		#########################################################################
		so                = self.browse(cr, uid, ids[0] , context=context)

		#########################################################################
		# skip if state != cancel, gagal cancel
		#########################################################################
		if so.state != 'cancel':
			return res

		point             = so.point or 0
		pr_obj            = self.pool.get('vit_sale_reward.partner_reward')
		pr_obj.point_trx(cr, uid, so.partner_id.id, -point, 'out', '%s - CANCEL' % (so.name), context=context)


		return res
