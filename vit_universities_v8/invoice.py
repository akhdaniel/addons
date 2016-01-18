from openerp.osv import osv, fields

class account_invoice(osv.Model):
	_inherit = "account.invoice"

	_columns = {
		'npm' : fields.related('partner_id','npm',type='char',string='NPM',readonly=True,store=True),
		'krs_id': fields.many2one('operasional.krs','Kartu Studi'),
	}

account_invoice()