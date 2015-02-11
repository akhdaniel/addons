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
        .oe_text_center {text-align: center;}
        .oe_right {text-align: right !important}
        .oe_clear {clear: both;}
    </style>
</head>

<body>
    <div class="page">
    	<div>${o.partner_id.name}</div>
        <h4 class="oe_text_center">Faktur Pembelian</h4>
        <table frame="void" width="100%">
            <tr>
                <td>Supplier#</td>
                <td>No. DO</td>
                <td>Term.</td>
                <td>Tanggal</td>
                <td>Jatuh Tempo</td>
                <td>No. Faktur</td>
            </tr>
            <tr>
                <td>${o.partner_id.code}</td>
                <td></td>
                <td>${o.payment_term.name}</td>
                <td>${formatLang(o.date_invoice , date=True)}</td>
                <td>${formatLang(o.date_due , date=True)}</td>
                <td>${o.number}</td>
            </tr>
        </table>  
        <p class="oe_clear"> </p> 
        %if o.invoice_line :
        <table  style="page-break-inside: avoid" class="list_table" width="100%" cellpadding="5" cellspacing="20">
            <thead>
                <tr class="col1">
                    <th>Barang</th>
                    <th>Nama Barang</th>
                    <th>Big Qty</th>
                    <th>Unit</th>
                    <th>Small Qty</th>
                    <th>Unit</th>
                    <th>Harga</th>
                    <th>Gross</th>
                    <th>  %  </th>
                    <th>Disc.Reg</th>
                </tr>
            </thead>
            <tbody>
            <% sno=1 %>
            % for il in o.invoice_line:
                <tr style="page-break-inside:avoid !important;">   
                	<td>${il.product_id.default_code}</td>
                	<td>${il.name}</td>
                	<td>${il.qty}</td>
                	<td>${il.uos_id.name}</td>
                	<td>${il.quantity2}</td>
                	<td>${il.uom_id.name}</td>
                	<td>${il.price_unit}</td>
                	<td>${il.price_subtotal}</td>
                	<td>0</td>
                	<td>${il.discount}</td>
            	</tr>
            	%endfor
        	</tbody>
    	</table>
        %endif

    	<p class="oe_clear"> </p> 
        <table frame="void" width="100%">
        	<tr>
        		<td>Hormat Kami,</td>
        		<td>Pengirim,</td>
        		<td>Penerima,</td>
        		<td class="oe_right">Subtotal :</td>
        		<td class="oe_right">${o.amount_untaxed}</td>
    		</tr>
    		<tr>
        		<td colspan="3"/>
        		<td class="oe_right">Ppn :</td>
        		<td class="oe_right">${o.amount_tax}</td>
    		</tr>
    		<tr>
    			<td>${user.name}</td>
    			<td colspan="2"/>
        		<td class="oe_right">Netto :</td>
        		<td class="oe_right"><B>${o.amount_total}</B></td>
    		</tr>
    		<tr class="list_table">
        		<td colspan="2">Harga Beli belum termasuk Ppn.</td>
        		<td class="oe_right">Printed : ${time}</td> 
    			<td colspan="2"/>
    		</tr>
		</table>

    </div>
    <!-- <p style="page-break-after:always"></p> -->
</body>
</html>
% endfor