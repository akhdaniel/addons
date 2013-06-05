from osv import osv
from osv import fields
#from _common import rounding
import time
from tools.translate import _
import decimal_precision as dp
from array import *
from decimal import Decimal, ROUND_DOWN

class product_pricelist_item(osv.osv):
    _inherit="product.pricelist.item"
    _name="product.pricelist.item"
    _columns={
        "core_price": fields.float('Core Price', digits=(12,4)),
        "price_surcharge": fields.float('Ex Ref Price', digits=(12,4)),
    }
product_pricelist_item()

class product_product(osv.osv):
    _inherit="product.product"
    _name="product.product"
    _columns={
        'property_account_exref': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Ex Ref Account",
            view_load=True,
            help="This account will be used for invoices to value differential for the current product"),
    }    
product_product()

class product_pricelist(osv.osv):
    _inherit="product.pricelist"
    _name="product.pricelist"

    def price_get_multi(self, cr, uid, pricelist_ids, products_by_qty_by_partner, context=None):
        """multi products 'price_get'.
           @param pricelist_ids:
           @param products_by_qty:
           @param partner:
           @param context: {
             'date': Date of the pricelist (%Y-%m-%d),}
           @return: a dict of dict with product_id as key and a dict 'price by pricelist' as value
           
           TODO: harus diubah supaya panggil parent price_get_multi
           
        """

        def _create_parent_category_list(id, lst):
            if not id:
                return []
            parent = product_category_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_parent_category_list(parent, lst)
            else:
                return lst
        # _create_parent_category_list

        if context is None:
            context = {}

        date = time.strftime('%Y-%m-%d')
        if 'date' in context:
            date = context['date']

        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.product')
        product_template_obj = self.pool.get('product.template')
        product_category_obj = self.pool.get('product.category')
        product_uom_obj = self.pool.get('product.uom')
        supplierinfo_obj = self.pool.get('product.supplierinfo')
        price_type_obj = self.pool.get('product.price.type')
        product_pricelist_version_obj = self.pool.get('product.pricelist.version')

        # product.pricelist.version:
        if pricelist_ids:
            pricelist_version_ids = pricelist_ids
        else:
            # all pricelists:
            pricelist_version_ids = self.pool.get('product.pricelist').search(cr, uid, [], context=context)

        pricelist_version_ids = list(set(pricelist_version_ids))
        plversions_search_args = [
            ('pricelist_id', 'in', pricelist_version_ids),
            '|',
            ('date_start', '=', False),
            ('date_start', '<=', date),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', date),
        ]

        plversion_ids = product_pricelist_version_obj.search(cr, uid, plversions_search_args)
        if len(pricelist_version_ids) != len(plversion_ids):
            msg = "At least one pricelist has no active version !\nPlease create or activate one."
            raise osv.except_osv(_('Warning !'), _(msg))

        # product.product:
        product_ids = [i[0] for i in products_by_qty_by_partner]
        #products = dict([(item['id'], item) for item in product_obj.read(cr, uid, product_ids, ['categ_id', 'product_tmpl_id', 'uos_id', 'uom_id'])])
        products = product_obj.browse(cr, uid, product_ids, context=context)
        products_dict = dict([(item.id, item) for item in products])

        # product.category:
        product_category_ids = product_category_obj.search(cr, uid, [])
        product_categories = product_category_obj.read(cr, uid, product_category_ids, ['parent_id'])
        product_category_tree = dict([(item['id'], item['parent_id'][0]) for item in product_categories if item['parent_id']])

        results = {}
        core_price=0.0
        for product_id, qty, partner in products_by_qty_by_partner:
            for pricelist_id in pricelist_version_ids:
                price = False

                tmpl_id = products_dict[product_id].product_tmpl_id and products_dict[product_id].product_tmpl_id.id or False

                categ_id = products_dict[product_id].categ_id and products_dict[product_id].categ_id.id or False
                categ_ids = _create_parent_category_list(categ_id, [categ_id])
                if categ_ids:
                    categ_where = '(categ_id IN (' + ','.join(map(str, categ_ids)) + '))'
                else:
                    categ_where = '(categ_id IS NULL)'

                cr.execute(
                    'SELECT i.*, pl.currency_id '
                    'FROM product_pricelist_item AS i, '
                        'product_pricelist_version AS v, product_pricelist AS pl '
                    'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = %s) '
                        'AND (product_id IS NULL OR product_id = %s) '
                        'AND (' + categ_where + ' OR (categ_id IS NULL)) '
                        'AND price_version_id = %s '
                        'AND (min_quantity IS NULL OR min_quantity <= %s) '
                        'AND i.price_version_id = v.id AND v.pricelist_id = pl.id '
                    'ORDER BY sequence',
                    (tmpl_id, product_id, plversion_ids[0], qty))
                res1 = cr.dictfetchall()
                uom_price_already_computed = False
                for res in res1:
                    if res:
                        if res['base'] == -1:
                            if not res['base_pricelist_id']:
                                price = 0.0
                            else:
                                #price
                                price_tmp = self.price_get(cr, uid,
                                        [res['base_pricelist_id']], product_id,
                                        qty, context=context)[res['base_pricelist_id']]
                                ptype_src = self.browse(cr, uid, res['base_pricelist_id']).currency_id.id
                                price = currency_obj.compute(cr, uid, ptype_src, res['currency_id'], price_tmp, round=False)
                        elif res['base'] == -2:
                            # this section could be improved by moving the queries outside the loop:
                            where = []
                            if partner:
                                where = [('name', '=', partner) ]
                            sinfo = supplierinfo_obj.search(cr, uid,
                                    [('product_id', '=', tmpl_id)] + where)
                            price = 0.0
                            if sinfo:
                                qty_in_product_uom = qty
                                product_default_uom = product_template_obj.read(cr, uid, [tmpl_id], ['uom_id'])[0]['uom_id'][0]
                                supplier = supplierinfo_obj.browse(cr, uid, sinfo, context=context)[0]
                                seller_uom = supplier.product_uom and supplier.product_uom.id or False
                                if seller_uom and product_default_uom and product_default_uom != seller_uom:
                                    uom_price_already_computed = True
                                    qty_in_product_uom = product_uom_obj._compute_qty(cr, uid, product_default_uom, qty, to_uom_id=seller_uom)
                                cr.execute('SELECT * ' \
                                        'FROM pricelist_partnerinfo ' \
                                        'WHERE suppinfo_id IN %s' \
                                            'AND min_quantity <= %s ' \
                                        'ORDER BY min_quantity DESC LIMIT 1', (tuple(sinfo),qty_in_product_uom,))
                                res2 = cr.dictfetchone()
                                if res2:
                                    price = res2['price']
                        else:
                            price_type = price_type_obj.browse(cr, uid, int(res['base']))
                            price = currency_obj.compute(cr, uid,
                                    price_type.currency_id.id, res['currency_id'],
                                    product_obj.price_get(cr, uid, [product_id],
                                        price_type.field,context=context)[product_id], round=False, context=context)

                            uom_price_already_computed = True

                        if price is not False:
                            price_limit = price

                            price = price * (1.0+(res['price_discount'] or 0.0))
                            price = rounding(price, res['price_round'])
                            price += (res['price_surcharge'] or 0.0)
                            if res['price_min_margin']:
                                price = max(price, price_limit+res['price_min_margin'])
                            if res['price_max_margin']:
                                price = min(price, price_limit+res['price_max_margin'])
                            c=(res['core_price'] or 0.0)
                            core_price = prettyFloat( c )

                    else:
                        # False means no valid line found ! But we may not raise an
                        # exception here because it breaks the search
                        price = False

                if price:
                    if 'uom' in context and not uom_price_already_computed:
                        product = products_dict[product_id]
                        uom = product.uos_id or product.uom_id
                        price = self.pool.get('product.uom')._compute_price(cr, uid, uom.id, price, context['uom'])
                        core_price = self.pool.get('product.uom')._compute_price(cr, uid, uom.id, core_price , context['uom'])

                if results.get(product_id):
                    results[product_id][pricelist_id] = price
                else:
                    results[product_id] = {pricelist_id: price}
                    
                results[product_id]['core_price']= core_price

        return results
product_pricelist()

class product_category(osv.osv):
    _inherit = "product.category"
    _inherit = "product.category"
    _columns = {
        'property_account_discount_categ': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Discount Account",
            view_load=True,
            help="This account will be used for invoices instead of the default one to value discount for the current product"),
    }
product_category()

class account_invoice(osv.osv):
    _inherit="account.invoice"
    _name="account.invoice"

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        #import pdb; pdb.set_trace()
        res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context=None)
        res['invoice_line_id']=x.get('invoice_line_id',False)
        return res

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        Hook method to be overridden in additional modules to verify and possibly alter the
        move lines to be created by an invoice, for special cases.
        :param invoice_browse: browsable record of the invoice that is generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines (as for create())
        :return: the (possibly updated) final move_lines to create for this invoice
        
        insert 2 new journal entries: 
            Dr NPA dreceivable      <diff_amount>
            Cr     Differential         <diff_amount>
        
        <diff_amount> is the difference of the product core_price - price_surcharge
            
            
        """
        
        if invoice_browse.journal_id.code != 'EXREF':
             return move_lines
        
        context={}
        discount_total=0
                
        company_currency = invoice_browse.company_id.currency_id.id
        diff_currency_p = invoice_browse.currency_id.id <> company_currency
        currency_id = invoice_browse.currency_id.id
        cur_obj = self.pool.get('res.currency')
        #total, total_currency, iml = self.compute_invoice_totals(cr, uid, invoice_browse, company_currency, 'ref', move_lines)

        partner_id = move_lines[0][2]['partner_id']
        period_id = invoice_browse.period_id.id
        default_credit_account_id = invoice_browse.journal_id.default_credit_account_id.id
        if not default_credit_account_id:
            raise osv.except_osv(_('Error !'), _('Ex Journal does not have Default Credit Account. Please set it up through Accounting - Configuration - Journals ') )
        
        default_debit_account_id = invoice_browse.journal_id.default_debit_account_id.id
        if not default_debit_account_id:
            raise osv.except_osv(_('Error !'), _('Ex Journal does not have Default Debit Account. Please set it up through Accounting - Configuration - Journals ') )
        date_due= invoice_browse.date_due
        

        #import pdb; pdb.set_trace()

        """
        find the sales order originating the invoice
        """
        
        origins = invoice_browse.origin.split(":")
        
        order_obj = self.pool.get('sale.order')
        order_id = order_obj.search(cr, uid, [('name','=', origins[-1] )])[0]
        order = order_obj.browse(cr, uid, order_id, context)
        
        pricelist = order.pricelist_id.id
        date_order = order.date_order
        tot_diff_amount = 0.0
        diff_amounts = []
        
        account_obj = self.pool.get('account.account')
        
        #import pdb; pdb.set_trace()

        """""""""""
        loop for each product items in the invoice
        to generate Differential Journal and Discount Journal
        """""""""""
        for il in invoice_browse.invoice_line:
            uom = il.uos_id.id
            qty = il.quantity
            subtotal = il.price_subtotal
            product_id = il.product_id.id
            product_name = il.product_id.name
            product_xfer_account = il.product_id.property_account_exref.id
            
            #discount in local currency
            discount_currency = il.discount_nominal * qty
            discount = cur_obj.compute(cr, uid, currency_id, company_currency, discount_currency, context={'date': invoice_browse.date_invoice}) 

            discount_account=il.product_id.categ_id.property_account_discount_categ.id
            if not discount_account:
                raise osv.except_osv(_('Error !'), _('Product %s does not have Discount Account. Please set it up through Product Category Accounting Tab') % (product_name))

            if not product_xfer_account:
                raise osv.except_osv(_('Error !'), _('Product %s does not have Ex Ref Account. Please set it up through Product Ex Ref Tab') % (product_name))
            
            """
            modify original move_lines to add discount to the credit/debit amount
            misal discount=10 dan 20
            
            asli:
            
            AR     400
                Sales   100   product 1
                Sales   300   product 2
                
            COGS    50        product 1
                Inv    50
            COGS    100       product 2
                Inv    100
            
            modif:
            
            AR        400 + 30
                Sales       100 + 10 prod1
                Sales       300 + 20 prod2

            COGS      50
                Inv        50
    
            """
            
            i=0
            #import pdb; pdb.set_trace()
            for ml in move_lines:
                # if SALES account for same product_id
                account = account_obj.browse(cr, uid, ml[2]['account_id'])

                if account.user_type.code == 'income' \
                and ml[2]['account_id'] != product_xfer_account \
                and 'credit' in ml[2] \
                and ml[2]['invoice_line_id'] == il.id\
                and ml[2]['product_id'] == il.product_id.id:
                #and ml[2]['credit'] == subtotal:
                    #import pdb; pdb.set_trace()
                    move_lines[i][2]['credit'] += discount
                    move_lines[i][2]['credit'] = prettyFloat(move_lines[i][2]['credit'])

                elif account.user_type.code == 'receivable' \
                and ml[2]['account_id'] != product_xfer_account \
                and 'debit' in ml[2] \
                and ml[2]['account_id'] != default_credit_account_id\
                and ml[2]['account_id'] != default_debit_account_id:
                    move_lines[i][2]['debit'] += discount
                    move_lines[i][2]['debit'] = prettyFloat(move_lines[i][2]['debit']) 
                i += 1  
  
            """
            find the core price of the product
            """
            core_price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                product_id,  qty, partner_id, {
                    'uom': uom,
                    'date': date_order,
                }) 
            
            val_currency = (core_price['core_price'] - il.price_unit ) * qty
            val = cur_obj.compute(cr, uid, currency_id, company_currency, val_currency, context={'date': invoice_browse.date_invoice}) 


            """
            differential journal, core price > exref price
            NPA receivable
            kondisi normal
            """    
            if val > 0:
                move_lines.append((0,0,{
                   'type': 'dest',
                   'name': 'Differential ' + product_name,
                   'credit': prettyFloat(val),
                   'price': prettyFloat(val),
                   'account_id': product_xfer_account,
                   'date_maturity': date_due,
                   'amount_currency': diff_currency_p \
                       and -1*val_currency or False,
                   'currency_id': diff_currency_p \
                       and currency_id or False,
                   'ref': 'test',
                   'period_id': period_id,
                   'partner_id':partner_id,                           
                   'product_id':product_id,
                }))
                """
                NPA journal
                """         
                move_lines.append((0,0,{
                   'type': 'dest',
                   'name': 'NPA receivable',
                   'debit' : prettyFloat(val),
                   'price': prettyFloat(val),
                   'account_id': default_debit_account_id ,
                   'date_maturity': date_due,
                   'amount_currency': diff_currency_p \
                        and val_currency or False,
                   'currency_id': diff_currency_p \
                        and currency_id or False,
                   'ref': 'test',
                   'period_id':period_id,
                   'partner_id':partner_id,
                   'product_id':product_id,
                }))             
            else:
                """
                differential journal, core price > exref price
                NPA payable
                """   
                val = val *-1
                move_lines.append((0,0,{
                   'type': 'dest',
                   'name': 'NPA payable',
                   'credit': prettyFloat(val),
                   'price': prettyFloat(val),
                   'account_id': default_credit_account_id ,
                   'date_maturity': date_due,
                   'amount_currency': diff_currency_p \
                       and -1*val_currency or False,
                   'currency_id': diff_currency_p \
                       and currency_id or False,
                   'ref': 'test',
                   'period_id': period_id,
                   'partner_id':partner_id,                           
                   'product_id':product_id,
                }))
                """
                NPA journal
                """         
                move_lines.append((0,0,{
                   'type': 'dest',
                   'name': 'Differential ' + product_name,
                   'debit' : prettyFloat(val),
                   'price': prettyFloat(val),
                   'account_id': product_xfer_account ,
                   'date_maturity': date_due,
                   'amount_currency': diff_currency_p \
                        and val_currency or False,
                   'currency_id': diff_currency_p \
                        and currency_id or False,
                   'ref': 'test',
                   'period_id':period_id,
                   'partner_id':partner_id,
                   'product_id':product_id,
                }))             
                
            #tot_diff_amount = tot_diff_amount + val
            
            if discount > 0:
                """
                generate discount journal
                Dr Discount (product discount account)
                Cr   customer (invoice_browse.account.id)
                """
                
                move_lines.append((0,0,{
                   'type': 'dest',
                   'name': 'Discount ' + product_name,
                   'debit' : prettyFloat(discount),
                   'price': 0.0,
                   'account_id': discount_account ,
                   'date_maturity': date_due,
                   'amount_currency': diff_currency_p \
                        and discount_currency or False,
                   'currency_id': diff_currency_p \
                        and currency_id or False,
                   'ref': 'test',
                   'period_id':period_id,
                   'partner_id':partner_id,
                   'product_id':product_id,
                }))             
                move_lines.append((0,0,{
                   'type': 'dest',
                   'name': 'Discount ' + product_name,
                   'credit' : prettyFloat(discount),
                   'price': 0.0,
                   'account_id': invoice_browse.account_id.id ,
                   'date_maturity': date_due,
                   'amount_currency': diff_currency_p \
                        and -1*discount_currency or False,
                   'currency_id': diff_currency_p \
                        and currency_id or False,
                   'ref': 'test',
                   'period_id':period_id,
                   'partner_id':partner_id,
                   'product_id':product_id,
                }))
                
        #end for invoice_lines
        return move_lines
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _name = "account.invoice.line"

    def move_line_get_item(self, cr, uid, line, context=None):
        #import pdb; pdb.set_trace()
        res = {}
        res = super(account_invoice_line, self).move_line_get_item(cr, uid, line, context=None)
        res['invoice_line_id']=line.id
        return res
account_invoice_line()

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _name = "account.move.line"

    _columns = {
        'invoice_line_id': fields.integer('Invoice Line ID' ),
    }
account_move_line()

def rounding(f, r):
    if not r:
        return f
    return round(f / r) * r

def roundf(f, prec=0):
    return Decimal(str(f)).quantize(Decimal('0.001') )

class prettyFloat(float):
    def __repr__(self):
        return "%0.4f" % self
