from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class mrp_production_custom(osv.osv):
    """
    Production Orders / Manufacturing Orders
    """
    _name = 'mrp.production.custom'
    _description = 'Manufacturing Order'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    _columns = {
        'name': fields.char('Reference', required=True, copy=False),
        'origin': fields.char('Source Document', help="Reference of the document that generated this production order request.", copy=False),
        'priority': fields.selection([('0', 'Not urgent'), ('1', 'Normal'), ('2', 'Urgent'), ('3', 'Very Urgent')], 'Priority',
            select=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Product', required=True, domain=[('type','!=','service')]),
        'product_qty': fields.float('Product Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True, ),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure'),


        'location_src_id': fields.many2one('stock.location', 'Product Location', required=True, help="Location where the system will look for components."),
        'date_planned': fields.datetime('Scheduled Date', required=True, select=1, copy=False),
        'date_start': fields.datetime('Start Date', select=True, readonly=True, copy=False),
        'date_finished': fields.datetime('End Date', select=True, readonly=True, copy=False),
        
        'move_prod_id': fields.many2one('stock.move', 'Product Move',copy=False),
        
        'move_created_ids': fields.one2many('stock.move', 'custom_production_id', 'Products to Produce'),
        
        'move_created_ids2': fields.one2many('stock.move', 'custom_production_id', 'Produced Products'),
        
        
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
    
    _defaults={
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'mrp.production.custom') or '/',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'mrp.production.custom', context=c),
    }
    
    
    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Reference must be unique per Company!'),
    ]