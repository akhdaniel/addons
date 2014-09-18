from openerp.osv import osv, fields

class invoice(osv.Model):
	_name    = 'account.invoice'
	_inherit = 'account.invoice'
	_columns = {
		'tax_number' : fields.char('Tax Number')
	}
	