% for o in objects :
<% setLang(user.lang) %>
<html>
<head>
    <style type="text/css">
        ${css}
        .page {page-break-after: auto}
        .title {font-weight: bold}
        .nominal {text-align: right !important}
        .col1 {background: rgba(0, 0, 0, 0.1)}
        .colt {background: rgba(0, 0, 0, 0.2)}
        .tbltd {border-bottom-style:none !important}
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

        <!-- W1 -->
        %if o.sch_ids1 :
        <table class="list_table" width="100%" cellpadding="5" cellspacing="20">
            <thead>
                <tr>
                    <th colspan=5>Week 1</th>
                    <th colspan=2 class="col1">Purchase Order 1</th>
                    <th colspan=2>Purchase Order 2</th>
                    <th colspan=2 class="col1">Purchase Order 3</th>
                    <th colspan=2>Purchase Order 4</th>
                    <th colspan=2 class="col1">Purchase Order 5</th>
                    <th colspan=2>Purchase Order 6</th>
                    <th colspan=2 class="colt">Total</th>
                </tr>
                <tr>
                    <td colspan=5 class="tbltd"></td>
                    <td class="col1 tbltd"><b>Weight</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == 'nol': 
                            ${n.wgt1}
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Weight</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '1': 
                            ${n.wgt1}
                        %endif
                    %endfor</td>
                    <td class="col1 tbltd"><b>Weight</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '2': 
                            ${n.wgt1}
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Weight</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '3': 
                            ${n.wgt1}
                        %endif
                    %endfor</td>
                    <td class="col1 tbltd"><b>Weight</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '4': 
                            ${n.wgt1}
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Weight</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '5': 
                            ${n.wgt1}
                        %endif
                    %endfor</td>
                    <td colspan=2 class="colt"></td>
                </tr>
                <tr>
                    <td colspan=5 class="tbltd"></td>
                    <td class="col1 tbltd"><b>Volume</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == 'nol': 
                            ${n.vol1}
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Volume</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '1': 
                            ${n.vol1}
                        %endif
                    %endfor</td>
                    <td class="col1 tbltd"><b>Volume</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '2': 
                            ${n.vol1}
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Volume</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '3': 
                            ${n.vol1}
                        %endif
                    %endfor</td>
                    <td class="col1 tbltd"><b>Volume</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '4': 
                            ${n.vol1}
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Volume</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '5': 
                            ${n.vol1}
                        %endif
                    %endfor</td>
                    <td colspan=2 class="colt"></td>
                </tr>
                <tr>
                    <td colspan=5 class="tbltd"></td>
                    <td class="col1 tbltd"><b>Jenis Truck</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == 'nol': 
                            %for f in n.fleet_id:
                                <b>${f.model_id.brand_id.name}</b>&#47;${f.model_id.modelname}&#47;${f.license_plate}<br/>
                            %endfor
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Jenis Truck</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '1': 
                            %for f in n.fleet_id:
                                <b>${f.model_id.brand_id.name}</b>&#47;${f.model_id.modelname}&#47;${f.license_plate}&#44;<br/>
                            %endfor
                        %endif
                    %endfor</td>
                    <td class="col1 tbltd"><b>Jenis Truck</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '2': 
                            %for f in n.fleet_id:
                                <b>${f.model_id.brand_id.name}</b>&#47;${f.model_id.modelname}&#47;${f.license_plate}&#44;<br/>
                            %endfor
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Jenis Truck</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '3': 
                            %for f in n.fleet_id:
                                <b>${f.model_id.brand_id.name}</b>&#47;${f.model_id.modelname}&#47;${f.license_plate}&#44;<br/>
                            %endfor
                        %endif
                    %endfor</td>
                    <td class="col1 tbltd"><b>Jenis Truck</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '4': 
                            %for f in n.fleet_id:
                                <b>${f.model_id.brand_id.name}</b>&#47;${f.model_id.modelname}&#47;${f.license_plate}&#44;<br/>
                            %endfor
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Jenis Truck</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '5': 
                            %for f in n.fleet_id:
                                <b>${f.model_id.brand_id.name}</b>&#47;${f.model_id.modelname}&#47;${f.license_plate}&#44;<br/>
                            %endfor
                        %endif
                    %endfor</td>
                    <td colspan=2 class="colt"></td>
                </tr>
                <tr>
                    <td colspan=5 class="tbltd"></td>
                    <td class="col1 tbltd"><b>Tgl. Order</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == 'nol': 
                            ${n.name}
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Tgl. Order</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '1': 
                            ${n.name}
                        %endif
                    %endfor</td>
                    <td class="col1 tbltd"><b>Tgl. Order</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '2': 
                            ${n.name}
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Tgl. Order</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '3': 
                            ${n.name}
                        %endif
                    %endfor</td>
                    <td class="col1 tbltd"><b>Tgl. Order</b></th>
                    <td class="col1 tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '4': 
                            ${n.name}
                        %endif
                    %endfor</td>
                    <td class="tbltd"><b>Tgl. Order</b></th>
                    <td class="tbltd">
                    %for n in o.sch_ids1: 
                        %if n.alias == '5': 
                            ${n.name}
                        %endif
                    %endfor</td>
                    <td colspan=2 class="colt"></td>
                </tr>
                <tr>
                    <th>Kategori</th>
                    <th>Nama Barang</th>
                    <th>Harga per karton</th>
                    <th>Kode Brg. JHHP</th>
                    <th>Unit</th>
                    <th class="col1">Jumlah</th>
                    <th class="col1">Total Rp</th>
                    <th>Jumlah</th>
                    <th>Total Rp</th>
                    <th class="col1">Jumlah</th>
                    <th class="col1">Total Rp</th>
                    <th>Jumlah</th>
                    <th>Total Rp</th>
                    <th class="col1">Jumlah</th>
                    <th class="col1">Total Rp</th>
                    <th>Jumlah</th>
                    <th>Total Rp</th>
                    <th class="colt">Jumlah</th>
                    <th class="colt">Total Rp</th>
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
                    <td class="col1 nominal">${formatLang(l.w11 or 0 ,digits=0)}</td>
                    <td class="col1 nominal">${formatLang(l.price_unit * l.w11 or 0 ,digits=0)}</td>
                    <td class="nominal">${formatLang(l.w12 or 0 ,digits=0)}</td>
                    <td class="nominal">${formatLang(l.price_unit * l.w12 or 0 ,digits=0)}</td>
                    <td class="col1 nominal">${formatLang(l.w13 or 0 ,digits=0)}</td>
                    <td class="col1 nominal">${formatLang(l.price_unit * l.w13 or 0 ,digits=0)}</td>
                    <td class="nominal">${formatLang(l.w14 or 0 ,digits=0)}</td>
                    <td class="nominal">${formatLang(l.price_unit * l.w14 or 0 ,digits=0)}</td>
                    <td class="col1 nominal">${formatLang(l.w15 or 0 ,digits=0)}</td>
                    <td class="col1 nominal">${formatLang(l.price_unit * l.w15 or 0 ,digits=0)}</td>
                    <td class="nominal">${formatLang(l.w16 or 0 ,digits=0)}</td>
                    <td class="nominal">${formatLang(l.price_unit * l.w16 or 0 ,digits=0)}</td>
                    <td class="col1 nominal">${formatLang(l.w1 or 0 ,digits=0)}</td>
                    <td class="col1 nominal">${formatLang(l.price_unit * l.w1 or 0 ,digits=0)}</td>
                </tr>
            % endfor
            </tbody>
        </table> 
        %endif

        

    <p class="nominal title" style="font-size: 12px;background: rgba(0, 0, 0, 0.1)">Total : Rp ${o.amount_total}</p>
    <br />
    Printed by ${user.name}
    </div>
    <p style="page-break-after:always"></p>
</body>
</html>
% endfor