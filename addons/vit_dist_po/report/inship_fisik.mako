% for o in objects :
<% setLang(user.lang) %>
<html>
<head>
    <style type="text/css">
        ${css}
        .page   { page-break-after: auto; font-size : 12px !important}
        .title  { font-weight: bold}
        .aright { text-align: right !important}
        .col1   { background: rgba(0, 0, 0, 0.1)}
        .colt   { background: rgba(0, 0, 0, 0.2)}
        .tbltd  { border-bottom-style:none !important}
        .pbtr   { page-break-inside:avoid !important; page-break-after:always !important}
        .oe_text_center {text-align: center;}
        .oe_right {text-align: right !important}
        .oe_clear {clear: both;}
    </style>
</head>

<body>
    <div class="page">
        <table frame="void" width="100%">
            <tr class="title" style="font-size : 16px !important">
                <td width="50%">${company.partner_id.name |entity} &#13;</td>
                <td width="20%">
                <td class="oe_right">Bukti Penerimaan Barang</td>
            </tr>
            <tr>
                <td >
                ${company.street or ''}
                ${company.street2 or ''}
                ${company.city or ''}
                <!-- ${company.state_id.name or ''} -->
                </td>
                <td ></td>
                <td ></td>
            </tr>
        </table>
        <p class="oe_clear"> </p> 

        <table frame="void" width="100%">
            <thead style="vertical-align:top">
                <tr>
                    <td width="14%">No. Faktur</td>
                    <td width="1%"> : </td>
                    <td width="25%">${o.name}</td>
                    <td width="20%"/>
                    <td width="14%">Pemasok</td>
                    <td width="1%"> : </td>
                    <td width="25%">${o.partner_id.name}</td>
                </tr>
                <tr>
                    <td>Tgl Faktur</td>
                    <td> : </td>
                    <td>${formatLang(o.date, date=True)}</td>
                    <td>

                    <td>Alamat</td>
                    <td> : </td>
                    <td>${o.partner_id.street or ''} 
                    ${o.partner_id.street2 or ''} 
                    ${o.partner_id.city or ''} 
                    <!-- ${o.partner_id.state_id.name or ''} --> 
                    ${o.partner_id.zip or ''} 
                    </td>
                </tr>
                <tr>
                    <td colspan="4"/>

                    <td>Reff.</td>
                    <td> : </td>
                    <td>${o.origin}</td>
                </tr>
            </thead>
        </table>
        <p class="oe_clear"> </p> 

        %if o.move_lines :
        <table  style="page-break-inside: avoid" class="list_table" width="100%" cellpadding="5" cellspacing="20">
            <thead>
                <tr class="col1">
                    <th>No</th>
                    <th>Gudang</th>
                    <th>Nama Barang</th>
                    <th>Qty</th>
                    <th>Unit</th>
                </tr>
            </thead>
            <tbody>
            <% no=1 %>
            % for m in o.move_lines:
                <tr>
                    <td>${no}</td>
                    <td>${m.location_dest_id.name}</td>
                    <td>${m.product_id.name}</td>
                    <td class="aright">${m.product_qty}</td>
                    <td>${m.product_uom.name}</td>

                </tr>
                <% no+=1 %>
            %endfor
            </tbody>
        </table>
        <p class="oe_clear"> </p> 
        %endif

        <table frame="void" width="60%">
            <tr>
                <td width="20%">Admin,</td>
                <td width="20%">Diterima</td>
                <td width="20%">Diperiksa</td>
            </tr>
            <tr height="60px"/>
            <tr>
                <td>${user.name}</td>
                <td></td>
                <td></td>
            </tr>
        </table>

    </div>
</body>
</html>
% endfor