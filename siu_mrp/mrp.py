import time
import math
import datetime
import calendar
from openerp.osv import osv, fields

class MaterialRequirement(osv.osv):
    _name = 'material.requirement'
    _columns = {
        'name': fields.char('Reference', size=64, required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'plan_id': fields.many2one('production.plan', 'Production Plan', readonly=True, required=True, select=True, domain=[('state', '=', 'done')], states={'draft': [('readonly', False)]}),
        'notes': fields.text('Notes'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
            ('done', 'Done'),
            ], 'Plan State', readonly=True, select=True),
        'requirement_line': fields.one2many('material.requirement.line', 'requirement_id', 'Material Requirement Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'requisition_line': fields.one2many('purchase.requisition', 'requirement_id', 'Purchase Requisition', readonly=True),
        'manufacture_line': fields.one2many('mrp.production', 'requirement_id', 'Manufacture Order', readonly=True)
    }

    _defaults = {
                 'name': lambda self, cr, uid, context={}: self.pool.get('ir.sequence').get(cr, uid, 'material.requirement'),
                 'state' : 'draft',
    }
    
    _order = 'name desc'
    
    def material_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True                               
    
    def material_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True                                  
         
    def material_confirm(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        bom_obj = self.pool.get('mrp.bom')    
        product_obj = self.pool.get('product.product')
        
#         for x in val.requirement_line:
#             product = product_obj.browse(cr, uid, x.product_id.id)
#             bom_id = bom_obj._bom_find(cr, uid, x.product_id.id, x.product_uom.id)
#             
#             if not bom_id:
#                 raise osv.except_osv(('Perhatian !'), ('Finish part %s tidak memiliki BoM  !' % x.product_id.default_code))                                                      
#             bom_line = self.get_children([bom_obj.browse(cr, uid, bom_id)])[1:]
#             
#             for b in bom_line:
#                 plan = 1
#                 if b['level'] == 1:
#                     plan = b['pqty'] * x.plan
#                 self.pool.get('bom.parts').create(cr, uid, {
#                                                         'name': b['name'],
#                                                         'pcode': b['pcode'],
#                                                         'uname': b['uname'],
#                                                         'pid': b['pid'],
#                                                         'level': b['level'],
#                                                         'pqty': b['pqty'],
#                                                         'plan': plan,
#                                                         'supply': product_obj.browse(cr, uid, b['pid']).supply_method, 
#                                                         'mrp_id': b['mrp_id'],              
#                                                         'line_id': x.id,
#                                                         })
            
        self.write(cr, uid, ids, {'state': 'approve'})
        return True
    
    def material_validate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        return True 

    def get_children(self, object, level=0):
        result = []
 
        def _get_rec(object,level):
            for l in object:
                res = {}
                res['name'] = l.name
                res['pid'] = l.product_id.id
                res['pcode'] = l.product_id.default_code
                res['pqty'] = l.product_qty
                res['uname'] = l.product_uom.id
                #res['uomid'] = l.product_uom.id
                res['level'] = level
                res['mrp_id'] = l.id
                res['purchase'] = l.product_id.purchase_ok
                result.append(res)
                if l.child_complete_ids:
                    if level<6:
                        level += 1
                    _get_rec(l.child_complete_ids,level)
                    if level>0 and level<6:
                        level -= 1
            return result
 
        children = _get_rec(object,level)
 
        return children

    def plan_change(self, cr, uid, ids, plan): 
        val = self.pool.get('production.plan').browse(cr, uid, plan) 
        product_obj = self.pool.get('product.product')          
        rqn = []
        for x in val.plan_line:
            rqn.append({
                'product_id': x.product_id.id,
                'product_uom': x.product_uom.id,
                'plan': x.plan,
                'name': product_obj.name_get(cr, uid, [x.product_id.id])[0][1]
            }) 
                 
        return {'value': {'requirement_line': rqn}}

    def compute(self, cr, uid, ids, context={}):
        data = self.browse(cr, uid, ids)[0]  
#         bom_obj = self.pool.get('bom.parts')
#         for part in data.requirement_line:
#             for comp in part.bom_line:
#                 if comp.level == 2:
#                     bid = bom_obj.search(cr, uid, [('pid', '=', comp.mrp_id.bom_id.product_id.id), ('level', '=', 1), ('line_id', '=', part.id)])  
#                     bom = bom_obj.browse(cr, uid, bid)[0]
#                     bom_obj.write(cr, uid, [comp.id], {'plan': comp.pqty * bom.plan})
#                 elif comp.level == 3:
#                     bid = bom_obj.search(cr, uid, [('pid', '=', comp.mrp_id.bom_id.product_id.id), ('level', '=', 2), ('line_id', '=', part.id)])  
#                     bom = bom_obj.browse(cr, uid, bid)[0]
#                     bom_obj.write(cr, uid, [comp.id], {'plan': comp.pqty * bom.plan})
#                 elif comp.level == 4:
#                     bid = bom_obj.search(cr, uid, [('pid', '=', comp.mrp_id.bom_id.product_id.id), ('level', '=', 3), ('line_id', '=', part.id)])  
#                     bom = bom_obj.browse(cr, uid, bid)[0]
#                     bom_obj.write(cr, uid, [comp.id], {'plan': comp.pqty * bom.plan})
        return True

    def procurement(self, cr, uid, ids, context={}):
        data = self.browse(cr, uid, ids)[0]
        bom_obj = self.pool.get('mrp.bom')
        mrp_obj = self.pool.get('mrp.production')    
        
        purchase = []; produce = []; beli = {}
        for part in data.requirement_line:
            ada = mrp_obj.search(cr, uid, [('origin', '=', data.name), ('product_id', '=', part.product_id.id)])
            if not ada :
                self.pool.get('mrp.production').create(cr,uid, {
                                    'origin': data.name,
                                    'requirement_id': data.id,
                                    'product_id': part.product_id.id,
                                    'product_qty': part.plan,
                                    'product_uom': part.product_uom.id,
                                    'bom_id': 13841}) #bom_obj._bom_find(cr, uid, part.product_id.id, part.product_uom.id)})
                    
            
#             for comp in part.bom_line:
#                 if comp.supply == 'buy':
#                     beli[comp.pid.id] = {'product_qty': [],'product_uom': comp.mrp_id.product_uom.id} 
#                     purchase.append({
#                                      'product_id': comp.pid.id,
#                                      'product_qty': comp.plan,
#                                      'product_uom': comp.uname.id,
#                                      })
#                                         
#                 else:
#                     bom_id = bom_obj._bom_find(cr, uid, comp.pid.id, comp.uname.id)
#                     if not bom_id:
#                         raise osv.except_osv(('Perhatian !'), ('Product %s tidak memiliki BoM  !' % comp.pid.default_code))
#                     produce.append(comp)
        
        
#         for p in purchase:
#             beli[p['product_id']]['product_qty'].append(p['product_qty'])    
#                 
#         if purchase:
#             exis = self.pool.get('purchase.requisition').search(cr, uid, [('origin', '=', data.name)])
#             if not exis :
#                 pri = self.pool.get('purchase.requisition').create(cr,uid, {
#                                         'origin': data.name,
#                                         'requirement_id': data.id,
#                                         'description': 'Procurement untuk proses MPS',
#                                         'company_id': 1})
#                  
#                  
#                 for b in beli :
#                     self.pool.get('purchase.requisition.line').create(cr,uid, {
#                                         'product_id': b,
#                                         'product_qty': self.reordering_rules(cr, uid, ids, b, sum(beli[b]['product_qty'])),
#                                         'product_uom_id': beli[b]["product_uom"],
#                                         'requisition_id': pri})
#                  
#         if produce:
#             for x in produce:
#                 a = mrp_obj.search(cr, uid, [('origin', '=', data.name), ('product_id', '=', x.pid.id)])
#                 if not a:
#                     self.pool.get('mrp.production').create(cr,uid, {
#                                     'origin': data.name,
#                                     'requirement_id': data.id,
#                                     'product_id': x.pid.id,
#                                     'product_qty': self.reordering_rules(cr, uid, ids, x.pid.id, x.plan),
#                                     'product_uom': x.uname.id,
#                                     'bom_id': bom_obj._bom_find(cr, uid, x.pid.id, x.uname.id)})
         
        return True


    def reordering_rules(self, cr, uid, ids, pid, order):
        min = 0; max = 0; plan = order
        obj_orderpoint = self.pool.get('stock.warehouse.orderpoint')
        sid = obj_orderpoint.search(cr, uid, [('product_id', '=', pid)])
        if sid:
            product = self.pool.get('product.product').browse(cr, uid, pid)
            sto = obj_orderpoint.browse(cr, uid, sid)[0]
            min = sto.product_min_qty
            max = sto.product_max_qty
            
            plan = 0
            if product.qty_available - order == 0 :
                plan = max
            elif product.qty_available - order <= 0 :
                plan = abs(product.qty_available - order) + max
            elif product.qty_available - order < min:
                plan = max - (product.qty_available - order)
                
        return plan
                
        
MaterialRequirement()


class MaterialRequirementLine(osv.osv):
    _name = 'material.requirement.line' 
    _columns = {
        'requirement_id': fields.many2one('material.requirement', 'Requirement Reference', required=True, ondelete='cascade', select=True),
        'name': fields.char('Description', size=256, required=True, select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True, domain=[('sale_ok', '=', True)], change_default=True),
        'plan': fields.float('Requirement', required=True),
        'product_uom': fields.many2one('product.uom', 'UoM', required=True),
        'bom_line': fields.one2many('bom.parts', 'line_id', 'Component Parts'),
    }
    
    def product_id_change(self, cr, uid, ids, product):
        res = {}
        product_obj = self.pool.get('product.product')
        if product:
            res['name'] = product_obj.name_get(cr, uid, [product])[0][1]
            res['product_uom'] = product_obj.browse(cr, uid, product).uom_id.id
        return {'value': res}

MaterialRequirementLine()


class BomParts(osv.osv):
    _name = "bom.parts"
    _columns = {
                'name': fields.char('Name', size=100),
                'pcode': fields.char('Code', size=100),
                'uname': fields.many2one('product.uom', 'UoM'),
                'pid': fields.many2one('product.product', 'Product'),
                'level': fields.integer('Level'),
                'pqty': fields.float('Unit', digits=(16, 2)),
                'plan': fields.float('Requirement', digits=(16, 2)),
                'supply': fields.selection([('buy', 'Purchase'), ('produce', 'Manufacture')], 'Supply Method'),
                'mrp_id': fields.many2one('mrp.bom', 'Parent BoM', select=True),              
                'line_id': fields.many2one('material.requirement.line', 'Component', ondelete='cascade')
    }
      
BomParts()


class mrp_production(osv.osv):
    _inherit = "mrp.production"
    _columns = {
            'requirement_id': fields.many2one('material.requirement', 'Requirement Reference', ondelete='cascade', select=True),

    }
    
mrp_production()
    
class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"
    _columns = {
            'requirement_id': fields.many2one('material.requirement', 'Requirement Reference', ondelete='cascade', select=True),

    }

purchase_requisition()

#     def compute_procurement(self, cr, uid, ids, context={}):
#         val = self.browse(cr, uid, ids)[0]
#         
#         part = []
#         for x in val.requirement_line:
#             for i in x.bom_line:
#                 part.append({
#                              'product_id': i.pid.id,
#                              'plan': i.qty_plan1,
#                              'plan2': i.qty_plan2,
#                              'plan3': i.qty_plan3,
#                              'previous': i.previous
#                              })    
#         
#         idp = []
#         purchase = []
#         for p in part:
#             if p['product_id'] not in idp:
#                 purchase.append({'product_id': p['product_id'], 'plan': [p['plan']], 'plan2': [p['plan2']], 'plan3': [p['plan3']], 'previous': [p['previous']]})
#                 idp.append(p['product_id'])
#             else:
#                 for r in purchase:
#                     if p['product_id'] == r['product_id']:
#                         r['plan'].append(p['plan'])
#                         r['plan2'].append(p['plan2'])
#                         r['plan3'].append(p['plan3'])
#                         r['previous'].append(p['previous'])
#         
#         for a in val.stock_line:
#             for z in purchase:
#                 if a.product_id.id == z['product_id']:
#                     self.pool.get('stock.level').write(cr, uid, [a.id], { 
#                                                                          'plan': sum(z['plan']), 
#                                                                          'plan2': sum(z['plan2']), 
#                                                                          'plan3': sum(z['plan3']), 
#                                                                          'previous': sum(z['previous'])})
#         for u in val.stock_line:
#             beli = 0; beli2 = 0; beli3 = 0
#             endstok = u.qty + u.outstanding + u.additional - u.previous
#             if u.qty + u.outstanding - u.previous > u.min:
#                 endstok = u.qty + u.outstanding - u.previous
#                 self.pool.get('stock.level').write(cr, uid, [u.id], {'additional': 0})
#             if endstok - u.plan < u.min:
#                 if endstok - u.plan < 0:
#                     beli = abs(endstok - u.plan) + u.max
#                 else:
#                     beli = u.max - (endstok - u.plan)
# 
# 
#             if endstok + beli - u.plan - u.plan2 < u.min :
#                 if endstok + beli - u.plan - u.plan2 < 0:
#                     beli2 = abs(endstok + beli - u.plan - u.plan2) + u.max
#                 else:
#                     beli2 = u.max - (endstok + beli - u.plan - u.plan2)
# 
# 
#             if endstok + beli - u.plan - u.plan2 + beli2 - u.plan3 < u.min:
#                 if endstok + beli - u.plan - u.plan2 + beli2 - u.plan3 < 0:
#                     beli3 = abs(endstok + beli - u.plan - u.plan2 + beli2 - u.plan3) + u.max
#                 else:
#                     beli3 = u.max - (endstok + beli - u.plan - u.plan2 + beli2 - u.plan3)
# 
#             self.pool.get('stock.level').write(cr, uid, [u.id], {
#                                                                  'endstockmonth': endstok, 
#                                                                  'purchase': beli, 
#                                                                  'endmonth': endstok + beli - u.plan,
#                                                                  'purchase2': beli2,
#                                                                  'endmonth2': endstok + beli - u.plan - u.plan2 + beli2,
#                                                                  'purchase3': beli3
#                                                                 })
#         
#         return True

#     def endstock(self, cr, uid, ids, context={}):
#         val = self.browse(cr, uid, ids)[0]
#         
#         tahun = datetime.datetime.now().year
#         start = time.strftime('%Y-%m-%d', time.strptime("01 %d %d" % (val.plan_id.month_period, tahun),"%d %m %Y"))
#         finish = time.strftime('%Y-%m-%d', time.strptime("%d %d %d" % (calendar.monthrange(tahun, val.plan_id.month_period)[1], val.plan_id.month_period, tahun),"%d %m %Y"))      
#   
#         for u in val.stock_line:
#             sisa = [] 
#             psid = self.pool.get('purchase.order').search(cr, uid, [('jenis', '=', 'loc'), ('state', '=', 'approved')])
#             if psid:
#                 lsid = self.pool.get('purchase.order.line').search(cr, uid, [('order_id', 'in', psid), ('product_id', '=', u.product_id.id)])
#                 if lsid:
#                     sisa += [x.outstanding for x in self.pool.get('purchase.order.line').browse(cr, uid, lsid)]
#                     
#             ron = 10
#             tambahan = abs(u.qty+u.outstanding-u.previous-u.max)
#             qa = tambahan/ron
#             if len(str(int(tambahan))) == 3:
#                 ron = 100
#                 qa = tambahan/ron
#             if len(str(int(tambahan))) == 4:
#                 ron = 1000
#                 qa = tambahan/ron
#             if len(str(int(tambahan))) == 5:
#                 ron = 1000
#                 qa = tambahan/ron
# 
#             add = math.ceil(qa)*ron
#             self.pool.get('stock.level').write(cr, uid, [u.id], {'additional': add})
#                         
#         return True



#     def create_order(self, cr, uid, ids, context={}):
#         val = self.browse(cr, uid, ids)[0]
#         
#         if val.purchase:
#             raise osv.except_osv(('Perhatian !'), ('MRP %s sudah dibuatkan ordernya  !' % val.name))
#         
#         additional = []
#         nextpurchase = []
#         for x in val.stock_line:
#             if x.product_id.purchase_ok:
#                 if not x.product_id.seller_ids:
#                     raise osv.except_osv(('Perhatian !'), ('Product %s belum ditentukan suppliernya  !' % x.product_id.default_code))
#                 for i in x.product_id.seller_ids:
#                     additional.append({
#                                      'product_id': x.product_id.id,
#                                      'partner_id': i.name.id,
#                                      'purchase': x.additional,
#                                      'ratio': i.ratio,
#                                      'multiple': i.min_qty,
#                                      'product_uom': x.product_uom.id,
#                                      })
#                     nextpurchase.append({
#                                      'product_id': x.product_id.id,
#                                      'partner_id': i.name.id,
#                                      'purchase': x.purchase,
#                                      'ratio': i.ratio,
#                                      'multiple': i.min_qty,
#                                      'product_uom': x.product_uom.id,
#                                      })
# 
#         self.create_purchase(cr, uid, ids, additional)
#         self.create_purchase(cr, uid, ids, nextpurchase)
# 
#     def create_purchase(self, cr, uid, ids, supplier):
#         val = self.browse(cr, uid, ids)[0]
#         obj_purchase = self.pool.get("purchase.order")
#         obj_purchase_line = self.pool.get('purchase.order.line')
# 
#         idp = []
#         purchase = []
#         for s in supplier:
#             if s['partner_id'] not in idp:
#                 purchase.append({'partner_id': s['partner_id'], 'product': [{
#                                                                              'product_id': s['product_id'],
#                                                                              'purchase': s['purchase'],
#                                                                              'ratio': s['ratio'],
#                                                                              'multiple': s['multiple'],
#                                                                              'product_uom': s['product_uom']
#                                                                              }]})
#                 idp.append(s['partner_id'])
#             else:
#                 for r in purchase:
#                     if s['partner_id'] == r['partner_id']:
#                         r['product'].append({
#                                             'product_id': s['product_id'],
#                                             'purchase': s['purchase'],
#                                             'ratio': s['ratio'],
#                                             'multiple': s['multiple'],
#                                             'product_uom': s['product_uom']
#                                             })
#         
#         for order in purchase:
#             partner = obj_purchase.onchange_partner_id(cr, uid, ids, order['partner_id'])['value']
#             sid = obj_purchase.create(cr, uid, {
#                                                  'jenis': 'loc',
#                                                  'date_order': val.plan_id.start_date,
#                                                  'partner_id': order['partner_id'],
#                                                  'partner_address_id': partner['partner_address_id'],
#                                                  'pricelist_id': partner['pricelist_id'],
#                                                  'location_id': 12
#                                                 })
#             for line in order['product']:
#                 kali = line['multiple']
#                 if not kali :
#                     kali = 1
#                 jml = math.ceil(((line['purchase']*line['ratio'])/100)/kali)*kali
#                 vals = obj_purchase_line.product_id_change(cr, uid, ids, partner['pricelist_id'], line['product_id'], qty = jml, uom_id = line['product_uom'], partner_id = order['partner_id'], date_order = val.plan_id.start_date)['value']
#                 obj_purchase_line.create(cr, uid, {
#                                                     'order_id': sid,
#                                                     'name': vals['name'],
#                                                     'product_id': line['product_id'],
#                                                     'product_qty': jml,
#                                                     'outstanding': jml,
#                                                     'product_uom': line['product_uom'],
#                                                     'price_unit': vals['price_unit'], 
#                                                     'date_planned': val.plan_id.start_date,                                                                   
#                                                   })    
#          
#         
#         self.write(cr, uid, ids, {'purchase': True})
#         return True



#'stock_line': fields.one2many('stock.level', 'requirement_id', 'Stock Level', states={'done': [('readonly', True)]}),


# class StockLevel(osv.osv):
#     _name = 'stock.level' 
#     _columns = {
#         'requirement_id': fields.many2one('material.requirement', 'Requirement Reference', required=True, ondelete='cascade', select=True),
#         'name': fields.char('Description', size=256, select=True),
#         'product_id': fields.many2one('product.product', 'Product', required=True, change_default=True),
#         'qty': fields.float('Current Quantity'),
#         'previous': fields.float('Current Plan'),
#         'endstockmonth': fields.float('End Stock'),
#         'outstanding': fields.float('Outstanding PO'),
#         'additional': fields.float('Additional PO'),
#         'min': fields.float('Min'),
#         'max': fields.float('Max'),
#         'plan': fields.float('Plan of Period'),
#         'purchase': fields.float('Purchase Order'),
#         'endmonth': fields.float('End of Period'),
#         'plan2': fields.float('Plan Next Period'),
#         'purchase2': fields.float('Forecast'),
#         'endmonth2': fields.float('End of Next Period'),
#         'plan3': fields.float('Plan Last Period'),
#         'purchase3': fields.float('Next Forecast'),
#         'product_uom': fields.many2one('product.uom', 'UoM', required=True),
#     }
#     
# 
# StockLevel()
