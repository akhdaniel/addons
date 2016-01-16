
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<title>Untitled Document</title>
<style type="text/css">
<!--
.style1 {font-size: 9px}
-->
</style>
</head>

<body>
<h1>&nbsp;</h1>
<h1>
  <label title="">Surat Perintah Kerja Cutting</label>
</h1>
% for o in objects :
<table width="951" border="1">
  <tr>
    <th scope="col">No</th>
    <th scope="col">Tanggal Cutting </th>
    <th scope="col">Tanggal Selesai </th>
    <th scope="col">Kode Cutter </th>
    <th scope="col">Nama Cutter </th>
    <th scope="col">No Meja </th>
  </tr>
  <tr>
    <td>${ o.name }</td>
    <td>${ o.date_start_cutting }</td>
    <td>${ o.date_end_cutting }</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
</table>
<table width="951" border="1">
  <caption align="top">
   <strong> Model   </strong>
  </caption>
  
  <tr>
    <th width="243" scope="col">Model Image </th>
    <th scope="col">Sample Warna Bahan </th>
    <th width="183" scope="col">Sample Warna Kain </th>
    <th width="230" scope="col">Keterangan</th>
  </tr>
  <tr>
    <td><div align="center" class="style1">${ helper.embed_image('png',o.type_product_id.image,200,200)|n }</div></td>
    <td width="180">&nbsp;</td>
    <td width="183">&nbsp;</td>
    <td width="230"><p>Model : ${ o.type_product_id.model_product }</p>
      <p>Kategori : ${ o.category }</p>
      <p>Jumlah Komponen :</p>
      <ul>
        <li>Badan : ${ o.component_main_qty}</li>
        <li>Variasi :${o.component_variation_qty}</li>
        <li>Keterangan Lain : ${o.keterangan}</li>
      </ul>
    <p>&nbsp;</p></td>
  </tr>
</table>
<table width="951" border="1">
  <caption align="top">
  <strong>KEBUTUHAN  BAHAN </strong>
  </caption>
  
  <tr>
    <th width="161" scope="col">Kategori Bahan </th>
    <th width="433" scope="col">Nama Bahan </th>
    <th width="275" scope="col">Jumlah</th>
  </tr>
  <tr>
    <td>
		% for line in o.consumed_line_ids:
			<li>	
		  		${ line.type }
			</li>
		 % endfor
	</td>
    <td>
		% for line in o.consumed_line_ids:
			<li>	
		  		${ line.material.name }
			</li>
		 % endfor
	</td>
    <td>
		% for line in o.consumed_line_ids:
			<li>	
		  		${ line.qty_total_material }   ${ line.product_uom.name}
			</li>
		 % endfor
	</td>
  </tr>
</table>
<table width="951" border="1">
  <tr>
    <th colspan="7" scope="col">JUMLAH ORDER </th>
  </tr>
  <tr>
    <td width="106"><strong>S/2</strong></td>
    <td width="111"><strong>M/4</strong></td>
    <td width="107"><strong>L/6</strong></td>
    <td width="119"><strong>XL/8</strong></td>
    <td width="120"><strong>XXL/10</strong></td>
    <td width="109"><strong>XXXL/12</strong></td>
    <td width="99"><strong>Jumlah</strong></td>
  </tr>
  <tr>
    <td>${ o.s_order }</td>
    <td>${ o.m_order }</td>
    <td>${ o.l_order }</td>
    <td>${ o.xl_order }</td>
    <td>${o. xxl_order }</td>
    <td>${o. xxxl_order }</td>
    <td>${ o.qty_order }</td>
  </tr>
</table>
<table width="951" border="1">
  <tr>
    <th colspan="10" scope="col">PEMAKAIAN BAHAN </th>
  </tr>
  <tr>
    <td colspan="6"><div align="center"><strong>Pengambilan</strong></div></td>
    <td width="48"><div align="center"><strong>Jumlah</strong></div></td>
    <td width="47"><div align="center"><strong>Sisa</strong></div></td>
    <td colspan="2"><div align="center"><strong>Penanggung Jawab </strong></div></td>
  </tr>
  <tr>
    <td width="60" rowspan="2"><strong>Badan : </strong></td>
    <td width="17">&nbsp;</td>
    <td width="17">&nbsp;</td>
    <td width="17">&nbsp;</td>
    <td width="17">&nbsp;</td>
    <td width="17">&nbsp;</td>
    <td width="48">&nbsp;</td>
    <td width="47">&nbsp;</td>
    <td width="177"><div align="center">Gudang</div></td>
    <td width="179"><div align="center">Cutting</div></td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td rowspan="3">&nbsp;</td>
    <td rowspan="3">&nbsp;</td>
  </tr>
  <tr>
    <td rowspan="2"><strong>Variasi : </strong></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td colspan="6"><div align="center"><strong>Kekurangan</strong></div></td>
    <td><strong>Jumlah</strong></td>
    <td><strong>Sisa</strong></td>
    <td rowspan="3">&nbsp;</td>
    <td rowspan="3">&nbsp;</td>
  </tr>
  <tr>
    <td><strong>Badan : </strong></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td><strong>Variasi :</strong></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
</table>
<table width="951" border="1">
  <tr>
    <th colspan="11" scope="col"><strong>CUTTING</strong></th>
  </tr>
  <tr>
    <td colspan="7"><div align="center"><strong>Hasil Cutting </strong></div></td>
    <td colspan="2"><div align="center"><strong>Waktu </strong></div></td>
    <td colspan="2"><div align="center"><strong>Penanggung Jawab </strong></div></td>
  </tr>
  <tr>
    <td width="21">S/2</td>
    <td width="26">M/4</td>
    <td width="21"><div align="center">L/6</div></td>
    <td width="32"><div align="center">XL/8</div></td>
    <td width="51"><div align="center">XXL/10</div></td>
    <td width="62"><div align="center">XXXL/12</div></td>
    <td width="41"><div align="center">Jumlah</div></td>
    <td width="72"><div align="center">Cut Mulai </div></td>
    <td width="80"><div align="center">Cut Selesai </div></td>
    <td width="77"><div align="center">Cutting</div></td>
    <td width="89"><div align="center">QC Cutting </div></td>
  </tr>
  <tr>
    <td width="21">&nbsp;</td>
    <td width="26">&nbsp;</td>
    <td width="21">&nbsp;</td>
    <td width="32">&nbsp;</td>
    <td width="51">&nbsp;</td>
    <td width="62">&nbsp;</td>
    <td width="41">&nbsp;</td>
    <td rowspan="4">&nbsp;</td>
    <td rowspan="4">&nbsp;</td>
    <td rowspan="4">&nbsp;</td>
    <td rowspan="4">&nbsp;</td>
  </tr>
  <tr>
    <td colspan="7"><div align="center"><strong>Reject</strong> <strong>Cutting</strong> </div></td>
  </tr>
  <tr>
    <td>S/2</td>
    <td>M/4</td>
    <td><div align="center">L/6</div></td>
    <td><div align="center">XL/8</div></td>
    <td><div align="center">XXL/10</div></td>
    <td><div align="center">XXXL/12</div></td>
    <td><div align="center">Jumlah</div></td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td colspan="7"><div align="center"><strong>Hasil QC Pass </strong></div></td>
    <td><div align="center">QC Mulai </div></td>
    <td><div align="center">QC Selesai </div></td>
    <td><div align="center">QC Cutting</div></td>
    <td><div align="center">Supervisor</div></td>
  </tr>
  <tr>
    <td>S/2</td>
    <td>M/4</td>
    <td><div align="center">L/6</div></td>
    <td><div align="left">XL/8</div></td>
    <td><div align="center">XXL/10</div></td>
    <td><div align="center">XXXL/12</div></td>
    <td><div align="center">Jumlah</div></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td colspan="7"><div align="center"><strong>Reject QC </strong></div></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>S/2</td>
    <td>M/4</td>
    <td>L/6</td>
    <td>XL/8</td>
    <td>XXL/10</td>
    <td>XXXL/12</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
</table>
<table width="951" border="1">
  <tr>
    <th width="154" scope="col"><div align="center">Prepared By </div></th>
    <th width="157" scope="col"><div align="center">Approved By </div></th>
    <th width="138" scope="col">&nbsp;</th>
    <th width="133" scope="col">&nbsp;</th>
    <th width="134" scope="col">&nbsp;</th>
  </tr>
  <tr>
    <td height="110">&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
</table>
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
</body>
% endfor
</html>
