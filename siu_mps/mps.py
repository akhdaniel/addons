import time
import datetime
import calendar
from openerp.osv import osv, fields


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'mps': fields.boolean('MPS ? '),
    }
    
    
sale_order()


class ProductionPlan(osv.osv):
    _name = 'production.plan'
    _columns = {
        'name': fields.char('Reference', size=64, required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'date': fields.date('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'notes': fields.text('Notes'),
        'state': fields.selection([ ('draft', 'Draft'), ('cancel', 'Cancel'), ('approve', 'Approve'), ('done', 'Done')], 'Plan State', readonly=True, select=True),
        'order_ids': fields.many2many('sale.order','plan_sale_rel', 'plan_order_id', 'order_id', 'Sale Order', 
                        domain="[('mps', '=', False), ('state', 'in', ('sent', 'progress', 'manual'))]", readonly=True, states={'draft': [('readonly', False)]}),
        'stock_ids': fields.many2many('stock.order','plan_stock_rel', 'plan_stock_id', 'stock_id', 'Stock Order', 
                        domain="[('mps', '=', False), ('state', '=', 'done')]", readonly=True, states={'draft': [('readonly', False)]}),
        'stockw_ids': fields.many2many('stockw.order','plan_stockw_rel', 'plan_stockw_id', 'stockw_id', 'Warehouse Order', 
                        domain="[('mps', '=', False), ('state', '=', 'done')]", readonly=True, states={'draft': [('readonly', False)]}),
        'plan_line': fields.one2many('production.plan.line', 'plan_id', 'Production Plan Lines'),
        'mr_exist': fields.boolean("MR Exist?", readonly=True),
    }

    _defaults = {
                 'name': lambda self, cr, uid, context={}: self.pool.get('ir.sequence').get(cr, uid, 'production.plan'),
                 'state' : 'draft',
                 'date': lambda *a: time.strftime('%Y-%m-%d'), 
    }
    
    _order = 'name desc'

    def plan_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True                               
    
    def plan_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True                                  
         
    def plan_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approve'})
        return True
    
    def plan_validate(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids, context={})[0]
        for x in val.order_ids:
            self.pool.get('sale.order').write(cr, uid, [x.id], {'mps': True})
        
        for x in val.stock_ids:
            self.pool.get('stock.order').write(cr, uid, [x.id], {'mps': True})
       
        for x in val.stockw_ids:
            self.pool.get('stockw.order').write(cr, uid, [x.id], {'mps': True})
               
 
        self.write(cr, uid, ids, {'state': 'done'})
        return True 
    
    def compute(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids, context={})[0]
        product_obj = self.pool.get('product.product')
        
        if val.plan_line:
            for x in val.plan_line:
                plan = x.plan
                if x.real - x.total == 0 :
                    plan = x.max
                elif x.real - x.total <= 0 :
                    plan = abs(x.real - x.total) + x.max
                elif x.real - x.total < x.min:
                    plan = x.max - (x.real - x.total)
                self.pool.get('production.plan.line').write(cr, uid, [x.id], {'plan': plan, 'end': x.real - x.total + plan})
        else:
            product = []
            for x in val.order_ids:
                for l in x.order_line:
                    product.append({'product_id': l.product_id.id, 'line': l, 'qty': l.product_uom_qty, 'uom': l.product_uom.id})
            for x in val.stock_ids:
                for l in x.stock_line:
                    product.append({'product_id': l.product_id.id, 'line': l, 'qty': l.product_qty, 'uom': l.product_uom.id})
            for x in val.stockw_ids:
                for l in x.stock_line:
                    product.append({'product_id': l.product_id.id, 'line': l, 'qty': l.product_qty, 'uom': l.product_uom.id})

                    
            data = {}
            for p in product:
                data[p['product_id']] = {'qty': [], 'uom': p['uom'], 'line': []}
            for p in product:
                data[p['product_id']]['qty'].append(p['qty'])
                data[p['product_id']]['line'].append(p['line'])
                    
            for i in data:
                order = sum(data[i]['qty'])
                brg = product_obj.browse(cr, uid, i)
                min = 0; max = 0; plan = order
                sid = self.pool.get('stock.warehouse.orderpoint').search(cr, uid, [('product_id', '=', i)])
                if sid:
                    sto = self.pool.get('stock.warehouse.orderpoint').browse(cr, uid, sid)[0]
                    min = sto.product_min_qty
                    max = sto.product_max_qty
                    
                    plan = 0
                    if brg.qty_available - order == 0 :
                        plan = max
                    elif brg.qty_available - order <= 0 :
                        plan = abs(brg.qty_available - order) + max
                    elif brg.qty_available - order < min:
                        plan = max - (brg.qty_available - order)
                
                     
                self.pool.get('production.plan.line').create(cr, uid, {
                                                                   'plan_id': val.id,
                                                                   'product_id': i,
                                                                   'product_uom': data[i]['uom'],
                                                                   'total': order,
                                                                   'name': product_obj.name_get(cr, uid, [i])[0][1],
                                                                   'real': brg.qty_available,
                                                                   'min': min,
                                                                   'max': max,
                                                                   'plan': plan,
                                                                   'end': brg.qty_available - order + plan 
                                                                   })
        return True 

ProductionPlan()


class ProductionPlanLine(osv.osv):
    _name = 'production.plan.line' 
    _columns = {
        'plan_id': fields.many2one('production.plan', 'Plan Reference', required=True, ondelete='cascade', select=True),
        'name': fields.char('Description', size=256, required=True, select=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True, readonly=True),
        'total': fields.float('Total Order', readonly=True),
        'real': fields.float('On Hand'),
        'min': fields.float('Min'),
        'max': fields.float('Max'),
        'plan': fields.float('Plan'),
        'end': fields.float('End of Stock', readonly=True),
        'product_uom': fields.many2one('product.uom', 'UoM', readonly=True),
    }
    
    def product_id_change(self, cr, uid, ids, product):
        res = {}
        product_obj = self.pool.get('product.product')
        if product:
            res['name'] = product_obj.name_get(cr, uid, [product])[0][1]
            res['product_uom'] = product_obj.browse(cr, uid, product).uom_id.id
        return {'value': res}

ProductionPlanLine()




#         for detail in val.detail_pb_ids:
#             suppliers[detail.suplier.id] = []
#         for detail in val.detail_pb_ids:
#             suppliers[detail.suplier.id].append(detail)
    

#         suppliers = {}
#         for detail in val.detail_pb_ids:
#             if detail.suplier.id not in suppliers:
#                 suppliers[detail.suplier.id] = {}
#                 suppliers[detail.suplier.id][detail.po_will_be_print] = []
#             if detail.po_will_be_print not in suppliers[detail.suplier.id]:
#                 suppliers[detail.suplier.id][detail.po_will_be_print] = []
#             suppliers[detail.suplier.id][detail.po_will_be_print].append(detail)


# class MRPProduction(osv.osv):
#     _inherit = 'mrp.production'
#     _columns = {
#         'week': fields.integer('Week'),
#         'schedule_id': fields.many2one('production.schedule', 'Production Schedule', ondelete='set null', select=True),
#     }
# 
#     _defaults = {'schedule_id': False}
# 
# 
# MRPProduction()

 
#     def compute_plan(self, cr, uid, ids, context=None):
#         val = self.browse(cr, uid, ids)[0]
# 
#         for line in val.plan_line:
#             wc_obj = self.pool.get('mrp.workcenter')                            
#             
#             plan = 0
#             kapasitas = 1
#             estimate = line.qty_estimation
#             kapid = wc_obj.search(cr, uid, [('product_id', '=', line.product_id.id)])
#             if line.product_id.sale_ok and line.product_id.purchase_ok :
#                 pass
#             else:
#                 if not kapid:
#                     raise osv.except_osv(('Perhatian !'), ('Product %s tidak memiliki kapasitas produksi  !' % line.product_id.default_code))
#                 else:
#                     kapasitas = wc_obj.browse(cr, uid, kapid[0]).capacity_per_cycle
#             
#             if estimate - line.qty_forecast < line.qty_min:
#                 plan =  math.ceil((line.qty_max - (estimate - line.qty_forecast))/float(kapasitas)) * kapasitas
#             
#             endstock = estimate+plan-line.qty_forecast       
#             
#             plan1 = 0
#             if endstock - line.forecast1 < line.qty_min:
#                 plan1 =  math.ceil((line.qty_max - (endstock - line.forecast1))/float(kapasitas)) * kapasitas
#             
#             endstock1 = endstock+plan1-line.forecast1       
#                 
#             plan2 = 0
#             if endstock1 - line.forecast2 < line.qty_min:
#                 plan2 =  math.ceil((line.qty_max - (endstock1 - line.forecast2))/float(kapasitas)) * kapasitas
#             
#             endstock2 = endstock1+plan2-line.forecast2       
#             
#             plan3 = 0
#             if endstock2 - line.forecast3 < line.qty_min:
#                 plan3 =  math.ceil((line.qty_max - (endstock2 - line.forecast3))/float(kapasitas)) * kapasitas
#              
#             endstock3 = endstock2+plan3-line.forecast3
#             
#             self.pool.get('production.plan.line').write(cr, uid, [line.id], { 
#                                                                             'qty_total': plan,
#                                                                             'endstock': endstock,               
#                                                                             'endstock1': endstock1,
#                                                                             'endstock2': endstock2,
#                                                                             'endstock3': endstock3,
#                                                                             'plan1': plan1,
#                                                                             'plan2': plan2,
#                                                                             'plan3': plan3,
#                                                                             })
#         return True
#         
#     
#     def period_change(self, cr, uid, ids, forecast): 
#         val = self.pool.get('sale.forecast').browse(cr, uid, forecast)
#         return {'value': {'month_period': val.month_from}}
# 
#     def get_estimate(self, cr, uid, ids, product, start, finish):
#         opname = [0];deliver = [0];produksi = [0]
#         vid = self.pool.get('stock.inventory').search(cr, uid, [('date', '>=', start), ('date', '<=', finish)])
#         if vid:
#             vad = self.pool.get('stock.inventory.line').search(cr, uid, [('inventory_id', '=', vid[0]), ('product_id', '=', product)])
#             opname = [x.product_qty for x in self.pool.get('stock.inventory.line').browse(cr, uid, vad)]
#         
#         did = self.pool.get('stock.picking').search(cr, uid, [('type', '=', 'out'), ('state', '!=', 'cancel'), ('min_date', '>=', start), ('min_date', '<=', finish)])
#         if did:
#             dad = self.pool.get('stock.move').search(cr, uid, [('picking_id', 'in', did), ('product_id', '=', product)])
#             deliver = [x.product_qty for x in self.pool.get('stock.move').browse(cr, uid, dad)]
#         
#         pid = self.pool.get('mrp.production').search(cr, uid, [('product_id', '=', product), ('state', '!=', 'cancel'), ('date_planned', '>=', start), ('date_planned', '<=', finish)])
#         if pid:
#             produksi = [x.product_qty for x in self.pool.get('mrp.production').browse(cr, uid, pid)]
#         
#         return sum(opname)-sum(deliver)+sum(produksi)
#       
#     def forecast_change(self, cr, uid, ids, forecast): 
#         val = self.pool.get('sale.forecast').browse(cr, uid, forecast)
#                
#         tahun = datetime.datetime.now().year
#         week = calendar.month(tahun, val.month_from).split('\n')[2:-1]
#         start = time.strftime('%Y-%m-%d', time.strptime("01 %d %d" % (val.month_from, tahun),"%d %m %Y"))
#         finish = time.strftime('%Y-%m-%d', time.strptime("%d %d %d" % (calendar.monthrange(tahun, val.month_from)[1], val.month_from, tahun),"%d %m %Y"))
#                 
#         pln = []
#         for x in val.forecast_line:
#             sid = self.pool.get('stock.warehouse.orderpoint').search(cr, uid, [('product_id', '=', x.product_id.id)])
#             if not sid:
#                 raise osv.except_osv(('Perhatian !'), ('Product %s tidak memiliki Stock Minimum Rule  !' % x.product_id.default_code))
#             sto = self.pool.get('stock.warehouse.orderpoint').browse(cr, uid, sid)[0]
#             
#             awal = val.month_from-1
#             
#             if awal == 0:
#                 awal = 12
#             
#             estimate = self.get_estimate(cr, uid, ids, x.product_id.id, time.strftime('%Y-%m-%d', time.strptime("01 %d %d" % (awal, tahun),"%d %m %Y")), time.strftime('%Y-%m-%d', time.strptime("%d %d %d" % (calendar.monthrange(tahun, awal)[1], awal, tahun),"%d %m %Y")))
#             pln.append({
#                 'product_id': x.product_id.id,
#                 'product_uom': x.product_uom.id,
#                 'qty_forecast': x.n1,
#                 'forecast1': x.n2,
#                 'forecast2': x.n3,
#                 'forecast3': x.n4,
#                 'qty_estimation': estimate,
#                 'qty_real': x.product_id.qty_available,
#                 'qty_min': sto.product_min_qty,
#                 'qty_max': sto.product_max_qty,
#                 'location_id': 12,
#                 'name': self.pool.get('product.product').name_get(cr, uid, [x.product_id.id])[0][1],
#             })
#         
#         return {'value': {'plan_line':pln, 'forecast_id': val.id, 'month_period': val.month_from, 'start_date': start, 'finish_date': finish}}
#     