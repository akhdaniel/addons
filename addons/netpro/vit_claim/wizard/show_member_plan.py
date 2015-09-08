from openerp.osv import fields,osv

class claim_member_plan(osv.osv_memory):
	_name = 'claim_member_plan'

	def default_get(self, cr, uid, fields, context=None):
		if context is None:
			context = {}
		res = super(claim_member_plan, self).default_get(cr, uid, fields, context=context)  
		if context.get('active_model') == 'netpro.claim':            
			if context.get('active_id'):
				claim = self.pool.get('netpro.claim').browse(cr, uid, context['active_id'], context=context)
				if 'member_plan_ids' in fields:
					member_plans = self.pool.get('netpro.member_plan').search(cr, uid, [('member_id', '=', claim.member_id.id)], context=context)
					res.update({'member_plan_ids': member_plans})	
		return res	

	_columns = {
		'member_plan_ids' : fields.one2many('netpro.member_plan','member_id','Benefit'),
	}

