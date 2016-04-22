from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class partner(osv.osv):
	_name 		= "res.partner"
	_inherit 	= "res.partner"
	_columns = {
		'refi_no_debitur'			: fields.char("REFI No Debitur", select=1),
		'refi_wilayah'				: fields.char("REFI Wilayah"),
		'refi_status_rumah'			: fields.char("REFI Status Rumah"),
		'refi_pisah_harta'			: fields.char("REFI Pisah Harta"),
		'refi_tanggunan'			: fields.char("REFI Jumlah Tanggunan"),

		"refi_domisili_kecamatan" 	: fields.char("REFI Domisili Kecamatan"),
		"refi_domisili_kota"		: fields.char("REFI Domisili Kota"),
		"refi_domisili_propinsi"	: fields.char("REFI Domisili Propinsi"),
		"refi_kode_pos"				: fields.char("REFI Domisili Kode POS"),
		"refi_tipe_id"				: fields.char("REFI Tipe ID"),

		"refi_parent_id"			: fields.many2one('res.partner', "REFI Perusahaan", select=1),
		"refi_tanggal_bayar"		: fields.char("REFI Tanggal Bayar"),
		"refi_frek_bayar"			: fields.char("REFI Frek Bayar"),
		"refi_tanggal_masuk_kerja"			: fields.char("REFI Tanggal Masuk Kerja"),
	}



