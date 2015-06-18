import time
from openerp import netsvc
import datetime
import calendar
from openerp.osv import fields, osv

class stockw_order(osv.osv):
    _name = "stockw.order"    
    _columns = {
        'name': fields.char('Reference', size=64, required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
     #   'shop_id': fields.many2one('wtc.shop', 'Shop', required=False),
        'description': fields.char('Description', size=256, readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date('Date', readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
            ('done', 'Done'),
            ], 'State', readonly=True, select=True),
        'mps': fields.boolean('MPS ? '),
        'user_id': fields.many2one('res.users', 'Wrh Person', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True, track_visibility='onchange'),
        'stock_line': fields.one2many('stockw.order.line', 'stock_id', 'Stock Lines', readonly=True, required=True, states={'draft': [('readonly', False)]}),   
    }
     
    _defaults = {
        'name': lambda self, cr, uid, context={}: self.pool.get('ir.sequence').get(cr, uid, 'stockw.order'),
        'state':'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'date': lambda *a: time.strftime('%Y-%m-%d'),        
    }

    _order = 'name desc'

    def user_id_change(self, cr, uid, ids, idp):
        res = {}                       
        res['user_id'] = uid        
        return {'value': res}


    def stockw_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True                               
    
    def stockw_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True                                  
         
    def stockw_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approve'})
        return True
    
    def stockw_validate(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids, context={})[0]
        # import pdb;pdb.set_trace()
        type_id = self.pool.get("stock.picking.type").search(cr,uid,[('name','ilike','Internal')])
        if val.stock_line:
            pid = self.pool.get('stock.picking').create(cr,uid, {
                                        'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking'),
                                        'origin': val.name,
                                        # 'stock_id': val.id,
                                        # 'type': 'internal',
                                        'picking_type_id': type_id[0],
                                        'move_type': 'one',
                                        'state': 'waiting',
                                        # 'shop_id': val.shop_id.id,
                                        'date': val.date,
                                        'auto_picking': True,
                                        'company_id': 1,
                                        'picking_type_id': 2,
                                    })
                
            for x in val.stock_line:    
                self.pool.get('stock.move').create(cr,uid, {
                                        'name': x.product_id.partner_ref,
                                        'picking_id': pid,
                                        'product_id': x.product_id.id,
                                        'product_uom': x.product_uom.id,
                                        'product_uom_qty': x.product_qty,                                        
                                        'date': val.date,
                                        'location_id': self.pool.get('stock.warehouse').browse(cr, uid, 1).lot_stock_id.id,
                                        'location_dest_id': self.pool.get('stock.warehouse').browse(cr, uid, 1).lot_stock_id.id,
                                        'state': 'waiting',
                                        'company_id': 1})
                
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'stock.picking', pid, 'button_confirm', cr)
            
        self.write(cr, uid, ids, {'state': 'done'})
        return True 
         
stockw_order()

class stockw_order_line(osv.osv):
    _name = 'stockw.order.line' 
    _columns = {
        'stock_id': fields.many2one('stockw.order', 'Warehouse Order', required=True, ondelete='cascade'),
        'name': fields.char('Description', size=256, required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True, domain=[('sale_ok', '=', True),('categ_id.name','ilike','wip'),]),
        'product_qty': fields.integer('Quantity'),
        'product_uom': fields.many2one('product.uom', 'UoM', required=True),
    }
        
    _defaults = {
        'product_uom': 1,
        'product_qty': 1,
    }

    def product_id_change(self, cr, uid, ids, idp):
        res = {}                       
        product_obj = self.pool.get('product.product')
        if idp:
            product = product_obj.browse(cr, uid, idp)
            res['name'] = product_obj.name_get(cr, uid, [idp])[0][1]
            res['product_uom'] = product.uom_id.id           
                    
        return {'value': res}

stockw_order_line()


#'location_src_id': fields.many2one('stock.location', 'Source', required=True, domain=[('usage', '=', 'internal')]),
#'location_dest_id': fields.many2one('stock.location', 'Destination', required=True, domain=[('usage', '=', 'internal')]),
    