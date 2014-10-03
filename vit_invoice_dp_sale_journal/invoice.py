from osv import fields, osv, orm
import decimal_precision as dp

class prettyFloat(float):
    def __repr__(self):
        return "%0.4f" % self

class account_invoice_dp(osv.osv):
    _name = "account.invoice.dp"
    def account_move_line_change(self, cr, uid, ids, account_move_line_id):
        result={}
        domain={}
        context={}
        
        vou = self.pool.get('account.move.line').browse(cr, uid, account_move_line_id, context=context)
        result['amount']=vou.credit
        res_final = {'value':result, 'domain':domain}
        return res_final
    
    def account_move_line_change2(self, cr, uid, ids, account_move_line_id):
        result={}
        domain={}
        context={}
        
        vou = self.pool.get('account.move.line').browse(cr, uid, account_move_line_id, context=context)
        result['amount']=vou.debit
        res_final = {'value':result, 'domain':domain}
        return res_final
    
    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice Reference', ondelete='cascade', select=True),
        'account_move_line_id': fields.many2one('account.move.line', 'Down Payment Journals', ondelete='set null'),
        'amount': fields.float('Amount', required=True, digits_compute= dp.get_precision('Account')),
        'account_id': fields.related(
            'account_move_line_id',
            'account_id',
            type='many2one',
            relation='account.account',
            string='Account',
            store=True),
        'date': fields.related(
            'account_move_line_id',
            'date',
            type='date',
            relation='account.account',
            string='Date',
            store=True)

    }
account_invoice_dp()

class account_invoice_purchase_invoice(osv.osv):
    _name = "account.invoice.purchase_invoice"
    
    def purchase_invoice_change(self, cr, uid, ids, purchase_invoice_id):
        result={}
        domain={}
        context={}
        
        inv = self.pool.get('account.invoice').browse(cr, uid, purchase_invoice_id, context=context)
        result['amount']=inv.amount_untaxed
        res_final = {'value':result, 'domain':domain}
        return res_final
        
    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice Reference', ondelete='cascade', select=True),
        'purchase_invoice_id': fields.many2one('account.invoice', 'Purchase Invoices', ondelete='set null'),
        'amount': fields.float('Amount', required=True, digits_compute= dp.get_precision('Account')),
    }
account_invoice_purchase_invoice()

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice" 

    def action_cancel(self, cr, uid, ids, *args):
        r = super(account_invoice, self).action_cancel(cr, uid, ids, *args)
        context={}
        for invoice in self.browse(cr, uid, ids, context=context):
            """
            update account_move_line, set is_used = False
            """
            account_move_line = self.pool.get('account.move.line')
            for dp in invoice.dp_line:
                account_move_line.write(cr, uid, dp.account_move_line_id.id, {'is_used':False}, context={})
            
            """
            update purchase invoices, set is_used = False
            """
            inv_obj = self.pool.get('account.invoice')
            inv_obj.write(cr, uid, ids, {'is_used':False}, context={})


        return r    

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'dp_total':0.0,
                'sub_total':0.0,
                'cost_total':0.0
            }
            if invoice.dp_line:
                for line in invoice.dp_line:
                    res[invoice.id]['dp_total'] += line.amount
            if invoice.purchase_invoice_line:
                for line in invoice.purchase_invoice_line:
                    res[invoice.id]['cost_total'] += line.amount

            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += line.amount

            res[invoice.id]['sub_total'] = res[invoice.id]['amount_untaxed'] 
            res[invoice.id]['amount_untaxed'] -= res[invoice.id]['dp_total'] 
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']

            res[invoice.id]['dp_total'] = prettyFloat(res[invoice.id]['dp_total'])
            res[invoice.id]['sub_total'] = prettyFloat(res[invoice.id]['sub_total'])
            res[invoice.id]['amount_untaxed'] = prettyFloat(res[invoice.id]['amount_untaxed'])
            res[invoice.id]['amount_total'] = prettyFloat(res[invoice.id]['amount_total'])
        return res

    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        result = {}
        result=super(account_invoice, self)._amount_residual(cr, uid, ids, name, args, context=None)
        #import pdb; pdb.set_trace()
        for invoice in self.browse(cr, uid, ids, context=context):
            if result[invoice.id] != 0:
                result[invoice.id] -= invoice.dp_total

        return result

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        :param invoice_browse: browsable record of the invoice that is generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines (as for create())
        :return: the (possibly updated) final move_lines to create for this invoice
        
        CUSOTMER INVOICE (journal_id.type = sales):
        aslinya:
        AR                        4000
            Sales Product 1         1000
            Sales Procuct 2         3000
        COGS                      cost price
            Inventory               cost price
            
        diubah menjadi:
        AR                        2000
        DP Sales 1                1500
        DP Sales 2                 500
            Sales Product 1         1000
            Sales Procuct 2         3000
        COGS                      tot purchase_inv_id
            Inventory               tot purchase_inv_id
        
        setelah itu, update voucher.is_used=true
        
        SUPPLIER INVOICE (journal_id.type = purchase):
        aslinya:
        Inv Product 1         1000
        Inv Procuct 2         3000
            AP                        4000
            
        diubah menjadi:
        Inv Product 1         1000
        Inv Procuct 2         3000
            AP                        2000
            DP Purchase 1             1500
            DP Purchase 2              500
        
        setelah itu, update voucher.is_used=true
        update purchase_invocie.is_used=true
        """
        
        
        company_id = invoice_browse.company_id.id
        company_currency = invoice_browse.company_id.currency_id.id
        diff_currency_p = invoice_browse.currency_id.id <> company_currency
        currency_id = invoice_browse.currency_id.id
        partner_id = move_lines[0][2]['partner_id']
        period_id = invoice_browse.period_id.id
        date_due= invoice_browse.date_due
        journal_type = invoice_browse.journal_id.type
        context={}
        
        
        """
        tambah baris jurnal DP di credit
        """
        total_dp = 0
        if invoice_browse.dp_line:
            for dp in invoice_browse.dp_line:    
                total_dp += prettyFloat(dp.amount)
                dp_acc_id = dp.account_id.id
                
                if journal_type == 'sale':
                    debit = dp.amount
                    credit = 0
                elif journal_type == 'purchase':
                    debit = 0
                    credit = dp.amount
                    
                move_lines.append((0,0,{
                    'name': 'DP Sales',
                    'debit': debit,
                    'credit': credit,
                    'account_id': dp_acc_id,
                    'date_maturity': date_due,
                    'amount_currency': diff_currency_p \
                        and total_dp or False,
                    'currency_id': diff_currency_p \
                        and currency_id or False,
                    'ref': 'DP Sales',
                    'period_id': period_id,
                    'partner_id':partner_id,                           
                 }))

        """
        total purchaes invoice
        """
        # total_cost = 0
        # inv_ids=[]
        # for inv in invoice_browse.purchase_invoice_line:
        #     total_cost += prettyFloat(inv.amount)
        #     inv_ids.append(inv.purchase_invoice_id.id)
        # total_cost = prettyFloat(total_cost)

        """
        jika account = AR , maka kurangi debit nya dengan total DP yang dipakai.
        total DP didapat dari invoice_browse.dp_line.
        """
        account_obj = self.pool.get('account.account')
        i=0
        for ml in move_lines:
            account = account_obj.browse(cr, uid, ml[2]['account_id'])            
            if journal_type == 'sale':
                #kurangi AR 
                if (account and (account.user_type.code == 'receivable' or account.type  == 'receivable') ) \
                and 'debit' in ml[2] :
                    move_lines[i][2]['debit'] -= total_dp

                #update nilai COGS  
                # if (account.user_type.code == 'cogs' or account.type == 'cogs') and 'debit' in ml[2]:
                #     move_lines[i][2]['debit'] = total_cost

                #update nilai Inventory  
                # if (account.user_type.code == 'current asset' or account.type == 'current asset') and 'credit' in ml[2]:
                #     move_lines[i][2]['credit'] = total_cost
                    
            elif journal_type == 'purchase':
                if account and account.id:
                    if (account and (account.user_type.code == 'payable' or account.type  == 'payable') ) \
                    and 'credit' in ml[2] :
                        move_lines[i][2]['credit'] -= total_dp
            i+=1        
        

        """
        now, update account_move_line, set is_used = True
        """
        account_move_line = self.pool.get('account.move.line')
        for dp in invoice_browse.dp_line:
            if dp.account_move_line_id:
                account_move_line.write(cr, uid, dp.account_move_line_id.id, {'is_used':True}, context={})
        
        """
        now, update purchase invoices, set is_used = True
        """
        # invoice = self.pool.get('account.invoice')
        # invoice.write(cr, uid, inv_ids, {'is_used':True}, context={})


        #import pdb; pdb.set_trace()

        return move_lines

    def _get_invoice_line(self, cr, uid, ids, context=None):
        return super(account_invoice, self)._get_invoice_line(cr, uid, ids, context=None)

    def _get_invoice_from_line(self, cr, uid, ids, context=None):
        return super(account_invoice, self)._get_invoice_from_line(cr, uid, ids, context=None)

    def _get_invoice_from_reconcile(self, cr, uid, ids, context=None):
        return super(account_invoice, self)._get_invoice_from_reconcile(cr, uid, ids, context=None)

    _columns = {
        'dp_line'         : fields.one2many('account.invoice.dp', 'invoice_id', 'Down Payment Lines', readonly=True, states={'draft':[('readonly',False)]}),
        'sales_inv'       : fields.char('Sales Invoice', size=64, select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date_eta'        : fields.date('Date ETA', readonly=True, states={'draft':[('readonly',False)]}, select=True, 
                help="Estimate date of goods receival"),
        'ref_partner_id'  : fields.many2one('res.partner', ' Name(Master)', change_default=True, readonly=True, required=False, states={'draft':[('readonly',False)]}),
        'purchase_invoice_line':fields.one2many('account.invoice.purchase_invoice', 'invoice_id', 'Purchase Invoice Lines', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'is_used'         : fields.boolean('Is Used', required=False, default=False),
        'dp_total'        : fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='DP Total',
            store=True,
		#{
            #    'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['description','invoice_line','dp_line'], 20),            
            #},
            multi='all'),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed',
            store=True,
            multi='all'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed',
            store=True,
            multi='all'),
        'cost_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Cost Total',
            store=True,
            multi='all'),
        'sub_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Sub Total',
            store=True,
            multi='all'),
        'residual': fields.function(_amount_residual, digits_compute=dp.get_precision('Account'), string='Balance',
            store=True),
        'sale_dp_account_id' : fields.related('company_id', 'sale_dp_account_id' , type="many2one", 
            relation="account.account", string="Sale DP COA")
    }

    #####################################################################################
    # cari journal dp partner ini , kalau ada masukkan ke dp line
    #####################################################################################
    def fill_sale_dp(self,cr,uid,ids,context=None):
        return self.fill_dp(cr,uid,ids,'sale',context=None)

    def fill_purchase_dp(self,cr,uid,ids,context=None):
        return self.fill_dp(cr,uid,ids,'purchase',context=None)

    def fill_dp(self,cr,uid,ids,type,context=None):

        aml_obj =self.pool.get('account.move.line')
        inv_obj =self.pool.get('account.invoice')

        for inv in self.browse(cr, uid, ids, context=context):

            if type=='sale':
                cond = [('account_id','ilike', 'Uang Muka'), 
                             ('is_used','=',False), 
                             ('credit','>',0), 
                             ('partner_id','=', inv.partner_id.id)]
            elif type=='purchase':
                cond = [('account_id','ilike', 'Uang Muka'), 
                             ('is_used','=',False), 
                             ('debit','>',0), 
                             ('partner_id','=', inv.partner_id.id)]

            aml_ids = aml_obj.search(cr, uid, cond, context=context)

            if aml_ids:

                cr.execute("delete from account_invoice_dp where invoice_id=%d" % (inv.id) )

                amls = aml_obj.browse(cr, uid, aml_ids, context=context)
                dp_lines = [ (0,0,{ 'account_move_line_id': aml.id , 
                                    'amount' : aml.credit + aml.debit
                    }) for aml in amls]

                data = { 'dp_line' : dp_lines }
                inv_obj.write(cr, uid, [inv.id], data, context=context)
        
        return True 

    def create(self, cr, uid, vals, context=None):
        res = super(account_invoice, self).create(cr, uid, vals, context=context)    
        inv = self.browse(cr, uid, res, context=context)
        if inv.type=='out_invoice': #sales
            self.fill_sale_dp(cr, uid, [res], context=context)
        elif inv.type=='in_invoice': #purchase
            self.fill_purchase_dp(cr, uid, [res], context=context)

        return res


account_invoice()

class account_move_line(osv.osv):
    _name = "account.move.line"
    _inherit = "account.move.line" 
    

    _columns = {
        'is_used': fields.boolean('Is Used', required=False, default=False),

    }
account_move_line()


