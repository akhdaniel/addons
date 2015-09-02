from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

class mrp_production_workcenter_line(osv.osv):
	_name    = 'mrp.production.workcenter.line'
	_inherit = 'mrp.production.workcenter.line'
	_columns = {
		'partner_id' : fields.many2one('res.partner', "Partner", 
			domain="[('category_id','=','Makloon')]",
			help="Partner with category Makloon"),
		'input'      : fields.float("Input"),
		'output'     : fields.float("Output"),
		'efficiency' : fields.float("Efficiency"),
	}

	def onchange_input(self, cr, uid, ids, input, output):
		eff = self.calculate_efficiency(cr, uid, input, output)
		res = { 'value' : {'efficiency': eff} }
		return res

	def onchange_output(self, cr, uid, ids, input, output):
		eff = self.calculate_efficiency(cr, uid, input, output)
		res = { 'value' : {'efficiency': eff} }
		return res

	def calculate_efficiency(self, cr, uid, input, output):
		if input == 0:
			eff = 0.0
		else:
			eff = 100.0 * output / input 
		return eff
