{
    'name': 'Gross Subtotal Price Added On Sales Line',
	'version':'0.1',	
    'depends': ['sale'],
    'author'  :'vitraining.com',
    'category': 'sale',
    'description': """
    	* Menambahkan Field Gross Price di Sales Order Line, Merupakan
    	  Nilai Harga Price Sebelum di kalikan Diskon
        * Menambahkan Field Additional Debit Account Di Account Journal
        * Mengupdate Value Credit tiap barang penjualan sesuai dengan Qty * Price tiap line yang terbentuk di invoicenya 
          tanpa perkalian diskon defaulnya.
        * Menambahkan/Mengupdate COA tambahan diskon di setiap move_id atau jurnal sales nya
""",
    'installable':True,
    'data': ['sale.xml',
             'res_company_view.xml'],
}
