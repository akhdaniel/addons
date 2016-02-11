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
            return  dived
        def cekElem(arrDict):
            # input : arrDict = {'a':arrayA,'b':arrayB,'c':arrayC}
            # output : length array will same acording to the bigest length, append by " "
            kosong = arrDict['kosong']
            arrDict.pop('kosong')
            L=0
            if len(arrDict.keys()) > 1 :
                L= max(len(k) for k in arrDict.values())
                for div in  arrDict.keys():
                    while len(arrDict[div])<L:
                        arrDict[div].append(dikiri(kosong[div]-1," "))
            return arrDict,L

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
            phkpd = ' '.join([data.partner_id.phone or '',  data.partner_id.fax and str(" fax %s" % data.partner_id.fax) or ''])
            
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
            lgt = [26,12,10,14,12,16]        
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
                # names = names.split("\n")
                lines.append(' '.join([
                        dikiri(lgt[0],names[0]),
                        dikiri(lgt[1],taxes[:14]), 
                        dikiri(lgt[2],str(line.date_planned)), 
                        dikanan(lgt[3]," ".join([str(line.product_qty),line.product_uom.name])),
                        dikanan(lgt[4]," ".join([rp,str(line.price_unit)])),
                        dikanan(lgt[5]," ".join([rp,str(line.price_subtotal)])) 
                        ]))
                if len(names)>1:
                    names.remove(names[0])
                    for nm in names:
                        lines.append(dikiri(lgt[0],nm))
            # konstruk div for 3 cols
            footerkiri = []
            Lf={'1':tabs,'2':3,'3':20,'4':12}
            if data.notes2:
                footerkiri += [dikiri(Lf['1'],x) for x in diDiv(tabs,data.notes2)]
            footerkanan1 = [dikiri(Lf['3'],x) for x in ["-------------------","Total Without Taxes", "Taxes","-------------------","Total"]]
            footerkanan2 = [dikanan(Lf['4'],x) for x in  ["------------"," ".join([rp,str(data.amount_untaxed or 0.0)]) ,
                                " ".join([rp,str(data.amount_tax or 0.0)]) ,"------------",
                                " ".join([rp,str(data.amount_total or 0.0)])] ]
            
            kosong=[]
            elem = {}
            elem.update({'1':footerkiri,'2':kosong,'3':footerkanan1,'4':footerkanan2,'kosong':Lf})
            elem,L = cekElem(elem)
            
            L= max(len(k) for k in elem.values())
            i=0
            footer = []
            while i<L:
                all=[]
                for y in zip(x for x in elem.values()):
                    all.append(y[0][i])
                S = " ".join(all)
                footer.append(S)
                i+=1
            # print("\n".join(footer))
            ttd = [separator, ditengah(tabs/2,"    Supplier    "," ")+ditengah(tabs/2,"  Hormat Kami,  "," "), "\n\n"+ditengah(tabs/2,"( ________________ )"," ")+ditengah(tabs/2,"( ________________ )"," ")]
            result = '\n'.join(mainHeader+titles+lines+footer+ttd)
            self.write(cr,uid,data.id,{'barcode_data': result})
        return  True

    _columns = {
        'barcode_data': fields.text('Barcode Data'),  
    }

