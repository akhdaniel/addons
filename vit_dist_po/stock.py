from openerp.osv import fields,osv
from openerp import tools,netsvc
import time

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

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

    def test_bypass(self, cr, uid, ids, context=None):
        """ Test whether the move lines are done or not.
        @return: True or False
        """
        ok = False
        for pick in self.pool.get('stock.picking.in').browse(cr, uid, ids, context=context):
            if pick.state=='logistic_received':
                ok = True
        return ok

    # FIXME: needs refactoring, this code is partially duplicated in stock_move.do_partial()!
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom',False)
                product_price = partial_data.get('product_price',0.0)
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if product.id not in product_avail:
                        # keep track of stock on hand including processed lines not yet marked as done
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price, round=False)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        if product_avail[product.id] <= 0:
                            product_avail[product.id] = 0
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id])\
                                + (new_price * qty))/(product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})

                        product_avail[product.id] += qty

            # every line of the picking is empty, do not generate anything
            empty_picking = not any(q for q in move_product_qty.values() if q > 0)

            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking and not empty_picking:
                    new_picking_name = pick.name
                    self.write(cr, uid, [pick.id], 
                               {'name': sequence_obj.get(cr, uid,
                                            'stock.picking.%s'%(pick.type)),
                               })
                    pick.refresh()
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': new_picking_name,
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty': move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty
                            'prodlot_id': False,
                            'tracking_id': False,
                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], context=context)
                # workflow overide 
                import pdb;pdb.set_trace()
                if not context.get('bypass',False):
                    wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
                self.message_post(cr, uid, new_picking, body=_("Back order <em>%s</em> has been <b>created</b>.") % (pick.name), context=context)
            elif empty_picking:
                delivered_pack_id = pick.id
            else:
                self.action_move(cr, uid, [pick.id], context=context)
                import pdb;pdb.set_trace()
                if not context.get('bypass',False):
                    wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res

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
        # 'state':fields.related('pick_in_id','state',type="char",relation="stock.picking.in",string="State",store=True),
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
        'pick_in_id' : fields.many2one('stock.picking.in',"Picking",ondelete='cascade'),
        'bad_product_qty' : fields.float("Loss"),
        'product_id' : fields.many2one('product.product',"Products"),
        'barcode' : fields.related('product_id','barcode',type="char",relation="product.product",string="Barcode",store=True),
        'default_code' : fields.related('product_id','default_code',type="selection",relation="product.product",string="Code",store=True),
        'reason': fields.char('Alasan'),
    }

stock_moves_loss_summary()

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    _columns = {
        'move_summary_ids' : fields.one2many('stock.moves.summary','pick_in_id',"Stock move(s)"),
        'move_loss_summary_ids' : fields.one2many('stock.moves.loss.summary','pick_in_id',"Stock move(s) Loss"),
    }

    # overide fungsi done stock move karena ada status cek accounting
    # def test_finished(self, cr, uid, ids):
    #     """ Tests whether the move is in done or cancel state or not.
    #     @return: True or False
    #     """
    #     '''Jika sudah approve accounting, move:done
    #     Implement : overide workflow
    #     '''
    #     pick_in = self.pool.get('stock.picking.in').browse(cr,uid,ids[0],)
    #     move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id', 'in', ids)])
    #     for move in self.pool.get('stock.move').browse(cr, uid, move_ids):
    #         if move.state not in ('done', 'cancel'):
    #             if move.product_qty != 0.0:
    #                 return False
    #             elif pick_in.state == 'logistic_received':
    #                 pick_in.write({'state': 'office_logistic_approved'})
    #                 return False
    #             else:
    #                 move.write({'state': 'done'})
    #     return True

        # pick = self.browse(cr,uid,ids[0],)
        # if pick.type == 'in' and pick.state == 'logistic_received':
        #     self.pool.get('stock.picking.in').write(cr,uid,ids[0],{'state': 'office_logistic_approved'})
        #     return False
        # if pick.type == 'in' and pick.state == 'office_logistic_approved':
        #     return False


class stock_picking_in(osv.osv):
    _name = "stock.picking.in"
    _inherit = "stock.picking.in"        

    def logistik_confirm(self, cr, uid, ids, context=None):
        """ Test oleh logistik.
        @return: True or False
        """
        return self.write(cr,uid,ids,{'state': 'logistic_received'})

    def officeapproved(self, cr, uid, ids, context=None):
        """ Test oleh office logs.
        @return: True or False
        """
        return self.write(cr,uid,ids,{'state': 'office_logistic_approved'})

    def accountingapproved(self, cr, uid, ids, context=None):
        print self.write(cr,uid,ids,{'state': 'done'})

    _columns = {
        'move_summary_ids' : fields.one2many('stock.moves.summary','pick_in_id',"Stock move(s)"),
        'move_loss_summary_ids' : fields.one2many('stock.moves.loss.summary','pick_in_id',"Stock move(s) Loss"),
        'state': fields.selection(
            [('draft', 'Draft'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),     
            ('assigned', 'Ready to Receive'),  
            ('logistic_received', 'Ready to Confirm'),
            ('office_logistic_approved', 'Ready to Approve'),
            ('done', 'Received'),
            ('cancel', 'Cancelled'),],
            'Status', readonly=True, select=True,
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Receive: products reserved, waiting for confirmation in logistics.\n
                 * Ready to Confirm: products confirmed in warehouse, waiting for confirmation in office logistics.\n
                 * Ready to Approve: products confirmed in warehouse, noted, waiting for confirmation in Accounting.\n
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
                sum_move.append((0,0,{'product_qty':int(x[0]),'bad_product_qty':int(x[1]),'product_id':x[2] or False, 'po_qty':po_qty, 'office_qty':int(x[0]) }))

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