from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class lap_pkk(osv.osv):
	_name 		= "anggaran.lap_pkk"
	_columns 	= {
		'unit_id'  				: fields.many2one('anggaran.unit', 'Unit'),
		'tahun_id'  			: fields.many2one('account.fiscalyear', 'Tahun'),
		'rka_kegiatan_id' 		: fields.many2one('anggaran.rka_kegiatan', 'Kegiatan'),
		'kebijakan_id'			: fields.related('rka_kegiatan_id', 'kebijakan_id' , type="many2one", relation="anggaran.kebijakan", string="Kebijakan", store=True),
		'program_id'			: fields.related('rka_kegiatan_id', 'kegiatan_id' , 'program_id', type="many2one", relation="anggaran.program", string="Program", store=True),
		'input_rencana'			: fields.float("Input Rencana"),
		'input_realisasi'		: fields.float("Input Realisasi"),
		'proses_rencana'		: fields.float("Input Rencana"),
		'proses_realisasi'		: fields.float("Input Realisasi"),
		'output_rencana'		: fields.float("Input Rencana"),
		'output_realisasi'		: fields.float("Input Realisasi"),
		'cap_thn_lalu_rencana' 	: fields.float("Capaian Tahun Lalu Rencana"),
		'cap_thn_lalu_realisasi': fields.float("Capaian Tahun Lalu Realisasi"),
		'pct_capaian_target' 	: fields.float("Persen Capaian Target Renstra"),
		'outcome' 				: fields.float("Outcome"),
	}