CREATE TABLE IF NOT EXISTS `biller_tagihan` (
	`id_record_tagihan`			VARCHAR(30)	PRIMARY	KEY,
	`nomor_pembayaran`			VARCHAR(30),
	`nama`						VARCHAR(255),
	`kode_fakultas`				VARCHAR(20)	,
	`nama_fakultas`				VARCHAR(255),
	`kode_prodi`				VARCHAR(20),
	`nama_prodi`				VARCHAR(255),
	`kode_periode`				VARCHAR(20),
	`nama_periode`				VARCHAR(255),
	`is_tagihan_aktif`			INTEGER,
	`waktu_berlaku`				TIMESTAMP,
	`waktu_berakhir`			TIMESTAMP,
	`strata`					VARCHAR(255),
	`angkatan`					VARCHAR(255),
	`urutan_antrian`			INTEGER,
	`total_nilai_tagihan`		DOUBLE,
	`minimal_nilai_pembayaran`	DOUBLE,
	`maksimal_nilai_pembayaran`	DOUBLE,
	`nomor_induk`				VARCHAR(30),
	`pembayaran_atau_voucher`	VARCHAR(20),
	`voucher_nama`				VARCHAR(255),
	`voucher_nama_fakultas`		VARCHAR(255),
	`voucher_nama_prodi`		VARCHAR(255),
	`voucher_nama_periode`		VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS `biller_tagihan_detil` (
	`id_record_detil_tagihan` 	VARCHAR(30) PRIMARY KEY,
	`id_record_tagihan` 		VARCHAR(30),
	`urutan_detil_tagihan` 		INTEGER,
	`kode_jenis_biaya` 			VARCHAR(10) ,
	`label_jenis_biaya` 		VARCHAR(10) ,
	`label_jenis_biaya_panjang`	VARCHAR(255),
	`nilai_tagihan`				DOUBLE
);

    
CREATE TABLE IF NOT EXISTS `ca_pembayaran` (
	`id_record_pembayaran`		VARCHAR(30) PRIMARY KEY,
	`id_record_tagihan`			VARCHAR(30),
	`waktu_transaksi`			TIMESTAMP,
	`nomor_pembayaran`			VARCHAR(30),
	`kode_unik_transaksi_bank`	VARCHAR(30),
	`waktu_transaksi_bank`		VARCHAR(20),
	`kode_bank`					VARCHAR(10)  ,
	`kanal_bayar_bank`			VARCHAR(20),
	`kode_terminal_bank`		VARCHAR(20),
	`total_nilai_pembayaran`	DOUBLE,
	`status_pembayaran`			INTEGER,
	`id_record_rekonsiliasi`	VARCHAR(30),
	`id_record_settlement`		VARCHAR(30),
	`billref`					VARCHAR(30),
	`metode_pembayaran`			VARCHAR(10),
	`catatan`					VARCHAR(200),
	`key_val_1`					VARCHAR(255) ,
	`key_val_2`					VARCHAR(255) ,
	`key_val_3`					VARCHAR(255),
	`key_val_4`					VARCHAR(255),
	`key_val_5`					VARCHAR(255)
);