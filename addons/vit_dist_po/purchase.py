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
        'uom_karton_qty'    : fields.float('Qty Box', required=True),
        'avgMT'             : fields.float('Avg MT', readonly=True),
        'avgGT'             : fields.float('Avg GT', readonly=True),
        'bufMT'             : fields.float('Buffer MT', readonly=True),
        'bufGT'             : fields.float('Buffer GT', readonly=True),
        'barcode'           : fields.char('Barcode'),
        'int_code'          : fields.char('Internal Reference'),
        'W1'                : fields.float('W1'),
        'W2'                : fields.float('W2'),
        'W3'                : fields.float('W3'),
        'W4'                : fields.float('W4'),
        'sales_3m'          : fields.float('Sales 3 Months'),
        'stock_current'     : fields.float('Stock Current'),
        'ending_inv'        : fields.float('Ending Inventory'),
        'in_transit'        : fields.float('In Transit'),
        'stock_cover'       : fields.float('Stock Cover'),
        'qty2'              : fields.float('Qty2',readonly=True),
        'sales_3m2'         : fields.float('Sales 3 Months2',readonly=True),
        'stock_current2'    : fields.float('Stock Current2',readonly=True),
        'ending_inv2'       : fields.float('Ending Inventory2',readonly=True),
        'in_transit2'       : fields.float('In Transit2',readonly=True),
        'stock_cover2'      : fields.float('Stock Cover2',readonly=True),

    }

    def onchange_adj(self, cr, uid, ids, product_id, adjustment, suggested_order, product_uom, price_unit,volume_tot,weight_tot,stock_current,in_transit,sales_3m,stock_cover,prod_weight,prod_volume):
        stock_current   = stock_current or 0.00
        in_transit      = in_transit or 0.00
        sales_3m        = sales_3m or 0.00
        stk_cover       = stock_cover or 0.00
        qty             = adjustment + suggested_order
        prod_vol        = self.pool.get('product.product').browse(cr,uid,product_id,).volume
        prod_wgt        = self.pool.get('product.product').browse(cr,uid,product_id,).weight
        factor          = self.pool.get('product.uom').browse(cr,uid,product_uom,).factor
        ratio           = 1/factor
        wgt_tot         = prod_wgt * qty * ratio 
        vol_tot         = prod_vol * qty * ratio 
        sum_wgt         = weight_tot - prod_weight + wgt_tot
        sum_vol         = volume_tot - prod_volume + vol_tot
        ps              = qty * price_unit
        end_inv         = qty + stock_current + in_transit - sales_3m
        if sales_3m > 0.00 and end_inv > 0.00 : 
            stk_cover   = end_inv / sales_3m * 4
        return {'value':{
                        'product_qty': qty or 0.00,
                        # 'qty2': qty,
                        'price_subtotal':ps, 
                        'ending_inv' : end_inv or 0.00, 
                        # 'ending_inv2' : end_inv, 
                        'stock_cover' : stk_cover or 0.00,
                        # 'stock_cover2' : stk_cover or 0.00,     
                        'prod_weight'   : wgt_tot or 0.00,
                        'prod_volume'   : vol_tot or 0.00,
                        }}

purchase_order_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _name = "purchase.order"

    def _sel_partner(self, cr, uid, context):
        res = []
        sql_req= """
        SELECT rp.id 
        FROM res_partner rp
          JOIN res_user_res_partner_rel m2m on rp.id=m2m.partner_id
          JOIN res_users ru on ru.id=m2m.user_id
        WHERE
          rp.active=TRUE AND ru.id = %d
        """ % (uid,)
        cr.execute(sql_req)
        sql_res = cr.dictfetchall()
        if sql_res: 
            res_ids = [x['id'] for x in sql_res]
            res = str(res_ids)
            print res
        return res

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
        'volume_r1'     : fields.float('Volume'),
        'volume_r2'     : fields.float('Volume'),
        'volume_r3'     : fields.float('Volume'),
        'volume_r4'     : fields.float('Volume'),
        'weight_r1'     : fields.float('Weight'),
        'weight_r2'     : fields.float('Weight'),
        'weight_r3'     : fields.float('Weight'),
        'weight_r4'     : fields.float('Weight'),
        'volume_tot'    : fields.float('Total Volume'),
        'weight_tot'    : fields.float('Total Weight'),
        'effective_day' : fields.integer('Effective Day'),
        'days_cover'    : fields.integer('Days Cover'),
        'location_ids'  : fields.many2many('stock.location','stock_loc_po_rel','po_id','location_id','Related Location'),
        'principal_ids' : fields.many2many('res.partner','res_partner_po_rel','po_id','user_id',"User's Principal"),
        'loc_x'         : fields.many2one('stock.location',"Destination",domain="[('id','in',location_ids[0][2])]",limit=2,required=True),
        'partner_x'     : fields.many2one('res.partner',"Supplier",domain="[('id','in',principal_ids[0][2])]",required=True),
        # 
        }

    # def default_get(self, cr, uid, fields, context=None):
    #     data = super(purchase_order, self).default_get(cr, uid, fields, context=context)
    #     # import pdb;pdb.set_trace()
    #     domain_principal=data['principal_ids']
    #     data['domain_p']=str(domain_principal)
    #     return data

    def create(self, cr, uid, vals, context=None):
        emp = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)],)
        uom_obj = self.pool.get('product.uom')
       
        if emp <> []:
            loc = self.pool.get('hr.employee').browse(cr,uid,emp,)[0].location_id.code
            poname = str(loc or 'x') + 'FPH' + time.strftime("%y") + '-' + self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.seq')
            vals['name'] = poname
        return super(purchase_order, self).create(cr, uid, vals, context=context)    

    def onchange_partner_x(self, cr, uid, ids, partner_x, date_order, context=None):
        # poname = '/'
        # emp = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)],)
        # uom_obj = self.pool.get('product.uom')
        # if emp <> []:
        #     loc = self.pool.get('hr.employee').browse(cr,uid,emp,)[0].location_id.code
        #     poname = str(loc or 'x') + 'FPH' + time.strftime("%y") + '-' + self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.seq') or '/'
        if context is None:
            context = {}
        if not partner_x:
            return {'value': {
                'fiscal_position': False,
                'payment_term_id': False,
                }}
        partner = self.pool.get('res.partner')
        supplier_address = partner.address_get(cr, uid, [partner_x], ['default'])
        supplier = partner.browse(cr, uid, partner_x)
        order_lines = [];pid=[];tot_w=0;tot_v=0;location_ids = [];clause =' ';clause2 =' ';clause3 =' ';clause4 =' '
        ps = self.pool.get('product.supplierinfo').search(cr,uid,[('name','=',partner_x)],)

        for x in self.pool.get('product.supplierinfo').browse(cr,uid,ps,):
            prodID = self.pool.get('product.product').search(cr,uid,[('product_tmpl_id','=',x.product_id.id)],)
            pid.append(prodID[0])
        cr.execute('SELECT sl.id FROM stock_location sl JOIN stock_loc_res_users_rel m2m on sl.id=m2m.location_id '\
            'JOIN res_users ru on ru.id=m2m.user_id WHERE sl.active=TRUE AND ru.id = '+ str(uid))
        loc = cr.fetchall() 
        if len(loc)== 1:
            clause  = ' AND ai.location_id = '+str(loc[0][0])
            clause2 = ' AND location_dest_id = '+str(loc[0][0]) 
            clause3 = ' AND location_id = '+str(loc[0][0])
        if len(loc) > 1:
            for x in loc:
                location_ids.append(x[0])
            clause  = ' AND ai.location_id IN '+str(tuple(location_ids))
            clause2 = ' AND location_dest_id IN '+str(tuple(location_ids))
            clause3 = ' AND location_id IN '+str(tuple(location_ids))
            clause4 = ' AND sm.location_dest_id IN '+str(tuple(location_ids))
        for prd in self.pool.get('product.product').browse(cr,uid,pid,):
            MT= 0.00;GT=0.00;prod_id=prd.id;s3m=0.00
            BGT=0.00;BMT=0.00;sgt_order=0.00;adj=0.00;cs=0.00;it=0.00
            ratio=1/prd.uom_po_id.factor

            cr.execute('SELECT AVG(il.quantity3) '\
                'FROM account_invoice ai '\
                'JOIN res_partner rp on ai.partner_id=rp.id '\
                'JOIN res_partner_res_partner_category_rel m2m on m2m.partner_id = rp.id   '\
                'JOIN res_partner_category rpc on m2m.category_id = rpc.id  '\
                'JOIN account_invoice_line il on ai.id=il.invoice_id  '\
                'JOIN product_uom uom on il.uos_id = uom.id  '\
                'JOIN product_uom_categ puc on puc.id=uom.category_id   '\
                'WHERE state = \'paid\'  '\
                'AND il.product_id = ' +str(prd.id)+ 'AND ai.date_invoice >= (CURRENT_DATE - (INTERVAL \'3 months\'))  '\
                'AND rpc.name like \'%GT%\' '+clause )
            SOGT = cr.fetchone()
            # import pdb;pdb.set_trace()
            if SOGT != (None,) : 
                GT = SOGT[0]/ratio
                if GT != 0 : 
                    BGT = GT/2 
            
            cr.execute('SELECT AVG(il.quantity3) '\
                'FROM account_invoice ai '\
                'JOIN res_partner rp on ai.partner_id=rp.id '\
                'JOIN res_partner_res_partner_category_rel m2m on m2m.partner_id = rp.id   '\
                'JOIN res_partner_category rpc on m2m.category_id = rpc.id  '\
                'JOIN account_invoice_line il on ai.id=il.invoice_id  '\
                'JOIN product_uom uom on il.uos_id = uom.id  '\
                'JOIN product_uom_categ puc on puc.id=uom.category_id   '\
                'WHERE state = \'paid\'  '\
                'AND il.product_id = ' +str(prd.id)+ 'AND ai.date_invoice >= (CURRENT_DATE - (INTERVAL \'3 months\'))  '\
                'AND rpc.name like \'%MT%\' '+ clause )
            SOMT = cr.fetchone()
            if SOMT != (None,) : 
                MT = (SOMT[0]/ratio)
            s3m  = MT+GT

            # SELECT COALESCE(masuk,0)-COALESCE(keluar,0) as qty, COALESCE(unit_qty1,0)-COALESCE(unit_qty2,0) as unit_qty,coalesce(id1,id2) as produk_id FROM (
            #     SELECT SUM(product_qty) as masuk,product_id as id1,SUM(product_qty)/pu.factor as unit_qty1  FROM stock_move sm
            #     JOIN product_uom pu ON pu.id=sm.product_uom
            #     WHERE state = 'done' and product_id=160
            #     AND location_dest_id = 32
            #     GROUP BY product_id,pu.factor) as A 
            #     FULL OUTER JOIN 
            #     (SELECT SUM(product_qty)as keluar,product_id as id2,SUM(product_qty)/pu.factor as unit_qty2 FROM stock_move sm
            #     JOIN product_uom pu ON pu.id=sm.product_uom
            #     WHERE state = 'done' and product_id=160
            #     AND location_id = 32 --32=pdl,14=bdg
            #     GROUP BY product_id,pu.factor) as B on A.id1=B.id2

            cr.execute('SELECT COALESCE(masuk,0)-COALESCE(keluar,0) as qty, COALESCE(unit_qty1,0)-COALESCE(unit_qty2,0) as unit_qty,coalesce(id1,id2) as produk_id FROM ('\
                'SELECT SUM(product_qty) as masuk,product_id as id1,SUM(product_qty)/pu.factor as unit_qty1  FROM stock_move sm '\
                'JOIN product_uom pu ON pu.id=sm.product_uom '\
                'WHERE state = \'done\' and product_id= '+str(prd.id)+clause2+
                'GROUP BY product_id,pu.factor) as A '\
                'FULL OUTER JOIN '\
                '(SELECT SUM(product_qty)as keluar,product_id as id2,SUM(product_qty)/pu.factor as unit_qty2 FROM stock_move sm '\
                'JOIN product_uom pu ON pu.id=sm.product_uom '\
                'WHERE state = \'done\' and product_id= '+str(prd.id)+clause3+
                'GROUP BY product_id,pu.factor) as B on A.id1=B.id2')
            CS = cr.fetchone()
            cs = (CS and CS[1]) or 0
            cs = (cs/ratio)

            cr.execute('SELECT SUM(sm.product_qty) '\
                'FROM purchase_order po '\
                'JOIN stock_picking sp ON po.id=sp.purchase_id '\
                'JOIN stock_move sm ON sp.id=sm.picking_id '\
                'WHERE po.state=\'approved\' '+clause4+' AND sm.product_id = '+str(prd.id)+
                'AND sp.state=\'assigned\' ')

            IT = cr.fetchone()
            it = (IT and IT[0]) or 0
            it = (it/ratio)

            BMT=1*MT
            tot_bufer = BMT+BGT
            sgt_order = s3m+tot_bufer-cs-it

            print MT;print BGT;print GT;print cs;print sgt_order
            price   = prd.product_tmpl_id.standard_price 
            tot_v   = tot_v+prd.volume
            tot_w   = tot_w+prd.weight
            order_lines.append([0,0,{'product_id': prd.id or False, 
                'name'          : prd.name or '',
                'product_uom'   : prd.uom_po_id.id or False,
                'date_planned'  : date_order,
                'sales_3m'      : s3m,
                'sales_3m2'      : s3m,
                'avgMT'         : MT,
                'avgGT'         : GT,
                'bufMT'         : BMT,
                'bufGT'         : BGT,
                'suggested_order' : sgt_order,         
                'prod_weight'   : prd.weight * ratio * sgt_order,
                'prod_volume'   : prd.volume * ratio * sgt_order,
                'price_unit'    : price, 
                'product_uom'   : prd.uom_po_id.id, 
                'stock_current' : cs, 
                # 'stock_current2' : cs,     
                'ending_inv'    : 0.00,     
                'in_transit'    : it,    
                # 'in_transit2'    : it,     
                'stock_cover'   : 0.00, 
                'barcode'       : prd.barcode or '',
                'int_code'      : prd.default_code,
                'adjustment'    : 0.00,
                'product_qty'   : sgt_order,
                # 'qty2'   : sgt_order,
                }])
        return {'value': {
            'order_line'    : order_lines,
            'pricelist_id'  : supplier.property_product_pricelist_purchase.id or False,
            'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
            'payment_term_id': supplier.property_supplier_payment_term.id or False,
            'partner_code'  : supplier.code,
            # 'volume_tot'    : tot_v,
            # 'weight_tot'    : tot_w,
            'partner_id'    : partner_x,
            }}


    def onchange_percent(self, cr, uid, ids,volume_tot ,weight_tot, percent_rx, fname,percent_r1,percent_r2,percent_r3,percent_r4, context=None):
        if context is None:
            context = {}
        ptot = percent_r1+percent_r2+percent_r3+percent_r4
        if ptot>100:
            raise osv.except_osv(_('Error!'), _('Persentase lebih dari 100!'))
        vol_tot=volume_tot*percent_rx/100.00
        wgt_tot=weight_tot*percent_rx/100.00
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

    def act_calculate(self, cr, uid, ids, context=None):
        data = self.read(cr,uid,ids[0],)
        lines_obj = self.pool.get('purchase.order.line')
        vol=0.00;wgt=0.00
        v1=0.00;w1=0.00
        v2=0.00;w2=0.00
        v3=0.00;w3=0.00
        v4=0.00;w4=0.00
        # import pdb;pdb.set_trace()
        for x in lines_obj.browse(cr,uid,data['order_line'],context=None):
            vol += x.prod_volume
            wgt += x.prod_weight
        for x in lines_obj.browse(cr,uid,data['order_line'],context=None):
            v1=vol*data['percent_r1']/100
            w1=wgt*data['percent_r1']/100
            q1=x.product_qty*data['percent_r1']/100
            lines_obj.write(cr,uid,x.id,{'W1' : q1},context=None)
            v2=vol*data['percent_r2']/100
            w2=wgt*data['percent_r2']/100
            q2=x.product_qty*data['percent_r2']/100
            lines_obj.write(cr,uid,x.id,{'W2' : q2},context=None)
            v3=vol*data['percent_r3']/100
            w3=wgt*data['percent_r3']/100
            q3=x.product_qty*data['percent_r3']/100
            lines_obj.write(cr,uid,x.id,{'W3' : q3},context=None)
            v4=vol*data['percent_r4']/100
            w4=wgt*data['percent_r4']/100
            q4=x.product_qty*data['percent_r4']/100
            lines_obj.write(cr,uid,x.id,{'W4' : q4},context=None)
        self.write(cr,uid,ids,{
            'volume_tot'    : v1+v2+v3+v4, 
            'weight_tot'    : w1+w2+w3+w4,
            'volume_r1'     : v1, 
            'volume_r2'     : v2,
            'volume_r3'     : v3,
            'volume_r4'     : v4,
            'weight_r1'     : w1,
            'weight_r2'     : w2,
            'weight_r3'     : w3,
            'weight_r4'     : w4,
            })
        return True

    # def button_dummy(self, cr, uid, ids, context=None):
    #     lines = self.read(cr,uid,ids[0],)['order_line']
    #     lines_obj = self.pool.get('purchase.order.line')
    #     vol=0.00;wgt=0.00
    #     for x in lines_obj.browse(cr,uid,lines,context=None):
    #         vol += x.product_qty * x.prod_volume 
    #         wgt += x.product_qty * x.prod_weight
    #     self.write(cr,uid,ids,{'volume_tot' : vol, 'weight_tot' : wgt,}) 
    #     return True
    
    def _get_default_loc(self, cr, uid, context=None):  
        if context is None:
            context = {}
        location_ids = []
        cr.execute('SELECT sl.id FROM stock_location sl JOIN stock_loc_res_users_rel m2m on sl.id=m2m.location_id '\
            'JOIN res_users ru on ru.id=m2m.user_id WHERE sl.active=TRUE AND ru.id = '+ str(uid))
        loc = cr.fetchall() 
        if loc <> []:
            for x in loc:
                location_ids.append(x[0])
            return [(6, 0, location_ids)]
        return False

    def _get_default_principal(self, cr, uid, context=None):  
        if context is None:
            context = {}
        principal_ids = []
        # import pdb;pdb.set_trace()
        cr.execute('SELECT rp.id FROM res_partner rp JOIN res_user_res_partner_rel m2m on rp.id=m2m.partner_id '\
            'JOIN res_users ru on ru.id=m2m.user_id WHERE rp.active=TRUE AND ru.id = '+ str(uid))
        prin = cr.fetchall() 
        if prin <> []:
            for x in prin:
                principal_ids.append(x[0])
            return [(6,0,principal_ids)]
        return False

    def onchange_locx(self, cr, uid, ids, loc_x, location_id, context=None):
        if loc_x:
            return {'value':{'location_id':loc_x,}}

    _defaults = {
        'location_ids':_get_default_loc,
        'principal_ids':_get_default_principal,
        'r1': fields.date.context_today,
        'r2': fields.date.context_today,
        'r3': fields.date.context_today,
        'r4': fields.date.context_today,
        # 'domain_p':_sel_partner,
        }

purchase_order()

# class stock_move_split_lines_exist(osv.osv_memory):
#     _inherit = "stock.move.split.lines"
#     _name = "stock.move.split.lines"
#     #TODO:MOVE TO WIZARD

#     _columns = {
#         'expire': fields.date('Expire Date'),
#         }

# stock_move_split_lines_exist()

class stock_partial_picking_line(osv.TransientModel):
    _name = "stock.partial.picking.line"
    _inherit = "stock.partial.picking.line"

    def onchange_prodlot_id(self, cr, uid, ids, prodlot_id, context=None):
        datex = self.pool.get('stock.production.lot').browse(cr,uid,prodlot_id,).life_date or False
        return {'value': {'expired': datex}}

    _columns = {
        'expired': fields.date('Expire Date'),
        }

stock_partial_picking_line()