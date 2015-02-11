from openerp.osv import fields,osv
from openerp import tools,netsvc
import time
from openerp.tools.translate import _

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line

            EDIT : add qty : qty big

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

        return {
            'name': name,
            'origin': origin,
            'invoice_id': invoice_id,
            'uos_id': uos_id,
            'product_id': move_line.product_id.id,
            'account_id': account_id,
            'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
            'discount': self._get_discount_invoice(cr, uid, move_line),
            'quantity': move_line.product_uos_qty or move_line.product_qty,
            'qty': move_line.product_uos_qty or move_line.product_qty,
            'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
            'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
        }

    # def action_process(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     """Open the partial picking wizard"""
    #     context.update({
    #         'active_model': self._name,
    #         'active_ids': ids,
    #         'active_id': len(ids) and ids[0] or False
    #     })
    #     return {
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'stock.partial.picking',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #         'context': context,
    #         'nodestroy': True,
    #     }

    # def _get_price_unit_invoice(self, cr, uid, move_line, type, context=None):
    #     """ Gets price unit for invoice
    #     @param move_line: Stock move lines
    #     @param type: Type of invoice
    #     @return: The price unit for the move line
    #     """
    #     if context is None:
    #         context = {}

    #     import pdb;pdb.set_trace()
    #     if type in ('in_invoice', 'in_refund'):
    #         # Take the user company and pricetype
    #         context['currency_id'] = move_line.company_id.currency_id.id
    #         amount_unit = move_line.product_id.price_get('standard_price', context=context)[move_line.product_id.id]
    #         return amount_unit
    #     else:
    #         return move_line.product_id.list_price

    # def test_bypass(self, cr, uid, ids, context=None):
    #     """ Test whether the move lines are done or not.
    #     @return: True or False
    #     """
    #     ok = False
    #     for pick in self.pool.get('stock.picking.in').browse(cr, uid, ids, context=context):
    #         if pick.state=='logistic_received':
    #             ok = True
    #     return ok

    _columns = {
        'move_summary_ids' : fields.one2many('stock.moves.summary','pick_in_id',"Stock move(s)"),
        'move_loss_summary_ids' : fields.one2many('stock.moves.loss.summary','pick_in_id',"Stock move(s) Loss"),
    }

stock_picking()


class stock_moves_summary(osv.osv):
    _name = "stock.moves.summary"
    
    _columns = {
        'pick_in_id' : fields.many2one('stock.picking.in',"Picking",ondelete='cascade'),
        'product_qty' : fields.float("Qty Gudang"),
        'bad_product_qty' : fields.float("Loss"),
        'product_id' : fields.many2one('product.product',"Products"),
        'barcode' : fields.related('product_id','barcode',type="char",relation="product.product",string="Barcode",store=True),
        'default_code' : fields.related('product_id','default_code',type="char",relation="product.product",string="Code",store=True),
        'po_qty': fields.float("Qty DO"),
        'office_qty': fields.float("Qty Office",required=True),
        'gap_qty' : fields.float("Gap"),
        'state':fields.related('pick_in_id','state',type="selection",relation="stock.picking.in",string="State",store=True),
    }

    def onchange_office_qty(self, cr, uid, ids, po_qty, product_qty, office_qty, context=None):
        do = product_qty or 0.00
        of = office_qty or 0.00
        self.write(cr,uid,ids,{'gap_qty':of-do})
        return {'value':{'gap_qty':of-do}}

stock_moves_summary()

class stock_moves_loss_summary(osv.osv):
    _name = "stock.moves.loss.summary"
    _order = 'product_id'
    
    _columns = {
        'pick_in_id' : fields.many2one('stock.picking.in',"Picking",ondelete='cascade',readonly=True),
        'bad_product_qty' : fields.float("Loss",readonly=True),
        'product_id' : fields.many2one('product.product',"Products",readonly=True),
        'barcode' : fields.related('product_id','barcode',type="char",relation="product.product",string="Barcode",store=True,readonly=True),
        'default_code' : fields.related('product_id','default_code',type="char",relation="product.product",string="Code",store=True,readonly=True),
        'reason': fields.char('Alasan',readonly=True),
    }

stock_moves_loss_summary()

# class stock_picking(osv.osv):
#     _name = "stock.picking"
#     _inherit = "stock.picking"

#     _columns = {
#         'move_summary_ids' : fields.one2many('stock.moves.summary','pick_in_id',"Stock move(s)"),
#         'move_loss_summary_ids' : fields.one2many('stock.moves.loss.summary','pick_in_id',"Stock move(s) Loss"),
#     }


class stock_picking_in(osv.osv):
    _name = "stock.picking.in"
    _inherit = "stock.picking.in" 

    def _name_set(self, cr, uid, vals):
        name = vals.get('name') or ''
        emp = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)],)
        loc = self.pool.get('hr.employee').browse(cr,uid,emp,)[0].location_id.code or '---'
        # BDG-SPB/15-0000001
        name = str(loc[:3] or '') + '-SPB/' + time.strftime("%y") + '-' + self.pool.get('ir.sequence').get(cr, uid, 'picking.in.vit.seq')
        return name       

    def create(self, cr, uid, vals, context=None):
        if vals.get('type')=='in':
            vals['name'] = self._name_set(cr, uid, vals) 
        new_id = super(stock_picking_in, self).create(cr, uid, vals, context)
        return new_id

    def logistik_confirm(self, cr, uid, ids, context=None):
        """ Test oleh logistik.
        """
        for move in self.browse(cr,uid,ids,)[0].move_lines:
            if not move.prodlot_id:
                raise osv.except_osv(_('Serial Number kosong!'), _('Isi S/N untuk produk \n%s.') % _(move.product_id.name_template))
        self.write(cr,uid,ids,{'state':'assigned'})
        return True

    def officeapproved(self, cr, uid, ids, context=None):
        """ Receive oleh office logs.
        
        Makes moves done. Send partial picking to accounting
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: true or false
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        self.action_move(cr, uid, ids, context=context)
        self.write(cr,uid,ids,{'state': 'accounting'})           
        return True 

    def accountingapproved(self, cr, uid, ids, context=None):
        print self.write(cr,uid,ids,{'state': 'done'})

    _columns = {
        'move_summary_ids' : fields.one2many('stock.moves.summary','pick_in_id',"Stock move(s)"),
        'move_loss_summary_ids' : fields.one2many('stock.moves.loss.summary','pick_in_id',"Stock move(s) Loss"),
        'state': fields.selection(
            [('draft', 'Draft'),
            ('logistik', 'Receiving logistik'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Receive by Office'),
            ('accounting', 'Checking Accounting'),
            ('done', 'Received'),
            ('cancel', 'Cancelled'),],
            'Status', readonly=True, select=True,
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Receive: products reserved, simply waiting for confirmation.\n
                 * Received: has been processed, can't be modified or cancelled anymore\n
                 * Cancelled: has been cancelled, can't be confirmed anymore"""),
    }

    def query_summarize_stock_move(self,cr, uid,ids, context=None): 
        inship =self.browse(cr,uid,ids,context)[0] 
        mids   =[]
        sum_move=[];sum_loss=[];data=[]
        if inship.move_lines:
            mids    =[x.id for x in inship.move_lines]
            mids    =str(mids)[1:-1]
            cr.execute("""
                SELECT 
                    SUM(product_qty) as product_qty, 
                    SUM(bad_qty) as bad_qty,
                    product_id
                FROM (
                    SELECT product_qty, bad_qty, product_id FROM(
                        SELECT 
                            0 as product_qty,
                            SUM(product_qty) as bad_qty,
                            product_id 
                        FROM stock_move 
                        WHERE 
                            id in ("""+mids+""")
                            AND picking_id = """+str(ids[0])+"""
                            AND is_bad = true
                        GROUP BY product_id) A
                        union all (
                        SELECT 
                            SUM(product_qty) as product_qty,
                            0 as bad_qty,
                            product_id
                        FROM stock_move 
                        WHERE 
                            id in ("""+mids+""")
                            AND picking_id = """+str(ids[0])+"""
                            AND (is_bad is null or is_bad = false)
                        GROUP BY product_id
                        )
                ) as CUMUL
                GROUP BY product_id
                """)
            data = cr.fetchall()

            # Summarize from PO otherwise from stock_move
            if inship.purchase_id:
                po_line = str([l.id for l in inship.purchase_id.order_line])[1:-1]
                cr.execute("SELECT SUM(product_qty) qty,product_id from purchase_order_line where id in ("+po_line+") group by product_id")
                po = cr.fetchall()
            if not inship.purchase_id:
                cr.execute("SELECT SUM(product_qty) qty,product_id from stock_move where id in ("+mids+") group by product_id")
                po = cr.fetchall()
            for x in data:
                po_qty = 0.00
                for p in po:
                    if p[1]==x[2] : po_qty = p[0]
                sum_move.append((0,0,{'product_qty':int(x[0]),'bad_product_qty':int(x[1]),'product_id':x[2] or False, 'po_qty':po_qty, 'office_qty':po_qty }))

            cr.execute("""
                        SELECT 
                            product_qty,
                            product_id,
                            reason
                        FROM stock_move 
                        WHERE 
                            id in ("""+mids+""")
                            AND picking_id = """+str(ids[0])+"""
                            AND is_bad = true
                """)
            data2 = cr.fetchall()
            # grouping by product_id
            #                 SUM(product_qty) as bad_qty,
            #             GROUP BY product_id,reason
            for x in data2:
                sum_loss.append((0,0,{'reason':x[2] or '', 'bad_product_qty':int(x[0]),'product_id':x[1]}))
            
        if inship.move_summary_ids:
            self.pool.get('stock.moves.summary').unlink(cr, uid, [x.id for x in inship.move_summary_ids], context=None)
        if inship.move_loss_summary_ids:
            self.pool.get('stock.moves.loss.summary').unlink(cr, uid, [x.id for x in inship.move_loss_summary_ids], context=None)
        self.write(cr,uid,ids[0],{'move_summary_ids':sum_move,'move_loss_summary_ids':sum_loss})
        return True

    # def summarize_stock_move(self,cr, uid,ids, context=None): 
    #     inship =self.browse(cr,uid,ids,context)[0] 
    #     sum_move=[];data=[];li=[]
    #     import itertools
    #     if inship.move_lines:
    #         for l in sorted(inship.move_lines, key=lambda sku_order: (sku_order.product_id.id,sku_order.is_bad), reverse=False):
    #             li.append({'product_id':l.product_id.id,'product_qty':l.product_qty,'is_bad':l.is_bad})
    #         for key, group in itertools.groupby(li, lambda item: (item["product_id"],item['is_bad'])):
    #             data.append({
    #                 'product_id':key[0],
    #                 'product_qty':not key[1] and sum([item['product_qty'] for item in group]) ,
    #                 'bad_product_qty':key[1] and sum([item['product_qty'] for item in group]) ,
    #                 })
    #         for dat in data:
    #             sum_move.append((0,0,{
    #                 'product_qty':dat['product_qty'],
    #                 'bad_product_qty':dat['bad_product_qty'],
    #                 'product_id':dat['product_id']
    #                 }))
    #     if inship.move_summary_ids:
    #         self.pool.get('stock.moves.summary').unlink(cr, uid, [x.id for x in inship.move_summary_ids], context=None)
    #     self.write(cr,uid,ids[0],{'move_summary_ids':sum_move})
    #     return True

#----------------------------------------------------------
# Stock Location
#----------------------------------------------------------
class stock_location(osv.osv):
    _name = "stock.location"
    _inherit = "stock.location"

    _columns = {
        'bad_location': fields.boolean('Bad Stock', help='Check this box to set as Bad Stock Location.'),
    } 

    _defaults = {
        'bad_location': False,
    }