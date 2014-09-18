from openerp.osv import fields, osv

#############################################################
# 2 (dua) digit pertama adalah Kode Transaksi
# 1 (satu) digit berikutnya adalah Kode Status
# 3 (tiga) digit berikutnya adalah Kode Cabang
# 2 (dua) digit berikutnya adalah Kode Tahun
# 8 (delapan) digit berikutnya adalah Nomor Seri Faktur Pajak
#############################################################

class tax_numbering(osv.osv):
	_name    	= "vit_dist_ppn.tax_numbering"
	_rec_name   = 'year'
	_columns    = {
		'prefix'       : fields.char('Prefix', required=True),
		'start_no'     : fields.char('Start No', required=True),
		'end_no'       : fields.char('End No', required=True),
		'current_no'   : fields.char('Current No', required=True),
		'year'         : fields.integer('Year', required=True),
	}
