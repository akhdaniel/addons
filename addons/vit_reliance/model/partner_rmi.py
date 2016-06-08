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
		"rmi_sid"						: fields.char("RMI SID", select=1),
		"rmi_account_no"				: fields.char("RMI Account Number", select=1),
		"rmi_tanggal_lahir"				: fields.char("RMI Tanggal Lahir", select=1),
		"rmi_alamat_surat_menyurat"		: fields.char("RMI Alamat Surat Menyurat"),
		"rmi_kota_surat_menyurat"		: fields.char("RMI Kota Surat Menyurat"),
		"rmi_propinsi_surat_menyurat"	: fields.char("RMI Propinsi Surat Menyurat"),
		"rmi_kode_pos_surat_menyurat"	: fields.char("RMI Kode Pos Surat Menyurat"),
		"rmi_negara_surat_menyurat"		: fields.char("RMI Negara Surat Menyurat"),
		"rmi_alasan_berinvestasi"		: fields.char("RMI Alasan Berinvestasi"),

		"rmi_product_id"				:	fields.char("RMI Product Id", select=1),
		"rmi_tanggal"					:	fields.char("RMI Tanggal", select=1),
		"rmi_product_name"				:	fields.char("RMI Product Name", select=1),
		"rmi_unit_penyertaan"			:	fields.float("RMI Unit Penyertaan"),
		"rmi_nab_saat_beli"				:	fields.float("RMI NAB Saat Beli"),
		"rmi_nab_sampai_hari_ini"		:	fields.float("RMI NAB Sampai Hari Ini"),
		"rmi_nominal_investasi_awal"	:	fields.float("RMI Nominal Invst. Awal"),
		"rmi_nominal_investasi_akhir"	:	fields.float("RMI Nominal Invst. Akhir"),
		"rmi_profit_capital_loss"		:	fields.float("RMI Profit Capital Loss"),	
	}


	def get_rmi_customer(self, cr, uid, reliance_id, context=None):
		member = self.search_read(cr,uid,[('reliance_id','=',reliance_id)],context=context)
		return member		


	def get_rmi_customer_by_sid(self, cr, uid, sid, context=None):
		member = self.search_read(cr,uid,[('rmi_sid','=',sid)],context=context)
		return member		
