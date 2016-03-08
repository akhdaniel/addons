from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class res_partner(osv.osv):
	_inherit 	= "res.partner"
	_name 		= "res.partner"
	_columns 	= {
		'reliance_id' 				: fields.char('Reliance ID', select=1),
		'nomor_participant' 		: fields.char('Nomor Participant', select=1),
		'sid' 						: fields.char('SID', select=1),
		'nomor_polis' 				: fields.char('Nomor Polis', select=1),
		'nomor_nasabah' 			: fields.char('Nomor Nasabah', select=1),
		'cif' 						: fields.char('CIF', select=1),
		'agent_id' 					: fields.char('Agent', select=1),

		'perusahaan_npwp' 						: fields.char('NPWP'),
		'perusahaan_bidang_usaha' 				: fields.char('Bidang Usaha'),
		'perusahaan_siup' 						: fields.char('SIUP'),
		'perusahaan_tdp' 						: fields.char('TDP'),
		'perusahaan_akte_pendirian' 			: fields.char('Akte Pendirian'),
		'perusahaan_nomor_ijin_usaha' 			: fields.char('Nomor Ijin Usaha'),
		'perusahaan_nama_direktur' 				: fields.char('Nama Direktur'),
		'perusahaan_sumber_dana' 				: fields.char('Sumber dana'),
		'perusahaan_tujuan_asuransi_investasi' 	: fields.char('Tujuan Asuransi/Investasi'),
		'perusahaan_bentuk_badan_usaha' 		: fields.char('Bentuk Badan Usaha'),
		'perusahaan_nama_direksi' 				: fields.char('Nama Direksi'),
		'perusahaan_domisili_perusahaan' 		: fields.char('Domisili Perusahaan'),
		'perusahaan_tanggal_kedaluarsa_siup' 	: fields.char('Tanggal Kedaluarsa SIUP'),
		'perusahaan_kode_nasabah' 				: fields.char('Kode Nasabah'),
		'perusahaan_karakteristik_perusahaan' 	: fields.char('Karakteristik Perusahaan'),
		'perusahaan_status_domisili_kantor' 	: fields.char('Status Domisili Kantor'),
		'perusahaan_persentase_kepemilikan_saham' 	: fields.char('Persentase Kepemilikan saham'),
		'perusahaan_tanggal_kedaluarsa_tdp' 	: fields.char('Tanggal Kedaluarsa TDP'),
		'perusahaan_nomor_single_investor_id' 	: fields.char('Nomor Single Investor ID'),
		'perusahaan_nama_bank_nomor_rekening' 	: fields.char('Nama bank & nomor rekening'),
		'perusahaan_nomor_formulir' 			: fields.char('Nomor Formulir'),
		'perusahaan_nama_equity_sales' 			: fields.char('Nama Equity Sales'),
		'perusahaan_kode_equity_sales' 			: fields.char('Kode Equity Sales'),
		'perusahaan_kantor_perwakilan_galery' 	: fields.char('Kantor Perwakilan/Galery'),
		'perusahaan_nomor_sub_rekening_efek' 	: fields.char('Nomor Sub Rekening Efek'),
		'perusahaan_nama_komisaris' 			: fields.char('Nama Komisaris'),
		'perusahaan_jabatan' 					: fields.char('Jabatan '),
		'perusahaan_diterbitkan_di' 			: fields.char('Diterbitkan di'),
		'perusahaan_nomor_ijin_pma' 			: fields.char('Nomor Ijin PMA'),
		'perusahaan_tanggal_kedaluarsa_pma' 	: fields.char('Tanggal Kedaluarsa PMA'),
		'perusahaan_diterbitkan_di' 			: fields.char('Diterbitkan di'),
		'perusahaan_tahun_berdiri_perusahaan' 	: fields.char('Tahun berdiri perusahaan'),
		'perusahaan_jumlah_karyawan' 			: fields.char('Jumlah karyawan'),
		'perusahaan_jumlah_karyawan_yang_diikutsertakan' : fields.char('Jumlah karyawan yang diikutsertakan'),
		'perusahaan_polis_lain_yang_dimiliki' 	: fields.char('Polis lain yang dimiliki'),
		'perusahaan_tujuan_menutup_asuransi' 	: fields.char('Tujuan menutup Asuransi'),
		'perusahaan_modal_disetor' 				: fields.char('Modal disetor'),
		'perusahaan_total_asset' 				: fields.char('Total Asset'),
		'perusahaan_total_kewajiban' 			: fields.char('Total Kewajiban'),
		'perusahaan_laba_bersih' 				: fields.char('Laba bersih'),
		'perusahaan_pendapatan_operasional' 	: fields.char('Pendapatan Operasional'),
		'perusahaan_pendapatan_non_operasional' : fields.char('Pendapatan non Operasional'),
		
		'perorangan_tempat_tanggal_lahir' 		: fields.char('Tempat Tanggal Lahir'),
		'perorangan_nomor_ktp' 					: fields.char('Nomor KTP'),
		'perorangan_kewarganegaraan' 			: fields.char('Kewarganegaraan'),
		'perorangan_npwp' 						: fields.char('NPWP'),
		'perorangan_status_perkawinan' 			: fields.char('Status Perkawinan'),
		'perorangan_alamat_surat_menyurat' 		: fields.char('Alamat surat menyurat'),
		'perorangan_jenis_kelamin' 				: fields.char('Jenis Kelamin'),
		'perorangan_nama_istri_suami' 			: fields.char('Nama istri/ suami'),
		'perorangan_alamat_email' 				: fields.char('Alamat Email'),
		'perorangan_pendidikan_terakhir' 		: fields.char('Pendidikan Terakhir'),
		'perorangan_masa_berlaku_ktp' 			: fields.char('Masa berlaku KTP'),
		'perorangan_agama' 						: fields.char('Agama'),
		'perorangan_tujuan_investasi' 			: fields.char('Tujuan Investasi'),
		'perorangan_kitas' 						: fields.char('Kitas'),
		'perorangan_masa_berlaku_kitas' 		: fields.char('Masa berlaku Kitas'),
		'perorangan_paspor' 					: fields.char('Paspor'),
		'perorangan_masa_berlaku_paspor' 		: fields.char('Masa berlaku Paspor'),
		'perorangan_nama_gadis_ibu_kandung' 				: fields.char('Nama gadis ibu kandung'),
		'perorangan_sumber_dana_yg_akan_diinvestasikan' 	: fields.char('Sumber dana yg akan diinvestasikan'),
		'perorangan_alamat_tempat_tinggal_saat_ini' 		: fields.char('Alamat tempat tinggal saat ini'),
		'perorangan_periode_asuransi' 			: fields.char('Periode Asuransi'),
		'perorangan_lokasi_resiko' 				: fields.char('Lokasi Resiko'),
		'perorangan_harga_pertanggungan' 		: fields.char('Harga Pertanggungan'),
		'perorangan_kondisi_bangunan' 			: fields.char('Kondisi Bangunan'),
		'perorangan_penggunaan_bangunan_kendaraan' 	: fields.char('Penggunaan Bangunan/Kendaraan'),
		'perorangan_wilayah_kendaraan' 			: fields.char('Wilayah Kendaraan'),
		'perorangan_obyek_pertanggungan' 		: fields.char('Obyek Pertanggungan'),
		'perorangan_jenis_pertanggungan' 		: fields.char('Jenis Pertanggungan'),
		'perorangan_jenis_perluasan' 			: fields.char('Jenis Perluasan'),
		'perorangan_pengalaman_klaim' 			: fields.char('Pengalaman Klaim'),
		'perorangan_status_nasabah' 			: fields.char('Status Nasabah'),
		'perorangan_kegiatan_berorganisasi' 	: fields.char('Kegiatan berorganisasi'),
		'perorangan_nama_organisasi' 			: fields.char('Nama organisasi'),
		'perorangan_jabatan' 					: fields.char('Jabatan'),

		'pekerjaan_nama' 						: fields.char('Pekerjaan'),
		'pekerjaan_nama_perusahaan' 			: fields.char('Nama perusahaan'),
		'pekerjaan_alamat_perusahaan' 			: fields.char('Alamat Perusahaan'),
		'pekerjaan_bidang_usaha' 				: fields.char('Bidang Usaha'),
		'pekerjaan_penghasilan_per_tahun' 		: fields.char('Penghasilan per tahun'),
		'pekerjaan_jabatan' 					: fields.char('Jabatan'),
		'pekerjaan_penghasilan_per_bulan' 		: fields.char('Penghasilan per bulan'),
		'pekerjaan_nomor_npwp' 					: fields.char('Nomor NPWP'),
		'pekerjaan_nomor_telepon' 				: fields.char('Nomor Telepon'),
		'pekerjaan_alamat_email' 				: fields.char('Alamat Email'),
		'pekerjaan_masa_kerja' 					: fields.char('Masa Kerja'),
		'pekerjaan_nama_direktur' 				: fields.char('Nama Direktur'),
		'pekerjaan_nomor_extension' 			: fields.char('Nomor Extension'),
		'pekerjaan_nomor_faksimile' 			: fields.char('Nomor Faksimile'),

		'partner_account_ids' 					: fields.one2many('reliance.partner_account','partner_id','Accounts', ondelete="cascade", select=1),
		'partner_ahli_waris_ids' 				: fields.one2many('reliance.ahli_waris','partner_id','Ahli Waris', ondelete="cascade", select=1),
		'partner_keluarga_ids' 					: fields.one2many('reliance.keluarga','partner_id','Keluarga', ondelete="cascade", select=1),

	}


class ahli_waris(osv.osv):
	_name = "reliance.ahli_waris"
	_columns 	= {
		'partner_id' 		: fields.many2one('res.partner', 'Partner'),
		'nama' 				: fields.char('Nama'),
		'nomor_telepon' 	: fields.char('Nomor Telepon'),
		'hubungan_keluarga' : fields.char('Hubungan keluarga'),
		'alamat' 			: fields.char('Alamat'),
		'pendidikan_terakhir' : fields.char('Pendidikan terakhir'),
	}


class keluarga(osv.osv):
	_name = "reliance.keluarga"
	_columns 	= {
		'partner_id' 		: fields.many2one('res.partner', 'Partner'),
		'nama' 				: fields.char('Nama'),
		'nomor_telepon' 	: fields.char('Nomor Telepon'),
		'hubungan_keluarga' : fields.char('Hubungan keluarga'),
		'alamat' 			: fields.char('Alamat'),
	}


class partner_account(osv.osv):
	_name = "reliance.partner_account"
	_columns 	= {
		'partner_id' : fields.many2one('res.partner', 'Partner'),
		'product_id' : fields.many2one('product.product', 'Product')
	}

