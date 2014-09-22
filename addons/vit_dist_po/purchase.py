from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
from datetime import timedelta, date

class purchase_order_line(osv.osv):
    _name       = 'purchase.order.line'
    _inherit    = 'purchase.order.line'

    _columns = {
        'suggested_order'   : fields.float('Suggested Order', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'adjustment'        : fields.float('Adjustment', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'prod_weight'       : fields.float('Weight'),
        'prod_volume'       : fields.float('Volume'),
        'sales_3m'          : fields.float('Sales 3 Months'),
        'stock_current'     : fields.float('Stock Current'),
        # 'stock_current'     : fields.function(_stock_current_value, type='float', string='Stock Current', digits_compute=dp.get_precision('Account')),
        'ending_inv'        : fields.float('Ending Inventory'),
        'in_transit'        : fields.float('In Transit'),
        'stock_cover'       : fields.float('Stock Cover'),
        'uom_karton_qty'    : fields.integer('Qty Box', required=True),
        'avgMT'             : fields.integer('Avg MT', readonly=True),
        'avgGT'             : fields.integer('Avg GT', readonly=True),
        'bufMT'             : fields.integer('Buffer MT', readonly=True),
        'bufGT'             : fields.integer('Buffer GT', readonly=True),
        'barcode'           : fields.char('Barcode'),
        'int_code'          : fields.char('Internal Reference'),
    }

    # def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
    #         partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
    #         name=False, price_unit=False, context=None):
    #     res = {}
    #     if context is None:
    #         context = {}
    #     res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
    #         partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned,
    #         name=name, price_unit=price_unit, context=context)
    #     res['value'].update({'suggested_order' : 1000.00 })
    #     return res

    def onchange_adj(self, cr, uid, ids, adjustment, suggested_order, product_uom, price_unit):
        uom = self.pool.get('product.uom').search(cr,uid,[('name','ilike','karton')])
        if not product_uom in uom:
            raise osv.except_osv(_('Error!'), _('Satuan produk tidak dalam karton'))
        qty = adjustment + suggested_order
        ps = qty * price_unit
        return {'value':{'product_qty': qty,'price_subtotal':ps}}

purchase_order_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        'notes': fields.text('Keterangan'),
        'r1'            : fields.date('R1'),
        'r2'            : fields.date('R2'),
        'r3'            : fields.date('R3'),
        'r4'            : fields.date('R4'),
        'percent_r1'    : fields.float('Q1'),
        'percent_r2'    : fields.float('Q2'),
        'percent_r3'    : fields.float('Q3'),
        'percent_r4'    : fields.float('Q4'),
        'volume_r1'     : fields.float('Volume', readonly=True),
        'volume_r2'     : fields.float('Volume', readonly=True),
        'volume_r3'     : fields.float('Volume', readonly=True),
        'volume_r4'     : fields.float('Volume', readonly=True),
        'weight_r1'     : fields.float('Weight', readonly=True),
        'weight_r2'     : fields.float('Weight', readonly=True),
        'weight_r3'     : fields.float('Weight', readonly=True),
        'weight_r4'     : fields.float('Weight', readonly=True),
        'volume_tot'    : fields.float('Volume Total', readonly=True),
        'weight_tot'    : fields.float('Weight Total', readonly=True),
        'effective_day' : fields.integer('Effective Day'),
        'days_cover'    : fields.integer('Days Cover'),
        'partner_code'  : fields.char('Code', readonly=True),
        'no_bukti'      : fields.char('Application No.', readonly=True, size=64, help="Kode cabang dan jenis transaksi pembelian."),
        }

    # def create(cr, user, vals, context=None):
    #     # def _get_no_bukti(self, cr, uid, context=None):
    #     if context is None:
    #         context = {}
    #     import pdb;pdb.set_trace()
    #     emp = self.pool.get('hr.employee').search(cr,uid,[('location_id','=',False)],)
    #     if emp :
    #         return super(purchase_order,self).create(cr, user, vals, context=context)
    #     loc = self.pool.get('hr.employee').browse(cr,uid,uid,).location_id.code 
    #     sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.seq')
    #     if sequence:
    #         vals['no_bukti'] = str(code.upper() + 'FPH' + time.strftime("%y") + '-' + sequence)
    #         return super(purchase_order,self).create(cr, user, vals, context=context)

    def onchange_partner_id(self, cr, uid, ids, partner_id, date_order, location_id, context=None):
        if context is None:
            context = {}
        partner = self.pool.get('res.partner')
        if not partner_id:
            return {'value': {
                'fiscal_position': False,
                'payment_term_id': False,
                }}
        supplier_address = partner.address_get(cr, uid, [partner_id], ['default'])
        supplier = partner.browse(cr, uid, partner_id)
        if not location_id:
            return {'value': {
                'fiscal_position': False,
                'payment_term_id': False,
                'partner_code': supplier.code,
                }}
        order_lines = [];pid=[];tot_w=0;tot_v=0
        ps = self.pool.get('product.supplierinfo').search(cr,uid,[('name','=',partner_id)],)
        for x in self.pool.get('product.supplierinfo').browse(cr,uid,ps,):
            pid.append(x.product_id.id)
        for prd in self.pool.get('product.product').browse(cr,uid,pid,):
            MT= 0.0;GT=0;prod_id=prd.id;s3m=0
            BGT=0;sgt_order=100;adj=0
            cr.execute('SELECT so.id '\
                'FROM sale_order so '\
                'JOIN res_partner rp on so.partner_id=rp.id '\
                'LEFT JOIN res_partner_res_partner_category_rel m2m on m2m.partner_id = rp.id '\
                'LEFT JOIN res_partner_category rpc on m2m.category_id = rpc.id '\
                'WHERE so.state in (\'done\',\'sent\',\'done\') '\
                'AND rpc.name like \'%MT%\' AND so.date_order >= (CURRENT_DATE - (INTERVAL \'3 months\')) '\
                'AND so.location_id = '+str(location_id) )
            SOMT = cr.fetchall()
            
            if SOMT != [] : 
                cr.execute('SELECT AVG(product_uom_qty) FROM sale_order_line '\
                    'WHERE order_id IN %s AND product_id = '+ str(prod_id), (tuple(SOMT), ))
                MT = cr.fetchone()
                if MT==(None,):
                    MT=0
                else : MT=MT[0]

            cr.execute('SELECT so.id '\
                'FROM sale_order so '\
                'JOIN res_partner rp on so.partner_id=rp.id '\
                'LEFT JOIN res_partner_res_partner_category_rel m2m on m2m.partner_id = rp.id '\
                'LEFT JOIN res_partner_category rpc on m2m.category_id = rpc.id '\
                'WHERE so.state in (\'done\',\'sent\',\'done\') '\
                'AND rpc.name like \'%GT%\' AND so.date_order >= (CURRENT_DATE - (INTERVAL \'3 months\')) '\
                'AND so.location_id = '+str(location_id) )
            SOGT = cr.fetchall()

            if SOGT != [] : 
                cr.execute('SELECT AVG(product_uom_qty) FROM sale_order_line '\
                    'WHERE order_id IN %s AND product_id = '+ str(prod_id), (tuple(SOGT), ))
                GT = cr.fetchone()
                if GT==(None,):
                    GT=0
                else : 
                    GT=GT[0]
                    if GT <> 0 : BGT=GT/2

            s3m=MT+GT
            tot_v=tot_v+prd.volume
            tot_w=tot_w+prd.weight
            order_lines.append([0,0,{'product_id': prd.id or False, 
                'name': prd.name or '',
                'product_uom'   : prd.uom_po_id.id or False,
                'date_planned'  : date_order,
                'sales_3m'      : s3m,
                'avgMT'         : MT,
                'avgGT'         : GT,
                'bufMT'         : MT,
                'bufGT'         : BGT,
                'suggested_order' : sgt_order,         
                'prod_weight'   : prd.weight,
                'prod_volume'   : prd.volume,
                'price_unit'    : prd.standard_price, 
                'product_uom'   : prd.uom_po_id.id, 
                'product_qty'   : int(sgt_order + adj),
                'stock_current' : 0.00,     
                'ending_inv'    : 0.00,     
                'in_transit'    : 0.00,     
                'stock_cover'   : 0.00, 
                'barcode'       : prd.barcode or '',
                'int_code'      : prd.default_code,
                }])
        return {'value': {
            'order_line' : order_lines,
            'pricelist_id': supplier.property_product_pricelist_purchase.id or False,
            'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
            'payment_term_id': supplier.property_supplier_payment_term.id or False,
            'partner_code': supplier.code,
            'volume_tot' : tot_v,
            'weight_tot' : tot_w,
            }}

    def _get_default_loc(self, cr, uid, context=None):  
        if context is None:
            context = {}
        emp = self.pool.get('hr.employee').search(cr,uid,[('location_id','=',False)],)
        if emp :
            return False
        loc = self.pool.get('hr.employee').browse(cr,uid,uid,).location_id.id 
        return loc

    def onchange_percent(self, cr, uid, ids,volume_tot ,weight_tot, percent_rx, fname,percent_r1,percent_r2,percent_r3,percent_r4, context=None):
        # import pdb;pdb.set_trace()
        if context is None:
            context = {}
        ptot = percent_r1+percent_r2+percent_r3+percent_r4
        if ptot>100:
            raise osv.except_osv(_('Error!'), _('Persentase lebih dari 100!'))
        vol_tot=volume_tot*percent_rx/100
        wgt_tot=weight_tot*percent_rx/100
        if fname == '1':
            return {'value':{
                'volume_r1':vol_tot,
                'weight_r1':wgt_tot,}}
        if fname == '2':
            return {'value':{
                'volume_r2':vol_tot,
                'weight_r2':wgt_tot,}}
        if fname == '3':
            return {'value':{
                'volume_r3':vol_tot,
                'weight_r3':wgt_tot,}}
        if fname == '4':
            return {'value':{
                'volume_r4':vol_tot,
                'weight_r4':wgt_tot,}}

    _defaults = {
        'r1': fields.date.context_today,
        'r2': fields.date.context_today,
        'r3': fields.date.context_today,
        'r4': fields.date.context_today,
        }

purchase_order()

class stock_move_split_lines_exist(osv.osv_memory):
    _inherit = "stock.move.split.lines"

    _columns = {
        'expire': fields.date('Expire Date'),
        }

stock_move_split_lines_exist()