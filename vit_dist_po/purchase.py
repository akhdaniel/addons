from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
from datetime import timedelta, date, datetime
from lxml import etree

class purchase_order_line(osv.osv):
    _name       = 'purchase.order.line'
    _inherit    = 'purchase.order.line'
    _order      = 'stock_current'

    def _determin_w(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines: 
            result[line.id] = { 'w1' : line.product_qty * line.order_id.percent_r1/100 or 0,
                                'w2' : line.product_qty * line.order_id.percent_r2/100 or 0,
                                'w3' : line.product_qty * line.order_id.percent_r3/100 or 0,
                                'w4' : line.product_qty * line.order_id.percent_r4/100 or 0,}
        return result    

    def _get_aliasw1(self,line,fields):
        pxi={}
        for x in line.order_id.sch_ids1:
            pxi.update({x.alias : x.p1/100.00})
        return pxi

    def _get_aliasw2(self,line,fields):
        pxj={}
        for x2 in line.order_id.sch_ids2:
            pxj.update({x2.alias2 : x2.p2/100.00})
        return pxj

    def _get_aliasw3(self,line,fields):
        pxk={}
        for x3 in line.order_id.sch_ids3:
            pxk.update({x3.alias3 : x3.p3/100.00})
        return pxk

    def _get_aliasw4(self,line,fields):
        pxl={}
        for x4 in line.order_id.sch_ids4:
            pxl.update({x4.alias4 : x4.p4/100.00})
        return pxl

    def _determin_qw1(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        px={}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines:
            px[line.id] = self._get_aliasw1(line,field_names)
            result[line.id] = { 'w11' : 'nol' in px[line.id] and px[line.id]['nol'] * line.product_qty or 0,
                                'w12' : '1' in px[line.id] and px[line.id]['1'] * line.product_qty or 0,
                                'w13' : '2' in px[line.id] and px[line.id]['2'] * line.product_qty or 0,
                                'w14' : '3' in px[line.id] and px[line.id]['3'] * line.product_qty or 0,
                                'w15' : '4' in px[line.id] and px[line.id]['4'] * line.product_qty or 0,
                                'w16' : '5' in px[line.id] and px[line.id]['5'] * line.product_qty or 0,}
        return result

    def _determin_qw2(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        p2={}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines:
            p2[line.id] = self._get_aliasw2(line,field_names)
            result[line.id] = { 'w21' : 'nol' in p2[line.id] and p2[line.id]['nol'] * line.product_qty or 0,
                                'w22' : '1' in p2[line.id] and p2[line.id]['1'] * line.product_qty or 0,
                                'w23' : '2' in p2[line.id] and p2[line.id]['2'] * line.product_qty or 0,
                                'w24' : '3' in p2[line.id] and p2[line.id]['3'] * line.product_qty or 0,
                                'w25' : '4' in p2[line.id] and p2[line.id]['4'] * line.product_qty or 0,
                                'w26' : '5' in p2[line.id] and p2[line.id]['5'] * line.product_qty or 0,}
        return result

    def _determin_qw3(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        p3={}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines:
            p3[line.id] = self._get_aliasw3(line,field_names)
            result[line.id] = { 'w31' : 'nol' in p3[line.id] and p3[line.id]['nol'] * line.product_qty or 0,
                                'w32' : '1' in p3[line.id] and p3[line.id]['1'] * line.product_qty or 0,
                                'w33' : '2' in p3[line.id] and p3[line.id]['2'] * line.product_qty or 0,
                                'w34' : '3' in p3[line.id] and p3[line.id]['3'] * line.product_qty or 0,
                                'w35' : '4' in p3[line.id] and p3[line.id]['4'] * line.product_qty or 0,
                                'w36' : '5' in p3[line.id] and p3[line.id]['5'] * line.product_qty or 0,}
        return result

    def _determin_qw4(self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        p4={}
        lines = self.browse(cr, uid, ids, context=context)
        for line in lines:
            p4[line.id] = self._get_aliasw4(line,field_names)
            result[line.id] = { 'w41' : 'nol' in p4[line.id] and p4[line.id]['nol'] * line.product_qty or 0,
                                'w42' : '1' in p4[line.id] and p4[line.id]['1'] * line.product_qty or 0,
                                'w43' : '2' in p4[line.id] and p4[line.id]['2'] * line.product_qty or 0,
                                'w44' : '3' in p4[line.id] and p4[line.id]['3'] * line.product_qty or 0,
                                'w45' : '4' in p4[line.id] and p4[line.id]['4'] * line.product_qty or 0,
                                'w46' : '5' in p4[line.id] and p4[line.id]['5'] * line.product_qty or 0,}
        return result

    _columns = {
        'suggested_order'   : fields.float('Suggested Order', digits_compute=dp.get_precision('Product Unit of Measure')),
        'adjustment'        : fields.float('Adjustment', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'prod_weight'       : fields.float('Weight'),
        'prod_volume'       : fields.float('Volume'),
        'avgMT'             : fields.float('Avg MT', readonly=True),
        'avgGT'             : fields.float('Avg GT', readonly=True),
        'bufMT'             : fields.float('Buffer MT', readonly=True),
        'bufGT'             : fields.float('Buffer GT', readonly=True),
        'barcode'           : fields.char('Barcode'),
        'int_code'          : fields.char('Internal Reference'),
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
        'w1'                : fields.function(_determin_w,type='float',string='W1',store=False,multi='wx'),
        'w2'                : fields.function(_determin_w,type='float',string='W2',store=False,multi='wx'),
        'w3'                : fields.function(_determin_w,type='float',string='W3',store=False,multi='wx'),
        'w4'                : fields.function(_determin_w,type='float',string='W4',store=False,multi='wx'),
        'w11'               : fields.function(_determin_qw1,type='float',string='W1.1',store=False,multi='qwx'),
        'w12'               : fields.function(_determin_qw1,type='float',string='W1.2',store=False,multi='qwx'),
        'w13'               : fields.function(_determin_qw1,type='float',string='W1.3',store=False,multi='qwx'),
        'w14'               : fields.function(_determin_qw1,type='float',string='W1.4',store=False,multi='qwx'),
        'w15'               : fields.function(_determin_qw1,type='float',string='W1.5',store=False,multi='qwx'),
        'w16'               : fields.function(_determin_qw1,type='float',string='W1.6',store=False,multi='qwx'),
        'w21'               : fields.function(_determin_qw2,type='float',string='W2.1',store=False,multi='qwy'),
        'w22'               : fields.function(_determin_qw2,type='float',string='W2.2',store=False,multi='qwy'),
        'w23'               : fields.function(_determin_qw2,type='float',string='W2.3',store=False,multi='qwy'),
        'w24'               : fields.function(_determin_qw2,type='float',string='W2.4',store=False,multi='qwy'),
        'w25'               : fields.function(_determin_qw2,type='float',string='W2.5',store=False,multi='qwy'),
        'w26'               : fields.function(_determin_qw2,type='float',string='W2.6',store=False,multi='qwy'),
        'w31'               : fields.function(_determin_qw3,type='float',string='W3.1',store=False,multi='qwz'),
        'w32'               : fields.function(_determin_qw3,type='float',string='W3.2',store=False,multi='qwz'),
        'w33'               : fields.function(_determin_qw3,type='float',string='W3.3',store=False,multi='qwz'),
        'w34'               : fields.function(_determin_qw3,type='float',string='W3.4',store=False,multi='qwz'),
        'w35'               : fields.function(_determin_qw3,type='float',string='W3.5',store=False,multi='qwz'),
        'w36'               : fields.function(_determin_qw3,type='float',string='W3.6',store=False,multi='qwz'),
        'w41'               : fields.function(_determin_qw4,type='float',string='W4.1',store=False,multi='qwo'),
        'w42'               : fields.function(_determin_qw4,type='float',string='W4.2',store=False,multi='qwo'),
        'w43'               : fields.function(_determin_qw4,type='float',string='W4.3',store=False,multi='qwo'),
        'w44'               : fields.function(_determin_qw4,type='float',string='W4.4',store=False,multi='qwo'),
        'w45'               : fields.function(_determin_qw4,type='float',string='W4.5',store=False,multi='qwo'),
        'w46'               : fields.function(_determin_qw4,type='float',string='W4.6',store=False,multi='qwo'),
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
        prd             = self.pool.get('product.product').browse(cr,uid,product_id,)
        prod_vol        = prd.volume
        prod_wgt        = prd.weight
        factor          = self.pool.get('product.uom').browse(cr,uid,product_uom,).factor
        ratio           = 1/factor
        wgt_tot         = prod_wgt * qty * ratio 
        vol_tot         = prod_vol * qty * ratio 
        # ps              = qty * price_unit
        end_inv         = qty + stock_current + in_transit - sales_3m
        if sales_3m > 0.00 and end_inv > 0.00 : 
            stk_cover   = end_inv / sales_3m * 4
        # price_unit      = prd.product_tmpl_id.standard_price
        return {'value':{
                        'product_qty'       : round(qty) or 0.00,
                        # 'price_subtotal'    : ps or 0.00, 
                        'ending_inv'        : end_inv or 0.00, 
                        'stock_cover'       : stk_cover,
                        'prod_weight'       : wgt_tot or 0.00,
                        'prod_volume'       : vol_tot or 0.00,
                        'suggested_order'   : round(suggested_order),
                        # 'price_unit'        : price_unit or 0.00,
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
        'r1'             : fields.date('From'),
        'r2'             : fields.date('From'),
        'r3'             : fields.date('From'),
        'r4'             : fields.date('From'),
        'r1e'            : fields.date('To'),
        'r2e'            : fields.date('To'),
        'r3e'            : fields.date('To'),
        'r4e'            : fields.date('To'),
        'percent_r1'     : fields.float('Percent'),
        'percent_r2'     : fields.float('Percent'),
        'percent_r3'     : fields.float('Percent'),
        'percent_r4'     : fields.float('Percent'),
        'volume_r1'      : fields.float('Volume'),
        'volume_r2'      : fields.float('Volume'),
        'volume_r3'      : fields.float('Volume'),
        'volume_r4'      : fields.float('Volume'),
        'weight_r1'      : fields.float('Weight'),
        'weight_r2'      : fields.float('Weight'),
        'weight_r3'      : fields.float('Weight'),
        'weight_r4'      : fields.float('Weight'),
        'qr1'            : fields.integer("Qty"),
        'qr2'            : fields.integer("Qty"),
        'qr3'            : fields.integer("Qty"),
        'qr4'            : fields.integer("Qty"),
        'fleet_id'       : fields.many2one('fleet.vehicle',"Vehicle"),
        'no_vehicle'     : fields.float('Total Truck'),
        'no_vehicle2'    : fields.float('Total Truck'),
        'no_vehicle3'    : fields.float('Total Truck'),
        'no_vehicle4'    : fields.float('Total Truck'),
        'volume_tot'     : fields.float('Total Volume'),
        'weight_tot'     : fields.float('Total Weight'),
        'effective_day'  : fields.integer('Effective Day'),
        'days_cover'     : fields.integer('Days Cover'),
        'location_ids'   : fields.many2many('stock.location','stock_loc_po_rel','po_id','location_id','Related Location'),
        'principal_ids'  : fields.many2many('res.partner','res_partner_po_rel','po_id','user_id',"User's Principal"),
        'loc_x'          : fields.many2one('stock.location',"Destination",domain="[('id','in',location_ids[0][2])]",limit=2,required=True),
        'partner_x'      : fields.many2one('res.partner',"Supplier",domain="[('id','in',principal_ids[0][2])]",required=True),
        'sch_ids1'       : fields.one2many('purchase.order.schedule.r1','po_id1',"R1"), 
        'sch_ids2'       : fields.one2many('purchase.order.schedule.r2','po_id2',"R2"), 
        'sch_ids3'       : fields.one2many('purchase.order.schedule.r3','po_id3',"R3"), 
        'sch_ids4'       : fields.one2many('purchase.order.schedule.r4','po_id4',"R4"), 
        'periode'        : fields.char('Periode'),
        'view_w1'        : fields.boolean('Show/hide'),
        'view_w2'        : fields.boolean('Show/hide'),
        'view_w3'        : fields.boolean('Show/hide'),
        'view_w4'        : fields.boolean('Show/hide'),
        # 'columns_exixst1': fields.char("c.exixt"),
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
        sumw2=0;sumv2=[]
        sumw3=0;sumv3=[]
        sumw4=0;sumv4=[]
        if vals['sch_ids1']:
            for y in vals['sch_ids1']: sumw += y[2]['p1']
            for x in vals['sch_ids1']: sumv += x[2]['fleet_id'][0][2]
        if vals['sch_ids2']:
            for y in vals['sch_ids2']: sumw2 += y[2]['p2']
            for x in vals['sch_ids2']: sumv2 += x[2]['fleet_id2'][0][2]
        if vals['sch_ids2']:
            for y in vals['sch_ids3']: sumw3 += y[2]['p3']
            for x in vals['sch_ids3']: sumv3 += x[2]['fleet_id3'][0][2]
        if vals['sch_ids2']:
            for y in vals['sch_ids4']: sumw4 += y[2]['p4']
            for x in vals['sch_ids4']: sumv4 += x[2]['fleet_id4'][0][2]
        vals['no_vehicle']  = len(sumv)
        vals['no_vehicle2'] = len(sumv2)
        vals['no_vehicle3'] = len(sumv3)
        vals['no_vehicle4'] = len(sumv4)
        if sumw != vals['percent_r1']:
            raise osv.except_osv(_('Error W1!'), _('Jumlah persentase breakdown tidak sama dengan persentase per minggu'))
        if sumw2 != vals['percent_r2']:
            raise osv.except_osv(_('Error W2!'), _('Jumlah persentase breakdown tidak sama dengan persentase per minggu'))
        if sumw3 != vals['percent_r3']:
            raise osv.except_osv(_('Error W3!'), _('Jumlah persentase breakdown tidak sama dengan persentase per minggu'))
        if sumw4 != vals['percent_r4']:
            raise osv.except_osv(_('Error W4!'), _('Jumlah persentase breakdown tidak sama dengan persentase per minggu'))
        return super(purchase_order, self).create(cr, uid, vals, context=context)    

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        return {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            'product_uos_qty': order_line.product_qty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'move_dest_id': order_line.move_dest_id.id,
            'state': 'draft',
            'type':'in',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': order_line.price_unit
        }

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

            ''' 
            Range tanggal pertama 3 bln lalu s/d tgl terakhir bulan lalu
            (date_trunc('MONTH',CURRENT_DATE) - INTERVAL '1 day')::date as lastday_lastmounth,
            (date_trunc('MONTH',CURRENT_DATE) - INTERVAL '3 MONTH')::date as firstday_last3mounth
            '''
            cr.execute('SELECT SUM(il.quantity3) '\
                'FROM account_invoice ai '\
                'JOIN res_partner rp on ai.partner_id=rp.id '\
                'JOIN res_partner_res_partner_category_rel m2m on m2m.partner_id = rp.id   '\
                'JOIN res_partner_category rpc on m2m.category_id = rpc.id  '\
                'JOIN account_invoice_line il on ai.id=il.invoice_id  '\
                'JOIN product_uom uom on il.uos_id = uom.id  '\
                'JOIN product_uom_categ puc on puc.id=uom.category_id   '\
                'WHERE state = \'paid\'  '\
                'AND il.product_id = ' +str(prd.id)+ 
                ' AND ai.date_invoice BETWEEN (date_trunc(\'MONTH\',CURRENT_DATE) - INTERVAL \'3 MONTH\')::date '\
                ' AND (date_trunc(\'MONTH\',CURRENT_DATE) - INTERVAL \'1 day\')::date '\
                'AND rpc.name like \'%GT%\' '+clause )
            SOGT = cr.fetchone()
            if SOGT != (None,) : 
                GT = SOGT[0]/ratio
                if GT != 0 : 
                    BGT = GT/2 
            
            cr.execute('SELECT SUM(il.quantity3) '\
                'FROM account_invoice ai '\
                'JOIN res_partner rp on ai.partner_id=rp.id '\
                'JOIN res_partner_res_partner_category_rel m2m on m2m.partner_id = rp.id   '\
                'JOIN res_partner_category rpc on m2m.category_id = rpc.id  '\
                'JOIN account_invoice_line il on ai.id=il.invoice_id  '\
                'JOIN product_uom uom on il.uos_id = uom.id  '\
                'JOIN product_uom_categ puc on puc.id=uom.category_id   '\
                'WHERE state = \'paid\'  '\
                'AND il.product_id = ' +str(prd.id)+ 
                ' AND ai.date_invoice BETWEEN (date_trunc(\'MONTH\',CURRENT_DATE) - INTERVAL \'3 MONTH\')::date '\
                ' AND (date_trunc(\'MONTH\',CURRENT_DATE) - INTERVAL \'1 day\')::date '\
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

            # price   = prd.product_tmpl_id.standard_price 
            tot_v   = tot_v+prd.volume
            tot_w   = tot_w+prd.weight

            #standard_price
            price = prd.price_get('standard_price', context=context)[prd.id] / prd.uom_po_id.factor

            order_lines.append([0,0,{'product_id': prd.id or False, 
                'name'          : prd.name or '',
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
            'order_line'        : sorted(order_lines, key=lambda sku_order: sku_order[2]['stock_current'], reverse=False),
            'pricelist_id'      : supplier.property_product_pricelist_purchase.id or False,
            'fiscal_position'   : supplier.property_account_position and supplier.property_account_position.id or False,
            'payment_term_id'   : supplier.property_supplier_payment_term.id or False,
            'partner_code'      : supplier.code,
            'partner_id'        : partner_x,
            # 'volume_tot'      : tot_v,
            # 'weight_tot'      : tot_w,
            }}

    def onchange_rx(self, cr, uid, ids, p_rx, fname, p_r1, p_r2, p_r3, p_r4, 
            sch_ids, order_line, qrx, v_rx, w_rx, context=None):
        # if context is None:
        #     context = {}
        ptot = p_r1+p_r2+p_r3+p_r4
        if ptot>100:
            raise osv.except_osv(_('Error!'), _('Persentase lebih dari 100!'))       
        # if not r1:
        #     raise osv.except_osv(_('Warning!'), _('Isi R1!'))\
        if order_line[0][1] == False:
            sumqty=0;volr=0;wgtr=0
            for x in order_line: 
                sumqty += x[2]['product_qty']
                wgtr += x[2]['prod_weight']
                volr += x[2]['prod_volume']
        if ids != []:
            sumqty=0;volr=0;wgtr=0
            for x in self.pool.get('purchase.order.line').browse(cr,uid,[x[1] for x in order_line],): 
                sumqty += x.product_qty
                volr += x.prod_volume
                wgtr += x.prod_weight
        # Fix bug for replace ids
        # toremove = self.pool.get('purchase.order.schedule.r1').search(cr,uid,[('id','in',[x[1] for x in sch_ids1])],)
        # self.pool.get('purchase.order.schedule.r1').unlink(cr,uid,toremove,)
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
                # 'qr1'       : p_rx/100.00*sumqty or 0,
                # 'sch_ids1'  : sch_ids1,
                'volume_r1' : p_rx/100.00*volr or 0,
                'weight_r1' : p_rx/100.00*wgtr or 0,}}
        if fname == '2':
            return {'value':{
                'volume_r2':p_rx/100.00*volr or 0,
                'weight_r2':p_rx/100.00*wgtr or 0,}}
        if fname == '3':
            return {'value':{
                'volume_r3':p_rx/100.00*volr or 0,
                'weight_r3':p_rx/100.00*wgtr or 0,}}
        if fname == '4':
            return {'value':{
                'volume_r4':p_rx/100.00*volr or 0,
                'weight_r4':p_rx/100.00*wgtr or 0,}}

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

    # import pdb;pdb.set_trace()
    #TODO: implement messages system
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            valw1=0;valw2=0;valw3=0;valw4=0;
            if po.sch_ids1:
                for pw1 in po.sch_ids1: valw1 += pw1.p1
            if po.sch_ids2:
                for pw2 in po.sch_ids2: valw2 += pw2.p2
            if po.sch_ids3:
                for pw3 in po.sch_ids3: valw3 += pw3.p3
            if po.sch_ids4:
                for pw4 in po.sch_ids4: valw4 += pw4.p4
            if valw1 != po.percent_r1:
                raise osv.except_osv(_('Error Week 1!'), _('Jumlah persentase breakdown harus sama dengan persentase per minggu'))
            if valw2 != po.percent_r2:
                raise osv.except_osv(_('Error Week 2!'), _('Jumlah persentase breakdown harus sama dengan persentase per minggu'))
            if valw3 != po.percent_r3:
                raise osv.except_osv(_('Error Week 3!'), _('Jumlah persentase breakdown harus sama dengan persentase per minggu'))
            if valw4 != po.percent_r4:
                raise osv.except_osv(_('Error Week 4!'), _('Jumlah persentase breakdown harus sama dengan persentase per minggu'))
            if po.percent_r1 + po.percent_r2 + po.percent_r3 + po.percent_r4 != 100:
                raise osv.except_osv(_('Total!'), _('Jumlah persentase harus sama dengan 100%'))

            if not po.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)

        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
        return True

    _defaults = {
        'location_ids':_get_default_loc,
        'principal_ids':_get_default_principal,
        'view_w1':True,
        'view_w2':True,
        'view_w3':True,
        'view_w4':True,
        # 'r1': fields.date.context_today, TODO: copy for r2-r4
        }

purchase_order()

class purchase_order_schedule_r1(osv.Model):
    _name = 'purchase.order.schedule.r1'

    _columns={
        'name'      : fields.date("Date",required=True),
        'alias'     : fields.selection([('nol','W1.1'),('1','W1.2'),('2','W1.3'),('3','W1.4'),('4','W1.5'),('5','W1.6')],"Name"),
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

    def onchange_name(self, cr, uid, ids, namex, namexs, aliasx, sch_idsx, rx, rxe, context=None):
        if namex:
            namexs = datetime.strptime(namex, '%Y-%m-%d')
            namexs = namexs.strftime("%A")
            if rx:
                namex = datetime.strptime(namex, '%Y-%m-%d')
                rx   = datetime.strptime(rx, '%Y-%m-%d')
                if namex < rx:
                    raise osv.except_osv(_('Error!'), _('Tanggal diluar range'))
            if rxe:
                rxe   = datetime.strptime(rxe, '%Y-%m-%d')
                if namex > rxe:
                    raise osv.except_osv(_('Error!'), _('Tanggal diluar range'))
            if sch_idsx == []:
                return {'value':{'name1s':namexs, 'alias':'nol'}}
            return {'value':{'name1s':namexs, 'alias':str(len(sch_idsx))}}

    def onchange_percent(self, cr, uid, ids, px, aliasx, percent_rx, order_line, context=None):
        prod_volume=0;prod_weight=0;q11=0
        if order_line[0][1]:
            lines = self.pool.get('purchase.order.line').browse(cr,uid,[x[1] for x in order_line],)
            for line in lines:
                prod_volume += line.prod_volume*px/100
                prod_weight += line.prod_weight*px/100
        if not order_line[0][1]:
            for x in order_line:
                prod_volume += x[2]['prod_volume']*px/100
                prod_weight += x[2]['prod_weight']*px/100
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

    _defaults = {
    'alias' : 'nol',
    }

purchase_order_schedule_r1()

class purchase_order_schedule_r2(osv.Model):
    _name = 'purchase.order.schedule.r2'

    _columns={
        'name2'      : fields.date("Date",required=True),
        'alias2'     : fields.selection([('nol','W2.1'),('1','W2.2'),('2','W2.3'),('3','W2.4'),('4','W2.5'),('5','W2.6')],"Name"),
        'po_id2'    : fields.many2one('purchase.order',"PO"),
        'fleet_id2'  : fields.many2many('fleet.vehicle','r2_fleet_rel','r2','fleet_id',string="Vehicle"),
        'volume2'    : fields.float('Capacity (Volume)'),
        'tonase2'    : fields.float('Capacity (Weight)'),
        'no_vehicle2': fields.float('Vehicle Required'),
        'name2s'    : fields.char("Day"),
        'p2'        : fields.float('Percent'),
        'vol2'      : fields.float('Volume'),
        'wgt2'      : fields.float('Weight'),
        'moq_m32'    : fields.selection([('cukup','Cukup'),('kurang','Kurang'),('lebih','Lebih')],"MOQ Bds Kubikasi"),
        'moq_kg2'    : fields.selection([('cukup','Cukup'),('kurang','Kurang'),('lebih','Lebih')],"MOQ Bds Tonase"),
    }     

    def onchange_name(self, cr, uid, ids, name2, name2s, alias2, sch_ids2, r2, r2e, context=None):
        value = self.pool.get('purchase.order.schedule.r1').onchange_name(cr, uid, ids, name2, name2s, alias2, sch_ids2, r2, r2e, context=None)
        return {'value':{
                'name2s':value['value']['name1s'], 
                'alias2':value['value']['alias'],}}

    def onchange_percent(self, cr, uid, ids, p2, alias2, percent_r2, order_line, context=None):
        value = self.pool.get('purchase.order.schedule.r1').onchange_percent(cr, uid, ids, p2, alias2, percent_r2, order_line, context=None)
        return {'value':{
                'vol2':value['value']['vol1'],
                'wgt2':value['value']['wgt1'],}}

    def onchange_fleet(self, cr, uid, ids, volume2, fleet_id2, tonase2, context=None): 
        value = self.pool.get('purchase.order.schedule.r1').onchange_fleet(cr, uid, ids, volume2, fleet_id2, tonase2, context=None)
        return {'value':{
                'volume2':value['value']['volume'],
                'tonase2':value['value']['tonase'],}}

purchase_order_schedule_r2()

class purchase_order_schedule_r3(osv.Model):
    _name = 'purchase.order.schedule.r3'

    _columns={
        'name3'      : fields.date("Date",required=True),
        'alias3'     : fields.selection([('nol','W3.1'),('1','W3.2'),('2','W3.3'),('3','W3.4'),('4','W3.5'),('5','W3.6')],"Name"),
        'po_id3'    : fields.many2one('purchase.order',"PO"),
        'fleet_id3'  : fields.many2many('fleet.vehicle','r3_fleet_rel','r3','fleet_id',string="Vehicle"),
        'volume3'    : fields.float('Capacity (Volume)'),
        'tonase3'    : fields.float('Capacity (Weight)'),
        'no_vehicle3': fields.float('Vehicle Required'),
        'name3s'    : fields.char("Day"),
        'p3'        : fields.float('Percent'),
        'vol3'      : fields.float('Volume'),
        'wgt3'      : fields.float('Weight'),
        'moq_m33'    : fields.selection([('cukup','Cukup'),('kurang','Kurang'),('lebih','Lebih')],"MOQ Bds Kubikasi"),
        'moq_kg3'    : fields.selection([('cukup','Cukup'),('kurang','Kurang'),('lebih','Lebih')],"MOQ Bds Tonase"),
    }     

    def onchange_name(self, cr, uid, ids, name3, name3s, alias3, sch_ids3, r3, r3e, context=None):
        value = self.pool.get('purchase.order.schedule.r1').onchange_name(cr, uid, ids, name3, name3s, alias3, sch_ids3, r3, r3e, context=None)
        return {'value':{
                'name3s':value['value']['name1s'], 
                'alias3':value['value']['alias'],}}

    def onchange_percent(self, cr, uid, ids, p3, alias3, percent_r3, order_line, context=None):
        value = self.pool.get('purchase.order.schedule.r1').onchange_percent(cr, uid, ids, p3, alias3, percent_r3, order_line, context=None)
        return {'value':{
                'vol3':value['value']['vol1'],
                'wgt3':value['value']['wgt1'],}}

    def onchange_fleet(self, cr, uid, ids, volume3, fleet_id3, tonase3, context=None): 
        value = self.pool.get('purchase.order.schedule.r1').onchange_fleet(cr, uid, ids, volume3, fleet_id3, tonase3, context=None)
        return {'value':{
                'volume3':value['value']['volume'],
                'tonase3':value['value']['tonase'],}}

purchase_order_schedule_r3()

class purchase_order_schedule_r4(osv.Model):
    _name = 'purchase.order.schedule.r4'

    _columns={
        'name4'      : fields.date("Date",required=True),
        'alias4'     : fields.selection([('nol','W4.1'),('1','W4.2'),('2','W4.3'),('3','W4.4'),('4','W4.5'),('5','W4.6')],"Name"),
        'po_id4'    : fields.many2one('purchase.order',"PO"),
        'fleet_id4'  : fields.many2many('fleet.vehicle','r4_fleet_rel','r4','fleet_id',string="Vehicle"),
        'volume4'    : fields.float('Capacity (Volume)'),
        'tonase4'    : fields.float('Capacity (Weight)'),
        'no_vehicle4': fields.float('Vehicle Required'),
        'name4s'    : fields.char("Day"),
        'p4'        : fields.float('Percent'),
        'vol4'      : fields.float('Volume'),
        'wgt4'      : fields.float('Weight'),
        'moq_m34'    : fields.selection([('cukup','Cukup'),('kurang','Kurang'),('lebih','Lebih')],"MOQ Bds Kubikasi"),
        'moq_kg4'    : fields.selection([('cukup','Cukup'),('kurang','Kurang'),('lebih','Lebih')],"MOQ Bds Tonase"),
    }     

    def onchange_name(self, cr, uid, ids, name4, name4s, alias4, sch_ids4, r4, r4e, context=None):
        value = self.pool.get('purchase.order.schedule.r1').onchange_name(cr, uid, ids, name4, name4s, alias4, sch_ids4, r4, r4e, context=None)
        return {'value':{
                'name4s':value['value']['name1s'], 
                'alias4':value['value']['alias'],}}

    def onchange_percent(self, cr, uid, ids, p4, alias4, percent_r4, order_line, context=None):
        value = self.pool.get('purchase.order.schedule.r1').onchange_percent(cr, uid, ids, p4, alias4, percent_r4, order_line, context=None)
        return {'value':{
                'vol4':value['value']['vol1'],
                'wgt4':value['value']['wgt1'],}}

    def onchange_fleet(self, cr, uid, ids, volume4, fleet_id4, tonase4, context=None): 
        value = self.pool.get('purchase.order.schedule.r1').onchange_fleet(cr, uid, ids, volume4, fleet_id4, tonase4, context=None)
        return {'value':{
                'volume4':value['value']['volume'],
                'tonase4':value['value']['tonase'],}}

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

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    def action_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Open the partial picking wizard"""
        import pdb;pdb.set_trace()
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': len(ids) and ids[0] or False
        })
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.partial.picking',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'nodestroy': True,
        }

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """
        if group:
            name = (picking.name or '') + '-' + move_line.name
        else:
            name = move_line.name
        origin = move_line.picking_id.name or ''
        if move_line.picking_id.origin:
            origin += ':' + move_line.picking_id.origin

        if invoice_vals['type'] in ('out_invoice', 'out_refund'):
            account_id = move_line.product_id.property_account_income.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_income_categ.id
        else:
            account_id = move_line.product_id.property_account_expense.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_expense_categ.id
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move_line.product_uos and move_line.product_uos.id or False
        if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
            uos_id = move_line.product_uom.id
        
        if invoice_vals['type'] == 'in_invoice':
            small_qty = move_line.product_uos_qty * (move_line.product_uos.factor or 1)
        
        return {
            'name': name,
            'origin': origin,
            'invoice_id': invoice_id,
            'uos_id': uos_id,
            'uom_id': move_line.product_id.product_tmpl_id.uom_id.id,
            'product_id': move_line.product_id.id,
            'account_id': account_id,
            'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
            'discount': self._get_discount_invoice(cr, uid, move_line),
            'quantity2': 0,#move_line.product_uos_qty or move_line.product_qty,
            'qty': move_line.product_uos_qty,
            'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
            'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
        }

    '''
    def _get_price_unit_invoice(self, cr, uid, move_line, type, context=None):
        """ Gets price unit for invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: The price unit for the move line
        """
        if context is None:
            context = {}

        if type in ('in_invoice', 'in_refund'):
            # Take the user company and pricetype
            context['currency_id'] = move_line.company_id.currency_id.id
            amount_unit = move_line.product_id.price_get('standard_price', context=context)[move_line.product_id.id]
            return amount_unit
        else:
            return move_line.product_id.list_price
    '''

stock_picking()