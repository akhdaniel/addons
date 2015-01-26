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
    <div class="page">
        <h4>Rencana Kedatangan Barang <br/>[ ${ o.state in ['draft','sent'] and 'Request for Quotation ' or 'Purchase Order '} no ${o.name} ]</h4>
        <table frame="void" width="100%">
            <tr>
                <td width="15%">Supplier</td>
                <td width="1%"> : </td>
                <td class="title"> [${o.partner_id.code}] ${o.partner_id.name}</td>
                <td class="aright">Printed by ${user.name}</td>
            </tr>
            <tr>
                <td width="15%">Ship to</td>
                <td width="1%"> : </td>
                <td class="title">${o.location_id.name}</td>
            </tr>
            <tr>
                <td width="15%">Periode</td>
                <td width="1%"> : </td>
                <td class="title">${o.period_id.name}</td>
            </tr>
            <!-- <p class="aright title" style="font-size: 12px;background: rgba(0, 0, 0, 0.1)">Total : Rp ${o.amount_total}</p> -->
        </table>  
        <p class="oe_clear"> </p>     

        <!-- W1 -->
        %if o.sch_ids :
        <table  style="page-break-inside: avoid" class="list_table" width="100%" cellpadding="5" cellspacing="20">
            <thead>
                <tr>
                    <td colspan=2></td>
                    <td colspan=2><b>Jenis Kendaraan</b></td>
                    <td class="aright">${o.fleet1.jenis  or ''}</td>
                    <td class="aright">${o.fleet2.jenis   or ''}</td>
                    <td class="aright">${o.fleet3.jenis   or ''}</td>
                    <td class="aright">${o.fleet4.jenis   or ''}</td>
                    <td class="aright">${o.fleet5.jenis   or ''}</td>
                    <td class="aright">${o.fleet6.jenis  or '' }</td>
                    <td class="aright">${o.fleet7.jenis  or '' }</td>
                    <td class="aright">${o.fleet8.jenis  or '' }</td>
                    <td class="aright">${o.fleet9.jenis   or ''}</td>
                    <td class="aright">${o.fleet10.jenis  or ''}</td>
                    <td class="aright">${o.fleet11.jenis  or ''}</td>
                    <td class="aright">${o.fleet12.jenis  or ''}</td>
                    <td class="aright">${o.fleet13.jenis  or ''}</td>
                    <td class="aright">${o.fleet14.jenis  or ''}</td>
                    <td class="aright">${o.fleet15.jenis  or ''}</td>
                    <td class="aright">${o.fleet16.jenis  or ''}</td>
                    <td class="aright">${o.fleet17.jenis  or ''}</td>
                    <td class="aright">${o.fleet18.jenis  or ''}</td>
                    <td class="aright">${o.fleet19.jenis  or ''}</td>
                    <td class="aright">${o.fleet20.jenis  or ''}</td>
                </tr>
                <tr>
                    <td colspan=2></td>
                    <td colspan=2><b>Kubikasi</b></td>
                    <td class="aright">${o.kubika1  or ''}</td>
                    <td class="aright">${o.kubika2  or ''}</td>
                    <td class="aright">${o.kubika3  or ''}</td>
                    <td class="aright">${o.kubika4  or ''}</td>
                    <td class="aright">${o.kubika5  or ''}</td>
                    <td class="aright">${o.kubika6  or ''}</td>
                    <td class="aright">${o.kubika7  or ''}</td>
                    <td class="aright">${o.kubika8  or ''}</td>
                    <td class="aright">${o.kubika9  or ''}</td>
                    <td class="aright">${o.kubika10 or ''}</td>
                    <td class="aright">${o.kubika11 or ''}</td>
                    <td class="aright">${o.kubika12 or ''}</td>
                    <td class="aright">${o.kubika13 or ''}</td>
                    <td class="aright">${o.kubika14 or ''}</td>
                    <td class="aright">${o.kubika15 or ''}</td>
                    <td class="aright">${o.kubika16 or ''}</td>
                    <td class="aright">${o.kubika17 or ''}</td>
                    <td class="aright">${o.kubika18 or ''}</td>
                    <td class="aright">${o.kubika19 or ''}</td>
                    <td class="aright">${o.kubika20 or ''}</td>
                </tr>
                <tr>
                    <td colspan=2></td>
                    <td colspan=2><b>Tonnase</b></td>
                    <td class="aright">${o.tonase1  or ''}</td>
                    <td class="aright">${o.tonase2  or ''}</td>
                    <td class="aright">${o.tonase3  or ''}</td>
                    <td class="aright">${o.tonase4  or ''}</td>
                    <td class="aright">${o.tonase5  or ''}</td>
                    <td class="aright">${o.tonase6  or ''}</td>
                    <td class="aright">${o.tonase7  or ''}</td>
                    <td class="aright">${o.tonase8  or ''}</td>
                    <td class="aright">${o.tonase9  or ''}</td>
                    <td class="aright">${o.tonase10 or ''}</td>
                    <td class="aright">${o.tonase11 or ''}</td>
                    <td class="aright">${o.tonase12 or ''}</td>
                    <td class="aright">${o.tonase13 or ''}</td>
                    <td class="aright">${o.tonase14 or ''}</td>
                    <td class="aright">${o.tonase15 or ''}</td>
                    <td class="aright">${o.tonase16 or ''}</td>
                    <td class="aright">${o.tonase17 or ''}</td>
                    <td class="aright">${o.tonase18 or ''}</td>
                    <td class="aright">${o.tonase19 or ''}</td>
                    <td class="aright">${o.tonase20 or ''}</td>
                </tr>
                <tr class="col1">
                    <th>No</th>
                    <th>Kode</th>
                    <th>Barcode</th>
                    <th>Nama Barang</th>
                    <th class="aright">${formatLang(o.w1  , date=True)}</th>
                    <th class="aright">${formatLang(o.w2  , date=True)}</th>
                    <th class="aright">${formatLang(o.w3  , date=True)}</th>
                    <th class="aright">${formatLang(o.w4  , date=True)}</th>
                    <th class="aright">${formatLang(o.w5  , date=True)}</th>
                    <th class="aright">${formatLang(o.w6  , date=True)}</th>
                    <th class="aright">${formatLang(o.w7  , date=True)}</th>
                    <th class="aright">${formatLang(o.w8  , date=True)}</th>
                    <th class="aright">${formatLang(o.w9  , date=True)}</th>
                    <th class="aright">${formatLang(o.w10 , date=True)}</th>
                    <th class="aright">${formatLang(o.w11 , date=True)}</th>
                    <th class="aright">${formatLang(o.w12 , date=True)}</th>
                    <th class="aright">${formatLang(o.w13 , date=True)}</th>
                    <th class="aright">${formatLang(o.w14 , date=True)}</th>
                    <th class="aright">${formatLang(o.w15 , date=True)}</th>
                    <th class="aright">${formatLang(o.w16 , date=True)}</th>
                    <th class="aright">${formatLang(o.w17 , date=True)}</th>
                    <th class="aright">${formatLang(o.w18 , date=True)}</th>
                    <th class="aright">${formatLang(o.w19 , date=True)}</th>
                    <th class="aright">${formatLang(o.w20 , date=True)}</th>
                </tr>
            </thead>
            <tbody>
            <% sno=1 %>
            % for s in o.sch_ids:
                <tr style="page-break-inside:avoid !important;">
                    <td>${sno}</td>
                    <td>${s.int_code}</td>
                    <td>${s.barcode}</td>
                    <td>${s.product_id.name_template}</td>
                    <td class="aright">${formatLang(s.w1  or 0.00)}</td>
                    <td class="aright">${formatLang(s.w2  or 0.00)}</td>
                    <td class="aright">${formatLang(s.w3  or 0.00)}</td>
                    <td class="aright">${formatLang(s.w4  or 0.00)}</td>
                    <td class="aright">${formatLang(s.w5  or 0.00)}</td>
                    <td class="aright">${formatLang(s.w6  or 0.00)}</td>
                    <td class="aright">${formatLang(s.w7  or 0.00)}</td>
                    <td class="aright">${formatLang(s.w8  or 0.00)}</td>
                    <td class="aright">${formatLang(s.w9  or 0.00)}</td>
                    <td class="aright">${formatLang(s.w10 or 0.00)}</td>
                    <td class="aright">${formatLang(s.w11 or 0.00)}</td>
                    <td class="aright">${formatLang(s.w12 or 0.00)}</td>
                    <td class="aright">${formatLang(s.w13 or 0.00)}</td>
                    <td class="aright">${formatLang(s.w14 or 0.00)}</td>
                    <td class="aright">${formatLang(s.w15 or 0.00)}</td>
                    <td class="aright">${formatLang(s.w16 or 0.00)}</td>
                    <td class="aright">${formatLang(s.w17 or 0.00)}</td>
                    <td class="aright">${formatLang(s.w18 or 0.00)}</td>
                    <td class="aright">${formatLang(s.w19 or 0.00)}</td>
                    <td class="aright">${formatLang(s.w20 or 0.00)}</td>
                </tr>
                <% sno+=1 %>
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
    <!-- <p style="page-break-after:always"></p> -->
</body>
</html>
% endfor