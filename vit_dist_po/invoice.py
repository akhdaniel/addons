from openerp.osv import fields, osv
import time

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"

    def _search_DO(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for inv in self.browse(cr,uid,ids,):
            pickings = ''
            separator = ''
            po_ids = self.pool.get('purchase.order').search(cr,uid,[('name','ilike',inv.origin)],)
            if po_ids:
                pick_ids = self.pool.get('stock.picking').search(cr,uid,[('purchase_id','=',po_ids)],)
                for p in pick_ids:
                    pickings += separator + str(self.pool.get('stock.picking').browse(cr,uid,p,).name or '')
                    separator = ', '
            res[inv.id] = pickings
        return res

    def create(self, cr, uid, vals, context=None):
        # Header Invoice adalah number bukan name
        emp = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)],)
        loc = self.pool.get('hr.employee').browse(cr,uid,emp[0],).location_id.code
        invname = str(loc or '') + '-BPJ/' + time.strftime("%y") + '-' + self.pool.get('ir.sequence').get(cr, uid, 'account.invoice.vit.seq')
        vals['name'] = invname 
        return super(account_invoice, self).create(cr, uid, vals, context=context)

    _columns = {
        'no_do' : fields.function(
            _search_DO,
            type='char',
            obj="stock.picking",
            method=True,
            store=True,
            string='Drop Order(s)'),
    }

account_invoice()


class account_invoice_line(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"

    _columns = {
        'harga_po' : fields.float('PO Value',help='Harga beli PO (persatuan besar).', readonly=True),
    }

account_invoice_line()