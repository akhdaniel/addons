import time
import base64
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
import pytz 
from openerp.tools.float_utils import float_round

class wtc_shop(osv.osv):
    _name = 'wtc.shop'
    _description = 'Shop'
    
    _columns = {
                'name' : fields.char(string='Shop Name', required=True),
        #        'picking_id' :fields.many2one('stock.picking',string='Outgoing Shipments',domain="[('picking_type_code','=','outgoing')]"),
                'payment_default_id': fields.many2one('account.payment.term', 'Default Payment Term', required=True),
                'pricelist_id': fields.many2one('product.pricelist', 'Pricelist'),
        #        'project_id': fields.many2one('account.analytic.account', 'Analytic Account', domain=[('parent_id', '!=', False)]),
                'company_id': fields.many2one('res.company', 'Company', required=False),
                'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=True),
    }
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'wtc.shop', context=c),
    }               
                  
    
class sales_order(osv.osv):
    _inherit = 'sale.order'
    
    _columns = {
                'shop_id' : fields.many2one('wtc.shop',string='Shop Name', required=True)
                }

class pos_product_available(osv.osv):
    _name = "pos.product.available"
    _rec_name = 'product_id'

    _columns = {
        'product_id' : fields.many2one('product.product','Products'),
        'pos_id' : fields.many2one('pos.session',string='Pos Session'),
        'warehouse_id': fields.many2one('stock.warehouse','Warehouse',help='Where product available in this warehouse'),
    }

class pos_order(osv.osv):
    _inherit = 'pos.order'
    
    _columns = {
        'shop_id' : fields.many2one('wtc.shop',string='Shop Name', required=False),
    }

class session_order(osv.osv):
    _inherit = 'pos.session'
    
    _columns = {
        'pos_prod_ids' : fields.one2many('pos.product.available','pos_id',"Stock Available"),
        'shop_id' : fields.many2one('wtc.shop',string='Shop Name', required=True)
    }    

    def onchange_shop(self, cr, uid, ids, shop_id, pos_prod_ids, context=None):
        return {} 