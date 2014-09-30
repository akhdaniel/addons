from openerp import tools
from openerp.osv import fields,osv
from openerp import netsvc
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class mrp_product_produce(osv.osv_memory):
    _name    = "mrp.product.produce"
    _inherit = "mrp.product.produce"

    _columns = {
        'product_id'          : fields.many2one('product.product', 'Product',
            readonly=True ),
        'product_grade_b_id'  : fields.many2one('product.product', 'Grade B Product',
            domain="[('categ_id','not ilike','bahan')]", help="Select Product with category Raw Material"),
        'product_waste_id'    : fields.many2one('product.product', 'Waste Product',
            domain="[('categ_id','ilike','waste')]" , help="Select Product with category Waste"),
        'product_grade_b_qty' : fields.float('Grade B Quantity', 
            digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_waste_qty'   : fields.float('Waste Quantity', 
            digits_compute=dp.get_precision('Product Unit of Measure')),
    }

    def _get_product_id(self, cr, uid, context):
        if context.get('active_model') == 'mrp.production':
            mrp = self.pool.get('mrp.production').browse(cr, uid, context.get('active_id', False), context=context)
            return mrp.product_id.id

        return False

    _defaults = {
        'product_id' : _get_product_id
    }

    def onchange_qty(self, cr, uid, ids, product_qty, context=None):
        mrp_id  = context.get('active_id')
        mrp     = self.pool.get('mrp.production').browse(cr, uid, mrp_id, context=context)
        old_qty = mrp.move_created_ids[0].product_qty 
        results = {
            'value' : {
                'product_grade_b_qty' : old_qty - product_qty
            }
        }
        return results

    def do_produce(self, cr, uid, ids, context=None):
        production_id = context.get('active_id', False)
        data = self.browse(cr, uid, ids[0], context=context)
        
        if data.mode == 'consume_produce':
            
            ##########################################################################
            # siapkan mrp.production
            ##########################################################################
            mrp_id  = context.get('active_id', False)
            mrp_obj = self.pool.get('mrp.production')
            mrp     = mrp_obj.browse(cr, uid, mrp_id, context=context)

            ##########################################################################
            # cek total old product_qty = product_qty + grade_b + waste
            # kalau data.product_grade_b_qty + data.product_waste_qty > 0
            # kalau ya, proses
            ##########################################################################
            old_qty = mrp.move_created_ids[0].product_qty 
            if data.product_grade_b_qty + data.product_waste_qty > 0:

                ##########################################################################
                # validasi product dan qty
                ##########################################################################
                if old_qty != data.product_qty + data.product_grade_b_qty + data.product_waste_qty:
                    raise osv.except_osv(_('Error'),_("Total Qty of Production Order must be the same as Product, Grade B, and Waste Quantity") ) 
                if data.product_grade_b_qty > 0 and not data.product_grade_b_id:
                    raise osv.except_osv(_('Error'),_("Please select Grade B Product") ) 
                if data.product_waste_qty > 0 and not data.product_waste_id:
                    raise osv.except_osv(_('Error'),_("Please select Waste Product") ) 

                ##########################################################################
                # siapkan stock.move
                ##########################################################################
                sm_obj = self.pool.get('stock.move')

                ##########################################################################
                # location production dan stock
                ##########################################################################
                prod_loc_id  = mrp.move_created_ids[0].location_id.id
                stock_loc_id = mrp.move_created_ids[0].location_dest_id.id

                ##########################################################################
                # proses grade b :
                # stock move dari production => stock
                # sebanyak qty grade b
                ##########################################################################
                if data.product_grade_b_qty:
                    print "moving producing grade b"
                    sm_data = {
                        'production_id'  : mrp.id,
                        'product_id'     : data.product_grade_b_id.id,
                        'product_qty'    : data.product_grade_b_qty,
                        'product_uom'    : data.product_grade_b_id.uom_id.id,
                        'name'           : "%s - Grade B" % (mrp.name),
                        'location_id'    : prod_loc_id,
                        'location_dest_id' : stock_loc_id,
                        'data_expected'  : time.strftime("%Y-%m-%d")
                    }
                    id = sm_obj.create(cr, uid, sm_data, context=context)
                    sm_obj.action_done(cr, uid, [id], context=context)

                ##########################################################################
                # proses waste
                # stock move dari production => stock
                # sebanyak qty waste
                ##########################################################################
                if data.product_waste_qty:
                    print "moving grade a and producing waste"
                    sm_data = {
                        'production_id'  : mrp.id,
                        'product_id'     : data.product_waste_id.id,
                        'product_qty'    : data.product_waste_qty,
                        'product_uom'    : data.product_grade_b_id.uom_id.id,
                        'name'           : "%s - Waste" % (mrp.name),
                        'location_id'    : prod_loc_id,
                        'location_dest_id' : stock_loc_id,
                        'data_expected'  : time.strftime("%Y-%m-%d")
                    }
                    id = sm_obj.create(cr, uid, sm_data, context=context)
                    sm_obj.action_done(cr, uid, [id], context=context)

                ##########################################################################
                # proses sisa produk asli, delete dari product to produce
                ##########################################################################
                cr.execute("delete from stock_move where name='%s' and state<>'done'" % (mrp.name))
                # ids = sm_obj.search(cr, uid, [('name','=',mrp.name)], context=context)
                # sm_obj.unlink(cr, uid, ids , context=context)

        res = super(mrp_product_produce, self).do_produce(cr, uid, ids, context=context)
        return res 


