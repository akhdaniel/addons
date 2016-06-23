from openerp.osv import fields, osv

class purchase_order(osv.osv):
	_inherit = 'purchase.order'
	_columns = {
				'department_id': fields.many2one('hr.department', 'Department'),
	}

	def action_picking_create(self, cr, uid, ids, context=None):
		res = super(purchase_order, self).action_picking_create(cr, uid, ids, context=context)
		cr.commit()
		for order in self.browse(cr, uid, ids):
			a = self.pool.get('stock.picking').write(cr,uid,res,{'department_id':order.department_id.id})
		return a