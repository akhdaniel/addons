
import time
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID
from openerp.addons.product import _common

class mrp_production_custom(osv.osv):
    """
    Production Orders / Manufacturing Orders
    """
    _name = 'mrp.production.custom'
    _description = 'Manufacturing Order'
    _date_name = 'date_planned'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    
    
    def _dest_id_default(self, cr, uid, ids, context=None):
        try:
            location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'location_production')
            self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
        except (orm.except_orm, ValueError):
            location_id = False
        return location_id
    
    
    def _src_id_default(self, cr, uid, ids, context=None):
        try:
            location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
            self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
        except (orm.except_orm, ValueError):
            location_id = False
        return location_id


    _columns = {
        'name': fields.char('Reference', required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=False),
        'origin': fields.char('Source Document', readonly=True, states={'draft': [('readonly', False)]},
            help="Reference of the document that generated this production order request.", copy=False),
        'priority': fields.selection([('0', 'Not urgent'), ('1', 'Normal'), ('2', 'Urgent'), ('3', 'Very Urgent')], 'Priority',
            select=True, readonly=True, states=dict.fromkeys(['draft', 'confirmed'], [('readonly', False)])),

        'product_id': fields.many2one('product.product', 'Raw Material Product', required=True, readonly=True, states={'draft': [('readonly', False)]}, 
                                      domain=[('type','!=','service')]),
        'product_qty': fields.float('Raw Material Product Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'waste_qty':fields.float('Waste (%)'),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True, readonly=True, states={'draft': [('readonly', False)]}),


        'location_src_id': fields.many2one('stock.location', 'Source Location', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
            help="Location where the system will look for components."),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
            help="Location where the system will look for components."),


        'product_lines': fields.one2many('mrp.production.custom.product.line', 'production_id', 'Scheduled goods',
            readonly=True),
        
        
        'date_planned': fields.datetime('Scheduled Date', required=True, select=1, readonly=True, states={'draft': [('readonly', False)]}, copy=False),
        'date_start': fields.datetime('Start Date', select=True, readonly=True, copy=False),
        'date_finished': fields.datetime('End Date', select=True, readonly=True, copy=False),
        'move_prod_id': fields.many2one('stock.move', 'Product Move', readonly=True, copy=False),
        

        'move_created_ids': fields.one2many('stock.move', 'custom_production_id', 'Products to Produce'),
        'move_created_ids2': fields.one2many('stock.move', 'custom_production_id', 'Produced Products',
                    domain=[('state', 'not in', ('done', 'cancel','draft'))]),
      #  'product_lines': fields.one2many('mrp.production.product.line', 'production_id', 'Scheduled goods',
       #     readonly=True),

        'state': fields.selection(
            [('draft', 'New'), ('cancel', 'Cancelled'), ('confirmed', 'Awaiting Raw Materials'),
                ('ready', 'Ready to Produce'), ('in_production', 'Production Started'), ('done', 'Done')],
            string='Status', readonly=True,
            track_visibility='onchange', copy=False,
            help="When the production order is created the status is set to 'Draft'.\n\
                If the order is confirmed the status is set to 'Waiting Goods'.\n\
                If any exceptions are there, the status is set to 'Picking Exception'.\n\
                If the stock is available then the status is set to 'Ready to Produce'.\n\
                When the production gets started then the status is set to 'In Production'.\n\
                When the production is over, the status is set to 'Done'."),
        'user_id': fields.many2one('res.users', 'Responsible'),
        'company_id': fields.many2one('res.company', 'Company', required=True),

    }

    _defaults = {
        'priority': lambda *a: '1',
        'state': lambda *a: 'draft',
        'date_planned': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'product_qty': lambda *a: 1.0,
        'user_id': lambda self, cr, uid, c: uid,
        'location_src_id': _src_id_default,
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'mrp.production.custom') or '/',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'mrp.production', context=c),
        'location_dest_id': _dest_id_default,
        'waste_qty': 10.00,
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Reference must be unique per Company!'),
    ]
    
    
    
    def action_assign(self, cr, uid, ids, context=None):
        """
        Checks the availability on the consume lines of the production order
        """
        from openerp import workflow
        move_obj = self.pool.get("stock.move")
        for production in self.browse(cr, uid, ids, context=context):
            
            move_obj.action_assign(cr, uid, [production.move_prod_id.id], context=context)
            
            #if self.pool.get('mrp.production').test_ready(cr, uid, [production.id]):
            production.write({'state': 'ready'}, context=context)
               # workflow.trg_validate(uid, 'mrp.production', production.id, 'moves_ready', cr)
                
                
    
    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms production order.
        @return: Newly generated Shipment Id.
        """
        stock_move = self.pool.get('stock.move')
        
        production = self.browse(cr,uid,ids,context=context)
        
        data = {
            'name': production.product_id.name,
            'product_id': production.product_id.id,
            'product_uom': production.product_uom.id,
            'product_qty': production.product_qty,
            'production_id': production.id,
        }
        
        self.pool.get('mrp.production.custom.product.line').create(cr,uid,data)

        
        for production in self.browse(cr, uid, ids, context=context):
            self._make_production_consume_line(cr, uid, production, context=context)
            
            
            for produced_product in production.move_created_ids:
                stock_move.write(cr,uid,produced_product.id,{'name':production.name,'origin':production.name},context=context)
                stock_move.action_confirm(cr, uid, [produced_product.id], context=context)
            production.write({'state': 'confirmed'}, context=context)

        return 0
    
    
    
    
    def _make_production_consume_line(self, cr, uid, line, context=None):
        return self._make_consume_line_from_data(cr, uid, line, line.product_id, line.product_uom.id, line.product_qty, context=context)
    
    def _make_consume_line_from_data(self, cr, uid, production, product, uom_id, qty, context=None):
        stock_move = self.pool.get('stock.move')
        loc_obj = self.pool.get('stock.location')
        # Internal shipment is created for Stockable and Consumer Products
        if product.type not in ('product', 'consu'):
            return False
        # Take routing location as a Source Location.
        source_location_id = production.location_src_id.id
        prod_location_id = source_location_id
        prev_move= False
        #if production.bom_id.routing_id and production.bom_id.routing_id.location_id and production.bom_id.routing_id.location_id.id != source_location_id:
         #   source_location_id = production.bom_id.routing_id.location_id.id
          #  prev_move = True

        destination_location_id = production.location_dest_id.id
        move_id = stock_move.create(cr, uid, {
            'name': production.name,
            'date': production.date_planned,
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': uom_id,
            'product_uos_qty': False,
            'product_uos': False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'company_id': production.company_id.id,
            'procure_method': 'make_to_stock',# or self._get_raw_material_procure_method(cr, uid, product, context=context), #Make_to_stock avoids creating procurement
           # 'raw_material_production_id': production.id,
            #this saves us a browse in create()
            'price_unit': product.standard_price,
            'origin': production.name,
            'warehouse_id': loc_obj.get_warehouse(cr, uid, production.location_src_id, context=context),
        }, context=context)
        
        #if prev_move:
        #    prev_move = self._create_previous_move(cr, uid, move_id, product, prod_location_id, source_location_id, context=context)
        stock_move.action_confirm(cr, uid, [move_id], context=context)
        self.write(cr,uid,[production.id],{'move_prod_id':move_id},context=context)
        return move_id
    
    
    
    
    def _make_production_produce_line(self, cr, uid, production, context=None):
        stock_move = self.pool.get('stock.move')
        source_location_id = production.product_id.property_stock_production.id
        destination_location_id = production.location_dest_id.id
        data = {
            'name': production.name,
            'date': production.date_planned,
            'product_id': production.product_id.id,
            'product_uom': production.product_uom.id,
            'product_uom_qty': production.product_qty,
            'product_uos_qty': False,
            'product_uos': False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'move_dest_id': production.move_prod_id.id,
            'company_id': production.company_id.id,
            'custom_production_id': production.id,
            'origin': production.name,
        }
        move_id = stock_move.create(cr, uid, data, context=context)
        #a phantom bom cannot be used in mrp order so it's ok to assume the list returned by action_confirm
        #is 1 element long, so we can take the first.
        return stock_move.action_confirm(cr, uid, [move_id], context=context)[0]
    
    

                
                
    def test_ready(self, cr, uid, ids):
        res = True
        for production in self.browse(cr, uid, ids):
            if production.move_created_ids:
                res = False
        return res
    
    
    def force_production(self, cr, uid, ids, *args):
        """ Assigns products.
        @param *args: Arguments
        @return: True
        """
        from openerp import workflow
        move_obj = self.pool.get('stock.move')
        for order in self.browse(cr, uid, ids):
            move_obj.force_assign(cr, uid, [x.id for x in order.move_created_ids])
            if self.pool.get('mrp.production').test_ready(cr, uid, [order.id]):
                workflow.trg_validate(uid, 'mrp.production', order.id, 'moves_ready', cr)
        return True
    
    def _get_subproduct_factor(self, cr, uid, production_id, move_id=None, context=None):
        """ Compute the factor to compute the qty of procucts to produce for the given production_id. By default,
            it's always equal to the quantity encoded in the production order or the production wizard, but if the
            module mrp_subproduct is installed, then we must use the move_id to identify the product to produce
            and its quantity.
        :param production_id: ID of the mrp.order
        :param move_id: ID of the stock move that needs to be produced. Will be used in mrp_subproduct.
        :return: The factor to apply to the quantity that we should produce for the given production order.
        """
        return 1
    
    def product_id_change(self, cr, uid, ids, product_id, product_qty=0, context=None):
        """ Finds UoM of changed product.
        @param product_id: Id of changed product.
        @return: Dictionary of values.
        """
        result = {}
        if not product_id:
            return {'value': {
                'product_uom': False,
            }}
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)

        product_uom_id = product.uom_id and product.uom_id.id or False
        result['value'] = {'product_uom': product_uom_id,}
        return result
    
    
    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce in the uom of the production order
        @param production_mode: specify production mode (consume/consume&produce).
        @param wiz: the mrp produce product wizard, which will tell the amount of consumed products needed
        @return: True
        """
        stock_mov_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get("product.uom")
        production = self.browse(cr, uid, production_id, context=context)
        production_qty_uom = uom_obj._compute_qty(cr, uid, production.product_uom.id, production_qty, production.product_id.uom_id.id)

        main_production_move = False
        if production_mode == 'consume_produce':
            # To produce remaining qty of final product
            produced_products = {}
            """
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty"""
            waste_product_qty = 0.0
            lot_id = False
            for produce_product in production.move_created_ids:
                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                
                if wiz:
                    lot_id = wiz.lot_id.id
                    print"lots >>>",wiz.lot_id.name
                #waste_product_qty += float(produce_product.product_uom_qty * produce_product.waste_qty)/100.0
                new_moves = stock_mov_obj.action_consume_custom(cr, uid, [produce_product.id], (subproduct_factor * produce_product.product_uom_qty),location_id=produce_product.location_id.id, restrict_lot_id=lot_id, context=context)
                print"New Moves >>>",new_moves
                stock_mov_obj.write(cr, uid, new_moves, {'custom_production_id': production_id}, context=context)
                if new_moves:
                #if produce_product.product_id.id == production.product_id.id and new_moves:
                    main_production_move = new_moves[0]

                
  
        
        if production_mode in ['consume', 'consume_produce']:
            consume_lines = []
            if wiz:
                #consume_lines = []
                #for cons in wiz.consume_lines:
                consume_lines.append({'product_id': wiz.product_id.id, 'lot_id': wiz.lot_id.id, 'product_qty': wiz.product_qty})
            else:
                consume_lines = self._calculate_qty(cr, uid, production, production_qty_uom, context=context)
            for consume in consume_lines:
                
                remaining_qty = consume['product_qty']
                if remaining_qty <= 0:
                        break
                if consume['product_id'] != production.product_id.id:
                    continue
                consumed_qty = min(remaining_qty, production.product_qty)
                stock_mov_obj.action_consume_custom(cr, uid, [production.move_prod_id.id], consumed_qty, production.move_prod_id.location_id.id, restrict_lot_id=consume['lot_id'], consumed_for=main_production_move, context=context)
                remaining_qty -= consumed_qty
                if remaining_qty:
                    #consumed more in wizard than previously planned
                    product = self.pool.get('product.product').browse(cr, uid, consume['product_id'], context=context)
                    extra_move_id = self._make_consume_line_from_data(cr, uid, production, product, product.uom_id.id, remaining_qty, False, 0, context=context)
                    if extra_move_id:
                        stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)
                        
                waste_qty = (production.product_qty * production.waste_qty)/100.00
                if waste_qty > 0.0:
                    
                    product_ids = self.pool.get('product.product').search(cr,uid,[('name','ilike','Waste')],context=context)
                    if product_ids:
                        data = {
                            'name': production.name,
                            'date': production.date_planned,
                            'product_id': product_ids[0],
                            'product_uom': production.product_uom.id,
                            'product_uom_qty': waste_qty,
                            'product_uos_qty': False,
                            'product_uos': False,
                            'location_id': production.location_dest_id.id,
                            'location_dest_id': production.location_src_id.id,
                            'move_dest_id': production.move_prod_id.id,
                            'company_id': production.company_id.id,
                            'custom_production_id': production.id,
                            'origin': production.name,
                            #'state':'done',
                        }
                        move_id = stock_mov_obj.create(cr, uid, data, context=context)
                        stock_mov_obj.action_confirm(cr, uid, [move_id], context=context)[0]
                        new_moves = stock_mov_obj.action_consume_custom(cr, uid, [move_id], (subproduct_factor * waste_qty),location_id=production.location_dest_id.id, restrict_lot_id=lot_id, context=context)
                
        self.message_post(cr, uid, production_id, body=_("%s produced") % self._description, context=context)
        production.write({'state': 'done'}, context=context)
        return True
    
    
    
    def action_in_production(self, cr, uid, ids, context=None):
        """ Changes state to In Production and writes starting date.
        @return: True
        """
        return self.write(cr, uid, ids, {'state': 'in_production', 'date_start': time.strftime('%Y-%m-%d %H:%M:%S')})

class mrp_production_custom_product_line(osv.osv):
    _name = 'mrp.production.custom.product.line'
    _description = 'Production Scheduled Product'
    _columns = {
        'name': fields.char('Name', required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_qty': fields.float('Product Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
        'production_id': fields.many2one('mrp.production.custom', 'Production Order', select=True),
    }
    
    
    
    
"""    
product_ids = self.pool.get('product.product').search(cr,uid,[('name','ilike','Waste')],context=context)
if product_ids:
    data = {
        'name': production.name,
        'date': production.date_planned,
        'product_id': product_ids[0],
        'product_uom': production.product_uom.id,
        'product_uom_qty': waste_product_qty,
        'product_uos_qty': False,
        'product_uos': False,
        'location_id': production.location_dest_id.id,
        'location_dest_id': production.location_src_id.id,
        'move_dest_id': production.move_prod_id.id,
        'company_id': production.company_id.id,
        'custom_production_id': production.id,
        'origin': production.name,
        #'state':'done',
    }
    move_id = stock_mov_obj.create(cr, uid, data, context=context)
    stock_mov_obj.action_confirm(cr, uid, [move_id], context=context)[0]
    new_moves = stock_mov_obj.action_consume_custom(cr, uid, [move_id], (subproduct_factor * waste_product_qty),location_id=production.location_dest_id.id, restrict_lot_id=lot_id, context=context)
    """