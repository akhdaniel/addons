import math
import re
import time
#from _common import ceiling

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import psycopg2

import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round, float_compare


class product_template(osv.osv):
    _inherit = "product.template"     

    def get_detail_total_avail(self, cr, uid, ids, field, arg, context=None):
        stock_move      = self.pool.get('stock.move')
        loc_obj         = self.pool.get('stock.location')
        results = {}

        source_location_id = loc_obj.search(cr,uid,[('name','=','Stock')], 
            context=context)[0]

        for product in self.browse(cr, uid, ids, context=context):
            total_qty = 0.00

            results[product.id] = 0.0

            #ambil 6 digit pertama, search dulu product yang sama
            product_ref = product.default_code[:6]

            # cari detail produk yang is_header = false dan kode produknya 6 digit pertama sama
            same_product = self.pool.get('product.product').search(cr,uid,
                [('default_code','ilike',str(product_ref+'%')),('is_header','=',False)])

            # print("product_ref",product_ref, "same_product",same_product)

            for prod in self.browse(cr, uid, same_product, context=context):
                print "   produk ", prod.id, " ", prod.default_code, " ", prod.virtual_available
                total_qty = total_qty  + prod.virtual_available
            # print "total ", total_qty
            results[product.id] = total_qty

        return results    

    _columns = {
        'detail_available' : fields.function(get_detail_total_avail, type='float', string="Detail Available"),
    }

