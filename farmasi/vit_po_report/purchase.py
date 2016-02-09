# -*- coding: utf-8 -*-
from openerp.osv import osv, fields

class purchase_order(osv.osv):
    _inherit  = 'purchase.order'

    _columns = {
        'barcode_data': fields.text('Barcode Data'),  
    }

    def write_bc(self,cr,uid,ids,context):
        # siapkan format penulisan L,R or C
        def dikiri(length,kata):
            txtFormat=''
            txtFormat = '{:<%d}' % length
            return txtFormat.format(kata)
        def dikanan(length,kata):
            txtFormat=''
            txtFormat = '{:>%d}' % length
            return txtFormat.format(kata)
        def ditengah(length,kata):
            txtFormat=''
            txtFormat = '{:%s^%d}' % (separator,length)
            return txtFormat.format(kata) 
        
        # grs separator 95chrs length
        separator="-----------------------------------------------------------------------------------------------"
        
        result=""
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

        # panjang karakter max tiap kolom, nanti joined by single space
        lgt = [24,14,10,14,12,16]        
        lineH = ["Description","Taxes","Date Req.","Qty","Unit Price","Net Price"]
        # format header
        header = ' '.join([dikiri(lgt[0],lineH[0]),dikiri(lgt[1],lineH[1]),dikiri(lgt[2],lineH[2]),dikiri(lgt[3],lineH[3]),dikiri(lgt[4],lineH[4]),dikiri(lgt[5],lineH[5])])
        
        lines=[]
        rp = data.currency_id.symbol
        # import pdb;pdb.set_trace()
        for line in data.order_line:
            taxes = ",".join([tax.name for tax in line.taxes_id]) or " "
            lines.append(' '.join([
                    dikiri(lgt[0],line.name[:24]),
                    dikiri(lgt[1],taxes[:14]), 
                    dikiri(lgt[2],str(line.date_planned)), 
                    dikanan(lgt[3]," ".join([str(line.product_qty),line.product_uom.name])),
                    dikanan(lgt[4]," ".join([rp,str(line.price_unit)])),
                    dikanan(lgt[5]," ".join([rp,str(line.price_subtotal)])) 
                    ]))
            if line.name[25:] or taxes[15:]:
                lines.append(" ".join([dikiri(lgt[0],line.name[25:48]),dikiri(lgt[1],taxes[15:])]))
        result = '\n'.join([comp,alamat,separator,titles,subtitleH,subtitle1,subtitle2,separator,header,separator]+lines)
        self.write(cr,uid,ids,{'barcode_data': result})
        return  True
