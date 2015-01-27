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

    # def create(self, cr, uid, vals, context=None):
    #     # Header Invoice adalah number bukan name
    #     emp = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)],)
    #     loc = self.pool.get('hr.employee').browse(cr,uid,emp[0],).location_id.code
    #     invname = str(loc or '') + '-BPJ/' + time.strftime("%y") + '-' + self.pool.get('ir.sequence').get(cr, uid, 'account.invoice.vit.seq')
    #     vals['name'] = invname 
    #     return super(account_invoice, self).create(cr, uid, vals, context=context)

    _columns = {
        'no_do' : fields.function(
            _search_DO,
            type='char',
            obj="stock.picking",
            method=True,
            store=True,
            string='Drop Order(s)'),
        'number': fields.char(readonly=True, size=64, string='Number'),
    }

    def action_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #TODO: not correct fix but required a frech values before reading it.
        self.write(cr, uid, ids, {})

        for obj_inv in self.browse(cr, uid, ids, context=context):
            invtype = obj_inv.type
            number = obj_inv.number
            move_id = obj_inv.move_id and obj_inv.move_id.id or False
            reference = obj_inv.reference or ''

            self.write(cr, uid, ids, {'internal_number': number})

            if invtype in ('in_invoice', 'in_refund'):
                # ganti number supplier_invoice
                emp = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)],)
                loc = self.pool.get('hr.employee').browse(cr,uid,emp[0],).location_id.code
                invname = str(loc or '') + '-SPJ/' + time.strftime("%y") + '-' + self.pool.get('ir.sequence').get(cr, uid, 'account.invoice.vit.seq')
                self.write(cr, uid, ids, {'number':invname})

                if not reference:
                    ref = self._convert_ref(cr, uid, number)
                else:
                    ref = reference
            else:
                ref = self._convert_ref(cr, uid, number)

            cr.execute('UPDATE account_move SET ref=%s ' \
                    'WHERE id=%s AND (ref is null OR ref = \'\')',
                    (ref, move_id))
            cr.execute('UPDATE account_move_line SET ref=%s ' \
                    'WHERE move_id=%s AND (ref is null OR ref = \'\')',
                    (ref, move_id))
            cr.execute('UPDATE account_analytic_line SET ref=%s ' \
                    'FROM account_move_line ' \
                    'WHERE account_move_line.move_id = %s ' \
                        'AND account_analytic_line.move_id = account_move_line.id',
                        (ref, move_id))
        return True

account_invoice()


class account_invoice_line(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"

    _columns = {
        'harga_po' : fields.float('PO Value',help='Harga beli PO (persatuan besar).', readonly=True),
    }

account_invoice_line()