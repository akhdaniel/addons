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
            a = self.pool.get('product.template').search(cr, uid, [('parent_id','=', product.id)])
            for b in self.browse(cr, uid, a):
                total_qty = total_qty + b.virtual_available 
            # print "total ", total_qty
            results[product.id] = total_qty

        return results

    def get_detail_total_qty(self, cr, uid, ids, field, arg, context=None):
        stock_move      = self.pool.get('stock.move')
        loc_obj         = self.pool.get('stock.location')
        results = {}

        source_location_id = loc_obj.search(cr,uid,[('name','=','Stock')], 
            context=context)[0]

        for product in self.browse(cr, uid, ids, context=context):

            total_qty = 0.00

            results[product.id] = 0.0
            #ambil 6 digit pertama, search dulu product yang sama
            a = self.pool.get('product.template').search(cr, uid, [('parent_id','=', product.id)])
            for b in self.browse(cr, uid, a):
                total_qty = total_qty + b.qty_available 
            # print "total ", total_qty
            results[product.id] = total_qty

        return results

    def get_detail_total_incoming(self, cr, uid, ids, field, arg, context=None):
        stock_move      = self.pool.get('stock.move')
        loc_obj         = self.pool.get('stock.location')
        results = {}

        source_location_id = loc_obj.search(cr,uid,[('name','=','Stock')], 
            context=context)[0]

        for product in self.browse(cr, uid, ids, context=context):

            total_qty = 0.00

            results[product.id] = 0.0
            #ambil 6 digit pertama, search dulu product yang sama
            a = self.pool.get('product.template').search(cr, uid, [('parent_id','=', product.id)])
            for b in self.browse(cr, uid, a):
                total_qty = total_qty + b.incoming_qty 
            # print "total ", total_qty
            results[product.id] = total_qty

        return results

    def get_detail_total_outgoing(self, cr, uid, ids, field, arg, context=None):
        stock_move      = self.pool.get('stock.move')
        loc_obj         = self.pool.get('stock.location')
        results = {}

        source_location_id = loc_obj.search(cr,uid,[('name','=','Stock')], 
            context=context)[0]

        for product in self.browse(cr, uid, ids, context=context):

            total_qty = 0.00

            results[product.id] = 0.0
            #ambil 6 digit pertama, search dulu product yang sama
            a = self.pool.get('product.template').search(cr, uid, [('parent_id','=', product.id)])
            for b in self.browse(cr, uid, a):
                total_qty = total_qty + b.outgoing_qty 
            # print "total ", total_qty
            results[product.id] = total_qty

        return results

    def get_detail_total_karantina(self, cr, uid, ids, field, arg, context=None):
        detail_karantina = 0
        # import pdb;pdb.set_trace()
        for dk in self.browse(cr,uid,ids):
            tmpl_id = dk.id
            product_id = self.pool.get("product.product").search(cr,uid,[("product_tmpl_id","=",tmpl_id)])[0]
            cr.execute("""SELECT product_id, SUM (qty) FROM stock_quant WHERE location_id = (SELECT id FROM stock_location WHERE complete_name LIKE '%GBA / Input') AND product_id = """+ str(product_id)+""" group by product_id""")
            results = cr.fetchone()
            if results:
                detail_karantina = results[0]
            return detail_karantina

    # def get_detail_total_spb(self, cr, uid, ids, field, arg, context=None):
    #     cr.execute('SELECT product_id, sum (qty) FROM vit_product_request_line WHERE product_id = 7 AND state = 'onprogress' group by product_id')
    #     results = cr.fetchone()

    #     if results:
    #         detail_spb_qty = results[0]
    #     else:
    #         detail_spb_qty = results
    #     return results[0]
        
    _columns = {
        'detail_available'      : fields.function(get_detail_total_avail, type='float', digits_compute=dp.get_precision('Product Price'), string="Detail Available"),
        'detail_qty_available'  : fields.function(get_detail_total_qty, type='float', digits_compute=dp.get_precision('Product Price'), string="Detail Qty On Hand"),
        'detail_incoming_qty'   : fields.function(get_detail_total_incoming, type='float', digits_compute=dp.get_precision('Product Price'), string="Detail Incoming Qty"),
        'detail_outgoing_qty'   : fields.function(get_detail_total_outgoing, type='float', digits_compute=dp.get_precision('Product Price'), string="Detail Outgoing Qty"),
        # 'detail_spb_qty'   : fields.function(detail_spb_qty, type='float', digits_compute=dp.get_precision('Product Price'), string="Detail SPB Qty"),
        'detail_karantina'      : fields.function(get_detail_total_karantina, type='float', digits_compute=dp.get_precision('Product Price'), string="Detail Qty Karantina"),
        # 'outgoing_qty': fields.function(_product_available, multi='qty_available',
        #     type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
        #     string='Outgoing',
        #     fnct_search=_search_product_quantity,
        #     help="Quantity of products that are planned to leave.\n"
        #          "In a context with a single Stock Location, this includes "
        #          "goods leaving this Location, or any of its children.\n"
        #          "In a context with a single Warehouse, this includes "
        #          "goods leaving the Stock Location of this Warehouse, or "
        #          "any of its children.\n"
        #          "Otherwise, this includes goods leaving any Stock "
        #          "Location with 'internal' type."),
    }

