import time
from openerp import netsvc
import datetime
import calendar
from openerp.osv import fields, osv

 
class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        if uid != 1:
                raise osv.except_osv(('Perhatian !'),('Purchase order hanya bisa di confirm oleh administrator.'))
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(('Error!'),('You cannot confirm a purchase order without any purchase order line.'))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)

        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
        return True


class account_invoice(osv.osv):
    _inherit = "account.invoice"    
    _columns = {
        'catatan': fields.text('Notes'),
        #'alamat_kirim': fields.text('Delivery Address'),
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'party_datetime': fields.datetime('Party Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'delivery_date': fields.datetime('Delivery Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
    }
    
    _defaults = {'delivery_date': time.strftime('%Y-%m-%d %H:%M:%S'), 'party_datetime': time.strftime('%Y-%m-%d %H:%M:%S')}
    
    def onchange_backdate(self, cr, uid, ids, date):
        if date:
            if date < str(datetime.date.today()):
                value = {'party_datetime': str(datetime.date.today()), 'delivery_date': str(datetime.date.today())}
                warning = {'title': ('Perhatian !'), 'message' : ('Tanggal Party & Delivery Minimal Hari Ini')}
                return {'value': value, 'warning': warning}
        return True


    def invoice_batal(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        obj_move_line = self.pool.get('account.move.line')
        
        self.pool.get('account.move').write(cr, uid, [val.move_id.id], {'state': 'draft'})
        
        for x in val.move_id.line_id:
            obj_move_line.write(cr, uid, [x.id], {'state': 'draft', 'reconcile_id': False, 'reconcile_partial_id': False})
            obj_move_line.unlink(cr, uid, [x.id])
        
        
        self.write(cr, uid, [val.id], {'state': 'open'})
        self.action_cancel(cr, uid, ids)
        
        
    
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"    
    _columns = {
        'ucapan': fields.text('Ucapan'),
    } 

    _defaults = {
        'invoice_line_tax_id' : False
    }

account_invoice_line()

    
class stock_picking(osv.osv):
    _inherit = "stock.picking"    
    _columns = {
        'party_datetime': fields.datetime('Party Date'),
        'delivery_date': fields.datetime('Delivery Date'),
        'shop_id':fields.many2one('wtc.shop', 'Shop'),
    }

    _defaults = {
        'delivery_date': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    def onchange_backdatetime(self, cr, uid, ids, date):
        if date:
            date = date.split(' ')[0]
            if date != str(datetime.date.today()):
                value = {'date': str(datetime.datetime.today())}
                warning = {'title': ('Perhatian !'), 'message' : ('Tanggal harus hari ini')}
                return {'value': value, 'warning': warning}
        return True

    def onchange_backdate(self, cr, uid, ids, date):
        if date:
            date = date.split(' ')[0]
            if date not in ( str(datetime.date.today()), str(datetime.date.today()+datetime.timedelta(days=1)) ):
                value = {'delivery_date': str(datetime.datetime.today())}
                warning = {'title': ('Perhatian !'), 'message' : ('Tanggal minimal hari ini atau besok')}
                return {'value': value, 'warning': warning}
        return True


    
class stock_move(osv.osv):
    _inherit = "stock.move"    

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if uid != 1:
            frozen_fields = set(['product_qty', 'product_uom', 'product_uos_qty', 'product_uos', 'location_id', 'location_dest_id', 'product_id'])
            for move in self.browse(cr, uid, ids, context=context):
                if move.state == 'done':
                    if frozen_fields.intersection(vals):
                        pass
#                         raise osv.except_osv(_('Operation Forbidden!'),
#                                              _('Quantities, Units of Measure, Products and Locations cannot be modified on stock moves that have already been processed (except by the Administrator).'))
        return  super(stock_move, self).write(cr, uid, ids, vals, context=context)

##class stock_picking_out(osv.osv):
##    _inherit = "stock.picking"    
##    _columns = {
##        'party_datetime': fields.datetime('Party Date'),
##        'delivery_date': fields.datetime('Delivery Date'),
      #  'shop_id':fields.many2one('wtc.shop', 'Shop'),
##    } 
    
class sale_order(osv.osv):
    _inherit = "sale.order"    
    _columns = {
        'catatan': fields.text('Notes'),
        #'alamat_kirim': fields.text('Delivery Address'),
        'party_datetime': fields.datetime('Party Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'delivery_date': fields.datetime('Delivery Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
    }

    _defaults = {
                 'delivery_date': time.strftime('%Y-%m-%d'),
                 'party_datetime': time.strftime('%Y-%m-%d %H:%M:%S'),
    }


    def onchange_dateorder(self, cr, uid, ids, date):
        if date:
            return {'value': {'date_order': str(datetime.date.today())}}
        return True

    def onchange_backdate(self, cr, uid, ids, date):
        if date:
            if date < str(datetime.date.today()):
                value = {'party_datetime': str(datetime.date.today()), 'delivery_date': str(datetime.date.today())}
                warning = {'title': ('Perhatian !'), 'message' : ('Tanggal Party & Delivery Minimal Hari Ini')}
                return {'value': value, 'warning': warning}
        return True

    def onchange_shop_id(self, cr, uid, ids, shop_id, context=None):
        v = {}
        if shop_id:
            shop = self.pool.get('wtc.shop').browse(cr, uid, shop_id, context=context)
            v['warehouse_id'] = shop.warehouse_id.id
            # if shop.project_id.id:
            #     v['project_id'] = shop.project_id.id
            # if shop.pricelist_id.id:
            #     v['pricelist_id'] = shop.pricelist_id.id
            # if shop.alamat_kirim:
            #     v['alamat_kirim'] = shop.alamat_kirim
        return {'value': v}


    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        
        alamat = ''
        if part.street :
            alamat += part.street
        if part.street2 :
            alamat += part.street2
                    
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
            #'alamat_kirim': alamat 
        }
        if pricelist:
            val['pricelist_id'] = pricelist
        return {'value': val}


    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'), _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'catatan': order.catatan,
            #'alamat_kirim': order.alamat_kirim,
            'shop_id': order.shop_id.id,
            'delivery_date': order.delivery_date,
            'party_datetime': order.party_datetime
        }

        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals


    def _prepare_order_picking(self, cr, uid, order, context=None):
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'type': 'out',
            'state': 'auto',
            'move_type': order.picking_policy,
            'shop_id': order.shop_id.id,
            'party_datetime': order.party_datetime,
            'delivery_date': order.delivery_date,
            'sale_id': order.id,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
        }


sale_order()


class res_users(osv.osv):
    _inherit = "res.users"    
    _columns = {
        'change_price': fields.boolean('Change Price'),
    } 


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"    
    _columns = {
        'ucapan': fields.text('Ucapan'),
        'catatan': fields.text('Catatan'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], 
            change_default=True, readonly=True, states={'draft': [('readonly', False)]}, ondelete='restrict'),
    } 
 

    def onchange_price_desc(self, cr, uid, ids, price, product, pricelist, qty, uom, partner_id, date_order):
        if product:
            kue = self.pool.get('product.product').browse(cr, uid, product)
            harga = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], product, qty or 1.0, partner_id, {
                                                                                                                     'uom': uom or kue.uom_id.id, 
                                                                                                                     'date': date_order
                                                                                                                     })[pricelist]
            user = self.pool.get('res.users').browse(cr, uid, uid)
            if user.change_price:
                harga = price
            return {'value': {'price_unit': harga, 'name': kue.partner_ref}}
        return True
   

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = {}
        if not line.invoiced:
            if not account_id:
                if line.product_id:
                    account_id = line.product_id.property_account_income.id
                    if not account_id:
                        account_id = line.product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise osv.except_osv(_('Error!'), _('Please define income account for this product: "%s" (id:%d).') % (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid, 'property_account_income_categ', 'product.category', context=context)
                    account_id = prop and prop.id or False
            uosqty = self._get_line_qty(cr, uid, line, context=context)
            uos_id = self._get_line_uom(cr, uid, line, context=context)
            pu = 0.0
            if uosqty:
                pu = round(line.price_unit * line.product_uom_qty / uosqty, self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
            fpos = line.order_id.fiscal_position or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
            if not account_id:
                raise osv.except_osv(_('Error!'), _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
            res = {
                'name': line.name,
                'sequence': line.sequence,
                'origin': line.order_id.name,
                'account_id': account_id,
                'price_unit': pu,
                'quantity': uosqty,
                'discount': line.discount,
                'uos_id': uos_id,
                'ucapan': line.ucapan,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }

        return res


sale_order_line()

 
class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
                'sertifikat_line' : fields.one2many('sertifikat.halal', 'product_id', 'Sertifikat Halal'),
    }
    

    def create(self, cr, uid, data, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if user.id != 1:
            raise osv.except_osv(('Perhatian !'), ('Selain admin (Ricky) tidak bisa membuat product  !'))
            
        return super(product_product, self).create(cr, uid, data, context)


product_product()


class sertifikat_halal(osv.osv):
    _name = "sertifikat.halal"        
    _columns = {
        'name': fields.text('No. Sertifikat'),
        'expired' : fields.date('Expired Date'),
        'product_id': fields.many2one('product.product', 'Sertifikat Halal', required=True, ondelete='cascade'),
    }

sertifikat_halal()     