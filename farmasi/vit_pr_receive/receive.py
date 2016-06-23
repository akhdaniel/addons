from openerp.osv import fields, osv

class receive(osv.osv):
	_inherit = 'stock.picking'
	_columns = {
				'department_id': fields.many2one('hr.department', 'Department'),
				'picking_type_id': fields.many2one('stock.picking.type', 'Picking Type', domain=[('code','=', 'suppliers')]),
	}