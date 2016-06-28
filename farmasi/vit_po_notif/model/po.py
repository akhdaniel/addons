from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class purchase_order(osv.osv):
	_name 		= "purchase.order"
	_inherit 	= "purchase.order"

	def action_cancel(self,cr,uid,ids,context=None):
		return super(purchase_order, self).action_cancel(cr, uid, ids, context=context)

	def create(self, cr, uid,vals,context=None):
		if context is None:
			context = {}

		new_id = super(purchase_order, self).create(cr, uid, vals, context=context)

		# add followers to purchase managers
		group_obj=self.pool.get('res.groups')
		group_ids = group_obj.search(cr, uid, [
			('name','=','Manager'),('category_id','=','Purchases')], context=context)
		partner_ids = []
		for group in group_obj.browse(cr, uid, group_ids):
			for user in group.users:
				partner_ids.append(user.partner_id.id)
			if partner_ids:
				self.write(cr, uid, new_id, {'message_follower_ids': [(4, pid) for pid in partner_ids]})

		return new_id

	def send_followers(self, cr, uid, ids, body, context=None):
		records = self._get_followers(cr, uid, ids, None, None, context=context)
		followers = records[ids[0]]['message_follower_ids']
		self.message_post(cr, uid, ids, body=body,
						  subtype='mt_comment',
						  partner_ids=followers,
						  context=context)


	def wkf_confirm_order(self, cr, uid, ids, context=None):
		res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
		body = _("PO Confirmed")
		self.send_followers(cr, uid, ids, body, context=context)
		return res

	def wkf_approve_order(self, cr, uid, ids, context=None):
		res = super(purchase_order, self).wkf_approve_order(cr, uid, ids, context=context)
		body = _("PO Aproved")
		self.send_followers(cr, uid, ids, body, context=context)
		return res



