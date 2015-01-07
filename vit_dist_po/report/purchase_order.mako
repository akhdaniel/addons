% for o in objects :
<% setLang(user.lang) %>
<html>
<head>
    <style type="text/css">
        ${css}
        .page   { page-break-after: auto}
        .title  { font-weight: bold}
        .aright { text-align: right !important}
        .col1   { background: rgba(0, 0, 0, 0.1)}
        .colt   { background: rgba(0, 0, 0, 0.2)}
        .tbltd  { border-bottom-style:none !important}
        .pbtr   { page-break-inside:avoid !important; page-break-after:always !important}
        @media print {
            tr.page-break  { display: block; page-break-before: always; }
        }   
        .oe_text_center {text-align: center;}
        .oe_clear {clear: both;}
    </style>
</head>

<body>
    <div class="page" width="100px">
        <h3 class="oe_text_center">${ o.state in ['draft','sent'] and 'Request for Quotation ' or 'Purchase Order '}</h3>
        <table frame="void" width="100%">
            <tr>
                <td width="15%">No. Bukti</td>
                <td width="1%"> : </td>
                <td class="title">${o.name}   [ ${o.partner_ref or ''} ]</td>
                <td class="aright">Printed by ${user.name}</td>
            </tr>
            <tr>
                <td width="15%">Supplier/Vendor/Principal</td>
                <td width="1%"> : </td>
                <td class="title">${o.partner_id.name}</td>
            </tr>
            <tr>
                <td width="15%" style="vertical-align:top">Source Data</td>
                <td width="1%"  style="vertical-align:top"> : </td>
                <td class="title">
                    % for loc in o.location_ids:
                        <div>${loc.name} </div>
                    % endfor
                </td>
            </tr>
            <tr>
                <td width="15%">Ship to</td>
                <td width="1%"> : </td>
                <td class="title">${o.location_id.name}</td>
            </tr>
            <tr>
                <td width="15%">Order Date</td>
                <td width="1%"> : </td>
                <td class="title">${formatLang(o.date_order, date=True)}</td>
            </tr>
            <tr>
                <td width="15%">Plan Receiving Date</td>
                <td width="1%"> : </td>
                <td class="title"> 
                <% 
                    dates=[]
                    for x in [o.w1,o.w2,o.w3,o.w4,o.w5,o.w6,o.w7,o.w8,o.w9,o.w10,o.w11,o.w12,o.w13,o.w14,o.w15,o.w16,o.w17,o.w18,o.w19,o.w20]:
                        if x != 'False': 
                            dates.append(x)
                        endif 
                    endfor
                    dates = sorted(dates,reverse=False) 
                    a = len(dates)-1
                %>
                ${dates != [] and formatLang(dates[0], date=True) or ''} - ${ a>0 and formatLang(dates[a], date=True) or ''}
                </td>
            </tr>
            <tr>
                <td width="10%">Total Value</td>
                <td width="2%"> : </td>
                <td class="title">Rp ${formatLang(o.amount_total, digits=0)}</td>
            </tr> 
            <!-- <p class="aright title" style="font-size: 12px;background: rgba(0, 0, 0, 0.1)">Total : Rp ${o.amount_total}</p> -->
        </table>  
        <p class="oe_clear"> </p>     

        <!-- W1 -->
        %if o.order_line :
        <table  style="page-break-inside: avoid" class="list_table" width="100%" cellpadding="5" cellspacing="20">
            <thead>
                <tr class="col1">
                    <th>No</th>
                    <th>Kode</th>
                    <th>Barcode</th>
                    <th>Nama Barang</th>
                    <th class="aright">Saran Order</th>
                    <th class="aright">Qty Besar</th>
                    <th>Satuan Besar</th>
                    <th class="aright">Qty Kecil</th>
                    <th>Satuan Kecil</th>
                    <th class="aright">Final Order</th>
                    <th class="aright">Harga Beli</th>
                    <th class="aright">Subtotal</th>
                    <th class="aright">Avg MT</th>
                    <th class="aright">Avg GT</th>
                    <th class="aright">Forecast MT </th>
                    <th class="aright">Forecast GT </th>
                    <th class="aright">Buffer MT </th>
                    <th class="aright">Buffer GT </th>
                    <th class="aright">Stock Current </th>
                    <th class="aright">Est. Stock Akhir </th>
                    <th class="aright">In Transit </th>
                    <th class="aright">Cover Weeks </th>
                </tr>
            </thead>
            <tbody>
            <% no=1 %>
            % for l in o.order_line:
                <tr>
                    <td>${no}</td>
                    <td>${l.int_code}</td>
                    <td>${l.product_id.seller_ids and l.product_id.seller_ids[0].product_code or ''}</td>
                    <td>${l.name}</td>
                    <td class="aright">${formatLang(l.suggested_order)}</td>
                    <td class="aright">${formatLang(l.adjustment)}</td>
                    <td>${l.product_uom.name}</td>
                    <td class="aright">${formatLang(l.small_qty)}</td>
                    <td>${l.small_uom.name or ''}</td>
                    <td class="aright">${formatLang(l.product_qty)}</td>
                    <td class="aright">${formatLang(l.price_unit)}</td>
                    <td class="aright">${formatLang(l.price_subtotal,digits=0)}</td>
                    <td class="aright">${formatLang(l.avgMT)}</td>
                    <td class="aright">${formatLang(l.avgGT)}</td>
                    <td class="aright">${formatLang(l.forecastMT)}</td>
                    <td class="aright">${formatLang(l.forecastGT)}</td>
                    <td class="aright">${formatLang(l.bufMT)}</td>
                    <td class="aright">${formatLang(l.bufGT)}</td>
                    <td class="aright">${formatLang(l.stock_current)}</td>
                    <td class="aright">${formatLang(l.ending_inv)}</td>
                    <td class="aright">${formatLang(l.in_transit)}</td>
                    <td class="aright">${formatLang(l.stock_cover)}</td>
                </tr>
                <% no+=1 %>
            %endfor
            </tbody>
        </table> 
        %endif
    %if o.notes:
    <br/>Keterangan :<br/>
    <div>
    <table width="500px">
        <tr><td>${str(o.notes)}</td></tr>
    </table> 
    </div>
    %endif
    </div>
</body>
</html>
% endfor