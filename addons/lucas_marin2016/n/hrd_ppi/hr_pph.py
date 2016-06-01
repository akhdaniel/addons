from osv import osv, fields

class pph(osv.osv):
    _name = 'hr_pph.pph'
    #_inherit = 'hr.payslip'
    
    columns= {
        'no_urut':fields.char('No Urut',7,),
        'npwp_pe_pajak':fields.char('NPWP Pemotong Pajak',15,), 
        'npwp_peg': fields.char('NPWP Pegawai atau Penerima Pensiun / THT / JHT',15,),
        'peg_asing':fields.boolean('Karyawan Asing'),
        'jns_tanggungan':fields.selection([('K','K'),('TK','TK',),('HB','HB')],'Jenis Tanggungan'),
        'jml_tanggungan':fields.integer('Jumlah Tanggungan',),
        'masa_peng_awal':fields.integer('Masa Perolehan Penghasilan Awal'),
        'masa_peng_akhir':fields.integer('Masa Perolehan Penghasilan Akhir'),
        'gaji':fields.char('1. Gaji/Pensiun/THT/JHT',12,),
        'tunjangan_pph':fields.char('2. Tunjangan PPh',12,),
        'tunjangan_lainya':fields.char('3. Tunjangan Lainya,Uang lembur,dan Sebagainya',12,),
        'honorarium':fields.char('4. Honorarium dan Imbalan Lain Sejenisnya',12),
        'premi_asuransi':fields.char('5. Premi Asuransi Yang di Bayar Pemberi Kerja',12),
        'natura':fields.char('6. Penerimaan Dalam Bentuk Natura',12),
        'jumlah':fields.char('7. Jumlah (1 s/d 6)'),
        'tantiem':fields.char('8. Tantiem,Bonus,Gratifikasi,Jasa Produksi dan THR',12),
        'bruto':fields.char('9. Jumlah Penghasilan Bruto (7 s/d 8)'),
        'biaya_jabatan7':fields.char('10. Biaya Jabatan / Biaya Pensiun Atas Penghasilan Pada Angka 7',12),
        'biaya_jabatan8':fields.char('11. Biaya Jabatan / Biaya Pensiun Atas Penghasilan Pada Angka 8',12),
        'iuran_pensiun':fields.char('12. Iuran Pensiun / THT / JHT',12),
        'jml_pengurangan':fields.char('13. jumlah Pengurangan (10 s/d 12)'),
        'jml_netto':fields.char('14. Jumlah Penghasilan Netto (9 s/d 13)'),
        'netto_sebelumnya':fields.char('15. Penghasilan Netto Massa Sebelumnya',12),
        'jml_netto_21':fields.char('16. Jumlah Penghasilan Netto Untuk Penghitungan PPh Pasal 21',12),
        'ptkp':fields.char('17. Penghasilan Tidak Kena Pajak (PTKP)',12),
        'P_kena_pajak':fields.char('18. Penghasilan Kena Pajak Setahun / Disetahunkan (16 s/d 17)',12),
        'pph_21_atas':fields.char('19. PPh Pasal 21 Atas Penghasilan Kena Pajak Setahun/Disetahunkan',12),
        'pph_21_yang':fields.char('20. PPh Pasal 21 Yang Telah Dipotong Massa Sebelumnya',12),
        'pph_21_terutang':fields.char('21. PPh pasal 21 Terutang',12),
        'pph_21_dan':fields.char('22. PPh Pasal 21 dan 26 Yang Telah Dipotong dan Dilunasi',12),
        'pph_pemerintah':fields.char('a. Dipotong dan Dilunasi Dengan SSP PPh Pasal 21 Ditanggung Pemerintah',12),
        'pph_ssp':fields.char('b. Dipotong dan Dilunasi Dengan SSP',12),
        'jml_pph':fields.selection([('yg_kurang_dipotong','Yang Kurang Dipotong (21-22)'),('yg_lebih_dipotong','Yang Lebih Dipotong (21-22)')],'Jumlah PPh pasal 21'),
        'jml_pph2':fields.char('23. Jumlah PPh Pasal 21',12),
        'jml_tsb':fields.selection([('dipotong','Dipotong Dari Pembayaran gaji'),('diperhitungkan','Diperhitungkan Dengan PPh Pasal21')],'jumlah Tersebut Pada Angka 23 Telah'),
        'tanggal':fields.date('Tanggal'),
        'jml_telah':fields.char('24. jumlah Tersebut Pada Angka 23 Telah',12),
        
            }
pph()
        
