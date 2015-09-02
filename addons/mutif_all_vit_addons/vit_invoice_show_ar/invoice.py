from osv import fields, osv, orm
import decimal_precision as dp

class account_invoice(osv.osv):
    _name    = "account.invoice"
    _inherit = "account.invoice" 

    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        context={}
        account_move_line = self.pool.get('account.move.line')

        for invoice in self.browse(cr, uid, ids, context=context):
            for ar in invoice.outstanding_ar_ids:
                account_move_line.write(cr, uid, ar.id, {'is_used':True}, context={})
        return res

    def action_cancel(self, cr, uid, ids, *args):
        r = super(account_invoice, self).action_cancel(cr, uid, ids, *args)
        context={}
        account_move_line = self.pool.get('account.move.line')

        for invoice in self.browse(cr, uid, ids, context=context):
            for ar in invoice.outstanding_ar_ids:
                account_move_line.write(cr, uid, ar.id, {'is_used':False}, context={})
        return r             

    def _outstanding_debit(self, cr, uid, ids, field, arg, context=None):
        results = {}
        for inv in self.browse(cr, uid, ids, context=context):
            results[inv.id] = 0.0
            for ar in inv.outstanding_ar_ids:
                results[inv.id] += ar.debit                
        return results 

    def _outstanding_credit(self, cr, uid, ids, field, arg, context=None):
        results = {}
        for inv in self.browse(cr, uid, ids, context=context):
            results[inv.id] = 0.0
            for ar in inv.outstanding_ar_ids:
                results[inv.id] += ar.credit                 
        return results 

    def _net_total(self, cr, uid, ids, field, arg, context=None):
        results = {}
        # return harus berupa dictionary dengan key id session
        # contoh kalau 3 records:
        # {
        #      1 : 50.8,
        #      2 : 25.5,
        #      3 : 10.0
        # }
        for inv in self.browse(cr, uid, ids, context=context):
            results[inv.id] = inv.amount_total + inv.outstanding_debit - inv.outstanding_credit
        return results    

    _columns = {
        'outstanding_ar_ids' : fields.many2many(
                    'account.move.line',     # 'other.object.name' dengan siapa dia many2many
                    'invoice_aml',     # 'relation object'
                    'invoice_id',            # 'actual.object.id' in relation table
                    'aml_id',           # 'other.object.id' in relation table
                    'Outstanding AR',              # 'Field Name'
                    required=False),
        'outstanding_debit': fields.function(_outstanding_debit, string="Total AR Unpaid",  type="float"),
        'outstanding_credit': fields.function(_outstanding_credit, string="Total AR Paid", type="float"),
        'net_total'   : fields.function(_net_total,  string="Net Total", type="float")
    }

    def fill_ar(self,cr,uid,ids,context=None):

        aml_obj =self.pool.get('account.move.line')
        inv_obj =self.pool.get('account.invoice')

        # import pdb; pdb .set_trace()
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type=='out_invoice':
                cr.execute("delete from invoice_aml where invoice_id=%d" % (inv.id) )

                cond = [
                         # ('is_used', '=', False ),
                         '|',('reconcile_id', '=', False),
                            ('reconcile_partial_id', '!=', False),
                         ('account_type', '=', 'receivable'),
                         ('partner_id','=', inv.partner_id.id)
                    ]
                aml_ids = aml_obj.search(cr, uid, cond, context=context)

                if aml_ids:
                    amls = aml_obj.browse(cr, uid, aml_ids, context=context)
                    ar_lines = [ aml.id for aml in amls ]
                    data = { 'outstanding_ar_ids' : [(6,0, ar_lines)] }
                    inv_obj.write(cr, uid, [inv.id], data, context=context)
        
        return True 

    def create(self, cr, uid, vals, context=None):
        id = super(account_invoice, self).create(cr, uid, vals, context=context)    
        inv = self.browse(cr, uid, id, context=context)
        if inv.type=='out_invoice': #sales
            self.fill_ar(cr, uid, [id], context=context)

        return id
account_invoice()


class account_move_line(osv.osv):
    _name = "account.move.line"
    _inherit = "account.move.line" 
    

    _columns = {
        'is_used' : fields.boolean('Is Used', help="Is User in other invoices as deposit"),
        'account_type': fields.related('account_id', 'type' , type="char", 
            relation="account.account", string="Account Type", store=False)

    }
account_move_line()



