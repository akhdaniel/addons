from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class espt(osv.osv):
	_name 		= "vit_dist_ppn.espt"
	_columns 	= {
        'invoice_id' 							: fields.many2one('account.invoice', 'Customer Invoice', required=True),
		'kode_pajak'							: fields.char('Kode Pajak'),
		'kode_transaksi'						: fields.char('Kode Transaksi'),
		'kode_status'							: fields.char('Kode Status'),
		'kode_dokumen'							: fields.char('Kode Dokumen'),
		'flag_vat'								: fields.char('Flag VAT'),
		'npwp_nomor_paspor'						: fields.char('NPWP / Nomor Paspor'),
		'nama_lawan_transaksi'					: fields.char('Nama Lawan Transaksi'),
		'nomor_faktur_dokumen'					: fields.char('Nomor Faktur / Dokumen'),
		'jenis_dokumen'							: fields.char('Jenis Dokumen'),
		'nomor_faktur_pengganti_retur'			: fields.char('Nomor Faktur Pengganti / Retur'),
		'jenis_dokumen_dokumen_pengganti_retur'	: fields.char('Jenis Dokumen Dokumen Pengganti / Retur'),
		'tanggal_faktur_dokumen'				: fields.char('Tanggal Faktur / Dokumen'),
		'tanggal_ssp'							: fields.char('Tanggal SSP'),
		'masa_pajak'							: fields.char('Masa Pajak'),
		'tahun_pajak'							: fields.char('Tahun Pajak'),
		'pembetulan'							: fields.char('Pembetulan'),
		'dpp'									: fields.char('DPP'),
		'ppn'									: fields.char('PPN'),
		'ppn_bm'								: fields.char('PPnBM'),
	}