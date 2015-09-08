from openerp.osv import fields,osv

class claim_member_history(osv.osv_memory):
	_name = 'claim_member_history'

	def default_get(self, cr, uid, fields, context=None):
		if context is None:
			context = {}
		import pdb;pdb.set_trace()
		res = super(claim_member_history, self).default_get(cr, uid, fields, context=context)
		if context.get('active_model') == 'netpro.claim':
			if context.get('active_id'):
				claim = self.pool.get('netpro.claim').browse(cr, uid, context.get('active_id'), context=context)
				if 'claim_history_ids' in fields:
					member_histories = self.pool.get('netpro.member_claim_history').search(cr, uid, [('member_id', '=', claim.member_id.id)], context=context)
					res.update({'claim_history_ids': member_histories})
		return res

	_columns = {
		'claim_history_ids' : fields.one2many('netpro.member_claim_history','member_id','Claim Histories')
	}