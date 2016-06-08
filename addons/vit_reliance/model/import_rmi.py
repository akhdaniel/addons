from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)

PARTNER_MAPPING = {
	"sid"						: "rmi_sid",
	"account_no"				: "rmi_account_no",
	"nama"						: "name",
	# "jenis_kelamin"				: "perorangan_jenis_kelamin",
	"alamat_ktp"				: "street",
	"no_ktp_siup"				: "perorangan_nomor_ktp",
	"propinsi"					: False,
	"kota"						: "city",
	"kode_pos"					: "zip",
	"negara"					: False,
	# "agama"						: "perorangan_agama",
	"tempat_lahir"				: "perorangan_tempat_lahir",
	# "tanggal_lahir"				: "rmi_tanggal_lahir",
	"nomor_tlp"					: "phone",
	"alamat_surat_menyurat"		: "rmi_alamat_surat_menyurat",
	"propinsi_surat_menyurat"	: "rmi_propinsi_surat_menyurat",
	"kota_surat_menyurat"		: "rmi_kota_surat_menyurat",
	"kode_pos_surat_menyurat"	: "rmi_kode_pos_surat_menyurat",
	"negara_surat_menyurat"		: "rmi_negara_surat_menyurat",
	"pendidikan_terakhir"		: "perorangan_pendidikan_terakhir",
	"fax"						: "fax",
	"telpon"					: False,
	"email"						: "email",
	"handphone"					: "mobile",
	"ahli_waris"				: False,
	"hubungan_dengan_ahli_waris": False,
	# "pekerjaan"					: "pekerjaan_nama",
	# "gaji_pertahun"				: "pekerjaan_penghasilan_per_tahun",
	"alasan_berinvestasi"		: "rmi_alasan_berinvestasi",
	# "kewarganegaraan"			: "perorangan_kewarganegaraan",
}
####################################################################
# partner data
# from rmi-customer csv file
####################################################################
class import_rmi(osv.osv): 
	_name 		= "reliance.import_rmi"
	_columns 	= {
		"no"						:	fields.char("No"),
		"account_no"				:	fields.char("AccountNo"),
		"sid"						:	fields.char("SID"),
		"nama"						:	fields.char("Nama"),
		"jenis_kelamin"				:	fields.char("Jenis Kelamin"),
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

		"ahli_waris"				:	fields.char("Ahli Waris"),
		"hubungan_dengan_ahli_waris":	fields.char("Hubungan dengan ahli waris"),

		"pekerjaan"					:	fields.char("Pekerjaan"),
		"gaji_pertahun"				:	fields.char("GajiPertahun"),
		"alasan_berinvestasi"		:	fields.char("AlasanBerinvestasi"),
		"kewarganegaraan"			:	fields.char("Kewarganegaraan"),

		'is_imported' 				: 	fields.boolean("Imported to Partner?", select=1),
		"notes"						:	fields.char("Notes"),
		"source"					:	fields.char("Source"),
	}

	def action_import(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import(self, cr, uid, context=None):
		rmi_import_partner_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'rmi_import_partner_limit')
		_logger.warning('running cron rmi_import_partner, limit=%s' % rmi_import_partner_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(rmi_import_partner_limit), context=context)
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

		partner =  self.pool.get('res.partner')
		country =  self.pool.get('res.country')
		master_agama = self.pool.get('reliance.agama')
		master_status_nikah = self.pool.get('reliance.status_nikah')
		master_warga_negara = self.pool.get('reliance.warga_negara')
		master_pekerjaan = self.pool.get('reliance.pekerjaan_rmi')
		master_range_penghasilan = self.pool.get('reliance.range_penghasilan_rmi')
		master_jenis_kelamin = self.pool.get('reliance.jenis_kelamin')
		states_mapping = self.pool.get('reliance.states_mapping')

		for import_rmi in self.browse(cr, uid, ids, context=context):
			if not import_rmi.account_no:
				ex = ex + 1
				self.write(cr, uid, import_rmi.id ,  {'notes':'empty line, no account_no'}, context=context)
				cr.commit()
				continue
			data = {}
			data2 = {}

			for k in PARTNER_MAPPING.keys():
				partner_fname = PARTNER_MAPPING[k]
				if partner_fname:
					import_rmi_fname = "import_rmi.%s" % k 
					data.update( {partner_fname : eval(import_rmi_fname)})

			########################## search country
			country_id = country.search(cr, uid, [('name','ilike',import_rmi.negara)], context=context)
			if not country_id:
				ex=ex+1
				self.write(cr, uid, import_rmi.id, {'notes':'NO COUNTRY'}, context=context)
				cr.commit()
				continue
			else:
				country_id = country_id[0]

			########################## search propinsi
			# if import_rmi.propinsi:
			# 	state_id = country.find_or_create_state(cr, uid, import_rmi.propinsi, country_id, context=context)
			# else:
			# 	state_id = False
			# import pdb;pdb.set_trace()
			state_id = states_mapping.get(cr, uid, import_rmi.propinsi, context=context)
			data2.update({'state_id': state_id})
			
			############################ cek master agama
			agama_id = master_agama.get(cr, uid, 'rmi', import_rmi.agama, context=context)
			data2.update({'perorangan_agama': agama_id})

			########################### cek master range_penghasilan_rmi
			range_penghasilan_id = master_range_penghasilan.get(cr, uid, import_rmi.gaji_pertahun, context=context)
			data2.update({'pekerjaan_penghasilan_per_tahun': range_penghasilan_id})

			############################ cek master pekerjaan rmi
			pekerjaan_id = master_pekerjaan.get(cr, uid, import_rmi.pekerjaan, context=context)
			data2.update({'pekerjaan_nama': pekerjaan_id})
						
			############################ cek master warga_negara
			warga_negara_id = master_warga_negara.get(cr, uid, 'rmi', import_rmi.kewarganegaraan, context=context)
			data2.update({'perorangan_kewarganegaraan': warga_negara_id})	

			############################ cek master jenis_kelamin
			jenis_kelamin_id = master_jenis_kelamin.get(cr, uid, 'rmi', import_rmi.jenis_kelamin, context=context)
			data2.update({'perorangan_jenis_kelamin': jenis_kelamin_id})


			############################# date birth
			date_birth = False
			if import_rmi.tanggal_lahir:
				try: 
					date_birth = datetime.strptime(import_rmi.tanggal_lahir, "%d-%m-%Y")
				except ValueError:
					self.write(cr, uid, import_rmi.id, {'notes':'date birth format error, use dd-mm-yyyy'}, context=context)
					ex = ex+1
					cr.commit()
					continue
			data.update( {'perorangan_tanggal_lahir':date_birth})


			########################## insert ahli waris
			if import_rmi.ahli_waris:
				partner_ahli_waris_ids = [(0,0,{
					'nama' 				: import_rmi.ahli_waris,
					'nomor_telepon' 	: False,
					'hubungan_keluarga' : import_rmi.hubungan_dengan_ahli_waris,
					'alamat' 			: False,
					'pendidikan_terakhir' : False,
				})]
			else:
				partner_ahli_waris_ids = False 

			########################## prepare data
			data.update({
				'comment'		: 'RMI',
				'state_id'		: state_id,
				'country_id'	: country_id,
				'partner_ahli_waris_ids': partner_ahli_waris_ids,
			})
			data2.update({'initial_bu'	: 'RMI'})

			########################## check exiting partner , create if not exists
			pid = partner.search(cr, uid, [('rmi_account_no','=',import_rmi.account_no)],context=context)
			if not pid:
				data.update(data2)
				pid = partner.create(cr, uid, data, context=context)	
				i = i + 1
			else:
				partner.write(cr, uid, pid, data2, context=context)	
				pid = pid[0]
				_logger.warning('Partner exist with rmi_account_no %s' % import_rmi.account_no)
				ex = ex + 1


			########################### commit per record
			cr.execute("update reliance_import_rmi set is_imported='t' where id=%s" % import_rmi.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped/updated %s' % (i, ex) )



####################################################################
# partner data
# from rmi-product-holding csv file
####################################################################

HOLDING_MAPPING = {
	"product_id"				:	"rmi_product_id",	
	"tanggal"					:	"rmi_tanggal",
	"product_name"				:	"rmi_product_name",
	"unit_penyertaan"			:	"rmi_unit_penyertaan",	
	"nab_saat_beli"				:	"rmi_nab_saat_beli",	
	"nab_sampai_hari_ini"		:	"rmi_nab_sampai_hari_ini",	
	"nominal_investasi_awal"	:	"rmi_nominal_investasi_awal",	
	"nominal_investasi_akhir"	:	"rmi_nominal_investasi_akhir",	
	"profit_capital_loss"		:	"rmi_profit_capital_loss",		
}

class import_rmi_product_holding(osv.osv): 
	_name 		= "reliance.import_rmi_product_holding"
	_columns 	= {
		"no"						:	fields.char("No"),
		"account_no"				:	fields.char("AccountNo"),
		"tanggal"					: 	fields.char("Tanggal"),
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
		"source"					:	fields.char("Source"),

	}


	def action_import(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import(self, cr, uid, context=None):
		rmi_import_product_holding_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'rmi_import_product_holding_limit')
		_logger.warning('running cron refi_import_kontrak, limit=%s' % rmi_import_product_holding_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(rmi_import_product_holding_limit), context=context)
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

		partner =  self.pool.get('res.partner')

		for import_rmi in self.browse(cr, uid, ids, context=context):

			if not import_rmi.account_no:
				ex = ex + 1
				self.write(cr, uid, import_rmi.id ,  {'notes':'empty line, no account_no'}, context=context)
				cr.commit()
				continue

			# pid = partner.search(cr, uid, [('rmi_sid','=', import_rmi.sid)], context=context)
			pid = partner.search(cr, uid, [
				('rmi_account_no','=', import_rmi.account_no),
				], context=context)
			if not pid:
				ex=ex+1
				self.write(cr, uid, import_rmi.id, {'notes':'NO PARTNER with account_no=%s' % (import_rmi.account_no)}, context=context)
				cr.commit()
				continue
			else:
				pid = pid[0]

			data = {}
			for k in HOLDING_MAPPING.keys():
				partner_fname = HOLDING_MAPPING[k]
				if partner_fname:
					import_rmi_fname = "import_rmi.%s" % k 
					data.update( {partner_fname : eval(import_rmi_fname)})		

			# clear koma
			for k in data.keys():
				if k in ['product_id','product_name']:
					continue
				if not data[k]:
					data[k] = 0.0
				else:
					data[k] = data[k].strip().replace(',','').replace('-','0').replace(')','').replace('(','-')

			tanggal = False
			if import_rmi.tanggal and import_rmi.tanggal != "NULL":
				try:
					tanggal = datetime.strptime(import_rmi.tanggal, "%d-%m-%Y")
				except ValueError:
					self.write(cr, uid, import_rmi.id, {'notes': 'tanggal format error, use dd-mm-yyyy'},
							   context=context)
					ex = ex + 1
					cr.commit()
					continue
			data.update({'rmi_tanggal': tanggal})

			pid = partner.write(cr, uid, pid, data, context=context)	


			#commit per record
			i = i +1
			cr.execute("update reliance_import_rmi_product_holding set is_imported='t' where id=%s" % import_rmi.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done updating %s partner and skipped %s' % (i, ex) )
