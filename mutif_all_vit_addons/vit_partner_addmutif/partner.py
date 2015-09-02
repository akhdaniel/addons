from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class res_partner(osv.osv):
	_description = 'Partner'
	_name = "res.partner"
	_inherit = "res.partner"
	
	_columns = {
     	'code': fields.char('Kode'),
        'point': fields.char('Point'),
        # 'discount': fields.char('Diskon'),
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
        'pin_bb': fields.char('Pin BB'),
        'no_rek': fields.char('No Rekening'),
        'status_pelanggan': fields.char('Status Pelanggan')
        
	}

