% for o in objects :
<% setLang(user.lang) %>
<html>
<head>
    <style type="text/css">
        ${css}
        .page {page-break-after: auto}
        .title {font-weight: bold}
        .nominal {text-align: right}
    </style>
</head>

<body>
    <div class="page" style="font-size: 10px">
        <h3>${ o.state in ['draft','sent'] and 'Request for Quotation ' or 'Purchase Order '} ${o.name}</h3>
        <table frame="void" width="100%">
            <tr>
                <td width="15%">Supplier</td>
                <td width="2%"> : </td>
                <td class="title">${o.partner_id.name}</td>
            </tr>
            <tr>
                <td width="15%">Destination</td>
                <td width="2%"> : </td>
                <td class="title">${o.location_id.name}</td>
            </tr>
            <tr>
                <td width="15%">Partner Reff.</td>
                <td width="2%"> : </td>
                <td class="title">${o.partner_ref or ''}</td>
            </tr>
            <tr>
                <td width="15%">Order Date</td>
                <td width="2%"> : </td>
                <td class="title">${formatLang(o.date_order, date=True)}</td>
            </tr>
        </table>
        <!--<h3>Purchase Order Details</h3>-->
        <table class="list_table" width="100%" cellpadding="5" cellspacing="20">
            <thead>
                <tr>
                    <th colspan=5></th>
                    <th colspan=2 style="background: rgba(0, 0, 0, 0.1)">Purchase Order 1</th>
                    <th colspan=2>Purchase Order 2</th>
                    <th colspan=2 style="background: rgba(0, 0, 0, 0.1)">Purchase Order 3</th>
                    <th colspan=2>Purchase Order 4</th>
                    <th colspan=2 style="background: rgba(0, 0, 0, 0.2)">Total PO</th>
                </tr>
                <tr>
                    <th>Kategori</th>
                    <th>Nama Barang</th>
                    <th>Harga per karton</th>
                    <th>Kode Brg. JHHP</th>
                    <th>Unit</th>
                    <th style="background: rgba(0, 0, 0, 0.1)">Jumlah</th>
                    <th style="background: rgba(0, 0, 0, 0.1)">Total Rp</th>
                    <th>Jumlah</th>
                    <th>Total Rp</th>
                    <th style="background: rgba(0, 0, 0, 0.1)">Jumlah</th>
                    <th style="background: rgba(0, 0, 0, 0.1)">Total Rp</th>
                    <th>Jumlah</th>
                    <th>Total Rp</th>
                    <th style="background: rgba(0, 0, 0, 0.2)">Jumlah</th>
                    <th style="background: rgba(0, 0, 0, 0.2)">Total Rp</th>
                </tr>
            </thead>
            <tbody>
            % for l in o.order_line:
                <tr>
                    <td>${l.product_id.categ_id.name}</td>
                    <td>${l.name}</td>
                    <td class="nominal">${formatLang(l.price_unit)}</td>
                    <td>${l.product_id.seller_ids and l.product_id.seller_ids[0].product_code or ''}</td>
                    <td>${l.product_uom.name}</td>
                    <td style="background: rgba(0, 0, 0, 0.1)" class="nominal">${formatLang(l.w1 or 0)}</td>
                    <td style="background: rgba(0, 0, 0, 0.1)" class="nominal">${formatLang(l.price_unit * l.w1 or 0)}</td>
                    <td class="nominal">${formatLang(l.w2 or 0)}</td>
                    <td class="nominal">${formatLang(l.price_unit * l.w2 or 0)}</td>
                    <td style="background: rgba(0, 0, 0, 0.1)" class="nominal">${formatLang(l.w3 or 0)}</td>
                    <td style="background: rgba(0, 0, 0, 0.1)" class="nominal">${formatLang(l.price_unit * l.w3 or 0)}</td>
                    <td class="nominal">${formatLang(l.w4 or 0)}</td>
                    <td class="nominal">${formatLang(l.price_unit * l.w4 or 0)}</td>
                    <td style="background: rgba(0, 0, 0, 0.2)" class="nominal">${formatLang(l.product_qty or 0)}</td>
                    <td style="background: rgba(0, 0, 0, 0.2)" class="nominal">${formatLang(l.price_subtotal or 0)}</td>
                </tr>
            % endfor
            </tbody>
        </table> 
    <p class="nominal title" style="font-size: 12px">Total : Rp ${o.amount_total}</p>
    <br/>
    <br/>
    Printed by ${user.name}
    </div>
    <p style="page-break-after:always"></p>
</body>
</html>
% endfor