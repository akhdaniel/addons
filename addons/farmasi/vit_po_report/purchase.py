from openerp.osv import osv, fields

class purchase_order(osv.osv):
    _inherit  = 'purchase.order'

    _columns = {
        'barcode_data': fields.text('Barcode Data'),  
    }

    def write_bc(self,cr,uid,ids,context):
        result=""
        separator="-----------------------------------------------------------------------------------------------------------------------------------------------"
        data = self.browse(cr,uid,ids[0],)
        comp = data.company_id.name.upper()
        alamat = ' '.join([str(data.company_id.street or ''),
                                    str(data.company_id.street2 or ''),
                                    str(data.company_id.city or ''),
                                    str(data.company_id.state_id and data.company_id.state_id.name or ''),
                                    str(data.company_id.zip or ''),
                                    str(data.company_id.country_id and data.company_id.country_id.name or '')])
        if data.company_id.partner_id.npwp:
            alamat = "\n".join([alamat,data.company_id.partner_id.npwp])
        kpd = data.partner_id.name
        almatkpd = ' '.join([str(data.partner_id.street or ''),
                                    str(data.partner_id.street2 or ''),
                                    str(data.partner_id.city or '')])
        phkpd = ' '.join(["phone : ",str(data.partner_id.phone or ''), ", fax : ", str(data.partner_id.fax or ''), data.partner_id.npwp and str(", NPWP : "+data.partner_id.npwp) or ''])

        titles = "\t\t\tPURCHASE ORDER"
        subtitleH = "\t".join(["No.Order :", "Order Date :","\tValidated By :","\t\t" + kpd])
        subtitle1 = "\t".join([ data.name, "\t" + data.date_order, data.validator.name,"\t\t" + almatkpd])
        subtitle2 = "\t\t\t\t\t\t\t\t\t" + phkpd
        lines=[]
        lineH = "\t".join(["Description\t\t\t\t","Taxes\t\t","Date Req.\t","Qty","Unit Price","Net Price"])
        rp = data.currency_id.symbol
        for line in data.order_line:
            taxes = ",".join([tax.name for tax in line.taxes_id]) or "\t\t\t"
            lines.append('\t'.join([line.name[:43],
                                                    taxes, 
                                                    str(line.date_planned), 
                                                    " ".join([str(line.product_qty),line.product_uom.name]),
                                                    " ".join([rp,str(line.price_unit)]),
                                                    " ".join([rp,str(line.price_subtotal)])
                                                    ]))
            # import pdb;pdb.set_trace()
            # print(len(lines[len(lines)-1]))
            if line.name[43:]:
                lines.append(line.name[43:86])
        result = '\n'.join([comp,alamat,separator,titles,subtitleH,subtitle1,subtitle2,separator,lineH,separator]+lines)
        self.write(cr,uid,ids,{'barcode_data': result})
        return  True
