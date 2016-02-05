from openerp.osv import osv, fields

class purchase_order(osv.osv):
    _inherit  = 'purchase.order'

    _columns = {
        'barcode_data': fields.text('Barcode Data'),  
    }

    def write_bc(self,cr,uid,ids,context):
        result=""
        data = self.browse(cr,uid,ids[0],)
        comp = data.company_id.name.upper()
        alamat = ' '.join([str(data.company_id.street or ''),
                                    str(data.company_id.street2 or ''),
                                    str(data.company_id.city or ''),
                                    str(data.company_id.state_id and data.company_id.state_id.name or ''),
                                    str(data.company_id.zip or ''),
                                    str(data.company_id.country_id and data.company_id.country_id.name or '')])
        kpd = data.partner_id.name
        almatkpd = ' '.join([str(data.partner_id.street or ''),
                                    str(data.partner_id.street2 or ''),
                                    str(data.partner_id.city or '')])
        phkpd = ' '.join([str(data.partner_id.phone or ''), str(data.partner_id.fax or ''),str(data.partner_id.vat or '')])
        lines=[]
        for line in data.order_line:
            lines.append(' '.join([line.product_id.name,str(line.product_qty),line.product_uom.name,str(line.price_unit),str(line.price_subtotal)]))
        # import pdb;pdb.set_trace()
        result = '\n'.join([comp,alamat,kpd,almatkpd,phkpd]+lines)
        self.write(cr,uid,ids,{'barcode_data': result})
        return  True
