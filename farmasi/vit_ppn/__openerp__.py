{
	"name": "PPN Indonesia", 
	"version": "1.0", 
	"depends": ["base","sale","account"], 
	"author": "vitraining.com", 
	"category": "Accounting", 
	"description": """\
Fitur PPN Module
=====================================================================

* Field NPWP dan PKP di master partner
* wizard pilih invoices per tanggal tertentu untuk diisi nomor seri faktur pajak
* update invoices dengan nomor seri faktur pajak 
* cetak form Faktur Pajak Standard
* master data nomor seri faktur pajak: no awal, no akhir, no sekarang, tahun
* master data nomor seri faktur pajak terupdate sesuai dengan yang terpakai terakhir
 
Format Nomor NPWP
=====================================================================
Contoh penulisan lengkap format kode NPWP yaitu 99.999.999.9-999.999 

Dua digit pertama menunjukkan Identitas Wajib Pajak, yaitu:

* 01 sampai 03 adalah Wajib Pajak Badan
* 04 dan 06 adalah Wajib Pajak Pengusaha
* 05 adalah Wajib Pajak Karyawan
* 07 sampai 09 adalah Wajib Pajak Orang Pribadi

Enam digit berikut menunjukkan Nomor Registrasi / Urut yang diberikan Kantor Pusat 
Direktorat Jenderal Pajak kepada Kantor Pelayanan Pajak (KPP).

Satu digit berikutnya berfungsi sebagai Alat 
Pengaman untuk menghindari terjadinya pemalsuan atau kesalahan pada NPWP.

Tiga digit berikut adalah Kode KPP, contohnya 015, 
berarti NPWP tersebut dikeluarkan di KPP Pratama Jakarta Tebet.

Tiga digit terakhir menunjukkan Status Wajib Pajak:

* 000 berarti Tunggal atau Pusat
* 00x (001,002 dst) berarti Cabang, dimana angka akhir menunjukkan urutan cabang  (cabang ke-1 maka 001; cabang ke-2 maka 002; dst.).

Format Nomor Faktur Pajak
=====================================================================
Contoh penulisan lengkap format kode faktur pajak yaitu 010.000-11.000001

Menurut peraturan yang berlaku yakni PER – 159/PJ./2006, Format kode Faktur Pajak Standar 
terdiri dari 16 (enam belas) digit yaitu :

* 2 (dua) digit pertama adalah Kode Transaksi
* 1 (satu) digit berikutnya adalah Kode Status
* 3 (tiga) digit berikutnya adalah Kode Cabang
* 2 (dua) digit berikutnya adalah Kode Tahun
* 8 (delapan) digit berikutnya adalah Nomor Seri Faktur Pajak

Kode Transaksi
---------------------
Kode transaksi yang dimaksud dalam Format Kode Faktur Pajak sesuai PER – 159/PJ./2006 adalah sebagai berikut :

* 01 – Untuk ‘Penyerahan kepada selain Pemungut PPN’
* 02 – Untuk ‘Penyerahan kepada Pemungut PPN Bendaharawan Pemerintah’
* 03 – Untuk ‘Penyerahan kepada Pemungut PPN Lainnya (selain Bendaharawan Pemerintah)’
* 04 – Untuk ‘Penyerahan yang menggunakan DPP Nilai Lain kepada selain Pemungut PPN’. Yang dimaksud DPP dengan Nilai Lain adalah sebagaimana yng dimaksud dalam Keputusan Menteri Keuangan Nomor 567/KMK.04/2000 tentang Nilai Lain Sebagai Dasar Pengenaan Pajak sebagaimana telah diubah dengan Keputusan Menteri Keuangan Nomor 251/KMK.03/2002.
* 05 – Untuk ‘Penyerahan yang Pajak Masukannya diDeemed kepada selain Pemungut PPN’
* 06 – Untuk ‘Penyerahan Lainnya kepada selain Pemungut PPN’
* 07 – Untuk ‘Penyerahan yang PPN atau PPN dan PPn BM-nya Tidak Dipungut kepada selain Pemungut PPN’
* 08 – Untuk ‘Penyerahan yang Dibebaskan dari pengenaan PPN atau PPN dan PPn BM kepada selain Pemungut PPN’
* 09 – Untuk ‘Penyerahan Aktiva Pasal 16D kepada selain Pemungut PPN’

Kode Status
---------------------
Kode status dari faktur pajak yang dimaksud yakni :

* 0 (nol) – Untuk status faktur pajak ‘Normal’
* 1(satu) – Untuk status faktur pajak ‘Pergantian’

Kode Cabang
---------------------
Penentuan kode cabang sebanyak 3 (tiga) digit untuk faktur pajak dibuat mengikuti aturan berikut :

* Dapat diurutkan menurut cara yang Anda anggap paling mudah, namun untuk penambahan Kode Cabang baru setelah berlakunya Peraturan Direktur Jenderal Pajak ini Pengusaha Kena Pajak dapat mengurutkan Kode Cabang berdasarkan tanggal pengukuhan masing-masing Kantor Cabang.
* Kode Cabang pada Kode Faktur Pajak Standar ditentukan sendiri secara berurutan, yaitu diisi dengan kode ’000′ untuk Kantor Pusat dan dimulai dari kode ’001′ untuk Kantor Cabang.
* Kode Cabang dapat ditambah dan/atau dihentikan penggunaannya karena adanya penambahan dan/atau pengurangan Cabang sesuai dengan perkembangan usaha.
* Peruntukan Kode Cabang tidak boleh berubah, dan Kode Cabang yang sudah dihentikan penggunaannya tidak boleh digunakan kembali

Kode Tahun
---------------------
Kode Tahun yang digunakan pada Nomor Seri Faktur Pajak Standar ditulis dengan mencatumkan dua digit terakhir dari tahun diterbitkannya Faktur Pajak Standar, contohnya tahun 2007 ditulis ’07′.

Nomor Seri Faktur Pajak
---------------------

Nomor seri Faktur Pajak Standar dimulai dari Nomor Urut 1 (ditulis 6 (enam digit) atau ’000001′) pada setiap awal tahun takwim, yaitu mulai Masa Pajak Januari dan secara berurutan, naun bagi Pengusaha Kena Pajak yang baru dikukuhkan, Nomor Urut 1 dimulai sejak Masa Pajak Pengusaha Kena Pajak dikukuhkan. Bagi Pengusaha Kena Pajak yang memiliki cabang, maka Nomor Urut 1 (satu) dimulai pada setiap awal tahun takwim Masa Pajak Januari pada masing-masing Kantor Pusat dan Kantor-kantor Cabangnya, kecuali bagi Kantor Cabang yang baru dikukuhkan, Nomor Urut 1 dimulai sejak Masa Pajak Pengusaha Kena Pajak dikukuhkan.

Maka sesuai contoh penulisan lengkap format kode faktur pajak yaitu ’010.000-11.000001′ mengandung makna Kode Transaksi ’01′ untuk Penyerahan kepada selin Pemungut PPN, kemudian Kode Status ’0′ untuk faktur pajak ‘Normal’, kemudian Kode Cabang ’000′ untuk Pusat, diikuti dengan Kode Tahun ’11′ untuk Tahun 2011, dan terakhir Nomor Seri Faktur Pajak urutan pertama yakni ’000001′.

Sedikit tambahan mengenai Nomor Urut pada Nomor Seri Faktur Pajak Standar dan tanggal Faktur Pajak Standar yang harus dibuat secara berurutan. Dengan tidak membedakan antara Kode Transaksi, Kode Status Faktur Pajak Standar, atau mata uang yang digunakan dalam transaksi. Faktur yang tidak sesuai urutan kejadian transaksi, dapat dikategorikan sbg faktur pajak yang cacat, dgn demikian dapat dianggap sbg tidak membuat faktur pajak. Sanksi faktur pajak diatur pada pasal 14 ayat (4) UU KUP sebesar 2% dari DPP.

Untuk memudahkan pembuatan faktur pajak, gunakanlah software Krishand PPN 1111 dan Krishand Invoicing. Agar Anda tidak perlu lagi khawatir mengenai kesalahan pengkodean dan penomoran faktur pajak yang akan dibuat. Karena setiap pembuatan faktur pajak dalam software Krishand PPN dan Invoicing.

Sistem akan secara otomatis membuatkan dan mengurutkan sesuai ketentuan format kode faktur pajak. Selain itu software ini juga dapat langsung mencetak faktur pajak melalui format continuous form atau blanko (pre-printed) serta pembuatan laporan SPT Masa PPN dan mengekspor hasilnya ke e-SPT dilengkapi dengan laporan-laporan internal seperti daftar atau rekap faktur pajak keluaran, masukan, nota retur, serta penjualan yang dapat disusun per-periode, per-supplier.


Sumber: http://www.pajak.net/

""",
	"data": [
		"tax_numbering.xml",
		"wizard/set_tax_numbering_wizard.xml",
		"invoice.xml",
		"partner.xml",
		"reports/faktur_pajak.xml",
		'security/ir.model.access.csv',
	],
	"installable": True,
	"auto_install": False,
}