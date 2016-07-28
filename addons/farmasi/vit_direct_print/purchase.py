# -*- coding: utf-8 -*-
from openerp.osv import osv, fields

class purchase_order(osv.osv):
    _inherit  = 'purchase.order'

    _columns = {
        'printer_data': fields.text('Printer Data'),  
    }



    def write_printer_data(self,cr,uid,ids,context):
        # siapkan format penulisan L,R or C
        def just_left(length,content):
            txtFormat=''
            txtFormat = '{:<%d}' % length
            return txtFormat.format(content)
        def just_right(length,content):
            txtFormat=''
            txtFormat = '{:>%d}' % length
            return txtFormat.format(content)
        def just_center(length,content):
            txtFormat=''
            txtFormat = '{:%s^%d}' % (separator,length)
            return txtFormat.format(content) 
        
        # grs separator 95chrs length
        separator="-----------------------------------------------------------------------------------------------"
        
        result=""
        data = self.browse(cr,uid,ids[0],)
        comp = data.company_id.name.upper()
        address = ' '.join([str(data.company_id.street or ''),
                                    str(data.company_id.street2 or ''),
                                    str(data.company_id.city or ''),
                                    str(data.company_id.state_id 
                                        and data.company_id.state_id.name or ''),
                                    str(data.company_id.zip or ''),
                                    str(data.company_id.country_id 
                                        and data.company_id.country_id.name or '')])

        partner = data.partner_id.name
        partner_address = ' '.join([str(data.partner_id.street or ''),
                                    str(data.partner_id.street2 or ''),
                                    str(data.partner_id.city or '')])
        partner_phone = ' '.join(["Phone : ",str(data.partner_id.phone or ''), ", Fax : ", 
            str(data.partner_id.fax or '') ])

        titles = "\t\t\tPURCHASE ORDER"
        subtitleH = "\t".join(["No.Order :", "Order Date :","\tValidated By :","\t\t" + partner])
        if data.validator.name != False:
            subtitle1 = "\t".join([ data.name, "\t" + data.date_order, data.validator.name,"\t\t" + 
                partner_address])
        else:
            subtitle1 = ""
        subtitle2 = "\t\t\t\t\t\t\t\t\t" + partner_phone

        # max character length each column, will be joined by single space
        lgt = [24,14,10,14,12,16]        
        lineH = ["Description","Taxes","Date Req.","Qty","Unit Price","Net Price"]

        # format header
        header = ' '.join([just_left(lgt[0],lineH[0]),just_left(lgt[1],lineH[1]),
            just_left(lgt[2],lineH[2]),just_left(lgt[3],lineH[3]),
            just_left(lgt[4],lineH[4]),just_left(lgt[5],lineH[5])])
        
        lines=[]
        rp = data.currency_id.symbol

        for line in data.order_line:
            taxes = ",".join([tax.name for tax in line.taxes_id]) or " "
            lines.append(' '.join([
                    just_left(lgt[0],line.name[:24]),
                    just_left(lgt[1],taxes[:14]), 
                    just_left(lgt[2],str(line.date_planned)), 
                    just_right(lgt[3]," ".join([str(line.product_qty),line.product_uom.name])),
                    just_right(lgt[4]," ".join([rp,str(line.price_unit)])),
                    just_right(lgt[5]," ".join([rp,str(line.price_subtotal)])) 
                    ]))
            if line.name[25:] or taxes[15:]:
                lines.append(" ".join([just_left(lgt[0],line.name[25:48]),just_left(lgt[1],taxes[15:])]))
        result = '\n'.join([comp,address,separator,titles,subtitleH,subtitle1,subtitle2,
            separator,
            header,separator]+lines)
        self.write(cr,uid,ids,{'printer_data': result})
        return  True
