import time
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
	('reject','Reject'), 
	('open','Open'),	
	('propose_winner','Propose Winner'),
	('done','Done')]

class eproc_lelang(osv.osv):
    _name = 'eproc.lelang'
     
    def action_draft(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[0][0]},context=context)

    def action_verify(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[1][0]},context=context)
 
    def action_reject(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[2][0]},context=context)
    	
    def action_open(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[3][0]},context=context)
    
    def action_propose_winner(self,cr,uid,ids,vals,context=None): 
        
        pes=self.browse(cr,uid,ids)[0]
        coy=pes.name
        le=self.pool.get('eproc.peserta_lelang')
        lel=le.search(cr,uid,[('name','=',coy)])
        lele=le.browse(cr,uid,lel,context=context)
        penawaran=[] 
        tam=[]  
        for pen in lele:    
            penawaran.append((0,0,{'partner_id':pen.partner_id.id,'evaluasiBiayaHargaPenawaran':pen.evaluasiBiayaHargaPenawaran,'evaluasiAkhir':True}))       
        tam=sorted(penawaran)
        ta=tam[0]
        vals['pesertaLelang']=[ta]
        vals['state']=LELANG_STATES[4][0]
    	return super(eproc_lelang,self).write(cr,uid,ids,vals,context=None)

    def action_review_winner(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[3][0]},context=context)

    def action_done(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':LELANG_STATES[5][0]},context=context)  
 
    def action_rangking(self,cr,uid,ids,vals,context=None): 
        pes=self.browse(cr,uid,ids)[0]
        coy=pes.name
        le=self.pool.get('eproc.peserta_lelang')
        lel=le.search(cr,uid,[('name','=',coy)])
        lele=le.browse(cr,uid,lel,context=context)
        penawaran=[]
        pemenang=[]
        pal=[] 
        for pen in lele: 
            penawaran.append((0,0,{'partner_id':pen.partner_id.id,'evaluasiBiayaHargaPenawaran':pen.evaluasiBiayaHargaPenawaran})) 
        tam=sorted(penawaran)
        ta=tam[0]
        vals['pesertaLelang']=tam
        vals['state']=LELANG_STATES[4][0]
        return super(eproc_lelang,self).write(cr,uid,ids,vals,context=None)
    
    def isi_master_jadwal(self, cr, uid, vals, context=None):      
        #import pdb;pdb.set_trace()
        jad=self.pool.get('eproc.master_jadwal_lelang')
        jas=jad.search(cr, uid, [], context=context)
        #ja=jad.browse(cr, uid, jas, context=context)[0]
        j_ids=[]
        for jadw in jad.browse(cr, uid, jas, context=context):
            j_ids.append((0,0, {'masterJadwalLelang':jadw.name}))
        vals['jadwalLelang']=j_ids    
        return vals
         
    def create(self, cr, uid, vals, context=None):       
        vals=self.isi_master_jadwal(cr, uid, vals, context=None)
        result= super(eproc_lelang,self).create (cr, uid, vals, context=None)
        return result  
        
    _columns = {
		'name' : fields.char('Nama', size=200,
			readonly=True, 
			states={'draft': [('readonly', False)], 'open': [('readonly', False)]}, 
			select=True),
		'paket' : fields.many2one('eproc.paket','Paket Pekerjaan'),
		'kategori' : fields.many2one('eproc.lelang_kategori','Kategori Lelang'),
		'metodaLelang' : fields.many2one('eproc.metoda_lelang', 'Metoda Lelang'),
		'metodaEvaluasi' : fields.many2one('eproc.metoda_evaluasi', 'Metoda Evaluasi'),
        #'jad': fields.one2many('eproc.master_jadwal_lelang','lelang','jadwal'),
		'nilaiHps' : fields.float('Nilai HPS'),
        'currency': fields.many2one('res.currency', 'Currency', help='The currency used to enter statement'),
        'pesertalelang': fields.many2one('eproc.peserta_lelang'),
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
            help="Gives the status of the Lelang."),
		'tahap' : fields.many2one('eproc.tahap_lelang','Tahap Lelang'),
		'beritaAcaraEvaluasiNo' : fields.char('Nomor Berita Acara Evaluasi'),
		'beritaAcaraEvaluasiFilename' : fields.binary('File Berita Acara Evaluasi'),
		'user_id' : fields.many2one('res.users', 'Creator','Masukan User ID Anda'),
	        }
    
    _defaults = {
        'state': LELANG_STATES[0][0],
        'user_id': lambda obj, cr, uid, context: uid,
      #  'jadwal': lambda*a : time.strftime('%y'),
    }  
        
eproc_lelang()

class eproc_lelang_product(osv.osv):
    _name = 'eproc.lelang_product'
    _columns = {
    	'lelang': fields.many2one('eproc.lelang','Lelang', domain=[('state','=','open')]),
        'product': fields.many2one('product.product', 'Product' ),
        'qty': fields.float('Jumlah'),
        'filename': fields.binary('Attachment Filename',required=True,),
        'specification': fields.char('Specification'),
        'name': fields.related('product',type="many2one", 
        	relation="product.product", string="Product Name", readonly=True),
    }
eproc_lelang_product()

class eproc_peserta_lelang(osv.osv):
    _name = 'eproc.peserta_lelang'
        
    def oto_produk(self, cr, uid,vals, context=None):
       # import pdb;pdb.set_trace()
        eproc=self.pool.get('eproc.lelang')
        per=eproc.browse(cr,uid,vals['lelang'],context)
        name=per.name
        prod_id=eproc.search(cr, uid,[('name','=',name)])
        pro=eproc.browse(cr,uid,prod_id,context)[0]
        prod_ids=[]
        for pr in pro.detailProduct:
            prod_ids.append((0,0, {'lelangProduct':pr.product.id}))
        vals['pesertaLelangProduct']=prod_ids   
        eproc=self.pool.get('res.partner')
        per=eproc.browse(cr,uid,vals['partner_id'],context)
        name=per.name
        prod_id=eproc.search(cr, uid,[('name','=',name)])
        pro=eproc.browse(cr,uid,prod_id,context)[0]
        prod_ids=[]
        for pr in pro.peralatan_ids:
            prod_ids.append((0,0, {'name':pr.name,'jumlah':pr.jumlah,'kapasitas':pr.kapasitas,'merk':pr.merk,'type':pr.type,'tahunPembuatan':pr.tahunPembuatan,'kondisi':pr.kondisi,'lokasiSekarang':pr.lokasiSekarang,'buktiKepemilikan':pr.buktiKepemilikan}))
        vals['pesertaLelangPeralatan']=prod_ids 
        nera_ids=[]
        for pr1 in pro.neraca_ids:
            nera_ids.append((0,0,{'tahun':pr1.tahun,'tanggal':pr1.tanggal,'aktivaTetap':pr1.aktivaTetap,'aktivaLancar':pr1.aktivaLancar,'aktivaLainnya' :pr1.aktivaLainnya,'hutangJangkaPanjang':pr1.hutangJangkaPanjang,'hutangJangkaPendek' :pr1.hutangJangkaPendek}))  
        vals['pesertaLelangNeraca']=nera_ids 
        IU_ids=[]
        for pr2 in pro.ijin_usaha_ids:
            IU_ids.append((0,0, {'filename':pr2.filename,'masterIjinUsaha':pr2.masterIjinUsaha.id,'nomor' :pr2.nomor,'berlakuSampai':pr2.berlakuSampai,'instansiPemberi':pr2.instansiPemberi,'kualifikasi':pr2.kualifikasi.id }))
        vals['pesertaLelangIjinUsaha']=IU_ids
        BP_ids=[]
        for pr3 in pro.bukti_pajak_ids:
            BP_ids.append((0,0, {'masterPajak':pr3.masterPajak.id,'nomor':pr3.nomor,'tanggal':pr3.tanggal,'masaTahun':pr3.masaTahun,'masaBulan':pr3.masaBulan,'filename':pr3.filename}))
        vals['pesertaLelangBuktiPajak']=BP_ids
        TA_ids=[]
        for pr4 in pro.tenaga_ahli_ids:
            TA_ids.append((0,0, {'name':pr4.name,'tanggalLahir':pr4.tanggalLahir,'pendidikanTerakhir':pr4.pendidikanTerakhir,'profesi':pr4.profesi,'tahunPengalamanKerja':pr4.tahunPengalamanKerja,'email':pr4.email,'wargaNegara':pr4.wargaNegara,'jabatan':pr4.jabatan,'statusPegawai':pr4.statusPegawai}))
        vals['pesertaLelangTenagaAhli']=TA_ids
        PENG_ids=[]
        for pr5 in pro.pengalaman_ids:
            PENG_ids.append((0,0, {'name':pr5.name,'lokasi':pr5.lokasi,'instansiPemberi':pr5.instansiPemberi,'alamatInstansi':pr5.alamatInstansi,'telponInstansi':pr5.telponInstansi,'tanggalKontrak':pr5.tanggalKontrak,'selesaiKontrak':pr5.selesaiKontrak,'nomorKontrak':pr5.nomorKontrak,'nilai':pr5.nilai,'tanggalPelaksanaan':pr5.tanggalPelaksanaan,'tanggalSerahTerima':pr5.tanggalSerahTerima,'prosentasePelaksanaan':pr5.prosentasePelaksanaan}))
        vals['pesertaLelangPengalaman']=PENG_ids
        return vals
        
    def create(self, cr, uid, vals, context=None):       
        vals=self.oto_produk(cr, uid, vals, context=None)
        result= super(eproc_peserta_lelang,self).create (cr, uid, vals, context=None)
        return result  
        
    _columns = {
        'name': fields.related('partner_id',type="many2one", 
            relation="res.partner", string="Supplier", readonly=True),
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
		'name' : fields.char('Nama', size=200),		
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
		#'lelang': fields.many2one('eproc.lelang','Lelang')		
    }
eproc_jenis_kontrak_imbalan()

class eproc_jenis_kontrak_jangka_waktu(osv.osv):
    _name = 'eproc.jenis_kontrak_jangka_waktu'
    _columns = {
		'name' : fields.char('Nama', size=200),
		#'lelang': fields.many2one('eproc.lelang','Lelang')		
    }
eproc_jenis_kontrak_jangka_waktu()

class eproc_jenis_kontrak_jumlah_pihak(osv.osv):
    _name = 'eproc.jenis_kontrak_jumlah_pihak'
    _columns = {
		'name' : fields.char('Nama', size=200),
		#'lelang': fields.many2one('eproc.lelang','Lelang')
    }
eproc_jenis_kontrak_jumlah_pihak()

class eproc_jadwal_lelang(osv.osv):
    _name = 'eproc.jadwal_lelang'
    _columns = {
		'masterJadwalLelang' : fields.char('Jadwal Lelang'),
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
	#	'jadwal':fields.time('bebas',readonly=True),
		'jadwal_lelang': fields.one2many('eproc.jadwal_lelang','masterJadwalLelang', 'Jadwal Lelang')		
    }
    _defaults = {
   #     'jadwal': lambda*a : time.strftime('1'),
    }     
eproc_master_jadwal_lelang()

class eproc_dokumen_lelang(osv.osv):
    _name = 'eproc.dokumen_lelang'
    _columns = {
		'name' : fields.char('Nama', size=200),
		'filename': fields.binary('Filename',required=True),
		'lelang': fields.many2one('eproc.lelang','Lelang')
    }
eproc_dokumen_lelang()

class eproc_peserta_lelang_ijin_usaha(osv.osv):
    _name = 'eproc.peserta_lelang_ijin_usaha'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'masterIjinUsaha' : fields.many2one('eproc.master_ijin_usaha','Ijin Usaha'), 
        'nomor' : fields.char('Nomor',size=100),
        'berlakuSampai' : fields.date('Berlaku Sampai'),
        'instansiPemberi' : fields.char('Instansi Pemberi', size=100),
        'filename' : fields.binary('Bukti Dokumen',required=True),
        'kualifikasi':fields.many2one('eproc.master_kualifikasi','Kualifikasi'),       
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
		'bukti' : fields.binary('Dokumen Bukti')
    }
eproc_peserta_lelang_dukungan_bank()

class eproc_peserta_lelang_bukti_pajak(osv.osv):
    _name = 'eproc.peserta_lelang_bukti_pajak'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'masterPajak' : fields.many2one('eproc.master_pajak','Master Pajak'),
        'nomor' : fields.char('Nomor',size=200),
        'tanggal' : fields.date('Tanggal'),
        'masaTahun' : fields.char('Masa Tahun',size=4),
        'masaBulan' : fields.char('Masa Bulan',size=200),
        'filename' : fields.binary('Filename',size=200,required=True),
    }
eproc_peserta_lelang_bukti_pajak()

class eproc_peserta_lelang_tenaga_ahli(osv.osv):
    _name = 'eproc.peserta_lelang_tenaga_ahli'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'tenaga_ahli': fields.many2one('eproc.tenaga_ahli','Tenaga Ahli'), 
		'name': fields.char('Name',size=300),
        'tanggalLahir' : fields.date('Tanggal Lahir'),
        'pendidikanTerakhir' : fields.char('Pendidikan Terakhir',size=300),
        'tahunPengalamanKerja' : fields.char('Tahun Pengalaman Kerja',size=4),
        'profesi' : fields.char('Profesi/Keahlian',size=300), 
        'email' : fields.char('Email',size=300),
        'wargaNegara' : fields.char('Warga Negara',size=300),
        'jabatan' : fields.char('Jabatan',size=300),
        'statusPegawai' : fields.char('Status Pegawai',size=300),
        'pengalaman_kerja' : fields.one2many('eproc.tenaga_ahli_pengalaman_kerja','tahun','Pengalaman Kerja'),
        'pendidikan' : fields.one2many('eproc.tenaga_ahli_pendidikan','tenaga_ahli','Pendidikan'),
        'sertifikat' : fields.one2many('eproc.tenaga_ahli_sertifikat','tenaga_ahli','Sertifikat'),
        'bahasa' : fields.one2many('eproc.tenaga_ahli_bahasa','tenaga_ahli','Bahasa'),
    }
eproc_peserta_lelang_tenaga_ahli()

class eproc_peserta_lelang_pengalaman(osv.osv):
    _name = 'eproc.peserta_lelang_pengalaman'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'name' : fields.char('Nama Pekerjaan',size=200),
        'lokasi' : fields.char('Lokasi',size=200),
        'instansiPemberi' : fields.char('Instansi Pemberi',size=200),
        'alamatInstansi' : fields.char('Alamat Instansi',size=200),
        'telponInstansi' : fields.char('Telpon Instansi',size=200),
        'tanggalKontrak' : fields.date('Tanggal Kontrak',size=200),
        'selesaiKontrak' : fields.date('Selesai Kontrak',size=200),
        'nomorKontrak' : fields.char('Nomor Kontrak',size=200),
        'nilai' : fields.integer('Nilai',size=200),
        'tanggalPelaksanaan' : fields.date('Tanggal Pelaksanaan'),
        'tanggalSerahTerima' : fields.date('Tanggal Serah Terima'),
        'prosentasePelaksanaan' : fields.float('Persentase Pelaksanaan'),
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
		'nomorKontrak' : fields.char('Nomor Kontrak',size=200),
		'tanggalKontrak' : fields.date('Tanggal Kontrak'),
		'selesaiKontrak' : fields.date('Selesai Kontrak'),		
    }
eproc_peserta_lelang_pekerjaan_sedang_berjalan()

class eproc_peserta_lelang_peralatan(osv.osv):
    _name = 'eproc.peserta_lelang_peralatan'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'peralatan': fields.many2one('eproc.peralatan','Peralatan'),    	
		'name' : fields.char('Nama Peralatan',size=200),
        'jumlah' : fields.integer('Jumlah',),
        'kapasitas' : fields.char('Kapasitas'),
        'merk' : fields.char('Merk',size=200),
        'type' : fields.char('Type',size=200),
        'tahunPembuatan' : fields.char('Tahun Pembuatan',size=4),
        'kondisi' : fields.char('Kondisi',size=200),
        'lokasiSekarang' : fields.char('Lokasi Sekarang',size=200),
        'buktiKepemilikan' : fields.char('Bukti Kepemilikan',size=200),
        'partner_id': fields.many2one('res.partner','Supplier'),
    }
eproc_peserta_lelang_peralatan()

class eproc_peserta_lelang_neraca(osv.osv):
    _name = 'eproc.peserta_lelang_neraca'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
    	'tahun' : fields.char('Tahun'),
        'tanggal' : fields.date('Tanggal'),
        'aktivaTetap' : fields.float('Aktiva Tetap'),
        'aktivaLancar' : fields.float('Aktiva Lancar'),
        'aktivaLainnya' : fields.float('Aktiva Lainnya'),
        'hutangJangkaPanjang' : fields.float('Hutang Jangka Panjang'),
        'hutangJangkaPendek' : fields.float('Hutang Jangka Pendek'),
        
    }
eproc_peserta_lelang_neraca()

class eproc_peserta_lelang_dokumen_penawaran(osv.osv):
    _name = 'eproc.peserta_lelang_dokumen_penawaran'
    _columns = {
    	'peserta_lelang': fields.many2one('eproc.peserta_lelang'),
		'name' : fields.char('Nama Dokumen',size=200),
		'filename' : fields.binary('Filename',required=True),
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
		'attachmentFilename' : fields.binary('Attachment Filename',required=True)
    }
eproc_penjelasan_dokumen()

class eproc_adendum_lelang(osv.osv):
    _name = 'eproc.adendum_lelang'
    _columns = {
		'name' : fields.char('Nama', size=200),
		'filename': fields.binary('Filename',required=True),		
		'lelang': fields.many2one('eproc.lelang','Lelang')
    }
eproc_adendum_lelang()



