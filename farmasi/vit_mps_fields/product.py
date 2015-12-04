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


class product_product(osv.osv):
    _inherit = "product.product"    

    def get_detail_total_avail(self, cr, uid, context=None):
        stock_move      = self.pool.get('stock.move')
        loc_obj         = self.pool.get('stock.location')

        product = self.browse(cr, uid, ids, context=context)

        #ambil 6 digit pertama, search dulu product yang sama
        product_ref = product.default_code[:6]
        lot_id = False
        qty_available = 0

        # cari detail produk yang is_header = false dan kode produknya 6 digit pertama sama
        same_product = self.pool.get('product.product').search(cr,uid,
            [('default_code','ilike',str(product_ref+'%')),('is_header','=',False)])
        print("product_ref",product_ref, "same_product",same_product)

        total_lot_qty = 0.00
        source_location_id = loc_obj.search(cr,uid,[('name','=','GBA/Stock')], context=context)[0]

        if same_product :

            # ambil lot ids nya
            cr.execute("SELECT id,product_id FROM stock_production_lot \
                        WHERE product_id IN %s AND life_date IS NOT NULL \
                        ORDER BY life_date ASC" , (tuple(same_product),))  
            lot_ids    = cr.fetchall()
            
            if lot_ids : # ada lot / serial number
                for lot in lot_ids:
                    #cari apakah ada stock barang dengan lot tsb
                    #cari di quant qty product sesuai dengan id lot
                    cr.execute ('SELECT sum(qty) FROM stock_quant WHERE location_id = %s AND lot_id = %s',
                        (source_location_id,lot[0]))
                    hasil   = cr.fetchone()
                    print "hasil",hasil
                    if hasil:
                        if hasil[0] != None : # ada stock lot 
                            lot_id = lot[0]
                            hasil = hasil[0]
                            total_lot_qty = total_lot_qty + hasil 


        return total_lot_qty

