from datetime import datetime, timedelta
from osv import fields,osv

class eproc_paket(osv.osv):
    _name = 'eproc.paket'
    _columns = {
		'branch_id' : fields.many2one('eproc.branch','Branch'),
		'mak' : fields.char('Mata Anggaran', size=200),
		'tahun' : fields.char('Tahun Anggaran', size=200),
		'keterangan' : fields.char('Keterangan', size=200),
		'name' : fields.char('Nama Paket', size=200),
		'lokasi' : fields.char('Lokasi', size=200),
		'pagu' : fields.float('PAGU', size=200)
    }
eproc_paket()

class eproc_branch(osv.osv):
    _name = 'eproc.branch'
    _columns = {
		'name' : fields.char('Name', size=200),
		'alamat' : fields.char('Address', size=200),
        'city_id': fields.many2one('eproc.city', "City"),
        'state_id': fields.many2one("res.country.state", 'State'),
        'country_id': fields.many2one('res.country', 'Country'),
        'zip': fields.char('Zip', change_default=True, size=24),
    }
eproc_branch()

LELANG_STATES =[
	('draft','Draft'),
	('verify','Verify'),
	('open','Open'),
	('reject','Reject'), 
	('propose_winner','Propose Winner'),
	('done','Done')]

class eproc_lelang(osv.osv):
    _name = 'eproc.lelang'

    def action_draft(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[0][0]},context=context)

    def action_verify(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[1][0]},context=context)

    def action_open(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[2][0]},context=context)

    def action_reject(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[3][0]},context=context)

    def action_propose_winner(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[4][0]},context=context)

    def action_review_winner(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[2][0]},context=context)

    def action_done(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[5][0]},context=context)

    def action_ikut(self,cr,uid,ids,context=None): 
    	return

    _columns = {
		'name' : fields.char('Nama', size=200,
			readonly=True, 
			states={'draft': [('readonly', False)], 'open': [('readonly', False)]}, 
			select=True),
		'paket' : fields.many2one('eproc.paket','Paket Pekerjaan'),
		'kategori' : fields.many2one('eproc.lelang_kategori','Kategori Lelang'),
		'metodaLelang' : fields.many2one('eproc.metoda_lelang', 'Metoda Lelang'),
		'metodaEvaluasi' : fields.many2one('eproc.metoda_evaluasi', 'Metoda Evaluasi'),

		'nilaiHps' : fields.float('Nilai HPS'),
        'currency': fields.many2one('res.currency', 'Currency', help='The currency used to enter statement'),

		'businessType' : fields.many2one( 'eproc.business_type','Business Type'),
		'subBusinessType' : fields.many2one( 'eproc.sub_business_type','Sub Business Type'),


		'jenisKontrakImbalan' : fields.many2one('eproc.jenis_kontrak_imbalan', 'Jenis Kontrak/Imbalan',''),
		'jenisKontrakJangkaWaktu' : fields.many2one('eproc.jenis_kontrak_jangka_waktu', 'Jenis Kontrak/Jangka Waktu',''),
		'jenisKontrakJumlahPihak' : fields.many2one('eproc.jenis_kontrak_jumlah_pihak', 'Jenis Kontrak/Jumlah Pihak',''),

		'syaratKualifikasi' : fields.one2many('eproc.syarat_kualifikasi', 'lelang','Syarat Kualifikasi'),
		'jadwalLelang' : fields.one2many('eproc.jadwal_lelang','lelang','Jadwal Lelang'),
		'dokumenLelang' : fields.one2many('eproc.dokumen_lelang','lelang', 'Dokumen Lelang'),
		'adendumLelang' : fields.one2many('eproc.adendum_lelang','lelang', 'Adendum Lelang'),
		'pesertaLelang' : fields.one2many('eproc.peserta_lelang','lelang', 'Peserta Lelang'),
		'penjelasanDokumen' : fields.one2many('eproc.penjelasan_dokumen','lelang', 'Aanwizing'),
		'detailProduct' : fields.one2many('eproc.lelang_product','lelang', 'Barang/Jasa'),

        'state': fields.selection(LELANG_STATES, 'Status', readonly=True, 
            help="Gives the status of the Lelang.", select=True),

		'tahap' : fields.many2one('eproc.tahap_lelang','Tahap Lelang'),

		'beritaAcaraEvaluasiNo' : fields.char('Berita Acara Evaluasi Nomor'),
		'beritaAcaraEvaluasiFilename' : fields.binary('File Berita Acara Evaluasi'),
		'user_id' : fields.many2one('res.users', 'Creator')
    }
    _defaults = {
        'state': LELANG_STATES[0][0],
        'user_id': lambda obj, cr, uid, context: uid
    }     
eproc_lelang()

class eproc_lelang_product(osv.osv):
    _name = 'eproc.lelang_product'
    _columns = {
    	'lelang': fields.many2one('eproc.lelang','Lelang', domain=[('state','=','open')]),
        'product': fields.many2one('product.product', 'Product' ),
        'qty': fields.float('Jumlah'),
        'filename': fields.binary('Attachment Filename'),
        'specification': fields.char('Specification'),
        'name': fields.related('product',type="many2one", 
        	relation="product.product", string="Product Name", readonly=True),
    }
eproc_lelang_product()

class eproc_peserta_lelang(osv.osv):
    _name = 'eproc.peserta_lelang'
    _columns = {
        'name': fields.related('lelang',type="many2one", 
            relation="eproc.lelang", string="Lelang", readonly=True),

    	'lelang': fields.many2one('eproc.lelang','Lelang',required=True, domain=[('state','=','open')]),
		'partner_id' : fields.many2one('res.partner','Supplier',required=True),
		'tanggalDaftar' : fields.date('Tanggal Daftar'),

		'pesertaLelangIjinUsaha'               : fields.one2many('eproc.peserta_lelang_ijin_usaha','peserta_lelang','Peserta Lelang Ijin Usaha'),
		'pesertaLelangDukunganBank'            : fields.one2many('eproc.peserta_lelang_dukungan_bank','peserta_lelang','Dukungan Bank'),
		'pesertaLelangBuktiPajak'              : fields.one2many('eproc.peserta_lelang_bukti_pajak','peserta_lelang','Peserta Lelang Bukti Pajak'),
		'pesertaLelangTenagaAhli'              : fields.one2many('eproc.peserta_lelang_tenaga_ahli','peserta_lelang','Peserta Lelang Tenaga Ahli'),
		'pesertaLelangPengalaman'              : fields.one2many('eproc.peserta_lelang_pengalaman','peserta_lelang','Peserta Lelang Pengalaman'),
		'pesertaLelangPekerjaanSedangBerjalan' : fields.one2many('eproc.peserta_lelang_pekerjaan_sedang_berjalan','peserta_lelang','Pekerjaan Sedang Berjalan'),
		'pesertaLelangPeralatan'               : fields.one2many('eproc.peserta_lelang_peralatan','peserta_lelang','Peserta Lelang Peralatan'),
		'pesertaLelangNeraca'                  : fields.one2many('eproc.peserta_lelang_neraca','peserta_lelang','Peserta Lelang Neraca'),
		'pesertaLelangDokumenPenawaran'        : fields.one2many('eproc.peserta_lelang_dokumen_penawaran','peserta_lelang','Dokumen Penawaran'),
		'pesertaLelangProduct'                 : fields.one2many('eproc.peserta_lelang_product','peserta_lelang','Detail Penawaran'),

		'evaluasiAdministrasiLulus' : fields.boolean('Evaluasi Administrasi Lulus'),
		'evaluasiAdministrasiAlasan' : fields.text('Evaluasi Administrasi Alasan'),

		'evaluasiTeknisLulus' : fields.boolean('Evaluasi Teknis Lulus'),
		'evaluasiTeknisAlasan' : fields.text('Evaluasi Teknis Alasan'),

		'evaluasiBiayaLulus' : fields.boolean('Evaluasi Biaya Lulus'),
		'evaluasiBiayaHargaPenawaran' : fields.float('Harga Penawaran'),
		'evaluasiBiayaHargaTerkoreksi' : fields.float('Harga Terkoreksi'),
		
		'evaluasiKualifikasiLulus' : fields.boolean('Evaluasi Kualifikasi Lulus'),
		'evaluasiKualifikasiAlasan' : fields.text('Evaluasi Kualifikasi Alasan'),
		
		'evaluasiUrutan' : fields.integer('Evaluasi Urutan'),
		'evaluasiAkhir' : fields.boolean('Evaluasi Akhir/Pemenang'),

		'user_id' : fields.many2one('res.users', 'Creator')
    }
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'tanggalDaftar': fields.date.context_today
    }     

eproc_peserta_lelang()



class eproc_lelang_kategori(osv.osv):
    _name = 'eproc.lelang_kategori'
    _columns = {
		'name' : fields.char('Nama', size=200)
    }
eproc_lelang_kategori()

class eproc_metoda_lelang(osv.osv):
    _name = 'eproc.metoda_lelang'
    _columns = {
		'name' : fields.char('Nama', size=200)
    }
eproc_metoda_lelang()


class eproc_metoda_evaluasi(osv.osv):
    _name = 'eproc.metoda_evaluasi'
    _columns = {
		'name' : fields.char('Nama', size=200)
    }
eproc_metoda_evaluasi()


class eproc_status_lelang(osv.osv):
    _name = 'eproc.status_lelang'
    _columns = {
		'name' : fields.char('Nama', size=200)
    }
eproc_status_lelang()


class eproc_syarat_kualifikasi(osv.osv):
    _name = 'eproc.syarat_kualifikasi'
    _columns = {
		'masterSyaratKualifikasi' : fields.many2one('eproc.master_syarat_kualifikasi', 'Syarat Kualifikasi'),
		'checkedSupplier' : fields.boolean('Checked Supplier'),
		'checkedBuyer' : fields.boolean('Checked Buyer'),
		'notes' : fields.char('Notes', size=500),
		'lelang': fields.many2one('eproc.lelang','Lelang')		
    }
eproc_syarat_kualifikasi()


class eproc_master_syarat_kualifikasi(osv.osv):
    _name = 'eproc.master_syarat_kualifikasi'
    _columns = {
		'name' : fields.char('Nama', size=200),
		'syaratKualifikasi': fields.one2many('eproc.syarat_kualifikasi','masterSyaratKualifikasi','Syarat Kualifikasi'),
		'mandatory': fields.boolean('Mandatory')
    }
eproc_master_syarat_kualifikasi()


class eproc_jenis_kontrak_imbalan(osv.osv):
    _name = 'eproc.jenis_kontrak_imbalan'
    _columns = {
		'name' : fields.char('Nama', size=200),
		'lelang': fields.many2one('eproc.lelang','Lelang')		
    }
eproc_jenis_kontrak_imbalan()

class eproc_jenis_kontrak_jangka_waktu(osv.osv):
    _name = 'eproc.jenis_kontrak_jangka_waktu'
    _columns = {
		'name' : fields.char('Nama', size=200),
		'lelang': fields.many2one('eproc.lelang','Lelang')		
    }
eproc_jenis_kontrak_jangka_waktu()

class eproc_jenis_kontrak_jumlah_pihak(osv.osv):
    _name = 'eproc.jenis_kontrak_jumlah_pihak'
    _columns = {
		'name' : fields.char('Nama', size=200),
		'lelang': fields.many2one('eproc.lelang','Lelang')
    }
eproc_jenis_kontrak_jumlah_pihak()


class eproc_jadwal_lelang(osv.osv):
    _name = 'eproc.jadwal_lelang'
    _columns = {
		'masterJadwalLelang' : fields.many2one('eproc.master_jadwal_lelang','Jadwal Lelang'),
		'startDate' : fields.date('Start Date'),
		'endDate' : fields.date('End Date'),
		'notes' : fields.char('Notes',size=500),
		'lelang': fields.many2one('eproc.lelang','Lelang')
    }
eproc_jadwal_lelang()


class eproc_master_jadwal_lelang(osv.osv):
    _name = 'eproc.master_jadwal_lelang'
    _columns = {
		'name' : fields.char('Nama', size=200),
		'jadwal_lelang': fields.one2many('eproc.jadwal_lelang','masterJadwalLelang', 'Jadwal Lelang')
    }
eproc_master_jadwal_lelang()


class eproc_dokumen_lelang(osv.osv):
    _name = 'eproc.dokumen_lelang'
    _columns = {
		'name' : fields.char('Nama', size=200),
		'filename': fields.binary('Filename'),
		'lelang': fields.many2one('eproc.lelang','Lelang')
    }
eproc_dokumen_lelang()

class eproc_peserta_lelang_ijin_usaha(osv.osv):
    _name = 'eproc.peserta_lelang_ijin_usaha'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'ijin_usaha': fields.many2one('eproc.ijin_usaha','Ijin Usaha'),
		'name' : fields.char('Notes', size=200)
    }
eproc_peserta_lelang_ijin_usaha()

class eproc_peserta_lelang_dukungan_bank(osv.osv):
    _rec_name = 'nomor'
    _name = 'eproc.peserta_lelang_dukungan_bank'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
		'namaBank' : fields.char('Nama Bank', size=200),
		'nomor' : fields.char('Nomor',size=200),
		'tanggal' : fields.date('Tanggal',size=200),
		'nilai' : fields.float('Nilai',size=200),
		'bukti' : fields.binary('Bukti')
    }
eproc_peserta_lelang_dukungan_bank()


class eproc_peserta_lelang_bukti_pajak(osv.osv):
    _name = 'eproc.peserta_lelang_bukti_pajak'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'bukti_pajak': fields.many2one('eproc.bukti_pajak','Bukti Pajak'),    	
		'name' : fields.char('Nama', size=200)
    }
eproc_peserta_lelang_bukti_pajak()


class eproc_peserta_lelang_tenaga_ahli(osv.osv):
    _name = 'eproc.peserta_lelang_tenaga_ahli'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'tenaga_ahli': fields.many2one('eproc.tenaga_ahli','Tenaga Ahli'), 
		'name' : fields.char('Nama', size=200)
    }
eproc_peserta_lelang_tenaga_ahli()


class eproc_peserta_lelang_pengalaman(osv.osv):
    _name = 'eproc.peserta_lelang_pengalaman'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'pengalaman': fields.many2one('eproc.pengalaman','Pengalaman Perusahaan'),    	
		'name' : fields.char('Nama', size=200)
    }
eproc_peserta_lelang_pengalaman()

class eproc_peserta_lelang_pekerjaan_sedang_berjalan(osv.osv):
    _name = 'eproc.peserta_lelang_pekerjaan_sedang_berjalan'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
		'name' : fields.char('Nama Pekerjaan',size=200),
		'lokasi' : fields.char('Lokasi',size=200),
		'instansiPemberi' : fields.char('Instansi Pemberi',size=200),
		'alamatInstansi' : fields.char('Alamat Instansi',size=200),
		'tanggalKontrak' : fields.date('Tanggal Kontrak'),
		'selesaiKontrak' : fields.date('Selesai Kontrak'),
		'nomorKontrak' : fields.char('Nomor Kontrak',size=200)
    }
eproc_peserta_lelang_pekerjaan_sedang_berjalan()

class eproc_peserta_lelang_peralatan(osv.osv):
    _name = 'eproc.peserta_lelang_peralatan'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'peralatan': fields.many2one('eproc.peralatan','Peralatan'),    	
		'name' : fields.char('Nama', size=200)
    }
eproc_peserta_lelang_peralatan()

class eproc_peserta_lelang_neraca(osv.osv):
    _name = 'eproc.peserta_lelang_neraca'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'neraca': fields.many2one('eproc.neraca','Neraca'),    	
		'name' : fields.char('Nama', size=200)
    }
eproc_peserta_lelang_neraca()

class eproc_peserta_lelang_dokumen_penawaran(osv.osv):
    _name = 'eproc.peserta_lelang_dokumen_penawaran'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
		'name' : fields.char('Nama Dokumen',size=200),
		'filename' : fields.binary('Filename'),
		'jenisDokumen' : fields.many2one('eproc.master_jenis_dokumen_penawaran','Jenis Dokumen')
    }
eproc_peserta_lelang_dokumen_penawaran()

class eproc_master_jenis_dokumen_penawaran(osv.osv):
    _name = 'eproc.master_jenis_dokumen_penawaran'
    _columns = {
    	'dokumen_penawaran': fields.one2many('eproc.dokumen_penawaran','jenisDokumen','Dokumen Penawaran'),
		'name' : fields.char('Nama', size=200)
    }
eproc_master_jenis_dokumen_penawaran()

class eproc_peserta_lelang_product(osv.osv):
    _name = 'eproc.peserta_lelang_product'
    _columns = {
		'peserta_lelang' : fields.many2one('eproc.peserta_lelang','Peserta Lelang'),
		'notes' : fields.text('Notes'),
		'lelangProduct' : fields.many2one('eproc.lelang_product','Produk'),
		'hargaPenawaran' : fields.float('Harga Penawaran'),
        'discount': fields.float('Discount'),
        'subTotal': fields.float('Sub Total'),        
    }
eproc_peserta_lelang_product()

class eproc_tahap_lelang(osv.osv):
    _name = 'eproc.tahap_lelang'
    _columns = {
		'name' : fields.char('Nama', size=200)
    }
eproc_tahap_lelang()


class eproc_penjelasan_dokumen(osv.osv):
    _name = 'eproc.penjelasan_dokumen'
    _columns = {
    	'lelang': fields.many2one('eproc.lelang', 'Lelang', required=True, domain=[('state','=','open')]),
		'name' : fields.char('Subjek', size=200, required=True),
		'dokumenLelang' : fields.many2one('eproc.dokumen_lelang', 'Dokumen Lelang', required=True),
		'bab' : fields.char('Bab', required=True),
		'pertanyaan' : fields.text('Pertanyaan', required=True),
		'partner_id' : fields.many2one('res.partner','Supplier', required=True),
		'jawaban' : fields.text('Jawaban'),
		'penjawab' : fields.char('Penjawab'),
		'attachmentFilename' : fields.binary('Attachment Filename')
    }
eproc_penjelasan_dokumen()

class eproc_adendum_lelang(osv.osv):
    _name = 'eproc.adendum_lelang'
    _columns = {
		'name' : fields.char('Nama', size=200),
		'filename': fields.binary('Filename'),		
		'lelang': fields.many2one('eproc.lelang','Lelang')
    }
eproc_adendum_lelang()


