from openerp.osv import fields, osv, orm
from openerp.tools.translate import _


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    _columns = {
        'is_makloon': fields.boolean("Is Makloon"),
        'makloon_partner_id': fields.many2one('res.partner', 
            'Makloon Partner', domain=[('category_id','ilike','makloon')],
            help="Partner with category makloon"),
    }


