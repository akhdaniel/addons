# -*- coding: utf-8 -*-
from openerp.osv import osv, fields

class purchase_order(osv.osv):
    _inherit  = 'purchase.order'

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
        def ditengah(length,kata,separator):
            if not separator: separator=" "
            txtFormat=''
            txtFormat = '{:%s^%d}' % (separator,length)
            return txtFormat.format(kata) 
        def diDiv(length,kata):
            kata = kata.split("\n")
            dived=[]
            for kt in kata:
                x0=0
                x=len(kt)
                L=[];st=[];fs=[]
                while x>0:
                    st.append(x0*length)
                    x0+=1
                    fs.append(x0*length)
                    x-=length
                for x,y in zip(st,fs):
                    L.append(kt[x:y])
                dived += L
            return "\n".join(dived)

        # grs separator 95chrs length
        separator="-----------------------------------------------------------------------------------------------"
        
        for data in self.browse(cr,uid,ids,):
            result=""
            comp = data.company_id.name.upper()
            alamatC = ' '.join([str(data.company_id.street or ''),
                                        str(data.company_id.street2 or ''),
                                        str(data.company_id.city or ''),
                                        str(data.company_id.state_id and data.company_id.state_id.name or ''),
                                        str(data.company_id.zip or ''),
                                        str(data.company_id.country_id and data.company_id.country_id.name or '')])
            phoneC = ' '.join([data.company_id.phone and str("phone %s" % data.company_id.phone) or '',  data.company_id.fax and str(", fax %s" % data.company_id.fax) or ''])
            if data.company_id.partner_id.npwp:
                phoneC = " ".join([phoneC,data.company_id.partner_id.npwp])
            
            # Company header
            mainHeader=[dikiri(95,comp),dikiri(95,alamatC),dikiri(95,phoneC),separator]

            partner = data.partner_id.name
            almatkpd = ' '.join([str(data.partner_id.street or ''),
                                        str(data.partner_id.street2 or ''),
                                        str(data.partner_id.city or '')])
            phkpd = ','.join([data.partner_id.phone or '',  data.partner_id.fax and str(" fax %s" % data.partner_id.fax) or ''])
            
            # main title
            titles = []
            hdL=[12,22,22,36]
            tabs = 58
            titles.append(ditengah(tabs,"PURCHASE ORDER"," "))
            titles.append(" ".join([dikiri(hdL[0],"No.Order :"), dikiri(hdL[1],"Order Date :"), dikiri(hdL[2],"Prepared By :"), dikiri(hdL[3],partner[:hdL[3]])]))
            titles.append(" ".join([dikiri(hdL[0],data.name), dikiri(hdL[1],data.date_order), dikiri(hdL[2],data.validator.name), dikiri(hdL[3],almatkpd[:hdL[3]])]))
            if almatkpd[hdL[3]:] : 
                titles.append(" ".join([dikanan(tabs," "),dikiri(hdL[3],almatkpd[hdL[3]:])]))
            titles.append(" ".join([dikanan(tabs," "),dikiri(tabs,phkpd[:hdL[3]])]))
            if phkpd[hdL[3]:] : 
                titles.append(" ".join([dikanan(tabs," "),dikiri(tabs,phkpd[37:])]))

            # lines
            lines=[]
            # panjang karakter max tiap kolom, to joined by single space
            lgt = [24,14,10,14,12,16]        
            lineH = ["Description","Taxes","Date Req.","Qty","Unit Price","Net Price"]
            # format header
            lines.append(separator)
            lines.append(' '.join([dikiri(lgt[0],lineH[0]),dikiri(lgt[1],lineH[1]),dikiri(lgt[2],lineH[2]),dikanan(lgt[3],lineH[3]),dikanan(lgt[4],lineH[4]),dikanan(lgt[5],lineH[5])]) )
            lines.append(separator)
            
            rp = str(data.currency_id.symbol)
            for line in data.order_line:
                taxes=[]
                for tx in line.taxes_id:
                    amt = tx.amount or 0.0
                    if tx.type == 'percent': 
                        taxes.append(" ".join([str(amt/100),"%"]))
                    elif tx.type == 'fixed': 
                        taxes.append(" ".join([rp,str(amt)]))
                    else : taxes.append(tx.name)
                taxes = ",".join(taxes)
                names = diDiv(lgt[0],line.name)
                names = names.split("\n")
                lines.append(' '.join([
                        dikiri(lgt[0],names[0]),
                        dikiri(lgt[1],taxes[:14]), 
                        dikiri(lgt[2],str(line.date_planned)), 
                        dikanan(lgt[3]," ".join([str(line.product_qty),line.product_uom.name])),
                        dikanan(lgt[4]," ".join([rp,str(line.price_unit)])),
                        dikanan(lgt[5]," ".join([rp,str(line.price_subtotal)])) 
                        ]))
                # import pdb;pdb.set_trace()
                if len(names)>1:
                    names.remove(names[0])
                    for nm in names:
                        lines.append(dikiri(lgt[0],nm))
            if data.notes2:
                notes = data.notes2.split("\n")
                lines.append("\n".join(["Catatan :",diDiv(tabs,data.notes2)]))

            result = '\n'.join(mainHeader+titles+lines)
            # import pdb;pdb.set_trace()
            self.write(cr,uid,data.id,{'barcode_data': result})
        print("OKe")
        return  True

    _columns = {
        'barcode_data': fields.text('Barcode Data'),  
    }

