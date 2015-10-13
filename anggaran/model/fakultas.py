from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class fakultas(osv.osv):
	_name 		= "anggaran.fakultas"
	_columns 	= {
		'code':	fields.char('Kode'),
		'name':	fields.char('Nama'),
		'alamat':	fields.char('Alamat'),
		'nama_bank':	fields.char('Nama Bank'),
		'nomor_rek':	fields.char('No Rekening'),
	}