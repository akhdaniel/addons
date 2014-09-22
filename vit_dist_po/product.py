from openerp.osv import osv, fields

class product_product(osv.osv):
	_inherit = "product.product"

	_columns = {
        'uom_pack': fields.integer(string='Quantity per pack'),
        'uom_karton': fields.integer(string='Pack per box'),
        }

product_product()   