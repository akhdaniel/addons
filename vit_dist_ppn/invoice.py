from openerp.osv import osv, fields

class invoice(osv.Model):
	_name    = 'account.invoice'
	_inherit = 'account.invoice'
	_columns = {
		'tax_number' : fields.char('Tax Number'),
		'harga_jual' : fields.boolean('Harga Jual?'),
		'penggantian': fields.boolean('Penggantian?'),
		'uang_muka'  : fields.boolean('Uang Muka?'),
		'termijn'    : fields.boolean('Termijn?'),
		'espt_export': fields.boolean('e-SPT Export?'),
		'espt_export_date': fields.date('e-SPT Export Date')
	}
	