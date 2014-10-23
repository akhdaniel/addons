from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
from datetime import timedelta, date, datetime

class purchase_order_line(osv.osv):
    _name       = 'purchase.order.line'
    _inherit    = 'purchase.order.line'
    _order      = 'stock_current'

    def _get_alias1(self,line,field):
        px=0;
        if field == 'w11':
            for x in line.order_id.sch_ids1:
                px += x.alias == '1' and x.p1/100.00
        if field == 'w12':
            for x in line.order_id.sch_ids1:
                px += x.alias == '2' and x.p1/100.00
        if field == 'w13':
            for x in line.order_id.sch_ids1:
                px += x.alias == '3' and x.p1/100.00
        if field == 'w14':
            for x in line.order_id.sch_ids1:
                px += x.alias == '4' and x.p1/100.00
        if field == 'w15':
            for x in line.order_id.sch_ids1:
                px += x.alias == '5' and x.p1/100.00
        if field == 'w16':
            for x in line.order_id.sch_ids1:
                px += x.alias == '6' and x.p1/100.00
        return px

    def _determin_qw11(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines:
            px = self._get_alias1(line,field_names)
            result[line.id] = px * line.product_qty or 0
        return result

    def _determin_qw12(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        # import pdb;pdb.set_trace()
        for line in lines:
            py = self._get_alias1(line,field_names)
            result[line.id] = py * line.product_qty or 0
        return result

    def _determin_qw13(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines:
            pz = self._get_alias1(line,field_names)
            result[line.id] = pz * line.product_qty or 0
        return result

    def _determin_qw14(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines:
            px = self._get_alias1(line,field_names)
            result[line.id] = px * line.product_qty or 0
        return result

    def _determin_qw15(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        # import pdb;pdb.set_trace()
        for line in lines:
            py = self._get_alias1(line,field_names)
            result[line.id] = py * line.product_qty or 0
        return result

    def _determin_qw16(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines:
            pz = self._get_alias1(line,field_names)
            result[line.id] = pz * line.product_qty or 0
        return result

    def _determin_w1(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines: 
            result[line.id] = line.product_qty * line.order_id.percent_r1/100 or 0
        return result    

    _columns = {
        'suggested_order'   : fields.float('Suggested Order', digits_compute=dp.get_precision('Product Unit of Measure')),
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
        # 'W1'                : fields.function(_determin_wx_from_precent_rx,type='float',string='W1',store=False),
        'W2'                : fields.float(string='W2'),
        'W3'                : fields.float(string='W3'),
        'W4'                : fields.float(string='W4'),
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
        'forecastMT'        : fields.float('Forecast MT',required=True),
        'forecastGT'        : fields.float('Forecast GT',required=True),
        'w1'                : fields.function(_determin_w1,type='float',string='W1',store=False),
        'w11'               : fields.function(_determin_qw11,type='float',string='W1.1',store=False),
        'w12'               : fields.function(_determin_qw12,type='float',string='W1.2',store=False),
        'w13'               : fields.function(_determin_qw13,type='float',string='W1.3',store=False),
        'w14'               : fields.function(_determin_qw14,type='float',string='W1.4',store=False),
        'w15'               : fields.function(_determin_qw15,type='float',string='W1.5',store=False),
        'w16'               : fields.function(_determin_qw16,type='float',string='W1.6',store=False),
    }

    def onchange_line(self, cr, uid, ids, product_id, adjustment, suggested_order, product_uom, price_unit,
        volume_tot,weight_tot,stock_current,in_transit,sales_3m,stock_cover,prod_weight,prod_volume,
        forecastMT,forecastGT, bufMT, bufGT):
        stock_current   = stock_current or 0.00
        in_transit      = in_transit or 0.00
        sales_3m        = sales_3m or 0.00
        stk_cover       = stock_cover or 0.00
        forecastMT      = forecastMT or 0.00
        forecastGT      = forecastGT or 0.00
        bufMT           = bufMT or 0.00
        bufGT           = bufGT or 0.00
        adjustment      = adjustment or 0.00
        suggested_order = (forecastMT + forecastGT + bufMT + bufGT - stock_current - in_transit) or 0.00
        qty             = adjustment + suggested_order
        prod_vol        = self.pool.get('product.product').browse(cr,uid,product_id,).volume
        prod_wgt        = self.pool.get('product.product').browse(cr,uid,product_id,).weight
        factor          = self.pool.get('product.uom').browse(cr,uid,product_uom,).factor
        ratio           = 1/factor
        wgt_tot         = prod_wgt * qty * ratio 
        vol_tot         = prod_vol * qty * ratio 
        ps              = qty * price_unit
        end_inv         = qty + stock_current + in_transit - sales_3m
        if sales_3m > 0.00 and end_inv > 0.00 : 
            stk_cover   = end_inv / sales_3m * 4
        prd             = self.pool.get('product.product').browse(cr,uid,product_id,)
        price_unit      = prd.product_tmpl_id.standard_price
        return {'value':{
                        'product_qty'       : round(qty) or 0.00,
                        'price_subtotal'    : ps or 0.00, 
                        'ending_inv'        : end_inv or 0.00, 
                        'stock_cover'       : stk_cover,
                        'prod_weight'       : wgt_tot or 0.00,
                        'prod_volume'       : vol_tot or 0.00,
                        'suggested_order'   : round(suggested_order),
                        'price_unit'        : price_unit or 0.00,
                        # 'qty2'            : qty,
                        # 'ending_inv2'     : end_inv, 
                        # 'stock_cover2'    : stk_cover or 0.00, 
                        }}

    # def onchange_forecast(self, cr, uid, ids, forecastMT, forecastGT, suggested_order, bufMT, bufGT, stock_current, in_transit):
    #     return {'value':{
    #         'suggested_order':suggested_order,
    #         'product_qty': suggested_order, 
    #         }}

purchase_order_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _name = "purchase.order"

    # def _sel_partner(self, cr, uid, context):
    #     res = []
    #     sql_req= """
    #     SELECT rp.id 
    #     FROM res_partner rp
    #       JOIN res_user_res_partner_rel m2m on rp.id=m2m.partner_id
    #       JOIN res_users ru on ru.id=m2m.user_id
    #     WHERE
    #       rp.active=TRUE AND ru.id = %d
    #     """ % (uid,)
    #     cr.execute(sql_req)
    #     sql_res = cr.dictfetchall()
    #     if sql_res: 
    #         res_ids = [x['id'] for x in sql_res]
    #         res = str(res_ids)
    #         print res
    #     return res

    def onchange_lines(self, cr, uid, ids, volume_tot, weight_tot, order_line, context=None):
        vol=0;wei=0
        if not ids:
            for ol in order_line:
                vol+=ol[2]['prod_volume']
                wei+=ol[2]['prod_weight']
        return {'value':{
            'volume_tot'    : vol, 
            'weight_tot'    : wei,}}

    _columns = {
        'notes': fields.text('Keterangan'),
        'r1'            : fields.date('From'),
        'r2'            : fields.date('From'),
        'r3'            : fields.date('From'),
        'r4'            : fields.date('From'),
        'r1e'            : fields.date('To'),
        'r2e'            : fields.date('To'),
        'r3e'            : fields.date('To'),
        'r4e'            : fields.date('To'),
        'percent_r1'    : fields.float('Percent'),
        'percent_r2'    : fields.float('Percent'),
        'percent_r3'    : fields.float('Percent'),
        'percent_r4'    : fields.float('Percent'),
        'qr1'           : fields.integer("Qty"),
        'qr2'           : fields.integer("Qty"),
        'qr3'           : fields.integer("Qty"),
        'qr4'           : fields.integer("Qty"),
        'volume_r1'     : fields.float('Volume'),
        'volume_r2'     : fields.float('Volume'),
        'volume_r3'     : fields.float('Volume'),
        'volume_r4'     : fields.float('Volume'),
        'weight_r1'     : fields.float('Weight'),
        'weight_r2'     : fields.float('Weight'),
        'weight_r3'     : fields.float('Weight'),
        'weight_r4'     : fields.float('Weight'),
        'fleet_id'      : fields.many2one('fleet.vehicle',"Vehicle"),
        # 'volume'        : fields.float('Capacity(Volume)'),
        # 'tonase'        : fields.float('Capacity(Weight)'),
        'no_vehicle'    : fields.float('Total Truck'),
        'volume_tot'    : fields.float('Total Volume'),
        'weight_tot'    : fields.float('Total Weight'),
        'effective_day' : fields.integer('Effective Day'),
        'days_cover'    : fields.integer('Days Cover'),
        'location_ids'  : fields.many2many('stock.location','stock_loc_po_rel','po_id','location_id','Related Location'),
        'principal_ids' : fields.many2many('res.partner','res_partner_po_rel','po_id','user_id',"User's Principal"),
        'loc_x'         : fields.many2one('stock.location',"Destination",domain="[('id','in',location_ids[0][2])]",limit=2,required=True),
        'partner_x'     : fields.many2one('res.partner',"Supplier",domain="[('id','in',principal_ids[0][2])]",required=True),
        'sch_ids1'      : fields.one2many('purchase.order.schedule.r1','po_id1',"R1"), 
        'sch_ids2'      : fields.one2many('purchase.order.schedule.r2','po_id2',"R2"), 
        'sch_ids3'      : fields.one2many('purchase.order.schedule.r3','po_id3',"R3"), 
        'sch_ids4'      : fields.one2many('purchase.order.schedule.r4','po_id4',"R4"), 
        'periode'       : fields.char('Periode'),
        'view_w1'       : fields.boolean('Show/hide'),
        }

    # def default_get(self, cr, uid, fields, context=None):
    #     data = super(purchase_order, self).default_get(cr, uid, fields, context=context)
    #     return data

        # q11 += p1
        # for y in sch_ids1:
        #     if y[1]:
        #         q11 += self.browse(cr,uid,y[1],).p1
        #     if not y[1]:
        #         q11 += y[2]['p1']
        # if q11 > percent_r1:

    def create(self, cr, uid, vals, context=None):
        emp = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)],)
        uom_obj = self.pool.get('product.uom')
        if emp <> []:
            loc = self.pool.get('hr.employee').browse(cr,uid,emp,)[0].location_id.code
            poname = str(loc or 'x') + 'FPH' + time.strftime("%y") + '-' + self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.seq')
            vals['name'] = poname
        #Cek jumlah q11 apakah melebihi w1    
        sumw=0;sumv=[]
        # import pdb;pdb.set_trace()
        if len(vals['sch_ids1'])>0:
            for y in vals['sch_ids1']: sumw += y[2]['p1']
            for x in vals['sch_ids1']: sumv += x[2]['fleet_id'][0][2]
        vals['no_vehicle'] = len(sumv)
        if sumw > vals['percent_r1']:
            raise osv.except_osv(_('Error W1!'), _('Jumlah persentase breakdown melebihi persentase per minggu'))
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

            cr.execute('SELECT COALESCE(masuk,0)-COALESCE(keluar,0) as qty, COALESCE(unit_qty1,0)-COALESCE(unit_qty2,0) as unit_qty,coalesce(id1,id2) as produk_id FROM ('\
                'SELECT SUM(product_qty) as masuk,product_id as id1,SUM(product_qty)/pu.factor as unit_qty1  FROM stock_move sm '\
                'JOIN product_uom pu ON pu.id=sm.product_uom '\
                'WHERE state = \'done\' and product_id= '+str(prd.id)+clause2+
                'GROUP BY product_id,pu.factor) as A '\
                'FULL OUTER JOIN '\
                '(SELECT SUM(product_qty) as keluar,product_id as id2,SUM(product_qty)/pu.factor as unit_qty2 FROM stock_move sm '\
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
                'sales_3m'      : round(s3m),
                'avgMT'         : round(MT),
                'avgGT'         : round(GT),
                'bufMT'         : round(BMT),
                'bufGT'         : round(BGT),
                'suggested_order' : 0.00,         
                'prod_weight'   : prd.weight * ratio * sgt_order,
                'prod_volume'   : prd.volume * ratio * sgt_order,
                'price_unit'    : price, 
                'product_uom'   : prd.uom_po_id.id, 
                'stock_current' : cs,      
                'ending_inv'    : 0.00,     
                'in_transit'    : round(it),    
                'stock_cover'   : 0.00, 
                'barcode'       : prd.barcode or '',
                'int_code'      : prd.default_code,
                'adjustment'    : 0.00,
                'product_qty'   : round(sgt_order),
                'forecastMT'    : 0.00,
                'forecastGT'    : 0.00,
                }])
        return {'value': {
            'order_line'        : order_lines,
            'pricelist_id'      : supplier.property_product_pricelist_purchase.id or False,
            'fiscal_position'   : supplier.property_account_position and supplier.property_account_position.id or False,
            'payment_term_id'   : supplier.property_supplier_payment_term.id or False,
            'partner_code'      : supplier.code,
            'partner_id'        : partner_x,
            # 'volume_tot'      : tot_v,
            # 'weight_tot'      : tot_w,
            }}


    def onchange_rx(self, cr, uid, ids, percent_rx, fname, percent_r1, percent_r2, percent_r3, percent_r4, 
            sch_ids1, r1, order_line, qr1, volume_r1, weight_r1, context=None):
        if context is None:
            context = {}
        ptot = percent_r1+percent_r2+percent_r3+percent_r4
        if ptot>100:
            raise osv.except_osv(_('Error!'), _('Persentase lebih dari 100!'))       
        # if not r1:
        #     raise osv.except_osv(_('Warning!'), _('Isi R1!'))\
        if order_line[0][1] == False:
            sumqty1=0;volr1=0;wgtr1=0
            for x in order_line: 
                sumqty1 += x[2]['product_qty']
                wgtr1 += x[2]['prod_weight']
                volr1 += x[2]['prod_volume']
        if ids != []:
            sumqty1=0;volr1=0;wgtr1=0
            for x in self.pool.get('purchase.order.line').browse(cr,uid,[x[1] for x in order_line],): 
                sumqty1 += x.product_qty
                volr1 += x.prod_volume
                wgtr1 += x.prod_weight
        # Fix bug for replace ids
        toremove = self.pool.get('purchase.order.schedule.r1').search(cr,uid,[('id','in',[x[1] for x in sch_ids1])],)
        self.pool.get('purchase.order.schedule.r1').unlink(cr,uid,toremove,)
        #here
        # sch_ids1=[]
        # dat=datetime.strptime(r1, '%Y-%m-%d')
        # for i in range(3):
        #     dat +=i*timedelta(days=2)
        #     name1s = dat.strftime("%A")
        #     sch_ids1.append(
        #         [0,0,{'name': datetime.strftime(dat, '%Y-%m-%d'),
        #         'alias'     : str(i+1),
        #         'name1s'    : name1s,
        #         'p1'        : percent_rx/3.00 or 0.00,
        #         'vol1'      : percent_rx/100.00*volr1/3.00 or 0.00,
        #         'wgt1'      : percent_rx/100.00*wgtr1/3.00 or 0.00}])
        if fname == '1':
            return {'value':{
                'qr1'       : percent_rx/100.00*sumqty1 or 0,
                'volume_r1' : percent_rx/100.00*volr1 or 0,
                'weight_r1' : percent_rx/100.00*wgtr1 or 0,}}
                # 'sch_ids1'  : sch_ids1}}
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
        #R1
        r1_lines = self.pool.get('purchase.order.schedule.r1')
        vol1_tot=0.00
        for y in r1_lines.browse(cr,uid,data['sch_ids1'],context=None):
            vol1_tot+=y.p1
        if vol1_tot>data['percent_r1']:
            raise osv.except_osv(_('Error!'), _('Jumlah Q1.1 lebih dari Q1!'))
        for y in r1_lines.browse(cr,uid,data['sch_ids1'],context=None):
            vol1=vol*y.p1/100 or 0.00
            wgt1=wgt*y.p1/100 or 0.00
            r1_lines.write(cr,uid,y.id,{'v_tot1':v1,'w_tot1':w1,'vol1':vol1,'wgt1':wgt1},context=None)
        #END R1
        return True
    
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
        'view_w1':True,
        # 'r1': fields.date.context_today, TODO: copy for r2-r4
        }

purchase_order()

class purchase_order_schedule_r1(osv.Model):
    _name = 'purchase.order.schedule.r1'

    _columns={
        'name'      : fields.date("Date",required=True),
        'alias'     : fields.selection([('1','W1.1'),('2','W1.2'),('3','W1.3'),('4','W1.4'),('5','W1.5'),('6','W1.6')],"Name"),
        'po_id1'    : fields.many2one('purchase.order',"PO"),
        'fleet_id'  : fields.many2many('fleet.vehicle','r1_fleet_rel','r1','fleet_id',string="Vehicle"),
        'volume'    : fields.float('Capacity (Volume)'),
        'tonase'    : fields.float('Capacity (Weight)'),
        'no_vehicle': fields.float('Vehicle Required'),
        'name1s'    : fields.char("Day"),
        'p1'        : fields.float('Percent',required=True),
        'vol1'      : fields.float('Volume'),
        'wgt1'      : fields.float('Weight'),
        'moq_m3'    : fields.selection([('cukup','Cukup'),('kurang','Kurang'),('lebih','Lebih')],"MOQ Bds Kubikasi"),
        'moq_kg'    : fields.selection([('cukup','Cukup'),('kurang','Kurang'),('lebih','Lebih')],"MOQ Bds Tonase"),
    }

    def onchange_fleet(self, cr, uid, ids, volume, fleet_id, tonase, context=None):      
        volume=0.00;tonase=0.00
        if fleet_id:
            for x in fleet_id[0][2]:
                volume+=self.pool.get('fleet.vehicle').browse(cr,uid,x).volume
                tonase+=self.pool.get('fleet.vehicle').browse(cr,uid,x).tonase
            return {'value':{'volume':volume,'tonase':tonase}}

    def onchange_name(self, cr, uid, ids, name, name1s, alias, sch_ids1, r1, r1e, context=None):
        if name:
            name1s = datetime.strptime(name, '%Y-%m-%d')
            name1s = name1s.strftime("%A")
            if r1:
                name = datetime.strptime(name, '%Y-%m-%d')
                r1   = datetime.strptime(r1, '%Y-%m-%d')
                if name < r1:
                    raise osv.except_osv(_('Error!'), _('Tanggal diluar range'))
            if r1e:
                r1e   = datetime.strptime(r1e, '%Y-%m-%d')
                if name > r1e:
                    raise osv.except_osv(_('Error!'), _('Tanggal diluar range'))
        return {'value':{'name1s':name1s, 'alias':str(len(sch_ids1)+1)}}

    def onchange_percent(self, cr, uid, ids, p1, alias, percent_r1, order_line, context=None):
        prod_volume=0;prod_weight=0;q11=0
        if order_line[0][1]:
            lines = self.pool.get('purchase.order.line').browse(cr,uid,[x[1] for x in order_line],)
            for line in lines:
                prod_volume += line.prod_volume*p1/100
                prod_weight += line.prod_weight*p1/100
        if not order_line[0][1]:
            for x in order_line:
                prod_volume += x[2]['prod_volume']*p1/100
                prod_weight += x[2]['prod_weight']*p1/100
        return {'value':{
                'vol1':prod_volume,
                'wgt1':prod_weight,}}

    # def act_upd(self, cr, uid, ids, context=None):
    #     data = self.read(cr,uid,ids[0],)
    #     prod_line1=[];vtot=0.00;wtot=0.00
    #     for x in self.pool.get("purchase.order").browse(cr,uid,data['po_id1'][0]).order_line: 
    #         if x.qty_left > 0.00:
    #             pr=x.product_id.id
    #             wp=x.product_id.weight or 0.00
    #             vp=x.product_id.volume or 0.00
    #             factor = 1/x.product_id.uom_po_id.factor or 1
    #             qtyprd=x.qty_left*data['p1']/100 or 0.00
    #             vp1=qtyprd*factor*vp or 0.00
    #             wp1=qtyprd*factor*wp or 0.00
    #             prod_line1.append([0,0,{'product_id': pr or False, 
    #                 'vol':vp1,
    #                 'wgt':wp1,
    #                 'qty':qtyprd,}])  
    #             self.pool.get("purchase.order.line").write(cr,uid,x.id,{'qty_left':0.00})
    #     return self.write(cr,uid,ids,{'sch1_detail':prod_line1})

purchase_order_schedule_r1()

class purchase_order_schedule_r2(osv.Model):
    _name = 'purchase.order.schedule.r2'

    _columns={
        'po_id2'    : fields.many2one('purchase.order',"PO"),
        'name'     : fields.date("Date"),
        'name2s'    : fields.char("Day",readonly=True),
        'p2'        : fields.float('Q'),
        'vol2'      : fields.float('Volume'),
        'wgt2'      : fields.float('Weight'),
        'v_tot2'    : fields.float('Total Volume'),
        'w_tot2'    : fields.float('Total Weight'), 
    }    

    def onchange_percent(self, cr, uid, ids, v_tot2 ,w_tot2, p2, vol2, wgt2, context=None):
        if context is None:
            context = {}
        vol_tot = p2*v_tot2/100 or 0.00
        wgt_tot = p2*w_tot2/100 or 0.00
        return {'value':{
                'vol2':vol_tot,
                'wgt2':wgt_tot,}} 

purchase_order_schedule_r2()

class purchase_order_schedule_r3(osv.Model):
    _name = 'purchase.order.schedule.r3'

    _columns={
        'po_id3'    : fields.many2one('purchase.order',"PO"),
        'name'     : fields.date("Date"),
        'name3s'     : fields.char("Day",readonly=True),
        'p3'        : fields.float('Q'),
        'vol3'      : fields.float('Volume'),
        'wgt3'      : fields.float('Weight'),
        'v_tot3'    : fields.float('Total Volume'),
        'w_tot3'    : fields.float('Total Weight'), 
    }
   
    def onchange_percent(self, cr, uid, ids, v_tot3 ,w_tot3, p3, vol3, wgt3, context=None):
        if context is None:
            context = {}
        vol_tot = p3*v_tot3/100 or 0.00
        wgt_tot = p3*w_tot3/100 or 0.00
        return {'value':{
                'vol3':vol_tot,
                'wgt3':wgt_tot,}} 

purchase_order_schedule_r3()

class purchase_order_schedule_r4(osv.Model):
    _name = 'purchase.order.schedule.r4'

    _columns={
        'po_id4'    : fields.many2one('purchase.order',"PO"),
        'names'     : fields.date("Date"),
        'name4s'    : fields.char("Day",readonly=True),
        'p4'        : fields.float('Q'),
        'vol4'      : fields.float('Volume'),
        'wgt4'      : fields.float('Weight'),
        'v_tot4'    : fields.float('Total Volume'),
        'w_tot4'    : fields.float('Total Weight'), 
    }

    def onchange_percent(self, cr, uid, ids, v_tot4 ,w_tot4, p4, vol4, wgt4, context=None):
        if context is None:
            context = {}
        vol_tot = p4*v_tot4/100 or 0.00
        wgt_tot = p4*w_tot4/100 or 0.00
        return {'value':{
                'vol4':vol_tot,
                'wgt4':wgt_tot,}} 

purchase_order_schedule_r4()

# class po_schedule_r1_detail(osv.Model):
#     _name = 'po.schedule.r1.detail'

#     _columns={
#         'product_id' : fields.many2one('product.product',"Product"),#,domain="[('id','in',order_line[0][2].product_id)]"
#         'vol'       : fields.float('Volume'),
#         'wgt'       : fields.float('Weight'),
#         'qty'       : fields.float('Qty'),
#         'r_id'      : fields.many2one('purchase.order.schedule.r1','Schedule'),
#     }
    
#     def onchange_qty(self, cr, uid, ids, qty, product_id, context=None):
#         data = self.read(cr,uid,ids[0],)
#         r_id = data['r_id'][0]
#         q0=data['qty']
#         order_lines = self.pool.get('purchase.order.schedule.r1').browse(cr,uid,r_id,).po_id1.order_line
#         for x in order_lines:
#             if x.product_id.id == product_id:
#                 qty1=q0-qty
#                 if qty1>0.00:
#                     self.pool.get("purchase.order.line").write(cr,uid,x.id,{'qty_left':qty1},context=None)
#         return True

# po_schedule_r1_detail()