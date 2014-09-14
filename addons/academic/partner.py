from openerp.osv import osv, fields

class partner(osv.Model):
	_name    = 'res.partner'
	_inherit = 'res.partner'
	_columns = {
		'is_instructor' : fields.boolean('Is Instructor')
	}
	