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
		"rmi_sid"						: fields.char("RMI Sid"),
		"rmi_tanggal_lahir"				: fields.char("RMI Tanggal Lahir"),
		"rmi_alamat_surat_menyurat"		: fields.char("RMI Alamat Surat Menyurat"),
		"rmi_kota_surat_menyurat"		: fields.char("RMI Kota Surat Menyurat"),
		"rmi_propinsi_surat_menyurat"	: fields.char("RMI Propinsi Surat Menyurat"),
		"rmi_kode_pos_surat_menyurat"	: fields.char("RMI Kode Pos Surat Menyurat"),
		"rmi_negara_surat_menyurat"		: fields.char("RMI Negara Surat Menyurat"),
		"rmi_alasan_berinvestasi"		: fields.char("RMI Alasan Berinvestasi"),

		"rmi_product_id"				:	fields.char("Product Id"),
		"rmi_product_name"				:	fields.char("Product Name"),
		"rmi_unit_penyertaan"			:	fields.float("Unit Penyertaan"),
		"rmi_nab_saat_beli"				:	fields.float("NAB Saat Beli"),
		"rmi_nab_sampai_hari_ini"		:	fields.float("NAB Sampai Hari Ini"),
		"rmi_nominal_investasi_awal"	:	fields.float("Nominal Investasi Awal"),
		"rmi_nominal_investasi_akhir"	:	fields.float("Nominal Investasi Akhir"),
		"rmi_profit_capital_loss"		:	fields.float("Profit Capital Loss"),	
	}



