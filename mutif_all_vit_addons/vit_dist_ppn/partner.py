from openerp.osv import osv, fields

class partner(osv.osv):
	_name 		= 'res.partner'
	_inherit 	= 'res.partner'
	_columns = {
		'npwp'	: fields.char('NPWP'),
		'pkp'	: fields.boolean('PKP'),
	}
