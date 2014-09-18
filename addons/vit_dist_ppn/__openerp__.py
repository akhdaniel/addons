{
	"name": "PPN Distributor", 
	"version": "1.0", 
	"depends": ["base","sale","account"], 
	"author": "vitraining.com", 
	"category": "Purchasing", 
	"description": """\
<p>Fitur PPN untuk Distributor</P>
<ul>
<li>NPWP dan PKP di partner master
<li>pilih invoices per tanggal tertentu untuk diisi nomor seri faktur pajak
<li>update invoices dengan nomor seri faktur pajak 
<li>master data nomor seri faktur pajak: no awal, no akhir, no sekarang, tahun
<li>master data nomor seri faktur pajak terupdate sesuai dengan yang terpakai terakhir
</ul> 
""",
	"data": [
		"tax_numbering.xml",
		"wizard/set_tax_numbering_wizard.xml",
		"invoice.xml",
		"partner.xml",
	],
	"installable": True,
	"auto_install": False,
}