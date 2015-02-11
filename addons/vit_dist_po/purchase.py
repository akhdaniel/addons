import time
import re
# import math
# from lxml import etree
from openerp.osv import fields, osv, expression
from openerp import netsvc
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import timedelta, date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools.float_utils import float_compare


class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        def _name_get(d):
            return (d['id'], d.get('name',''))
        result = []
        for product in self.browse(cr, user, ids, context=context):
            mydict = {
                      'id': product.id,
                      'name': product.name,
                      }
            result.append(_name_get(mydict))
        return result

    def _get_cur_principal_id(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in ids:
            #get the id of the current function of the employee of identifier "i"
            sql_req= """
            SELECT ps.name AS principal_id
            FROM product_product pr
                LEFT JOIN product_supplierinfo ps ON pr.product_tmpl_id = ps.product_id
            WHERE 
                (pr.id = %d)
            """ % (i,)
            cr.execute(sql_req)
            sql_res = cr.dictfetchone()
            if sql_res: #The employee has one associated contract
                res[i] = sql_res['principal_id']
            else:
                # res[i] harus diset False dan bukan None karena XML:RPC
                # "tidak bisa support None kecuali allow_none di-enabled"
                res[i] = False
        return res

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            ids = []
            if operator in positive_operators:
                ids = self.search(cr, user, [('default_code',operator,name)]+ args, limit=limit, context=context)
                #search bds barcode
                if not ids:
                    ids = self.search(cr, user, [('barcode',operator,name)]+ args, limit=limit, context=context)
                    # ean13 = default field
                    # if not ids:
                    #     ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
            if not ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(cr, user, args + [('default_code',operator,name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
                ids = list(ids)
            elif not ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                ids = self.search(cr, user, args + ['&', ('default_code', operator, name), ('name', operator, name)], limit=limit, context=context)
            if not ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('default_code','=', res.group(2))] + args, limit=limit, context=context)
                #search bds external code
                # if not res:
                #     ids0 = []
                #     ext_kode = name.join('%%')
                #     sql_req = u'select product_id from product_supplierinfo where product_code ilike \''+ ext_kode + u'\' limit ' + str(limit)
                #     cr.execute(sql_req)
                #     cr_ids = cr.fetchall()
                #     if len(cr_ids) > 0:
                #         for x in cr_ids: ids0.append(x[0]) 
                #         ids = self.search(cr, user, [('id','in',ids0)]+ args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

    _columns = {
        'principal_id' : fields.function(
            _get_cur_principal_id,
            type='many2one',
            obj="res.partner",
            method=True,
            store=True,
            string='Default Principal'),
    }

product_product()


class purchase_order_schedule(osv.Model):
    _name = 'purchase.order.schedule'
    _rec_name = 'product_id'

    _columns={
        # 'name'              : fields.char("Nama Barang",readonly=True),
        'int_code'          : fields.char(_('Kode'),readonly=True),
        'barcode'           : fields.char("Barcode",readonly=True),
        'po_id'             : fields.many2one('purchase.order',"PO", ondelete='cascade'),
        'product_id'        : fields.many2one('product.product',string="Nama Barang", readonly=True, required=True, domain="[('principal_id','=',parent.partner_id),]"),
        # 'product_uom'       : fields.many2one('product.uom', readonly=True, string=_('Satuan')),
        'wtot'              : fields.float('Qty',readonly=True),
        'w1'                : fields.float('Q 01'),
        'w2'                : fields.float('Q 02'),
        'w3'                : fields.float('Q 03'),
        'w4'                : fields.float('Q 04'),
        'w5'                : fields.float('Q 05'),
        'w6'                : fields.float('Q 06'),
        'w7'                : fields.float('Q 07'),
        'w8'                : fields.float('Q 08'),
        'w9'                : fields.float('Q 09'),
        'w10'               : fields.float('Q 10'),
        'w11'               : fields.float('Q 11'),
        'w12'               : fields.float('Q 12'),
        'w13'               : fields.float('Q 13'),
        'w14'               : fields.float('Q 14'),
        'w15'               : fields.float('Q 15'),
        'w16'               : fields.float('Q 16'),
        'w17'               : fields.float('Q 17'),
        'w18'               : fields.float('Q 18'),
        'w19'               : fields.float('Q 19'),
        'w20'               : fields.float('Q 20'),
        # 'w21'               : fields.float('Q 21'),
        # 'w22'               : fields.float('Q 22'),
        # 'w23'               : fields.float('Q 23'),
        # 'w24'               : fields.float('Q 24'),
        # 'w25'               : fields.float('Q 25'),
        # 'w26'               : fields.float('Q 26'),
        # 'w27'               : fields.float('Q 27'),
        # 'w28'               : fields.float('Q 28'),
        # 'w29'               : fields.float('Q 29'),
        # 'w30'               : fields.float('Q 30'),
        # 'w31'               : fields.float('Q 31'),
        }

    def onchange_check_w(self, cr, uid, ids, Wn,wtot,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13,w14,w15,w16,w17,w18,w19,w20, context=None):
        Wn=Wn or ''
        wtot=wtot or 0.00;w1=w1 or 0.00;w2=w2 or 0.00;w3=w3 or 0.00;w4=w4 or 0.00;w5=w5 or 0.00;w6=w6 or 0.00;w7=w7 or 0.00;w8=w8 or 0.00;w9=w9 or 0.00;w10=w10 or 0.00;
        w11=w11 or 0.00;w12=w12 or 0.00;w13=w13 or 0.00;w14=w14 or 0.00;w15=w15 or 0.00;w16=w16 or 0.00;w17=w17 or 0.00;w18=w18 or 0.00;w19=w19 or 0.00;w20=w20 or 0.00;
        if wtot < w1+w2+w3+w4+w5+w6+w7+w8+w9+w10+w11+w12+w13+w14+w15+w16+w17+w18+w19+w20:
            EA = 'Error '+ str(Wn) +'!'
            EB = 'Value melebihi total quantity produk ('+str(wtot)+').'
            raise osv.except_osv(_('%s') % (EA), _('%s') % (EB))
        return {}

purchase_order_schedule()


class purchase_order_line(osv.osv):
    # def _amount_line(self, cr, uid, ids, prop, arg, context=None):
    #     res = {}
    #     cur_obj=self.pool.get('res.currency')
    #     tax_obj = self.pool.get('account.tax')
    #     konversi = 0.00
    #     qty = 0.00
    #     import pdb;pdb.set_trace()
    #     for line in self.browse(cr, uid, ids, context=context):
    #         konversi = 1/line.product_uom.factor or 1.00
    #         qty = line.product_qty2 / konversi
    #         print qty
    #         taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, qty, line.product_id, line.order_id.partner_id)
    #         cur = line.order_id.pricelist_id.currency_id
    #         res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
    #     return res

    _name       = 'purchase.order.line'
    _inherit    = 'purchase.order.line'
    _order      = 'stock_current'

    def _upd_readonly(self, cr, uid, ids, field_name, arg, context):
        res = {}
        value = {}
        suggested_order = 0.00
        product_qty     = 0.00
        ending_inv      = 0.00
        stock_cover     = 0.00
            
        if ids:    
            for i in self.browse(cr,uid,ids,):
                data = {}
                # hanya update jika po masih draft
                if i.state != 'draft' :
                    continue
                value = self.onchange_product_id(cr, uid, i.id, False, i.product_id.id, i.product_qty2, i.product_uom.id, uid, False, False, False, False, False, i.order_id.datestart, i.order_id.dateend, context)['value']
                # jika readonly dari value, jika tidak dari database
                suggested_order = (i.forecastMT + i.forecastGT + value['bufMT'] + value['bufGT'] - value['stock_current'] - value['in_transit']) 
                suggested_order = suggested_order > 0.00 and suggested_order or 0.00
                # <tes
                product_qty     = i.adjustment + suggested_order
                if (i.small_qty > 0.00) and i.small_uom :
                    product_qty = self._jumlah_qty_small_and_big(cr,uid,i.product_id.id, product_qty, i.product_uom.id, i.small_qty, i.small_uom.id, context=context)
                    
                product_qty     = product_qty > 0.00 and product_qty or 0.00
                print product_qty
                # tes>
                product_qty     = i.product_qty2 or 0.00
                ending_inv      = round(suggested_order + i.adjustment) + value['stock_current'] + value['in_transit'] - value['sales_3m']
                if round(value['sales_3m']) > 0.00 and ending_inv > 0.00 : 
                    stock_cover   = ending_inv / round(value['sales_3m']) * 4
                
                self.write(cr,uid,i.id,{
                    'int_code'      : value['int_code'] or '',
                    'barcode'       : value['barcode'] or '',
                    # 'product_uom'   : value['product_uom'], 
                    'sales_3m'      : value['sales_3m'],
                    'avgMT'         : value['avgMT'],
                    'avgGT'         : value['avgGT'],
                    'bufMT'         : value['bufMT'],
                    'bufGT'         : value['bufGT'],
                    'stock_current' : value['stock_current'],
                    'in_transit'    : value['in_transit'],
                    'suggested_order': suggested_order,
                    'product_qty'   : product_qty,
                    'ending_inv'    : ending_inv,
                    'stock_cover'   : stock_cover,
                    'date_planned'  : i.order_id.date_order,
                    })
                res[i.id]=True
        return res

    _columns = {
        'suggested_order'   : fields.float(_('Saran Order'), readonly=True, digits_compute=dp.get_precision('Product Price')),
        'adjustment'        : fields.float(_('Qty Besar'), digits_compute=dp.get_precision('Product Price')), 
        'avgMT'             : fields.float('AVG MT', readonly=True, digits_compute=dp.get_precision('Product Price')),
        'avgGT'             : fields.float('AVG GT', readonly=True, digits_compute=dp.get_precision('Product Price')),
        'bufMT'             : fields.float('Buffer MT', readonly=True, digits_compute=dp.get_precision('Product Price')),
        'bufGT'             : fields.float('Buffer GT', readonly=True, digits_compute=dp.get_precision('Product Price')),
        'sales_3m'          : fields.float(_('Total AVG'), digits_compute=dp.get_precision('Product Price')),
        'stock_current'     : fields.float('Stock Current', digits_compute=dp.get_precision('Product Price')),
        'in_transit'        : fields.float('In Transit', digits_compute=dp.get_precision('Product Price')),
        'ending_inv'        : fields.float(_('Est. Stock Akhir'), digits_compute=dp.get_precision('Product Price'), readonly=True),
        'stock_cover'       : fields.float('Cover Weeks', readonly=True, digits_compute=dp.get_precision('Product Price')),
        'forecastMT'        : fields.float('Forecast MT', digits_compute=dp.get_precision('Product Price')),
        'forecastGT'        : fields.float('Forecast GT', digits_compute=dp.get_precision('Product Price')),
        'date_planned'      : fields.date('Scheduled Date', required=False, select=True),
        'prod_weight'       : fields.float('Weight'),
        'prod_volume'       : fields.float('Volume'),
        'barcode'           : fields.char(_('Barcode')),
        'int_code'          : fields.char(_('Kode')),
        'product_qty2'      : fields.float(_("Qty Total")),
        'small_qty'         : fields.float(_("Qty Kecil")),
        'small_uom'         : fields.many2one('product.uom', _('Satuan Kecil')),
        'product_id'        : fields.many2one('product.product', 'Product', 
            domain="[('principal_id','=',parent.partner_id),('purchase_ok','=',True),('bonus','=',False),]", required=True, change_default=True),
        'update_readonly'   : fields.function(
            _upd_readonly, 
            type='boolean',
            method=True,
            store=False,
            string='update readonly fields'),          
        # 'qty2'              : fields.float('Qty2',readonly=True),
        # 'sales_3m2'         : fields.float(_('Total AVG'),readonly=True, digits_compute=dp.get_precision('Product Price')),
        # 'stock_current2'    : fields.float('Stock Current2',readonly=True),
        # 'ending_inv2'       : fields.float('Ending Inventory2',readonly=True),
        # 'in_transit2'       : fields.float('In Transit2',readonly=True),
        # 'stock_cover2'      : fields.float('Stock Cover2',readonly=True),
    }

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, datestart=False, dateend=False, context=None):
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}
        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        if not product_id:
            return res

        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        res_partner = self.pool.get('res.partner')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        product_pricelist = self.pool.get('product.pricelist')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')

        # - check for the presence of partner_id and pricelist_id
        #if not partner_id:
        #    raise osv.except_osv(_('No Partner!'), _('Select a partner in purchase order to choose a product.'))
        #if not pricelist_id:
        #    raise osv.except_osv(_('No Pricelist !'), _('Select a price list in the purchase order form before choosing a product.'))

        # - determine name and notes based on product in partner lang.
        context_partner = context.copy()
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update( {'lang': lang, 'partner_id': partner_id} )
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        #call name_get() with partner in the context to eventually match name and description in the seller_ids field
        dummy, name = product_product.name_get(cr, uid, product_id, context=context_partner)[0]
        if product.description_purchase:
            name += '\n' + product.description_purchase
        res['value'].update({'name': name})

        # - set a domain on product_uom
        res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}

        # UOM gg dicek karena diset > uom_po_id
        # Force set satuan awal 
        uom_id = product.uom_po_id.id
        # - check that uom and product uom belong to the same category
        # product_uom_po_id = product.uom_po_id.id
        # if not uom_id:
        #     uom_id = product_uom_po_id

        # if product.uom_id.category_id.id != product_uom.browse(cr, uid, uom_id, context=context).category_id.id:
        #     if context.get('purchase_uom_check') and self._check_product_uom_group(cr, uid, context=context):
        #         res['warning'] = {'title': _('Warning!'), 'message': _('Selected Unit of Measure does not belong to the same category as the product Unit of Measure.')}
        #     uom_id = product_uom_po_id

        # res['value'].update({'product_uom': uom_id})

        # - determine product_qty and date_planned based on seller info
        if not date_order:
            date_order = fields.date.context_today(self,cr,uid,context=context)
        res['value'].update({'product_uom': uom_id})

        supplierinfo = False
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Unit of Measure')
        for supplier in product.seller_ids:
            if partner_id and (supplier.name.id == partner_id):
                supplierinfo = supplier
                if supplierinfo.product_uom.id != uom_id:
                    res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier only sells this product by %s') % supplierinfo.product_uom.name }
                min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                if float_compare(min_qty , qty, precision_digits=precision) == 1: # If the supplier quantity is greater than entered from user, set minimal.
                    if qty:
                        res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier has a minimal quantity set to %s %s, you should not purchase less.') % (supplierinfo.min_qty, supplierinfo.product_uom.name)}
                    qty = min_qty
        dt = self._get_date_planned(cr, uid, supplierinfo, date_order, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        # qty = qty or 1.0 (Default)
        qty = qty or 0.0
        res['value'].update({'date_planned': date_planned or dt})
        if qty:
            res['value'].update({'product_qty': qty})

        # - determine price_unit and taxes_id
        # if pricelist_id:
        #     price = product_pricelist.price_get(cr, uid, [pricelist_id],
        #             product.id, qty or 1.0, partner_id or False, {'uom': uom_id, 'date': date_order})[pricelist_id]
        # else:
        #     price = product.standard_price

        # taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
        # fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        # taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
        # res['value'].update({'price_unit': price, 'taxes_id': taxes_ids})

        #Tambahan code, barcode, dsb
        location_ids = [];clause =' ';clause2 =' ';clause3 =' ';clause4 =' '
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
        
        # only 1 product used
        MT= 0.00;GT=0.00;s3m=0.00
        BGT=0.00;BMT=0.00;sgt_order=0.00;adj=0.00;cs=0.00;it=0.00
        tot_w=0;tot_v=0;
        ratio=1/product.uom_po_id.factor or 1.00
        # Range tanggal pertama 3 bln lalu s/d tgl terakhir bulan lalu
        #   date_trunc('MONTH',CURRENT_DATE) - INTERVAL '1 day')::date   as endday_lastmounth,
        #   date_trunc('MONTH',CURRENT_DATE) - INTERVAL '3 MONTH')::date as firstday_last3mounth
        clause_startdate = ' AND ai.date_invoice BETWEEN (date_trunc(\'MONTH\',CURRENT_DATE) - INTERVAL \'3 MONTH\')::date '
        clause_enddate   = ' AND (date_trunc(\'MONTH\',CURRENT_DATE) - INTERVAL \'1 day\')::date '
        # if exist datestart and dateend
        if datestart and dateend:
            clause_startdate = " AND ai.date_invoice BETWEEN to_date(\'%s\',\'YYYY-MM-DD\')" % datestart
            clause_enddate   = " AND to_date(\'%s\',\'YYYY-MM-DD\')" % dateend

        cr.execute('SELECT SUM(il.quantity3) '\
            'FROM account_invoice ai '\
            'JOIN res_partner rp on ai.partner_id=rp.id '\
            'JOIN res_partner_res_partner_category_rel m2m on m2m.partner_id = rp.id   '\
            'JOIN res_partner_category rpc on m2m.category_id = rpc.id  '\
            'JOIN account_invoice_line il on ai.id=il.invoice_id  '\
            'JOIN product_uom uom on il.uos_id = uom.id  '\
            'JOIN product_uom_categ puc on puc.id=uom.category_id   '\
            'WHERE state = \'paid\' '\
            'AND il.product_id = ' +str(product.id)+ clause_startdate + clause_enddate +
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
            'AND il.product_id = ' +str(product.id) + clause_startdate + clause_enddate +
            'AND rpc.name like \'%MT%\' '+ clause )
        SOMT = cr.fetchone()
        if SOMT != (None,) : 
            MT = (SOMT[0]/ratio)
        s3m  = MT+GT

        cr.execute('SELECT COALESCE(masuk,0)-COALESCE(keluar,0) as qty, COALESCE(unit_qty1,0)-COALESCE(unit_qty2,0) as unit_qty,coalesce(id1,id2) as produk_id FROM ('\
            'SELECT SUM(product_qty) as masuk,product_id as id1,SUM(product_qty)/pu.factor as unit_qty1  FROM stock_move sm '\
            'JOIN product_uom pu ON pu.id=sm.product_uom '\
            'WHERE state = \'done\' and product_id= '+str(product.id)+clause2+
            'GROUP BY product_id,pu.factor) as A '\
            'FULL OUTER JOIN '\
            '(SELECT SUM(product_qty) as keluar,product_id as id2,SUM(product_qty)/pu.factor as unit_qty2 FROM stock_move sm '\
            'JOIN product_uom pu ON pu.id=sm.product_uom '\
            'WHERE state = \'done\' and product_id= '+str(product.id)+clause3+
            'GROUP BY product_id,pu.factor) as B on A.id1=B.id2')
        CS = cr.fetchone()
        cs = (CS and CS[1]) or 0
        cs = (cs/ratio)

        cr.execute('SELECT SUM(sm.product_qty) '\
            'FROM purchase_order po '\
            'JOIN stock_picking sp ON po.id=sp.purchase_id '\
            'JOIN stock_move sm ON sp.id=sm.picking_id '\
            'WHERE po.state=\'approved\' '+clause4+' AND sm.product_id = '+str(product.id)+
            'AND sp.state=\'assigned\' ')

        IT = cr.fetchone()
        it = (IT and IT[0]) or 0
        # it = (it/ratio) pembelian sudah dalam karton, jadi g dibagi ratio

        BMT=1*MT
        tot_bufer = BMT+BGT
        sgt_order = s3m+tot_bufer-cs-it

        tot_v   = tot_v+product.volume
        tot_w   = tot_w+product.weight

        # override standard_price
        # price = product.product_tmpl_id.standard_price 
        price = product.price_get('standard_price', context=context)[product.id] * ratio
        
        # end_inv & stk_cover
        stk_cover = 0.00
        end_inv         = cs + round(it) - round(s3m)
        if round(s3m) > 0.00 and end_inv > 0.00 : 
            stk_cover   = end_inv / round(s3m) * 4

        res['value'].update({
            'int_code'      : product.default_code or '',
            'barcode'       : product.barcode or '', #product.seller_ids[0].product_code or '',
            'product_qty'   : 0.00, 
            'product_qty2'   : 0.00, 
            'suggested_order' : 0.00,         
            'prod_weight'   : 0.00,
            'prod_volume'   : 0.00,
            # 'product_uom'   : product.uom_id.id, 
            'sales_3m'      : round(s3m),
            'avgMT'         : round(MT),
            'avgGT'         : round(GT),
            'bufMT'         : round(BMT),
            'bufGT'         : round(BGT),
            'price_unit'    : price, 
            'stock_current' : cs,      
            'ending_inv'    : end_inv,     
            'in_transit'    : round(it),    
            'stock_cover'   : stk_cover,
            })
        return res

    def onchange_line(self, cr, uid, ids, product_id, small_qty, small_uom, adjustment, suggested_order, product_uom, volume_tot, weight_tot,
        stock_current,in_transit,sales_3m,stock_cover,prod_weight,prod_volume,forecastMT,forecastGT, bufMT, bufGT, price_unit, 
        context=None):
        if context is None:
            context = {}
        res={'value':{}}
        stock_current   = stock_current or 0.00
        in_transit      = in_transit or 0.00
        sales_3m        = sales_3m or 0.00
        stk_cover       = stock_cover or 0.00
        forecastMT      = forecastMT or 0.00
        forecastGT      = forecastGT or 0.00
        bufMT           = bufMT or 0.00
        bufGT           = bufGT or 0.00
        adjustment      = adjustment or 0.00
        price           = price_unit or 0.00
        small_qty       = small_qty or 0.00
        small_uom       = small_uom or False
        # suggested_order = (forecastMT + forecastGT + bufMT + bufGT - stock_current - in_transit) or 0.00
        suggested_order = suggested_order or 0.00
        qty             = adjustment + suggested_order

        prd             = self.pool.get('product.product').browse(cr,uid,product_id,)
        prod_vol        = prd.volume
        prod_wgt        = prd.weight
        factor          = self.pool.get('product.uom').browse(cr,uid,product_uom,).factor
        ratio           = 1/factor
        wgt_tot         = prod_wgt * round(qty) * ratio 
        vol_tot         = prod_vol * round(qty) * ratio 
        # ps              = qty * price_unit
        end_inv         = qty + stock_current + in_transit - sales_3m
        if sales_3m > 0.00 and end_inv > 0.00 : 
            stk_cover   = end_inv / sales_3m * 4
        # price_unit      = prd.product_tmpl_id.standard_price

        if (small_qty>0.00) and small_uom:
            qty = self._jumlah_qty_small_and_big(cr,uid,product_id, qty, product_uom, small_qty, small_uom, context=context)
        
        res['value'].update({
                        # 'price_unit'        : price,
                        'product_qty'       : qty > 0 and round(qty) or 0.00,
                        'product_qty2'      : qty > 0 and round(qty) or 0.00,
                        # 'price_subtotal'    : ps or 0.00, 
                        'ending_inv'        : end_inv or 0.00, 
                        'stock_cover'       : stk_cover,
                        'prod_weight'       : qty > 0 and wgt_tot or 0.00,
                        'prod_volume'       : qty > 0 and vol_tot or 0.00,
                        'suggested_order'   : (suggested_order > 0) and round(suggested_order) or 0.00,
                        })
        return res

    def onchange_mtgt(self, cr, uid, ids, product_id, product_uom, small_qty, small_uom, stock_current, in_transit, 
        forecastMT, forecastGT, bufMT, bufGT, adjustment, sales_3m, stock_cover, price_unit, context=None):
        if forecastMT < 0 or forecastGT < 0 : 
            raise osv.except_osv(_('Error!'), _('Forecast MT or GT cannot less then 0.00'))
        res={'value':{}}
        stock_current   = float(stock_current) or 0.00
        in_transit      = float(in_transit) or 0.00
        forecastMT      = float(forecastMT) or 0.00
        forecastGT      = float(forecastGT) or 0.00
        bufMT           = float(bufMT) or 0.00
        bufGT           = float(bufGT) or 0.00
        adjustment      = float(adjustment) or 0.00
        sales_3m        = float(sales_3m) or 0.00
        stk_cover       = float(stock_cover) or 0.00
        price_u         = float(price_unit) or 0.00
        suggested_order = (forecastMT + forecastGT + bufMT + bufGT - stock_current - in_transit) or 0.00
        suggested_order = suggested_order > 0.00 and suggested_order
        end_inv         = round(suggested_order + adjustment) + stock_current + in_transit - sales_3m
        if sales_3m > 0.00 and end_inv > 0.00 : 
            stk_cover   = end_inv / sales_3m * 4
        
        if suggested_order < 0 :
            res['value'].update({
                        'suggested_order'   : 0.00, 
                        'product_qty'       : 0.00,  
                        'product_qty2'       : 0.00,                        
                        'prod_weight'       : 0.00,
                        'prod_volume'       : 0.00,
                        })
        prd             = self.pool.get('product.product').browse(cr,uid,product_id,)
        prod_vol        = prd.volume
        prod_wgt        = prd.weight
        factor          = self.pool.get('product.uom').browse(cr,uid,product_uom,).factor
        ratio           = 1/factor
        wgt_tot         = prod_wgt * suggested_order * ratio 
        vol_tot         = prod_vol * suggested_order * ratio 
        # price_unit      = prd.product_tmpl_id.standard_price
        # ps              = suggested_order * price_unit
        product_qty     = round(suggested_order + adjustment)
        if small_qty and small_uom:
            product_qty = self._jumlah_qty_small_and_big(cr,uid,product_id, product_qty, product_uom, small_qty, small_uom, context=context)
        res['value'].update({
                        'suggested_order'   : round(suggested_order), 
                        'product_qty'       : product_qty,
                        'product_qty2'       : product_qty,
                        'ending_inv'        : end_inv or 0.00, 
                        'stock_cover'       : stk_cover,
                        'prod_weight'       : suggested_order > 0 and wgt_tot or 0.00,
                        'prod_volume'       : suggested_order > 0 and vol_tot or 0.00,
                        })
        return res

    # def onchange_forecast(self, cr, uid, ids, forecastMT, forecastGT, suggested_order, bufMT, bufGT, stock_current, in_transit):
    #     return {'value':{
    #         'suggested_order':suggested_order,
    #         'product_qty': suggested_order, 
    #         }}

    def _jumlah_qty_small_and_big(self, cr, uid, product_id, product_qty, product_uom, small_qty, small_uom, context=None):
        uom_obj         = self.pool.get('product.uom')
        if uom_obj.browse(cr,uid,small_uom,).category_id.id <> uom_obj.browse(cr,uid,product_uom,).category_id.id:
            produk = 'Produk ' + str(self.pool.get('product.product').browse(cr,uid,i.product_id,).name_template or '') +'!'
            raise  osv.except_osv(_('%s') % (produk), _('Satuan kecil tidak sejenis dengan satuan besar'))
        small_uom_ratio = 1.00/(uom_obj.browse(cr,uid,small_uom,).factor or 1.00)
        big_uom_ratio   = 1.00/(uom_obj.browse(cr,uid,product_uom,).factor or 1.00)
        product_qty     += small_qty * small_uom_ratio / big_uom_ratio
        return product_qty

    def onchange_qty_kecil(self, cr, uid, ids, product_id, product_uom, small_qty, small_uom, 
        forecastMT,forecastGT, bufMT, bufGT, stock_current,in_transit, adjustment, context=None):
        if product_id:
            if not small_uom :
                small_uom = self.pool.get('product.product').browse(cr,uid,product_id,).uom_id.id
            forecastMT  =forecastMT or 0.00 
            forecastGT  =forecastGT  or 0.00
            bufMT       =bufMT  or 0.00
            bufGT       =bufGT  or 0.00
            stock_current=stock_current  or 0.00
            in_transit  =in_transit  or 0.00
            adjustment = adjustment  or 0.00
            
            suggested_order = (forecastMT + forecastGT + bufMT + bufGT - stock_current - in_transit) 
            suggested_order = suggested_order > 0.00 and suggested_order or 0.00
            product_qty     = adjustment + suggested_order

            product_qty = self._jumlah_qty_small_and_big(cr,uid,product_id, product_qty, product_uom, small_qty, small_uom, context=context)
            product_qty     = product_qty > 0.00 and product_qty or 0.00
            return {'value':{
                'small_uom' : small_uom,
                'product_qty':product_qty,
                'product_qty2': product_qty,}}

    _defaults = {
        'product_qty': lambda *a: 0.0,
        }

purchase_order_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _name = "purchase.order"

    # def onchange_schedule(self, cr, uid, ids,sch_ids,):
    #     import pdb;pdb.set_trace()
    #     for qty in sch_ids:
    #         for w in qty:
    #             w
    #     return 
                

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

    # def _period_get(self, cr, uid, context=None):
    #     return datetime.now().strftime("%b-%Y")

    _columns = {
        'notes'          : fields.text('Keterangan'),
        # 'r1'             : fields.date('Date'),
        # 'r2'             : fields.date('Date'),
        # 'r3'             : fields.date('Date'),
        # 'r4'             : fields.date('Date'),
        # 'r5'             : fields.date('Date'),
        # 'r1e'            : fields.date('To'),
        # 'r2e'            : fields.date('To'),
        # 'r3e'            : fields.date('To'),
        # 'r4e'            : fields.date('To'),
        # 'r5e'            : fields.date('To'),
        # 'percent_r1'     : fields.float('Contrib(%)'),
        # 'percent_r2'     : fields.float('Contrib(%)'),
        # 'percent_r3'     : fields.float('Contrib(%)'),
        # 'percent_r4'     : fields.float('Contrib(%)'),
        # 'percent_r5'     : fields.float('Contrib(%)'),
        # 'volume_r1'      : fields.float('Volume'),
        # 'volume_r2'      : fields.float('Volume'),
        # 'volume_r3'      : fields.float('Volume'),
        # 'volume_r4'      : fields.float('Volume'),
        # 'weight_r1'      : fields.float('Weight'),
        # 'weight_r2'      : fields.float('Weight'),
        # 'weight_r3'      : fields.float('Weight'),
        # 'weight_r4'      : fields.float('Weight'),
        # 'qr1'            : fields.integer("Qty"),
        # 'qr2'            : fields.integer("Qty"),
        # 'qr3'            : fields.integer("Qty"),
        # 'qr4'            : fields.integer("Qty"),
        # 'fleet_id'       : fields.many2one('fleet.vehicle',"Vehicle"),
        # 'no_vehicle'     : fields.float('Total Truck'),
        # 'no_vehicle2'    : fields.float('Total Truck'),
        # 'no_vehicle3'    : fields.float('Total Truck'),
        # 'no_vehicle4'    : fields.float('Total Truck'),
        'volume_tot'     : fields.float('Total Volume',help='Total volume in m3', readonly=True),
        'weight_tot'     : fields.float('Total Weight',help='Total weight in kg', readonly=True),
        # 'effective_day'  : fields.integer('Effective Day'),
        'days_cover'     : fields.integer('Days Cover'),
        'location_ids'   : fields.many2many('stock.location','stock_loc_po_rel','po_id','location_id','Related Location', readonly=True, states={'draft':[('readonly',False)]}, domain=[('usage','=','internal'),]),
        'principal_ids'  : fields.many2many('res.partner','res_partner_po_rel','po_id','user_id',"User's Principal", readonly=True, states={'draft':[('readonly',False)]}),
        'loc_x'          : fields.many2one('stock.location',"Cabang",domain="[('id','in',location_ids[0][2]),('usage','<>','view'),]",required=True, states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
        'loc_real'       : fields.many2one('stock.location',"Destination",domain="[('location_id','=',loc_x),('usage','<>','view'),('bad_location','=',False)]",required=True, states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
        'partner_x'      : fields.many2one('res.partner',"Supplier",domain="[('id','in',principal_ids[0][2])]",required=True, states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]},
            change_default=True, track_visibility='always',),
        # 'sch_ids1'       : fields.one2many('purchase.order.schedule.r1','po_id',"R1"), 
        # 'sch_ids2'       : fields.one2many('purchase.order.schedule.r2','po_id',"R2"), 
        # 'sch_ids3'       : fields.one2many('purchase.order.schedule.r3','po_id',"R3"), 
        # 'sch_ids4'       : fields.one2many('purchase.order.schedule.r4','po_id',"R4"), 
        # 'sch_ids5'       : fields.one2many('purchase.order.schedule.r5','po_id',"R5"), 
        # 'periode'        : fields.selection([('1','Jan'),('2','Feb'),('3','Mar'),('4','Apr'),('5','Mei'),('6','Jun'),
                                            # ('7','Jul'),('8','Aug'),('9','Sep'),('10','Oct'),('11','Nov'),('12','Dec')],"Periode"),
        'period_id'          : fields.many2one('account.period',"Periode",required=True,domain=[('special','=',False)], states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
        # 'th_periode'     : fields.char('Tahun', size=4, help="Tahun Periode"),
        # 'view_w1'        : fields.boolean('Show/hide'),
        # 'view_w2'        : fields.boolean('Show/hide'),
        # 'view_w3'        : fields.boolean('Show/hide'),
        # 'view_w4'        : fields.boolean('Show/hide'),
        # 'view_w5'        : fields.boolean('Show/hide'),
        # 'sch_ids1_detail': fields.one2many('purchase.order.schedule.r1.detail','po_id',"R1 Detail"),
        # 'sch_ids2_detail': fields.one2many('purchase.order.schedule.r2.detail','po_id',"R2 Detail"),
        # 'sch_ids3_detail': fields.one2many('purchase.order.schedule.r3.detail','po_id',"R3 Detail"),
        # 'sch_ids4_detail': fields.one2many('purchase.order.schedule.r4.detail','po_id',"R4 Detail"),
        # 'sch_ids5_detail': fields.one2many('purchase.order.schedule.r5.detail','po_id',"R5 Detail"),
        'datestart'             : fields.date('Date', readonly=True, states={'draft':[('readonly',False)]}),
        'dateend'            : fields.date('To', readonly=True, states={'draft':[('readonly',False)]}),
        # 'percent_r'      : fields.float('Contrib(%)'),
        # 'sch_ids_date'        : fields.one2many('purchase.order.date','po_id',"D"),
        # TODO: ini dipake buat report excel > 'sch_ids_cumul'  : fields.one2many('purchase.order.schedule.cumul','po_id',"Detail"),
        'sch_ids'        : fields.one2many('purchase.order.schedule','po_id',"Schedule Detail", readonly=True, states={'draft':[('readonly',False)]}),
        # 'order_lines_detail' : fields.one2many('purchase.order.line.detail','po_id',"Lines Detail"), 
        # "week_periode"  : fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5')],"Week of Month"),

        'w1'                : fields.date('Tanggal', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet1'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika1"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase1"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w2'                : fields.date('Q2', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet2'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika2"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase2"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w3'                : fields.date('Q3', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet3'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika3"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase3"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w4'                : fields.date('Q4', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet4'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika4"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase4"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w5'                : fields.date('Q5', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet5'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika5"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase5"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w6'                : fields.date('Q6', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet6'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika6"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase6"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w7'                : fields.date('Q7', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet7'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika7"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase7"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w8'                : fields.date('Q8', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet8'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika8"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase8"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w9'                : fields.date('Q9', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet9'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika9"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase9"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w10'               : fields.date('Q10', readonly=True, states={'draft':[('readonly',False)]}),
        "fleet10"           : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika10" : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase10"   : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w11'               : fields.date('Q11', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet11'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika11"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase11"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w12'               : fields.date('Q12', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet12'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika12"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase12"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w13'               : fields.date('Q13', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet13'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika13"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase13"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w14'               : fields.date('Q14', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet14'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika14"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase14"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w15'               : fields.date('Q15', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet15'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika15"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase15"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w16'               : fields.date('Q16', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet16'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika16"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase16"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w17'               : fields.date('Q17', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet17'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika17"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase17"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w18'               : fields.date('Q18', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet18'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika18"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase18"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w19'               : fields.date('Q19', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet19'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika19"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase19"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        
        'w20'               : fields.date('Q20', readonly=True, states={'draft':[('readonly',False)]}),
        'fleet20'            : fields.many2one('fleet.vehicle',"Kendaraan", readonly=True, states={'draft':[('readonly',False)]}),
        "kubika20"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Kubikasi", readonly=True, states={'draft':[('readonly',False)]}),
        "tonase20"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"Tonase", readonly=True, states={'draft':[('readonly',False)]}),
        'warning'   : fields.char('Warning',help="warning"),
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

    
    # def wkf_confirm_order(self, cr, uid, ids, context=None):
    #     import pdb;pdb.set_trace()
    #     return super(purchase_order,self).wkf_confirm_order(cr, uid, ids, context)

    def hapus_quotation(self,cr,uid,ids=None,context=None):
        # import pdb;pdb.set_trace()
        ids = self.search(cr,uid,[('state','=','draft')],) 
        if ids:
            self.unlink(cr,uid,ids,context=None)
        print ('po_scrapped_no '+str(ids))
        return True

    def create(self, cr, uid, vals, context=None):
        emp = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)],)
        uom_obj = self.pool.get('product.uom')
        if emp <> []:
            loc = self.pool.get('hr.employee').browse(cr,uid,emp,)[0].location_id.code
            # poname = str(loc or '') + 'FPH' + time.strftime("%y") + '-' + self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.vit.seq')
            # BDG-SPO/15-0000001
            poname = str(loc[0:3] or '') + '-SPO/' + time.strftime("%y") + '-' + self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.vit.seq')
            vals['name'] = poname 
        vol=0;wei=0
        for il in vals['order_line']:
            wei+='prod_weight' in il[2] and il[2]['prod_weight']
            vol+='prod_volume' in il[2] and il[2]['prod_volume']
        vals['volume_tot']=vol
        vals['weight_tot']=wei
        return super(purchase_order, self).create(cr, uid, vals, context=context)    
        #Cek jumlah q11 apakah melebihi w1    
        # sumw=0;sumv=[]
        # sumw2=0;sumv2=[]
        # sumw3=0;sumv3=[]
        # sumw4=0;sumv4=[]
        # if vals['sch_ids1']:
        #     for y in vals['sch_ids1']: sumw += y[2]['p1']
        #     for x in vals['sch_ids1']: sumv += x[2]['fleet_id'][0][2]
        # if vals['sch_ids2']:
        #     for y in vals['sch_ids2']: sumw2 += y[2]['p2']
        #     for x in vals['sch_ids2']: sumv2 += x[2]['fleet_id2'][0][2]
        # if vals['sch_ids2']:
        #     for y in vals['sch_ids3']: sumw3 += y[2]['p3']
        #     for x in vals['sch_ids3']: sumv3 += x[2]['fleet_id3'][0][2]
        # if vals['sch_ids2']:
        #     for y in vals['sch_ids4']: sumw4 += y[2]['p4']
        #     for x in vals['sch_ids4']: sumv4 += x[2]['fleet_id4'][0][2]
        # vals['no_vehicle']  = len(sumv)
        # vals['no_vehicle2'] = len(sumv2)
        # vals['no_vehicle3'] = len(sumv3)
        # vals['no_vehicle4'] = len(sumv4)
        # if sumw != vals['percent_r1']:
        #     raise osv.except_osv(_('Error W1!'), _('Jumlah persentase breakdown tidak sama dengan persentase per minggu'))
        # if sumw2 != vals['percent_r2']:
        #     raise osv.except_osv(_('Error W2!'), _('Jumlah persentase breakdown tidak sama dengan persentase per minggu'))
        # if sumw3 != vals['percent_r3']:
        #     raise osv.except_osv(_('Error W3!'), _('Jumlah persentase breakdown tidak sama dengan persentase per minggu'))
        # if sumw4 != vals['percent_r4']:
        #     raise osv.except_osv(_('Error W4!'), _('Jumlah persentase breakdown tidak sama dengan persentase per minggu'))

    def onchange_lines_sum_vol_wgt(self, cr, uid, ids, order_line, context=None):
        vol=0;wei=0
        for il in order_line:
            if not il[2]:
                wei+= self.pool.get('purchase.order.line').browse(cr,uid,il[1],).prod_weight
                vol+= self.pool.get('purchase.order.line').browse(cr,uid,il[1],).prod_volume
            elif il[2] :
                wei+='prod_weight' in il[2] and il[2]['prod_weight']
                vol+='prod_volume' in il[2] and il[2]['prod_volume']
        if not ids:
            return {'value':{
                'volume_tot'    : vol, 
                'weight_tot'    : wei,}}
        # else:
        #     return self.write(cr,uid,ids[0],{
        #         'volume_tot'    : vol, 
        #         'weight_tot'    : wei,})
        
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        '''Edit:
            'price_unit': order_line.price_unit or 0.0, >> dikonversi ke harga satuan kecil
        '''
        faktor = order_line.product_uom.factor or 1.0
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
            'price_unit': order_line.price_unit * faktor
        }

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """Collects require data from purchase order line that is used to create invoice line
        for that purchase order line
        :param account_id: Expense account of the product of PO line if any.
        :param browse_record order_line: Purchase order line browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        
        Edit: 
        dict qty        : big qty
             uos_id     : big uom
             quantity2  : small qty
             uom_id     : small uom

            'quantity': order_line.product_qty, << jadi fungsi
            'uos_id': order_line.product_uom.id or False, >> awal
            'price_unit': order_line.price_unit or 0.0, >> dikonversi ke harga satuan kecil
        """
        faktor = order_line.product_uom.factor or 1.00
        return {
            'name': order_line.name,
            'account_id': account_id,
            'price_unit': order_line.price_unit * faktor or 0.0,
            'product_id': order_line.product_id.id or False,
            'qty': order_line.product_qty or 0.0,
            'uos_id': order_line.product_uom.id or False, 
            'quantity2': order_line.small_qty,
            'uom_id': order_line.small_uom.id or ((order_line.small_qty == 0.00) and order_line.product_id.uom_id.id) or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
            'account_analytic_id': order_line.account_analytic_id.id or False,
            'harga_po' : order_line.price_unit or 0.0,
        }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        # Penambahan location source dan dest.
        cr.execute('SELECT id FROM stock_location where usage=\'supplier\' limit 1')
        source = cr.fetchone()
        source = source and source[0] or False
        inship_vals = {'name':self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in')}
        return {
            'name': self.pool.get('stock.picking.in')._name_set(cr,uid,inship_vals),
            'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'partner_id': order.partner_id.id,
            'invoice_state': '2binvoiced' if order.invoice_method == 'picking' else 'none',
            'type': 'in',
            'purchase_id': order.id,
            'company_id': order.company_id.id,
            'move_lines' : [],
            'location_id' : source,
            'location_dest_id':order.location_id.id,
        }

    def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None):
        # Delete lines that have not product qty
        """Creates pickings and appropriate stock moves for given order lines with, 
        then confirms the moves, makes them available, and confirms the picking.
        """
        if not picking_id:
            picking_id = self.pool.get('stock.picking').create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
        todo_moves = []
        stock_move = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        # mgids = []
        for order_line in order_lines:
            if not order_line.product_id:
                continue
            # if order line has product but qty == 0 skip create picking/incoming shipment but the order lines still exist
            # disini ditambah kondisi untuk qty kecil
            if order_line.product_qty == 0.00:
                continue
            if order_line.product_id.type in ('product', 'consu'):
                # # tambah stok move bayangan di move_group_ids
                # mgids.append((0,0,{'product_qty':order_line.product_qty,'product_id':order_line.product_id.id}))
                
                move = stock_move.create(cr, uid, self._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context))
                if order_line.move_dest_id and order_line.move_dest_id.state != 'done':
                    order_line.move_dest_id.write({'location_id': order.location_id.id})
                todo_moves.append(move)

        # Ini gg dipake = field bayangan gg dibutuhin
        # # tambah di stock piking in
        # self.pool.get('stock.picking.in').write(cr, uid, picking_id, {'move_group_ids':mgids}, context=context)
        
        stock_move.action_confirm(cr, uid, todo_moves)
        stock_move.force_assign(cr, uid, todo_moves)
        # import pdb;pdb.set_trace()
        # di cek dulu(dipindah) sama workflow untuk logistik dan office logistik
        # wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        self.pool.get('stock.picking.in').write(cr, uid,picking_id,{'state': 'logistik'})
        return [picking_id]

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
        
        # cr.execute('SELECT id FROM product_product p WHERE principal_id = '+ str(partner_x))
        # product_of_supplier = cr.fetchone()
        # if not product_of_supplier:
        #     return {'value': {
        #         'fiscal_position': False,
        #         'payment_term_id': False,
        #         'order_line'     : False,
        #         'warning'        : 'Tidak ada produk yang terkait dengan supplier', 
        #         }}
        #     # raise osv.except_osv(_('Produk!'), _('Tidak ada produk yang terkait dengan supplier.'))

        partner = self.pool.get('res.partner')
        supplier_address = partner.address_get(cr, uid, [partner_x], ['default'])
        supplier = partner.browse(cr, uid, partner_x)

        '''
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
            MT= 0.00;GT=0.00;
            # prod_id=prd.id;INI APA YA??GG dipake
            s3m=0.00;BGT=0.00;BMT=0.00;sgt_order=0.00;adj=0.00;cs=0.00;it=0.00
            ratio=1/prd.uom_po_id.factor

             
            # Range tanggal pertama 3 bln lalu s/d tgl terakhir bulan lalu
            # (date_trunc('MONTH',CURRENT_DATE) - INTERVAL '1 day')::date as lastday_lastmounth,
            # (date_trunc('MONTH',CURRENT_DATE) - INTERVAL '3 MONTH')::date as firstday_last3mounth
            
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
            # it = (it/ratio) pembelian sudah dalam karton, jadi gg dibagi ratio

            BMT=1*MT
            tot_bufer = BMT+BGT
            sgt_order = s3m+tot_bufer-cs-it

            tot_v   = tot_v+prd.volume
            tot_w   = tot_w+prd.weight

            #standard_price
            # price   = prd.product_tmpl_id.standard_price 
            price = prd.price_get('standard_price', context=context)[prd.id] / prd.uom_po_id.factor

            # end_inv & stk_cover
            stk_cover = 0.00
            end_inv         = cs + round(it) - round(s3m)
            if round(s3m) > 0.00 and end_inv > 0.00 : 
                stk_cover   = end_inv / round(s3m) * 4

            order_lines.append([0,0,{'product_id': prd.id or False, 
                'name'          : prd.name or '',
                'date_planned'  : date_order,
                'sales_3m'      : round(s3m),
                'avgMT'         : round(MT),
                'avgGT'         : round(GT),
                'bufMT'         : round(BMT),
                'bufGT'         : round(BGT),
                'price_unit'    : price, 
                'product_uom'   : prd.uom_po_id.id, 
                'stock_current' : cs,      
                'ending_inv'    : end_inv,     
                'in_transit'    : round(it),    
                'stock_cover'   : stk_cover, 
                'barcode'       : prd.seller_ids[0].product_code or '',
                'int_code'      : prd.default_code,
                # 'suggested_order' : 0.00,         
                # 'prod_weight'   : 0.00,  
                # 'prod_volume'   : 0.00,  #prd.volume * ratio * sgt_order,
                # 'adjustment'    : 0.00,
                # 'product_qty'   : 0.00,
                # 'forecastMT'    : 0.00,
                # 'forecastGT'    : 0.00,
                # 'small_qty'     : 0.00,
                }]) 
            '''

        return {'value': {
            # 'order_line'        : sorted(order_lines, key=lambda sku_order: sku_order[2]['stock_current'], reverse=False),
            'pricelist_id'      : supplier.property_product_pricelist_purchase.id or False,
            'fiscal_position'   : supplier.property_account_position and supplier.property_account_position.id or False,
            'payment_term_id'   : supplier.property_supplier_payment_term.id or False,
            'partner_code'      : supplier.code,
            'partner_id'        : partner_x,
            'warning'           : False,
            # 'volume_tot'      : tot_v,
            # 'weight_tot'      : tot_w,
            }}

    def onchange_fleet(self, cr, uid, ids, wn, kn, tn, fleet_id, sch_ids, context=None):
        fvalue={};kt=0.00;tt=0.00
        if fleet_id:
            if not sch_ids:
                raise osv.except_osv(_('Error!'), _('You cannot create breakdown for this week without schedule line(s)'))
            fl_obj = self.pool.get('fleet.vehicle')
            cap_vol = fl_obj.browse(cr,uid,fleet_id,).volume
            cap_ton = fl_obj.browse(cr,uid,fleet_id,).tonase
            prd_obj = self.pool.get('product.product')
            for x in sch_ids:
                kt += wn in x[2] and x[2][wn]*prd_obj.browse(cr,uid,x[2]['product_id'],).volume or 0.00
                tt += wn in x[2] and x[2][wn]*prd_obj.browse(cr,uid,x[2]['product_id'],).weight or 0.00
            if cap_ton == tt:
                fvalue[tn]='Cukup'
            elif cap_ton > tt:
                fvalue[tn]='Lebih'
            elif cap_ton < tt:
                fvalue[tn]='Kurang'
            if cap_vol == kt:
                fvalue[kn]='Cukup'
            elif cap_vol > kt:
                fvalue[kn]='Lebih'
            elif cap_vol < kt:
                fvalue[kn]='Kurang'
        return {'value':fvalue}

    def onchange_periode(self, cr, uid, ids, order_line, sch_ids, context=None):
        products=[]
        # if not order_line:
        #     raise osv.except_osv(_('Error!'), _('PO minimal memiliki 1 order'))
        # if sch_ids: 
        #     products=order_line
        prd_obj = self.pool.get('product.product')
        # product_qty = 0.00
        for x in order_line:
            product_id  = 'product_id' in x[2] and x[2]['product_id'] or False
            product_qty = 'product_qty2' in x[2] and x[2]['product_qty2'] or 0.00
            # product_uom = 'product_uom' in x[2] and x[2]['product_uom'] or False
            # forecastMT  ='forecastMT' in x[2] and x[2]['forecastMT'] or 0.00 
            # forecastGT  ='forecastGT' in x[2] and x[2]['forecastGT'] or 0.00
            # bufMT       ='bufMT' in x[2] and x[2]['bufMT'] or 0.00
            # bufGT       ='bufGT' in x[2] and x[2]['bufGT'] or 0.00
            # stock_current='stock_current' in x[2] and x[2]['stock_current'] or 0.00
            # in_transit  ='in_transit' in x[2] and x[2]['in_transit'] or 0.00
            # adjustment = 'adjustment' in x[2] and x[2]['adjustment'] or 0.00
            # small_qty   = 'small_qty' in x[2] and x[2]['small_qty'] or 0.00
            # small_uom   = 'small_uom' in x[2] and x[2]['small_uom'] or False
            
            # suggested_order = (forecastMT + forecastGT + bufMT + bufGT - stock_current - in_transit) 
            # suggested_order = suggested_order > 0.00 and suggested_order or 0.00
            # product_qty     = adjustment + suggested_order
            # if (small_qty > 0.00) and small_uom:
            #     product_qty = self.pool.get('purchase.order.line')._jumlah_qty_small_and_big(cr,uid,product_id, product_qty, product_uom, small_qty, small_uom, context=context)
            # product_qty     = product_qty > 0 and product_qty or 0.00
            barcode = prd_obj.browse(cr,uid,x[2]['product_id'],).barcode or ''
            default_code = prd_obj.browse(cr,uid,x[2]['product_id'],).default_code or ''
            # Append product dengan qty total dalam satuan besar
            if product_qty > 0.00:
                products.append([0,0,{'product_id':product_id,'barcode': barcode ,'int_code':default_code,'wtot':product_qty}])
            # Append product dengan qty small qty
            # if x[2]['small_qty'] > 0:
            #     products.append([0,0,{'product_id':x[2]['product_id'],'product_uom':x[2]['small_uom'],'barcode':prod_id.barcode or '','int_code':prod_id.default_code or '','wtot':x[2]['small_qty']}])
        return {'value' : {'sch_ids' : products}}

    # def onchange_sch_ids(self, cr, uid, ids,sch_ids,context=None):
    #     import pdb;pdb.set_trace()
    #     for sch in sch_ids:
    #         print sch


    # def onchange_contrib(self, cr, uid, ids, nfields, percent_r1, percent_r2, percent_r3, percent_r4, percent_r5, order_line, context=None):
    #     products=[]
    #     # percent_r1=percent_r1 or 0.00
    #     # percent_r2=percent_r2 or 0.00
    #     # percent_r3=percent_r3 or 0.00
    #     # percent_r4=percent_r4 or 0.00
    #     # percent_r5=percent_r5 or 0.00
    #     if not order_line:
    #         raise osv.except_osv(_('Error!'), _('PO minimal memiliki 1 order dengan Quantity minimal 1'))
    #     if (percent_r1 + percent_r2 + percent_r3 + percent_r4 + percent_r5) > 100:
    #         raise osv.except_osv(_('Error!'), _('Contribution(s) over 100%'))
    #     if nfields == 1:
    #         for x in order_line:
    #             if x[2]['product_qty'] > 0:
    #                 products.append([0,0,{'product_id':x[2]['product_id'],'name':x[2]['name'],'code':x[2]['barcode'],'w1':x[2]['product_qty']*percent_r1/100 or 0.00}])
    #         return {'value' : {'sch_ids1' : products}}
    #     elif nfields == 2:
    #         for x in order_line:
    #             if x[2]['product_qty'] > 0:
    #                 products.append([0,0,{'product_id':x[2]['product_id'],'name':x[2]['name'],'code':x[2]['barcode'],'w1':x[2]['product_qty']*percent_r2/100 or 0.00}])
    #         return {'value' : {'sch_ids2' : products}}
    #     elif nfields == 3:
    #         for x in order_line:
    #             if x[2]['product_qty'] > 0:
    #                 products.append([0,0,{'product_id':x[2]['product_id'],'name':x[2]['name'],'code':x[2]['barcode'],'w1':x[2]['product_qty']*percent_r3/100 or 0.00}])
    #         return {'value' : {'sch_ids3' : products}}
    #     elif nfields == 4:
    #         for x in order_line:
    #             if x[2]['product_qty'] > 0:
    #                 products.append([0,0,{'product_id':x[2]['product_id'],'name':x[2]['name'],'code':x[2]['barcode'],'w1':x[2]['product_qty']*percent_r4/100 or 0.00}])
    #         return {'value' : {'sch_ids4' : products}}
    #     elif nfields == 5:
    #         for x in order_line:
    #             if x[2]['product_qty'] > 0:
    #                 products.append([0,0,{'product_id':x[2]['product_id'],'name':x[2]['name'],'code':x[2]['barcode'],'w1':x[2]['product_qty']*percent_r5/100 or 0.00}])
    #         return {'value' : {'sch_ids5' : products}}

    # def onchange_rx(self, cr, uid, ids, p_rx, fname, p_r1, p_r2, p_r3, p_r4, 
    #         sch_ids, order_line, qrx, v_rx, w_rx, context=None):
    #     # if context is None:
    #     #     context = {}
    #     ptot = p_r1+p_r2+p_r3+p_r4
    #     if ptot>100:
    #         raise osv.except_osv(_('Error!'), _('Persentase lebih dari 100!'))       
    #     # if not r1:
    #     #     raise osv.except_osv(_('Warning!'), _('Isi R1!'))\
    #     if order_line[0][1] == False:
    #         sumqty=0;volr=0;wgtr=0
    #         for x in order_line: 
    #             sumqty += x[2]['product_qty']
    #             wgtr += x[2]['prod_weight']
    #             volr += x[2]['prod_volume']
    #     if ids != []:
    #         sumqty=0;volr=0;wgtr=0
    #         for x in self.pool.get('purchase.order.line').browse(cr,uid,[x[1] for x in order_line],): 
    #             sumqty += x.product_qty
    #             volr += x.prod_volume
    #             wgtr += x.prod_weight
    #     # Fix bug for replace ids
    #     # toremove = self.pool.get('purchase.order.schedule.r1').search(cr,uid,[('id','in',[x[1] for x in sch_ids1])],)
    #     # self.pool.get('purchase.order.schedule.r1').unlink(cr,uid,toremove,)
    #     # sch_ids1=[]
    #     # dat=datetime.strptime(r1, '%Y-%m-%d')
    #     # for i in range(3):
    #     #     dat +=i*timedelta(days=2)
    #     #     name1s = dat.strftime("%A")
    #     #     sch_ids1.append(
    #     #         [0,0,{'name': datetime.strftime(dat, '%Y-%m-%d'),
    #     #         'alias'     : str(i+1),
    #     #         'name1s'    : name1s,
    #     #         'p1'        : percent_rx/3.00 or 0.00,
    #     #         'vol1'      : percent_rx/100.00*volr1/3.00 or 0.00,
    #     #         'wgt1'      : percent_rx/100.00*wgtr1/3.00 or 0.00}])
    #     if fname == '1':       
    #         return {'value':{
    #             # 'qr1'       : p_rx/100.00*sumqty or 0,
    #             # 'sch_ids1'  : sch_ids1,
    #             'volume_r1' : p_rx/100.00*volr or 0,
    #             'weight_r1' : p_rx/100.00*wgtr or 0,}}
    #     if fname == '2':
    #         return {'value':{
    #             'volume_r2':p_rx/100.00*volr or 0,
    #             'weight_r2':p_rx/100.00*wgtr or 0,}}
    #     if fname == '3':
    #         return {'value':{
    #             'volume_r3':p_rx/100.00*volr or 0,
    #             'weight_r3':p_rx/100.00*wgtr or 0,}}
    #     if fname == '4':
    #         return {'value':{
    #             'volume_r4':p_rx/100.00*volr or 0,
    #             'weight_r4':p_rx/100.00*wgtr or 0,}}

    # def act_calculate(self, cr, uid, ids, context=None):
    #     data = self.read(cr,uid,ids[0],)
    #     lines_obj = self.pool.get('purchase.order.line')
    #     vol=0.00;wgt=0.00
    #     v1=0.00;w1=0.00
    #     v2=0.00;w2=0.00
    #     v3=0.00;w3=0.00
    #     v4=0.00;w4=0.00
    #     for x in lines_obj.browse(cr,uid,data['order_line'],context=None):
    #         vol += x.prod_volume
    #         wgt += x.prod_weight
    #     for x in lines_obj.browse(cr,uid,data['order_line'],context=None):
    #         v1=vol*data['percent_r1']/100
    #         w1=wgt*data['percent_r1']/100
    #         q1=x.product_qty*data['percent_r1']/100
    #         lines_obj.write(cr,uid,x.id,{'W1' : q1},context=None)
    #         v2=vol*data['percent_r2']/100
    #         w2=wgt*data['percent_r2']/100
    #         q2=x.product_qty*data['percent_r2']/100
    #         lines_obj.write(cr,uid,x.id,{'W2' : q2},context=None)
    #         v3=vol*data['percent_r3']/100
    #         w3=wgt*data['percent_r3']/100
    #         q3=x.product_qty*data['percent_r3']/100
    #         lines_obj.write(cr,uid,x.id,{'W3' : q3},context=None)
    #         v4=vol*data['percent_r4']/100
    #         w4=wgt*data['percent_r4']/100
    #         q4=x.product_qty*data['percent_r4']/100
    #         lines_obj.write(cr,uid,x.id,{'W4' : q4},context=None)
    #     self.write(cr,uid,ids,{
    #         'volume_tot'    : v1+v2+v3+v4, 
    #         'weight_tot'    : w1+w2+w3+w4,
    #         'volume_r1'     : v1, 
    #         'volume_r2'     : v2,
    #         'volume_r3'     : v3,
    #         'volume_r4'     : v4,
    #         'weight_r1'     : w1,
    #         'weight_r2'     : w2,
    #         'weight_r3'     : w3,
    #         'weight_r4'     : w4,
    #         })
    #     #R1
    #     r1_lines = self.pool.get('purchase.order.schedule.r1')
    #     vol1_tot=0.00
    #     for y in r1_lines.browse(cr,uid,data['sch_ids1'],context=None):
    #         vol1_tot+=y.p1
    #     if vol1_tot>data['percent_r1']:
    #         raise osv.except_osv(_('Error!'), _('Jumlah Q1.1 lebih dari Q1!'))
    #     for y in r1_lines.browse(cr,uid,data['sch_ids1'],context=None):
    #         vol1=vol*y.p1/100 or 0.00
    #         wgt1=wgt*y.p1/100 or 0.00
    #         r1_lines.write(cr,uid,y.id,{'v_tot1':v1,'w_tot1':w1,'vol1':vol1,'wgt1':wgt1},context=None)
    #     #END R1
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
        return []

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
        return []

    # def onchange_w1(self, cr, uid, ids, w1, order_line, context=None):
    #     # import pdb;pdb.set_trace()
    #     if not ids:
    #         for l in order_line:
    #             l[2]['date_planned']=w1
    #         return {'value':{'order_line':order_line,}}

    def onchange_locx(self, cr, uid, ids, loc_x, location_id, context=None):
        if loc_x:
            return {'value':{'location_id':loc_x,}}
    
    #TODO: implement messages system
    # def wkf_confirm_order(self, cr, uid, ids, context=None):
    #     todo = []
    #     for po in self.browse(cr, uid, ids, context=context):
    #         valw1=0;valw2=0;valw3=0;valw4=0;
    #         if po.sch_ids1:
    #             for pw1 in po.sch_ids1: valw1 += pw1.p1
    #         if po.sch_ids2:
    #             for pw2 in po.sch_ids2: valw2 += pw2.p2
    #         if po.sch_ids3:
    #             for pw3 in po.sch_ids3: valw3 += pw3.p3
    #         if po.sch_ids4:
    #             for pw4 in po.sch_ids4: valw4 += pw4.p4
    #         if valw1 != po.percent_r1:
    #             raise osv.except_osv(_('Error Week 1!'), _('Jumlah persentase breakdown harus sama dengan persentase per minggu'))
    #         if valw2 != po.percent_r2:
    #             raise osv.except_osv(_('Error Week 2!'), _('Jumlah persentase breakdown harus sama dengan persentase per minggu'))
    #         if valw3 != po.percent_r3:
    #             raise osv.except_osv(_('Error Week 3!'), _('Jumlah persentase breakdown harus sama dengan persentase per minggu'))
    #         if valw4 != po.percent_r4:
    #             raise osv.except_osv(_('Error Week 4!'), _('Jumlah persentase breakdown harus sama dengan persentase per minggu'))
    #         if po.percent_r1 + po.percent_r2 + po.percent_r3 + po.percent_r4 != 100:
    #             raise osv.except_osv(_('Total!'), _('Jumlah persentase harus sama dengan 100%'))

    #         if not po.order_line:
    #             raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
    #         for line in po.order_line:
    #             if line.state=='draft':
    #                 todo.append(line.id)

    #     self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
    #     for id in ids:
    #         self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
    #     return True

    def button_total(self, cr, uid, ids, context=None):
        data = self.read(cr,uid,ids[0],)
        lines_obj = self.pool.get('purchase.order.line')
        vol=0.00;wgt=0.00
        for x in lines_obj.browse(cr,uid,data['order_line'],context=None):
            vol += x.prod_volume
            wgt += x.prod_weight
        return self.write(cr,uid,ids,{
            'volume_tot'    : vol, 
            'weight_tot'    : wgt})

    def add_prod(self, cr, uid, ids, context=None):
        data = self.read(cr,uid,ids[0],)
        if not data['order_line']:
            raise osv.except_osv(_('Error!'), _('You cannot create breakdown for this week without purchase order line(s)'))
        lines_obj = self.pool.get('purchase.order.line')
        products =[]
        for x in lines_obj.browse(cr,uid,data['order_line'],context=None):
            if x.product_qty > 0:
                products.append([0,0,{'product_id':x.product_id.id,'name':x.name,'code':x.barcode,'wtot':x.product_qty}])
        return self.write(cr,uid,ids,{'sch_ids' : products,})

    _defaults = {
        'location_ids':_get_default_loc,
        'principal_ids':_get_default_principal,
        # 'th_periode': lambda self,cr,uid,context={}:datetime.now().strftime("%Y"),
        # 'view_w1':True,
        # 'view_w2':True,
        # 'view_w3':True,
        # 'view_w4':True,
        # 'view_w5':True,
        # 'periode':_period_get,
        # 'r1': fields.date.context_today, TODO: copy for r2-r4
        }

purchase_order()

# class purchase_order_schedule_cumul(osv.Model):
#     _name = 'purchase.order.schedule.cumul'
#     _auto = False
#     _description = 'schdetail'
#     _rec_name = 'po_id'

#     _columns = {
#         "po_id"     : fields.many2one('purchase.order',"PO"),
#         'fleet'     : fields.char("Jumlah Kendaraan"),
#         't2'        : fields.char("Date"),
#         't3'        : fields.char("Day"),
#         'partner_x' : fields.many2one('res.partner',"Supplier"),
#     }   

#     def init(self, cr):
#         tools.drop_view_if_exists(cr, 'purchase_order_schedule_cumul')
#         cr.execute("""
#             CREATE OR REPLACE VIEW purchase_order_schedule_cumul AS (
                
#                 SELECT po.partner_x,min(po_seq) as id, po_id, count(A.fleet_id) fleet, A.date t2, day t3, min(rid) as rid 
#                 FROM (
#                     SELECT po_seq,po_id, fleet_id, date, day, 1 as rid
#                       FROM purchase_order_schedule_r1_detail
#                     UNION ALL
#                     SELECT po_seq,po_id, fleet_id, date, day, 2 as rid
#                       FROM purchase_order_schedule_r2_detail
#                     UNION ALL
#                     SELECT po_seq,po_id, fleet_id, date, day, 3 as rid
#                       FROM purchase_order_schedule_r3_detail
#                     UNION ALL
#                     SELECT po_seq,po_id, fleet_id, date, day, 4 as rid
#                       FROM purchase_order_schedule_r4_detail
#                     UNION ALL
#                     SELECT po_seq,po_id, fleet_id, date, day, 5 as rid
#                       FROM purchase_order_schedule_r5_detail
#                     )A
#                 JOIN purchase_order po ON po.id=A.po_id 
#                 GROUP BY A.date, day, po_id, partner_x
#         )""")

# purchase_order_schedule_cumul()

class fleet_vehicle(osv.Model):
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        def _name_get(d):
            return (d['id'], d.get('name',''))
        result = []
        for record in self.browse(cr, user, ids, context=context):
            mydict = {
                      'id': record.id,
                      'name': record.model_id.brand_id.name
                      }
            if record.jenis:
                mydict.update({'name':record.jenis + ' / ' + mydict['name']})
            if record.license_plate and record.license_plate != '-':
                mydict.update({'name':mydict['name'] + ' / ' + record.license_plate})
            result.append(_name_get(mydict))
        return result

    _columns = {
        'jenis' : fields.char("Jenis",required=True,help="Daya angkut truk, seperti Engkel Tunggal, Tronton, Trinton, dll."),
        }

    _defaults = {
        'license_plate': '-',
    }
fleet_vehicle()

# class purchase_order_schedule_r1(osv.Model):
#     _name = 'purchase.order.schedule.r1'

#     _columns={
#         'name'              : fields.char("Product",readonly=True),
#         'po_id'             : fields.many2one('purchase.order',"PO", ondelete='cascade'),
#         'product_id'        : fields.many2one('product.product',string="Product"),
#         'code'              : fields.char("Barcode",readonly=True),
#         'w1'                : fields.float('W1'),
#         'w11'               : fields.float('W1.1'),
#         'w12'               : fields.float('W1.2'),
#         'w13'               : fields.float('W1.3'),
#         'w14'               : fields.float('W1.4'),
#         'w15'               : fields.float('W1.5'),
#         'w16'               : fields.float('W1.6'),
#         }

#     def onchange_wn(self, cr, uid, ids, fields_t, fields, wn, wn1, wn2, wn3, wn4, wn5, wn6, context=None):
#         tot = wn1 + wn2 + wn3 + wn4 + wn5 + wn6
#         if not tot > wn:
#             return True
#         EA = 'Error '+ str(fields) +'!'
#         EB = 'Value melebihi ' + str(fields_t) +'.'
#         raise osv.except_osv(_('%s') % (EA), _('%s') % (EB))

# purchase_order_schedule_r1()

# class purchase_order_schedule_r2(osv.Model):
#     _name = 'purchase.order.schedule.r2'

#     _columns={
#         'name'              : fields.char("Product",readonly=True),
#         'po_id'             : fields.many2one('purchase.order',"PO", ondelete='cascade'),
#         'product_id'        : fields.many2one('product.product',string="Product"),
#         'code'              : fields.char("Barcode",readonly=True),
#         'w1'                : fields.float('W2'),
#         'w11'               : fields.float('W2.1'),
#         'w12'               : fields.float('W2.2'),
#         'w13'               : fields.float('W2.3'),
#         'w14'               : fields.float('W2.4'),
#         'w15'               : fields.float('W2.5'),
#         'w16'               : fields.float('W2.6'),
#         }

#     def onchange_wn(self, cr, uid, ids, fields_t, fields, wn, wn1, wn2, wn3, wn4, wn5, wn6, context=None):
#         tot = wn1 + wn2 + wn3 + wn4 + wn5 + wn6
#         if not tot > wn:
#             return True
#         EA = 'Error '+ str(fields) +'!'
#         EB = 'Value melebihi ' + str(fields_t) +'.'
#         raise osv.except_osv(_('%s') % (EA), _('%s') % (EB))

# purchase_order_schedule_r2()

# class purchase_order_schedule_r3(osv.Model):
#     _name = 'purchase.order.schedule.r3'

#     _columns={
#         'name'              : fields.char("Product",readonly=True),
#         'po_id'             : fields.many2one('purchase.order',"PO", ondelete='cascade'),
#         'product_id'        : fields.many2one('product.product',string="Product"),
#         'code'              : fields.char("Barcode",readonly=True),
#         'w1'                : fields.float('W3'),
#         'w11'               : fields.float('W3.1'),
#         'w12'               : fields.float('W3.2'),
#         'w13'               : fields.float('W3.3'),
#         'w14'               : fields.float('W3.4'),
#         'w15'               : fields.float('W3.5'),
#         'w16'               : fields.float('W3.6'),
#         }

#     def onchange_wn(self, cr, uid, ids, fields_t, fields, wn, wn1, wn2, wn3, wn4, wn5, wn6, context=None):
#         tot = wn1 + wn2 + wn3 + wn4 + wn5 + wn6
#         if not tot > wn:
#             return True
#         EA = 'Error '+ str(fields) +'!'
#         EB = 'Value melebihi ' + str(fields_t) +'.'
#         raise osv.except_osv(_('%s') % (EA), _('%s') % (EB))

# purchase_order_schedule_r1()

# class purchase_order_schedule_r4(osv.Model):
#     _name = 'purchase.order.schedule.r4'

#     _columns={
#         'name'              : fields.char("Product",readonly=True),
#         'po_id'             : fields.many2one('purchase.order',"PO", ondelete='cascade'),
#         'product_id'        : fields.many2one('product.product',string="Product"),
#         'code'              : fields.char("Barcode",readonly=True),
#         'w1'                : fields.float('W4'),
#         'w11'               : fields.float('W4.1'),
#         'w12'               : fields.float('W4.2'),
#         'w13'               : fields.float('W4.3'),
#         'w14'               : fields.float('W4.4'),
#         'w15'               : fields.float('W4.5'),
#         'w16'               : fields.float('W4.6'),
#         }

#     def onchange_wn(self, cr, uid, ids, fields_t, fields, wn, wn1, wn2, wn3, wn4, wn5, wn6, context=None):
#         tot = wn1 + wn2 + wn3 + wn4 + wn5 + wn6
#         if not tot > wn:
#             return True
#         EA = 'Error '+ str(fields) +'!'
#         EB = 'Value melebihi ' + str(fields_t) +'.'
#         raise osv.except_osv(_('%s') % (EA), _('%s') % (EB))

# purchase_order_schedule_r2()

# class purchase_order_schedule_r5(osv.Model):
#     _name = 'purchase.order.schedule.r5'

#     _columns={
#         'name'              : fields.char("Product",readonly=True),
#         'po_id'             : fields.many2one('purchase.order',"PO", ondelete='cascade'),
#         'product_id'        : fields.many2one('product.product',string="Product"),
#         'code'              : fields.char("Barcode",readonly=True),
#         'w1'                : fields.float('W5'),
#         'w11'               : fields.float('W5.1'),
#         'w12'               : fields.float('W5.2'),
#         'w13'               : fields.float('W5.3'),
#         'w14'               : fields.float('W5.4'),
#         'w15'               : fields.float('W5.5'),
#         'w16'               : fields.float('W5.6'),
#         }

#     def onchange_wn(self, cr, uid, ids, fields_t, fields, wn, wn1, wn2, wn3, wn4, wn5, wn6, context=None):
#         tot = wn1 + wn2 + wn3 + wn4 + wn5 + wn6
#         if not tot > wn:
#             return True
#         EA = 'Error '+ str(fields) +'!'
#         EB = 'Value melebihi ' + str(fields_t) +'.'
#         raise osv.except_osv(_('%s') % (EA), _('%s') % (EB))

# purchase_order_schedule_r1()

# class purchase_order_schedule_r1_detail(osv.Model):
#     _name = 'purchase.order.schedule.r1.detail'

#     _columns={
#         "po_id"     : fields.many2one('purchase.order',"PO", ondelete='cascade'),
#         "alias"     : fields.selection([('satu','W1.1'),('dua','W1.2'),('tiga','W1.3'),('empat','W1.4'),('lima','W1.5'),('enam','W1.6')],"Summary of"),
#         "fleet_id"  : fields.many2one('fleet.vehicle',"KENDARAAN"),
#         "kubikasi"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"KUBIKASI"),
#         "tonase"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"TONASE"),
#         "date"      : fields.date("DATE" ),
#         'day'       : fields.char("DAY"),
#         "tot_ton"   : fields.float("Total Tonase"),
#         "tot_m3"    : fields.float("Total Kubikasi"),
#         "po_seq"    : fields.integer("tempID"),
#     }

#     _defaults = {
#         'po_seq': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'code.cumul.seq'),
#     }

#     def onchange_date(self, cr, uid, ids, dateN, dayN, r1N, r1eN, sch_idsN, context=None):
#         if dateN:
#             dayN = datetime.strptime(dateN, '%Y-%m-%d')
#             dayN = dayN.strftime("%A")
#             if r1N:
#                 dateN = datetime.strptime(dateN, '%Y-%m-%d')
#                 r1N   = datetime.strptime(r1N, '%Y-%m-%d')
#                 if dateN < r1N:
#                     raise osv.except_osv(_('Error!'), _('Date out of range'))
#             if r1eN:
#                 r1eN   = datetime.strptime(r1eN, '%Y-%m-%d')
#                 if dateN > r1eN:
#                     raise osv.except_osv(_('Error!'), _('Date out of range'))
#             if sch_idsN == []:
#                 return {'value':{'day':dayN,}}
#             return {'value':{'day':dayN,}}

#     def onchange_alias(self, cr, uid, ids, alias, sch, sch_detail, context=None):
#         vol_sum1 = 0;wgt_sum1 = 0
#         vol_sum2 = 0;wgt_sum2 = 0
#         vol_sum3 = 0;wgt_sum3 = 0
#         vol_sum4 = 0;wgt_sum4 = 0
#         vol_sum5 = 0;wgt_sum5 = 0
#         vol_sum6 = 0;wgt_sum6 = 0
#         vals={}
#         prd_obj = self.pool.get('product.product')
#         fl_obj = self.pool.get('fleet.vehicle')

#         if sch:
#             for x in  sch:
#                 vol_sum1 += 'w11' in x[2] and x[2]['w11'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum1 += 'w11' in x[2] and x[2]['w11'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum2 += 'w12' in x[2] and x[2]['w12'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum2 += 'w12' in x[2] and x[2]['w12'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum3 += 'w13' in x[2] and x[2]['w13'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum3 += 'w13' in x[2] and x[2]['w13'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum4 += 'w14' in x[2] and x[2]['w14'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum4 += 'w14' in x[2] and x[2]['w14'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum5 += 'w15' in x[2] and x[2]['w15'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum5 += 'w15' in x[2] and x[2]['w15'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum6 += 'w16' in x[2] and x[2]['w16'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum6 += 'w16' in x[2] and x[2]['w16'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
        
#         if sch_detail:
#             for x in sch_detail:
#                 vol_sum1 -= 'satu' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum1 -= 'satu' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum2 -= 'dua' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum2 -= 'dua' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum3 -= 'tiga' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum3 -= 'tiga' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum4 -= 'empat' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum4 -= 'empat' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum5 -= 'lima' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum5 -= 'lima' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum6 -= 'enam' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum6 -= 'enam' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
        
#         if alias == 'satu' :
#             vals['tot_ton'] = wgt_sum1
#             vals['tot_m3']  = vol_sum1

#         elif alias == 'dua' :
#             vals['tot_ton'] = wgt_sum2
#             vals['tot_m3']  = vol_sum2

#         elif alias == 'tiga' :
#             vals['tot_ton'] = wgt_sum3
#             vals['tot_m3']  = vol_sum3

#         elif alias == 'empat' :
#             vals['tot_ton'] = wgt_sum4
#             vals['tot_m3']  = vol_sum4

#         elif alias == 'lima' :
#             vals['tot_ton'] = wgt_sum5
#             vals['tot_m3']  = vol_sum5

#         elif alias == 'enam' :
#             vals['tot_ton'] = wgt_sum6
#             vals['tot_m3']  = vol_sum6

#         return {"value":vals}


#     def onchange_fleet_id(self, cr, uid, ids, fleet_id, tot_m3, tot_ton, context=None):
#         # cek kapasitas mobil dengan volume dan berat total barang    
#         values = {}
#         if fleet_id:
#             fl_obj = self.pool.get('fleet.vehicle')
#             cap_vol = fl_obj.browse(cr,uid,fleet_id,).volume
#             cap_ton = fl_obj.browse(cr,uid,fleet_id,).tonase

#             if cap_vol == tot_m3:
#                 values['kubikasi'] = 'Cukup'
#             elif cap_vol > tot_m3:
#                 values['kubikasi'] = 'Lebih'
#             elif cap_vol < tot_m3:
#                 values['kubikasi'] = 'Kurang'
                
#             if cap_ton == tot_ton:
#                 values['tonase'] = 'Cukup'
#             elif cap_ton > tot_ton:
#                 values['tonase'] = 'Lebih'
#             elif cap_ton < tot_ton:
#                 values['tonase'] = 'Kurang'

#         return {"value":values} 

# purchase_order_schedule_r1_detail()

# class purchase_order_schedule_r2_detail(osv.Model):
#     _name = 'purchase.order.schedule.r2.detail'

#     _columns={
#         "po_id"     : fields.many2one('purchase.order',"PO", ondelete='cascade'),
#         "alias"     : fields.selection([('satu','W2.1'),('dua','W2.2'),('tiga','W2.3'),('empat','W2.4'),('lima','W2.5'),('enam','W2.6')],"Summary of"),
#         "fleet_id"  : fields.many2one('fleet.vehicle',"KENDARAAN"),
#         "kubikasi"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"KUBIKASI"),
#         "tonase"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"TONASE"),
#         "date"      : fields.date("DATE" ),
#         'day'       : fields.char("DAY"),
#         "tot_ton"   : fields.float("Total Tonase"),
#         "tot_m3"    : fields.float("Total Kubikasi"),
#         "po_seq"    : fields.integer("tempID"),
#     }

#     _defaults = {
#         'po_seq': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'code.cumul.seq'),
#     }

#     def onchange_date(self, cr, uid, ids, dateN, dayN, r1N, r1eN, sch_idsN, context=None):
#         if dateN:
#             dayN = datetime.strptime(dateN, '%Y-%m-%d')
#             dayN = dayN.strftime("%A")
#             if r1N:
#                 dateN = datetime.strptime(dateN, '%Y-%m-%d')
#                 r1N   = datetime.strptime(r1N, '%Y-%m-%d')
#                 if dateN < r1N:
#                     raise osv.except_osv(_('Error!'), _('Date out of range'))
#             if r1eN:
#                 r1eN   = datetime.strptime(r1eN, '%Y-%m-%d')
#                 if dateN > r1eN:
#                     raise osv.except_osv(_('Error!'), _('Date out of range'))
#             if sch_idsN == []:
#                 return {'value':{'day':dayN,}}
#             return {'value':{'day':dayN,}}

#     def onchange_alias(self, cr, uid, ids, alias, sch, sch_detail, context=None):
#         vol_sum1 = 0;wgt_sum1 = 0
#         vol_sum2 = 0;wgt_sum2 = 0
#         vol_sum3 = 0;wgt_sum3 = 0
#         vol_sum4 = 0;wgt_sum4 = 0
#         vol_sum5 = 0;wgt_sum5 = 0
#         vol_sum6 = 0;wgt_sum6 = 0
#         vals={}
#         prd_obj = self.pool.get('product.product')
#         fl_obj = self.pool.get('fleet.vehicle')

#         if sch:
#             for x in  sch:
#                 vol_sum1 += 'w11' in x[2] and x[2]['w11'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum1 += 'w11' in x[2] and x[2]['w11'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum2 += 'w12' in x[2] and x[2]['w12'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum2 += 'w12' in x[2] and x[2]['w12'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum3 += 'w13' in x[2] and x[2]['w13'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum3 += 'w13' in x[2] and x[2]['w13'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum4 += 'w14' in x[2] and x[2]['w14'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum4 += 'w14' in x[2] and x[2]['w14'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum5 += 'w15' in x[2] and x[2]['w15'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum5 += 'w15' in x[2] and x[2]['w15'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum6 += 'w16' in x[2] and x[2]['w16'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum6 += 'w16' in x[2] and x[2]['w16'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
        
#         if sch_detail:
#             for x in sch_detail:
#                 vol_sum1 -= 'satu' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum1 -= 'satu' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum2 -= 'dua' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum2 -= 'dua' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum3 -= 'tiga' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum3 -= 'tiga' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum4 -= 'empat' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum4 -= 'empat' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum5 -= 'lima' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum5 -= 'lima' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum6 -= 'enam' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum6 -= 'enam' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
        
#         if alias == 'satu' :
#             vals['tot_ton'] = wgt_sum1
#             vals['tot_m3']  = vol_sum1

#         elif alias == 'dua' :
#             vals['tot_ton'] = wgt_sum2
#             vals['tot_m3']  = vol_sum2

#         elif alias == 'tiga' :
#             vals['tot_ton'] = wgt_sum3
#             vals['tot_m3']  = vol_sum3

#         elif alias == 'empat' :
#             vals['tot_ton'] = wgt_sum4
#             vals['tot_m3']  = vol_sum4

#         elif alias == 'lima' :
#             vals['tot_ton'] = wgt_sum5
#             vals['tot_m3']  = vol_sum5

#         elif alias == 'enam' :
#             vals['tot_ton'] = wgt_sum6
#             vals['tot_m3']  = vol_sum6

#         return {"value":vals}


#     def onchange_fleet_id(self, cr, uid, ids, fleet_id, tot_m3, tot_ton, context=None):
#         # cek kapasitas mobil dengan volume dan berat total barang    
#         values = {}
#         if fleet_id:
#             fl_obj = self.pool.get('fleet.vehicle')
#             cap_vol = fl_obj.browse(cr,uid,fleet_id,).volume
#             cap_ton = fl_obj.browse(cr,uid,fleet_id,).tonase

#             if cap_vol == tot_m3:
#                 values['kubikasi'] = 'Cukup'
#             elif cap_vol > tot_m3:
#                 values['kubikasi'] = 'Lebih'
#             elif cap_vol < tot_m3:
#                 values['kubikasi'] = 'Kurang'
                
#             if cap_ton == tot_ton:
#                 values['tonase'] = 'Cukup'
#             elif cap_ton > tot_ton:
#                 values['tonase'] = 'Lebih'
#             elif cap_ton < tot_ton:
#                 values['tonase'] = 'Kurang'

#         return {"value":values}

# purchase_order_schedule_r2_detail()

# class purchase_order_schedule_r3_detail(osv.Model):
#     _name = 'purchase.order.schedule.r3.detail'

#     _columns={
#         "po_id"     : fields.many2one('purchase.order',"PO", ondelete='cascade'),
#         "alias"     : fields.selection([('satu','W3.1'),('dua','W3.2'),('tiga','W3.3'),('empat','W3.4'),('lima','W3.5'),('enam','W3.6')],"Summary of"),
#         "fleet_id"  : fields.many2one('fleet.vehicle',"KENDARAAN"),
#         "kubikasi"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"KUBIKASI"),
#         "tonase"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"TONASE"),
#         "date"      : fields.date("DATE" ),
#         'day'       : fields.char("DAY"),
#         "tot_ton"   : fields.float("Total Tonase"),
#         "tot_m3"    : fields.float("Total Kubikasi"),
#         "po_seq"    : fields.integer("tempID"),
#     }

#     _defaults = {
#         'po_seq': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'code.cumul.seq'),
#     }

#     def onchange_date(self, cr, uid, ids, dateN, dayN, r1N, r1eN, sch_idsN, context=None):
#         if dateN:
#             dayN = datetime.strptime(dateN, '%Y-%m-%d')
#             dayN = dayN.strftime("%A")
#             if r1N:
#                 dateN = datetime.strptime(dateN, '%Y-%m-%d')
#                 r1N   = datetime.strptime(r1N, '%Y-%m-%d')
#                 if dateN < r1N:
#                     raise osv.except_osv(_('Error!'), _('Date out of range'))
#             if r1eN:
#                 r1eN   = datetime.strptime(r1eN, '%Y-%m-%d')
#                 if dateN > r1eN:
#                     raise osv.except_osv(_('Error!'), _('Date out of range'))
#             if sch_idsN == []:
#                 return {'value':{'day':dayN,}}
#             return {'value':{'day':dayN,}}

#     def onchange_alias(self, cr, uid, ids, alias, sch, sch_detail, context=None):
#         vol_sum1 = 0;wgt_sum1 = 0
#         vol_sum2 = 0;wgt_sum2 = 0
#         vol_sum3 = 0;wgt_sum3 = 0
#         vol_sum4 = 0;wgt_sum4 = 0
#         vol_sum5 = 0;wgt_sum5 = 0
#         vol_sum6 = 0;wgt_sum6 = 0
#         vals={}
#         prd_obj = self.pool.get('product.product')
#         fl_obj = self.pool.get('fleet.vehicle')

#         if sch:
#             for x in  sch:
#                 vol_sum1 += 'w11' in x[2] and x[2]['w11'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum1 += 'w11' in x[2] and x[2]['w11'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum2 += 'w12' in x[2] and x[2]['w12'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum2 += 'w12' in x[2] and x[2]['w12'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum3 += 'w13' in x[2] and x[2]['w13'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum3 += 'w13' in x[2] and x[2]['w13'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum4 += 'w14' in x[2] and x[2]['w14'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum4 += 'w14' in x[2] and x[2]['w14'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum5 += 'w15' in x[2] and x[2]['w15'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum5 += 'w15' in x[2] and x[2]['w15'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum6 += 'w16' in x[2] and x[2]['w16'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum6 += 'w16' in x[2] and x[2]['w16'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
        
#         if sch_detail:
#             for x in sch_detail:
#                 vol_sum1 -= 'satu' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum1 -= 'satu' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum2 -= 'dua' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum2 -= 'dua' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum3 -= 'tiga' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum3 -= 'tiga' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum4 -= 'empat' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum4 -= 'empat' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum5 -= 'lima' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum5 -= 'lima' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum6 -= 'enam' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum6 -= 'enam' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
        
#         if alias == 'satu' :
#             vals['tot_ton'] = wgt_sum1
#             vals['tot_m3']  = vol_sum1

#         elif alias == 'dua' :
#             vals['tot_ton'] = wgt_sum2
#             vals['tot_m3']  = vol_sum2

#         elif alias == 'tiga' :
#             vals['tot_ton'] = wgt_sum3
#             vals['tot_m3']  = vol_sum3

#         elif alias == 'empat' :
#             vals['tot_ton'] = wgt_sum4
#             vals['tot_m3']  = vol_sum4

#         elif alias == 'lima' :
#             vals['tot_ton'] = wgt_sum5
#             vals['tot_m3']  = vol_sum5

#         elif alias == 'enam' :
#             vals['tot_ton'] = wgt_sum6
#             vals['tot_m3']  = vol_sum6

#         return {"value":vals}


#     def onchange_fleet_id(self, cr, uid, ids, fleet_id, tot_m3, tot_ton, context=None):
#         # cek kapasitas mobil dengan volume dan berat total barang    
#         values = {}
#         if fleet_id:
#             fl_obj = self.pool.get('fleet.vehicle')
#             cap_vol = fl_obj.browse(cr,uid,fleet_id,).volume
#             cap_ton = fl_obj.browse(cr,uid,fleet_id,).tonase

#             if cap_vol == tot_m3:
#                 values['kubikasi'] = 'Cukup'
#             elif cap_vol > tot_m3:
#                 values['kubikasi'] = 'Lebih'
#             elif cap_vol < tot_m3:
#                 values['kubikasi'] = 'Kurang'
                
#             if cap_ton == tot_ton:
#                 values['tonase'] = 'Cukup'
#             elif cap_ton > tot_ton:
#                 values['tonase'] = 'Lebih'
#             elif cap_ton < tot_ton:
#                 values['tonase'] = 'Kurang'

#         return {"value":values} 

# purchase_order_schedule_r3_detail()

# class purchase_order_schedule_r4_detail(osv.Model):
#     _name = 'purchase.order.schedule.r4.detail'

#     _columns={
#         "po_id"     : fields.many2one('purchase.order',"PO", ondelete='cascade'),
#         "alias"     : fields.selection([('satu','W4.1'),('dua','W4.2'),('tiga','W4.3'),('empat','W4.4'),('lima','W4.5'),('enam','W4.6')],"Summary of"),
#         "fleet_id"  : fields.many2one('fleet.vehicle',"KENDARAAN"),
#         "kubikasi"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"KUBIKASI"),
#         "tonase"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"TONASE"),
#         "date"      : fields.date("DATE" ),
#         'day'       : fields.char("DAY"),
#         "tot_ton"   : fields.float("Total Tonase"),
#         "tot_m3"    : fields.float("Total Kubikasi"),
#         "po_seq"    : fields.integer("tempID"),
#     }

#     _defaults = {
#         'po_seq': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'code.cumul.seq'),
#     }

#     def onchange_date(self, cr, uid, ids, dateN, dayN, r1N, r1eN, sch_idsN, context=None):
#         if dateN:
#             dayN = datetime.strptime(dateN, '%Y-%m-%d')
#             dayN = dayN.strftime("%A")
#             if r1N:
#                 dateN = datetime.strptime(dateN, '%Y-%m-%d')
#                 r1N   = datetime.strptime(r1N, '%Y-%m-%d')
#                 if dateN < r1N:
#                     raise osv.except_osv(_('Error!'), _('Date out of range'))
#             if r1eN:
#                 r1eN   = datetime.strptime(r1eN, '%Y-%m-%d')
#                 if dateN > r1eN:
#                     raise osv.except_osv(_('Error!'), _('Date out of range'))
#             if sch_idsN == []:
#                 return {'value':{'day':dayN,}}
#             return {'value':{'day':dayN,}}

#     def onchange_alias(self, cr, uid, ids, alias, sch, sch_detail, context=None):
#         vol_sum1 = 0;wgt_sum1 = 0
#         vol_sum2 = 0;wgt_sum2 = 0
#         vol_sum3 = 0;wgt_sum3 = 0
#         vol_sum4 = 0;wgt_sum4 = 0
#         vol_sum5 = 0;wgt_sum5 = 0
#         vol_sum6 = 0;wgt_sum6 = 0
#         vals={}
#         prd_obj = self.pool.get('product.product')
#         fl_obj = self.pool.get('fleet.vehicle')

#         if sch:
#             for x in  sch:
#                 vol_sum1 += 'w11' in x[2] and x[2]['w11'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum1 += 'w11' in x[2] and x[2]['w11'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum2 += 'w12' in x[2] and x[2]['w12'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum2 += 'w12' in x[2] and x[2]['w12'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum3 += 'w13' in x[2] and x[2]['w13'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum3 += 'w13' in x[2] and x[2]['w13'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum4 += 'w14' in x[2] and x[2]['w14'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum4 += 'w14' in x[2] and x[2]['w14'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum5 += 'w15' in x[2] and x[2]['w15'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum5 += 'w15' in x[2] and x[2]['w15'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum6 += 'w16' in x[2] and x[2]['w16'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum6 += 'w16' in x[2] and x[2]['w16'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
        
#         if sch_detail:
#             for x in sch_detail:
#                 vol_sum1 -= 'satu' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum1 -= 'satu' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum2 -= 'dua' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum2 -= 'dua' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum3 -= 'tiga' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum3 -= 'tiga' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum4 -= 'empat' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum4 -= 'empat' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum5 -= 'lima' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum5 -= 'lima' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum6 -= 'enam' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum6 -= 'enam' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
        
#         if alias == 'satu' :
#             vals['tot_ton'] = wgt_sum1
#             vals['tot_m3']  = vol_sum1

#         elif alias == 'dua' :
#             vals['tot_ton'] = wgt_sum2
#             vals['tot_m3']  = vol_sum2

#         elif alias == 'tiga' :
#             vals['tot_ton'] = wgt_sum3
#             vals['tot_m3']  = vol_sum3

#         elif alias == 'empat' :
#             vals['tot_ton'] = wgt_sum4
#             vals['tot_m3']  = vol_sum4

#         elif alias == 'lima' :
#             vals['tot_ton'] = wgt_sum5
#             vals['tot_m3']  = vol_sum5

#         elif alias == 'enam' :
#             vals['tot_ton'] = wgt_sum6
#             vals['tot_m3']  = vol_sum6

#         return {"value":vals}


#     def onchange_fleet_id(self, cr, uid, ids, fleet_id, tot_m3, tot_ton, context=None):
#         # cek kapasitas mobil dengan volume dan berat total barang    
#         values = {}
#         if fleet_id:
#             fl_obj = self.pool.get('fleet.vehicle')
#             cap_vol = fl_obj.browse(cr,uid,fleet_id,).volume
#             cap_ton = fl_obj.browse(cr,uid,fleet_id,).tonase

#             if cap_vol == tot_m3:
#                 values['kubikasi'] = 'Cukup'
#             elif cap_vol > tot_m3:
#                 values['kubikasi'] = 'Lebih'
#             elif cap_vol < tot_m3:
#                 values['kubikasi'] = 'Kurang'
                
#             if cap_ton == tot_ton:
#                 values['tonase'] = 'Cukup'
#             elif cap_ton > tot_ton:
#                 values['tonase'] = 'Lebih'
#             elif cap_ton < tot_ton:
#                 values['tonase'] = 'Kurang'

#         return {"value":values}

# purchase_order_schedule_r4_detail()
# # Here

# class purchase_order_schedule_r5_detail(osv.Model):
#     _name = 'purchase.order.schedule.r5.detail'

#     _columns={
#         "po_id"     : fields.many2one('purchase.order',"PO", ondelete='cascade'),
#         "alias"     : fields.selection([('satu','W5.1'),('dua','W5.2'),('tiga','W5.3'),('empat','W5.4'),('lima','W5.5'),('enam','W5.6')],"Summary of"),
#         "fleet_id"  : fields.many2one('fleet.vehicle',"KENDARAAN"),
#         "kubikasi"  : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"KUBIKASI"),
#         "tonase"    : fields.selection([('Cukup','Cukup'),('Kurang','Kurang'),('Lebih','Lebih')],"TONASE"),
#         "date"      : fields.date("DATE" ),
#         'day'       : fields.char("DAY"),
#         "tot_ton"   : fields.float("Total Tonase"),
#         "tot_m3"    : fields.float("Total Kubikasi"),
#         "po_seq"    : fields.integer("tempID"),
#     }

#     _defaults = {
#         'po_seq': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'code.cumul.seq'),
#     }

#     def onchange_date(self, cr, uid, ids, dateN, dayN, r1N, r1eN, sch_idsN, context=None):
#         if dateN:
#             dayN = datetime.strptime(dateN, '%Y-%m-%d')
#             dayN = dayN.strftime("%A")
#             if r1N:
#                 dateN = datetime.strptime(dateN, '%Y-%m-%d')
#                 r1N   = datetime.strptime(r1N, '%Y-%m-%d')
#                 if dateN < r1N:
#                     raise osv.except_osv(_('Error!'), _('Date out of range'))
#             if r1eN:
#                 r1eN   = datetime.strptime(r1eN, '%Y-%m-%d')
#                 if dateN > r1eN:
#                     raise osv.except_osv(_('Error!'), _('Date out of range'))
#             if sch_idsN == []:
#                 return {'value':{'day':dayN,}}
#             return {'value':{'day':dayN,}}

#     def onchange_alias(self, cr, uid, ids, alias, sch, sch_detail, context=None):
#         vol_sum1 = 0;wgt_sum1 = 0
#         vol_sum2 = 0;wgt_sum2 = 0
#         vol_sum3 = 0;wgt_sum3 = 0
#         vol_sum4 = 0;wgt_sum4 = 0
#         vol_sum5 = 0;wgt_sum5 = 0
#         vol_sum6 = 0;wgt_sum6 = 0
#         vals={}
#         prd_obj = self.pool.get('product.product')
#         fl_obj = self.pool.get('fleet.vehicle')

#         if sch:
#             for x in  sch:
#                 vol_sum1 += 'w11' in x[2] and x[2]['w11'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum1 += 'w11' in x[2] and x[2]['w11'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum2 += 'w12' in x[2] and x[2]['w12'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum2 += 'w12' in x[2] and x[2]['w12'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum3 += 'w13' in x[2] and x[2]['w13'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum3 += 'w13' in x[2] and x[2]['w13'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum4 += 'w14' in x[2] and x[2]['w14'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum4 += 'w14' in x[2] and x[2]['w14'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum5 += 'w15' in x[2] and x[2]['w15'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum5 += 'w15' in x[2] and x[2]['w15'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 vol_sum6 += 'w16' in x[2] and x[2]['w16'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).volume/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
#                 wgt_sum6 += 'w16' in x[2] and x[2]['w16'] * (prd_obj.browse(cr,uid,x[2]['product_id'],).weight/prd_obj.browse(cr,uid,x[2]['product_id'],).uom_po_id.factor or 0.00) or 0.00
        
#         if sch_detail:
#             for x in sch_detail:
#                 vol_sum1 -= 'satu' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum1 -= 'satu' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum2 -= 'dua' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum2 -= 'dua' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum3 -= 'tiga' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum3 -= 'tiga' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum4 -= 'empat' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum4 -= 'empat' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum5 -= 'lima' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum5 -= 'lima' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
#                 vol_sum6 -= 'enam' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).volume or 0.00
#                 wgt_sum6 -= 'enam' in x[2]['alias'] and fl_obj.browse(cr,uid,x[2]['fleet_id'],).tonase or 0.00
        
#         if alias == 'satu' :
#             vals['tot_ton'] = wgt_sum1
#             vals['tot_m3']  = vol_sum1

#         elif alias == 'dua' :
#             vals['tot_ton'] = wgt_sum2
#             vals['tot_m3']  = vol_sum2

#         elif alias == 'tiga' :
#             vals['tot_ton'] = wgt_sum3
#             vals['tot_m3']  = vol_sum3

#         elif alias == 'empat' :
#             vals['tot_ton'] = wgt_sum4
#             vals['tot_m3']  = vol_sum4

#         elif alias == 'lima' :
#             vals['tot_ton'] = wgt_sum5
#             vals['tot_m3']  = vol_sum5

#         elif alias == 'enam' :
#             vals['tot_ton'] = wgt_sum6
#             vals['tot_m3']  = vol_sum6

#         return {"value":vals}


#     def onchange_fleet_id(self, cr, uid, ids, fleet_id, tot_m3, tot_ton, context=None):
#         # cek kapasitas mobil dengan volume dan berat total barang    
#         values = {}
#         if fleet_id:
#             fl_obj = self.pool.get('fleet.vehicle')
#             cap_vol = fl_obj.browse(cr,uid,fleet_id,).volume
#             cap_ton = fl_obj.browse(cr,uid,fleet_id,).tonase

#             if cap_vol == tot_m3:
#                 values['kubikasi'] = 'Cukup'
#             elif cap_vol > tot_m3:
#                 values['kubikasi'] = 'Lebih'
#             elif cap_vol < tot_m3:
#                 values['kubikasi'] = 'Kurang'
                
#             if cap_ton == tot_ton:
#                 values['tonase'] = 'Cukup'
#             elif cap_ton > tot_ton:
#                 values['tonase'] = 'Lebih'
#             elif cap_ton < tot_ton:
#                 values['tonase'] = 'Kurang'

#         return {"value":values}

# purchase_order_schedule_r5_detail()