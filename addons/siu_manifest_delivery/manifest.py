# -*- encoding: utf-8 -*-
import time
import datetime
import calendar
from openerp.osv import fields, osv
from openerp.tools.translate import _

class manifest_delivery(osv.osv):

    _name = "manifest.delivery"
    _columns = {
        'name': fields.char('Reference', required=True, size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'driver': fields.char('Driver', required=True, size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'nopol': fields.char('No Polisi', required=True, size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date('Date', readonly=True, states={'draft': [('readonly', False)]}),
        'order_ids': fields.many2many('stock.picking','merge_order_rel', 'merge_order_id', 'picking_id', 'Delivery Order', 
                        domain="[('state', 'in', ('confirmed', 'assigned')), ('type','=','out')]", readonly=True, states={'draft': [('readonly', False)]}),
        'stock_ids': fields.many2many('stock.picking','merge_stock_rel', 'merge_stock_id', 'picking_id', 'Delivery Stock', 
                        domain="[('state', 'in', ('confirmed', 'assigned')), ('type','=','internal'), ('shop_id','!=', False)]", readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel')], 'State', readonly=True),
        'note': fields.text('Notes'),
    }
    
    _defaults = {
        'name': lambda self, cr, uid, context={}: self.pool.get('ir.sequence').get(cr, uid, 'manifest.delivery'),
        'state': 'draft',
        #'date': time.strftime('%Y-%m-%d')
    }
    
    _order = 'name desc'

    def onchange_backdate(self, cr, uid, ids, date):
        if date:
            if date < str(datetime.today()):
                value = {'date': str(datetime.today())}
                warning = {'title': ('Perhatian !'), 'message' : ('Tanggal minimal hari ini atau besok')}
                return {'value': value, 'warning': warning}
        return True

    def manifest_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True                               
    
    def manifest_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True                                  
         
    def manifest_confirm(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids, context={})[0]
        obj_picking = self.pool.get("stock.picking")
        for i in val.order_ids:
            obj_picking.write(cr, uid, [i.id], {'manifest_id': val.id})
        for x in val.stock_ids:
            obj_picking.write(cr, uid, [x.id], {'manifest_id': val.id})
            
        self.write(cr, uid, ids, {'state': 'approve'})
        return True
    
    def manifest_validate(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids, context={})[0]
        picking = []
        if val.order_ids:
            picking += val.order_ids
        if val.stock_ids:
            picking += val.stock_ids
            
        for x in picking:
            partial_data = {'min_date' : val.date}
            for i in x.move_lines:
                partial_data['move%s' % (i.id)] = {
                    'product_id': i.product_id.id,
                    'product_qty': i.product_qty,
                    'product_uom': i.product_uom.id,
                    'prodlot_id': i.prodlot_id.id}
                
            self.pool.get("stock.picking").force_assign(cr, uid, [x.id], context)
            self.pool.get("stock.picking").do_partial(cr, uid, [x.id], partial_data)
        
        self.write(cr, uid, ids, {'state': 'done'})
        return True 
         
manifest_delivery()



class stock_picking(osv.osv):
    _inherit = 'stock.picking' 
    _columns = {
        'manifest_id': fields.many2one('manifest.delivery', 'Manifest', select=True),
        'stock_id': fields.many2one('stock.order', 'Stock Order', select=True),
    }



