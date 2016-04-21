from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)

####################################################################
# partner data
# from rmi-customer csv file
####################################################################
class import_rmi(osv.osv): 
	_name 		= "reliance.import_rmi"
	_columns 	= {

		"sid"						:	fields.char("SID"),
		"nama"						:	fields.char("Nama"),
		"alamat_ktp"				:	fields.char("Alamat KTP"),
		"no_ktp_siup"				:	fields.char("No KTP/SIUP"),
		"propinsi"					:	fields.char("Propinsi"),
		"kota"						:	fields.char("Kota"),
		"kode_pos"					:	fields.char("KodePos"),
		"negara"					:	fields.char("Negara"),
		"agama"						:	fields.char("Agama"),
		"tempat_lahir"				:	fields.char("Tempat Lahir"),
		"tanggal_lahir"				:	fields.char("TanggalLahir"),
		"nomor_tlp"					:	fields.char("Nomor Tlp"),
		"alamat_surat_menyurat"		:	fields.char("Alamat Surat Menyurat"),
		"propinsi_surat_menyurat"	:	fields.char("Propinsi Surat Menyurat"),
		"kota_surat_menyurat"		:	fields.char("KotaSuratMenyurat"),
		"kode_pos_surat_menyurat"	:	fields.char("Kode Pos Surat Menyurat"),
		"negara_surat_menyurat"		:	fields.char("NegaraSuratMenyurat"),
		"pendidikan_terakhir"		:	fields.char("PendidikanTerakhir"),
		"fax"						:	fields.char("Fax"),
		"telpon"					:	fields.char("Telpon"),
		"email"						:	fields.char("Email"),
		"handphone"					:	fields.char("Handphone"),
		"pekerjaan"					:	fields.char("Pekerjaan"),
		"gaji_pertahun"				:	fields.char("GajiPertahun"),
		"alasan_berinvestasi"		:	fields.char("AlasanBerinvestasi"),
		"kewarganegaraan"			:	fields.char("Kewarganegaraan"),
		"ahli_waris"				:	fields.char("Ahli Waris"),
		"hubungan_dengan_ahli_waris":	fields.char("Hubungan dengan ahli waris"),

		'is_imported' 				: 	fields.boolean("Imported to Partner?", select=1),
		"notes"						:	fields.char("Notes"),
	}

	def action_import_partner(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner(self, cr, uid, context=None):
		_logger.warning('running cron import_rmi')
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=100, context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		for import_rmi in self.browse(cr, uid, ids, context=context):

			partner_data = {
				'name'				: import_rmi.nama_partner,
				'rmi_sid'			: import_rmi.sid,
				'comment' 			: 'RMI'
			}
			
			########################## check exiting partner partner 
			pid = partner.search(cr, uid, [('rmi_policy_no','=',import_rmi.policy_no)],context=context)
			if not pid:
				pid = partner.create(cr, uid, partner_data, context=context)	
				i = i + 1
			else:
				pid = pid[0]
				_logger.warning('Partner exist with rmi_policy_no %s' % import_rmi.policy_no)
				ex = ex + 1

			partner_old = import_rmi.nama_partner

			#commit per record
			cr.execute("update reliance_import_rmi set is_imported='t' where id=%s" % import_rmi.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )



####################################################################
# partner data
# from rmi-product-holding csv file
####################################################################
class import_rmi_product_holding(osv.osv): 
	_name 		= "reliance.import_rmi_product_holding"
	_columns 	= {
		"sid"						:	fields.char("SID"),
		"nama_investor"				:	fields.char("Nama Investor"),
		"product_id"				:	fields.char("Product ID"),
		"product_name"				:	fields.char("Product name"),
		"unit_penyertaan"			:	fields.char("Unit Penyertaan"),
		"nab_saat_beli"				:	fields.char("NAB saat beli"),
		"nab_sampai_hari_ini"		:	fields.char("NAB sampai hari ini"),
		"nominal_investasi_awal"	:	fields.char("Nominal Investasi Awal"),
		"nominal_investasi_akhir"	:	fields.char("Nominal Investasi Akhir"),
		"profit_capital_loss"		:	fields.char("Profit/Capital Loss"),
		'is_imported' 				: 	fields.boolean("Imported to Product Holding?", select=1),
		"notes"						:	fields.char("Notes"),

	}


	def action_import_product_holding(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_product_holding(self, cr, uid, context=None):
		_logger.warning('running cron import_rmi')
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=100, context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no product_holding to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		return True 
