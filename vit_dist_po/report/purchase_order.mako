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
    <div class="page">
        <h1>${ o.state in ['draft','sent'] and 'Request for Quotation ' or 'Purcahse Order '} ${o.name}</h1>
        <table frame="void" width="100%">
            <tr>
                <td width="20%">Supplier</td>
                <td width="5%"> : </td>
                <td class="title">${o.partner_id.name}</td>
            </tr>
            <tr>
                <td width="20%">Destination</td>
                <td width="5%"> : </td>
                <td class="title">${o.location_id.name}</td>
            </tr>
            <tr>
                <td width="20%">Partner Reff.</td>
                <td width="5%"> : </td>
                <td class="title">${o.partner_ref or ''}</td>
            </tr>
            <tr>
                <td width="20%">Order Date</td>
                <td width="5%"> : </td>
                <td class="title">${formatLang(o.date_order, date=True)}</td>
            </tr>
        </table>
        <h3>Purchase Order Details</h3>
        <table class="list_table" width="100%" cellpadding="10" cellspacing="0">
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Barcode</th>
                    <th>Product</th>
                    <th>Sgt. order</th>
                    <th>Adj.</th>
                    <th>Quantity</th>
                    <th>Unit</th>
                    <th>Price Unit</th>
                    <th>Subtotal</th>
                    <th>Weight</th>
                    <th>Volume</th>
                    <th>Avg MT</th>
                    <th>Avg GT</th>
                    <th>Forecast MT</th>
                    <th>Forecast GT</th>
                    <th>Buffer MT</th>
                    <th>Buffer GT</th>
                    <th>Sales 3M</th>
                    <th>Stock</th>
                    <th>Ending Inv</th>
                    <th>In Transit</th>
                    <th>Stock Cover</th>
                    <th>W1</th>
                    <th>W2</th>
                    <th>W3</th>
                    <th>W4</th>
                </tr>
            </thead>
            <tbody>
            % for l in o.order_line:
                <tr>
                    <td>${l.int_code}</td>
                    <td>${l.barcode}</td>
                    <td>${l.name}</td>
                    <td class="nominal">${formatLang(l.suggested_order, digits=0)}</td>
                    <td class="nominal">${formatLang(l.adjustment, digits=0)}</td>
                    <td class="nominal">${formatLang(l.product_qty, digits=0)}</td>
                    <td>${l.product_uom.name}</td>
                    <td class="nominal">${formatLang(l.price_unit)}</td>
                    <td class="nominal">${formatLang(l.price_subtotal)}</td>
                    <td class="nominal">${formatLang(l.prod_weight, digits=0)}</td>
                    <td class="nominal">${formatLang(l.prod_volume, digits=0)}</td>
                    <td class="nominal">${formatLang(l.avgMT, digits=0)}</td>
                    <td class="nominal">${formatLang(l.avgGT, digits=0)}</td>
                    <td class="nominal">${formatLang(l.forecastMT, digits=0)}</td>
                    <td class="nominal">${formatLang(l.forecastGT, digits=0)}</td>
                    <td class="nominal">${formatLang(l.bufMT, digits=0)}</td>
                    <td class="nominal">${formatLang(l.bufGT, digits=0)}</td>
                    <td class="nominal">${formatLang(l.sales_3m, digits=0)}</td>
                    <td class="nominal">${formatLang(l.stock_current, digits=0)}</td>
                    <td class="nominal">${formatLang(l.ending_inv, digits=0)}</td>
                    <td class="nominal">${formatLang(l.in_transit, digits=0)}</td>
                    <td class="nominal">${formatLang(l.stock_cover, digits=0)}</td>
                    <td class="nominal">${formatLang(l.w1)}</td>
                    <td class="nominal">${formatLang(l.w2)}</td>
                    <td class="nominal">${formatLang(l.w3)}</td>
                    <td class="nominal">${formatLang(l.w4)}</td>
                </tr>
            % endfor
            </tbody>
        </table> 
    <br/>
    <br/>
    Printed by ${user.name} - ${time}
    </div>
    <p style="page-break-after:always"></p>
</body>
</html>
% endfor