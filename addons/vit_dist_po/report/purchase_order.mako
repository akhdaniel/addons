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
    </style>
</head>

<body>
    <div class="page" width="100px">
        <h3>${ o.state in ['draft','sent'] and 'Request for Quotation ' or 'Purchase Order '} ${o.name}</h3>
        <table frame="void" width="100%">
            <tr>
                <td width="10%">Supplier</td>
                <td width="2%"> : </td>
                <td class="title">${o.partner_id.name}</td>
                <td class="aright">Printed by ${user.name}</td>
            </tr>
            <tr>
                <td width="10%">Destination</td>
                <td width="2%"> : </td>
                <td class="title">${o.location_id.name}</td>
            </tr>
            <tr>
                <td width="10%">Partner Reff.</td>
                <td width="2%"> : </td>
                <td class="title">${o.partner_ref or ''}</td>
            </tr>
            <tr>
                <td width="10%">Order Date</td>
                <td width="2%"> : </td>
                <td class="title">${formatLang(o.date_order, date=True)}</td>
            </tr>
            <tr>
                <td width="10%">Total Value</td>
                <td width="2%"> : </td>
                <td class="title">Rp ${formatLang(o.amount_total, digits=0)}</td>
            </tr>
            <!-- <p class="aright title" style="font-size: 12px;background: rgba(0, 0, 0, 0.1)">Total : Rp ${o.amount_total}</p> -->
        </table>       

        <!-- W1 -->
        %if o.order_line :
        <table  style="page-break-inside: avoid" class="list_table" width="100%" cellpadding="5" cellspacing="20">
            <thead>
                <tr>
                    <th>No.</th>
                    <th>Kategori</th>
                    <th>Nama Barang</th>
                    <th>Harga per karton</th>
                    <th>Kode Brg. JHHP</th>
                    <th>Quantity</th>
                    <th>Unit</th>
                    <th class="col1">Total Rp</th>
                </tr>
            </thead>
            <tbody>
            <% no=1 %>
            % for l in o.order_line:
                <tr>
                    <td>${no}</td>
                    <td>${l.product_id.categ_id.name}</td>
                    <td>${l.name}</td>
                    <td class="aright">${formatLang(l.price_unit)}</td>
                    <td>${l.product_id.seller_ids and l.product_id.seller_ids[0].product_code or ''}</td>
                    <td class="aright">${formatLang(l.product_qty)}</td>
                    <td>${l.product_uom.name}</td>
                    <td class="col1 aright">${formatLang(l.price_subtotal,digits=0)}</td>
                </tr>
            %endfor
            </tbody>
        </table> 
        %endif
        

    </div>
    <p style="page-break-after:always"></p>
</body>
</html>
% endfor