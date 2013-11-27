from openerp.osv import osv, fields

class lc_management(osv.Model):
    _name = "lc.management"
    _rec_name = "no"

    _columns = {
        'no'  : fields.char("L/C Number",size=13, readonly=True),
        'certificate_date' : fields.date("In-Tank Certificate Date"),
        'readiness_date' : fields.date("Notice of Readiness Date"),
        'cod_date' : fields.date("COD Date"),
        'due_date' : fields.date("Maturity/ Due Date"),
        'credit_extention_due_period' : fields.date("Supplier Credit Extension Due Period"),
        're_financing_date' : fields.date("Re-financing Maturity Date"),
        'proforma_invoice' : fields.float("Proforma Inv. Value + TOL%",digits=(5,2)),
        'revised_invoice' : fields.float("Revised Inv. Value aft Discharge"),
        'lc_value' : fields.float("Final L/C Value"),
        'avail_bank_balance' : fields.float("Available Bank Balance"),
        'net' : fields.float("Net Cash-flow Requirement"),
        'remark' : fields.char("L/C Status or Remark"),
        'purchase_id': fields.many2one('purchase.order',"Purchase Order", domain="[('state','=','approved')]", required=True),
        'invoice_id': fields.many2one('account.invoice',"Supplier Invoice",domain="[('type','=','in_invoice'),('state','=','open')]", required=True),
        'supplier_id': fields.related('invoice_id','partner_id', readonly=True, 
            type="many2one", relation='res.partner', string="Supplier", store=False),
        'bank_name': fields.related('invoice_id','partner_bank_id', readonly=True, 
            type="many2one", relation='res.partner.bank', string="Bank Account", store=False),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Type', readonly=True, select=True, change_default=True, track_visibility='always'),
        }

    _defaults = {
        'no': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'lc.management'),
        }

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"

    _columns = {
        'lc_ids' : fields.one2many('lc.management','invoice_id',"L/C Number", readonly=True)
    }

class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"

    _columns = {
        'lc_ids' : fields.one2many('lc.management','purchase_id',"L/C Number", readonly=True)
    }