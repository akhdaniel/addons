from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime
import converter

_logger = logging.getLogger(__name__)


####################################################################
# mapping field import LS ke tabel res.partner
####################################################################

PARTNER_MAPPING = {
	"client_id"				:	"ls_client_id",
	"client_sid"			:	"ls_client_sid",
	"client_name"			:	"name",
	"place_birth"			:	"perorangan_tempat_lahir",
	"date_birth"			:	"perorangan_tanggal_lahir",
	# "cr_address"			:	"perorangan_alamat_tempat_tinggal_saat_ini",
	# "address"				:	"street",
	"cr_address"			:	"street",
	"cr_city"				:	"city",
	"cr_country"			:	"country_id",
	"cr_zip"				:	"zip",
	"id_card_type"			:	"ls_id_card_type",
	"id_card"				:	"perorangan_nomor_ktp",
	"id_card_expire_date"	:	"perorangan_masa_berlaku_ktp",
	"npwp"					:	"perorangan_npwp",
	# "nationality"			:	"perorangan_kewarganegaraan",
	# "marital_status"		:	"perorangan_status_perkawinan",
	"phone"					:	"phone",
	"cellular"				:	"mobile",
	"fax"					:	"fax",
	# "couplenames"			:	"", masuk ke keluarga
	"email"					:	"email",
	"education"				:	"perorangan_pendidikan_terakhir",
	# "religion"				:	"perorangan_agama",
	"mother_name"			:	"perorangan_nama_gadis_ibu_kandung",
	"mothers_maiden_name"	:	"perorangan_nama_gadis_ibu_kandung",
	"title"					:	"pekerjaan_profesi",
	"organization"			:	"perorangan_nama_organisasi",
	# "original_location"		:	"",
	# "occupation"			:	"pekerjaan_nama",
	"occupation_desc"		:	"pekerjaan_jabatan",
	"company_name"			:	"pekerjaan_nama_perusahaan",
	# "client_sid"			:	"", #SID perusahaan ?
	"company_address"		:	"pekerjaan_alamat_perusahaan",
	# "company_city"			:	"",
	# "company_country"		:	"",
	"company_description"	:	"pekerjaan_bidang_usaha",
	# "company_zip"			:	"",
	"company_phone"			:	"pekerjaan_nomor_telepon",
	"company_fax"			:	"pekerjaan_nomor_faksimile",
	"source_of_fund"		:	"perorangan_sumber_dana_yg_akan_diinvestasikan",
	# "source_of_fund_desc"	:	"",
	# "gross_income_per_year"	:	"pekerjaan_penghasilan_per_tahun",
	# "house_status"			:	"",
	# "registered"			:	"",
	# "void"					:	"",
}


####################################################################
# partner data
# from ls-customer csv file
####################################################################
class import_ls(osv.osv): 
	_name 		= "reliance.import_ls"
	_columns 	= {
		"client_id"				:		fields.char("ClientID", select=1),
		"client_sid"			:		fields.char("ClientSID", select=1),
		"client_name"			:		fields.char("ClientName", select=1),
		"place_birth"			:		fields.char("PlaceBirth"),
		"date_birth"			:		fields.char("DateBirth"),
		"cr_address"			:		fields.char("CrAddress"),
		"cr_city"				:		fields.char("CrCity"),
		"cr_country"			:		fields.char("CrCountry"),
		"cr_zip"				:		fields.char("CrZip"),
		"id_card_type"			:		fields.char("IDCardType"),
		"id_card"				:		fields.char("IDCard"),
		"id_card_expire_date"	:		fields.char("IDCardExpireDate"),
		"npwp"					:		fields.char("NPWP"),
		"nationality"			:		fields.char("Nationality"),
		"marital_status"		:		fields.char("MaritalStatus"),
		"phone"					:		fields.char("Phone"),
		"cellular"				:		fields.char("Cellular"),
		"fax"					:		fields.char("Fax"),
		"couplenames"			:		fields.char("Couplenames"),
		"email"					:		fields.char("Email"),
		"education"				:		fields.char("Education"),
		"religion"				:		fields.char("Religion"),
		"mother_name"			:		fields.char("MotherName"),
		"mothers_maiden_name"	:		fields.char("MothersMaidenName"),
		"title"					:		fields.char("Title"),
		"organization"			:		fields.char("Organization"),
		"original_location"		:		fields.char("OriginalLocation"),
		"occupation"			:		fields.char("Occupation"),
		"occupation_desc"		:		fields.char("OccupationDesc"),
		"company_name"			:		fields.char("CompanyName"),
		"client_sid2"			:		fields.char("ClientSID"),
		"company_address"		:		fields.char("CompanyAddress"),
		"company_city"			:		fields.char("CompanyCity"),
		"company_country"		:		fields.char("CompanyCountry"),
		"company_description"	:		fields.char("CompanyDescription"),
		"company_zip"			:		fields.char("CompanyZip"),
		"company_phone"			:		fields.char("CompanyPhone"),
		"company_fax"			:		fields.char("CompanyFax"),
		"source_of_fund"		:		fields.char("SourceOfFund"),
		"source_of_fund_desc"	:		fields.char("SourceOfFundDesc"),
		"gross_income_per_year"	:		fields.char("GrossIncomePerYear"),
		"house_status"			:		fields.char("HouseStatus"),
		"registered"			:		fields.char("Registered"),
		"void"					:		fields.char("Void"),
		'is_imported' 			: 		fields.boolean("Imported to Partner?", select=1),
		"notes"					:		fields.char("Notes"),
		"source"				:		fields.char("Source"),
	}

	def action_import_partner(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner(self, cr, uid, context=None):
		ls_import_partner_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ls_import_partner_limit')
		_logger.warning('running cron ls_import_partner, limit=%s' % ls_import_partner_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(ls_import_partner_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	################################################################
	# the import process
	# baca record ids, insert ke partner dengan field sesuai 
	# PARTNER_MAPPING
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')
		country = self.pool.get('res.country')
		master_agama = self.pool.get('reliance.agama')
		master_status_nikah = self.pool.get('reliance.status_nikah')
		master_warga_negara = self.pool.get('reliance.warga_negara')
		master_pekerjaan = self.pool.get('reliance.pekerjaan_ls')
		master_range_penghasilan = self.pool.get('reliance.range_penghasilan_ls')

		for import_ls in self.browse(cr, uid, ids, context=context):
			data = {}
			data2 = {} # khusus untuk yang update
			country_id = False

			for k in PARTNER_MAPPING.keys():
				partner_fname = PARTNER_MAPPING[k]
				import_ls_fname = "import_ls.%s" % k 
				data.update( {partner_fname : eval(import_ls_fname)})

			country_name = import_ls.cr_country
			country_id = country.search(cr, uid, [('name','ilike',country_name)], context=context)

			if not country_id:
				self.write(cr, uid, import_ls.id, {'notes':'NO COUNTRY found for CrCountry'}, context=context)
				ex = ex+1
				cr.commit()
				continue

			data.update( {'country_id' :country_id[0]})
			data.update( {'comment':'LS'})
			data2.update( {'initial_bu':'LS'})

			# date birth
			date_birth = False
			if import_ls.date_birth and import_ls.date_birth !="NULL":
				try: 
					date_birth = datetime.strptime(import_ls.date_birth, "%Y-%m-%d")
				except ValueError:
					self.write(cr, uid, import_ls.id, {'notes':'date birth format error, use yyyy-mm-dd'}, context=context)
					ex = ex+1
					cr.commit()
					continue
			data.update( {'perorangan_tanggal_lahir':date_birth})

			# cek master agama
			agama_id = master_agama.get(cr, uid, 'ls', import_ls.religion, context=context)
			data2.update({'perorangan_agama': agama_id})
			
			# cek master status_nikah
			status_nikah_id = master_status_nikah.get(cr, uid, 'ls', import_ls.marital_status, context=context)
			data2.update({'perorangan_status_perkawinan': status_nikah_id})
			
			# cek master warga_negara
			warga_negara_id = master_warga_negara.get(cr, uid, 'ls', import_ls.nationality, context=context)
			data2.update({'perorangan_kewarganegaraan': warga_negara_id})

			# cek master pekerjaan ls
			pekerjaan_id = master_pekerjaan.get(cr, uid, import_ls.occupation, context=context)
			data2.update({'pekerjaan_nama': pekerjaan_id})
			
			# cek master range_penghasilan_ls
			range_penghasilan_id = master_range_penghasilan.get(cr, uid, import_ls.gross_income_per_year, context=context)
			data2.update({'pekerjaan_penghasilan_per_tahun': range_penghasilan_id})

			# check exiting partner and create if not exists
			pid = partner.search(cr, uid, [('ls_client_id','=',import_ls.client_id)],context=context)
			if not pid:
				data.update(data2)
				pid = partner.create(cr, uid, data, context=context)	
				i = i + 1
			else:
				partner.write(cr, uid, pid, data2, context=context)	
				self.write(cr, uid, import_ls.id, {'notes':'Partner exist with CIF %s' % import_ls.client_id}, context=context)
				_logger.warning('Partner exist with CIF %s' % import_ls.client_id)
				ex = ex + 1


			#commit per record
			cr.execute("update reliance_import_ls set is_imported='t' where id=%s" % import_ls.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped/updated %s' % (i, ex) )			


####################################################################
# partner's cash
####################################################################
class import_ls_cash(osv.osv):
	_name 		= "reliance.import_ls_cash"
	_columns 	= {
		"client_id"		:		fields.char("ClientID", select=1),
		"date"			:		fields.char("Date", select=1),
		"cash_on_hand"	:		fields.char("CashOnHand"),
		"saldo_t1"		:		fields.char("SaldoT1"),
		"saldo_t2"		:		fields.char("SaldoT2"),
		'is_imported' 	: 		fields.boolean("Imported to Partner Cash?", select=1),
		"notes"			:		fields.char("Notes"),
		"source"		:		fields.char("Source"),
	}

	def action_import_partner_cash(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)

	def cron_import_partner_cash(self, cr, uid, context=None):
		ls_import_partner_cash_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ls_import_partner_cash_limit')
		_logger.warning('running cron ls_import_partner_cash, limit=%s' % ls_import_partner_cash_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(ls_import_partner_cash_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner cash to import"
		return True

	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0
		upd = 0
		date = False

		conv = converter.converter()

		partner = self.pool.get('res.partner')
		cash = self.pool.get('reliance.partner_cash')
		
		for import_cash in self.browse(cr, uid, ids, context=context):

			if not import_cash.client_id:
				ex = ex + 1
				self.write(cr, uid, import_cash.id ,  {'notes':'empty line'}, context=context)
				cr.commit()
				continue

			########## cari partner dulu ####################
			pid = partner.search(cr, uid, [( 'ls_client_id','=', import_cash.client_id)], context=context)
			if pid:
				###### cari existing Cash record ############
				cid = cash.search(cr, uid, [('partner_id','=', pid[0] )], context=context)

				###### convert date ############
				if import_cash.date:
					date = conv.convert_date(cr, uid, self, import_cash, "date", "%Y-%m-%d",ex, context=context)
					if not date:
						continue

				###### convert cash_on_hand ############
				cash_on_hand = conv.convert_float(cr, uid, self, import_cash, "cash_on_hand", ",", ".", ex, context=context)
				if cash_on_hand is False:
					continue

				###### convert saldo_t1 ############
				saldo_t1 = conv.convert_float(cr, uid, self, import_cash, "saldo_t1", ",", ".", ex, context=context)
				if saldo_t1 is False:
					continue

				###### convert saldo_t2 ############
				saldo_t2 = conv.convert_float(cr, uid, self, import_cash, "saldo_t2", ",", ".", ex, context=context)
				if saldo_t2 is False:
					continue

				data = {
					"partner_id"	: 	pid[0],	
					"date"			:	date ,
					"cash_on_hand"	:	cash_on_hand,
					# "net_ac"		:	import_cash.net_ac,
					"saldo_t1"		:	saldo_t1,
					"saldo_t2"		:	saldo_t2,
				}
				if not cid:
					cash.create(cr,uid,data,context=context)
					i = i + 1
				else:
					upd = upd + 1
					cash.write(cr, uid, cid, data, context=context)
					_logger.warning('Update Partner Cash for ClientID=%s' % (import_cash.client_id))
			else:
				ex = ex + 1
				self.write(cr, uid, import_cash.id ,  {'notes':'No Partner'}, context=context)
				_logger.warning('Partner ID not found for ClientID=%s' % import_cash.client_id)
				cr.commit()
				continue

			cr.execute("update reliance_import_ls_cash set is_imported='t' where id=%s" % import_cash.id)
			cr.commit()


		raise osv.except_osv( 'OK!' , 'Done creating %s partner_cash, skipped=%s,updated=%s ' % (i,ex, upd) )			



####################################################################
# partner's stock
####################################################################
class import_ls_stock(osv.osv):
	_name 		= "reliance.import_ls_stock"
	_columns 	= {	
		"date"				:	fields.char("Date", select=1),
		"client_id"			:	fields.char("ClientID", select=1),
		"stock_id"			:	fields.char("StockID", select=1),
		"stock_name"		:	fields.char("stockname", select=1),
		"avg_price"			:	fields.char("AvgPrice"),
		"close_price"		:	fields.char("ClosePrice"),
		"balance"			:	fields.char("Balance"),
		"lpp"				:	fields.char("LPP"),
		"stock_avg_value"	:	fields.char("StockAvgValue"),
		"market_value"		:	fields.char("MarketValue"),
		"stock_type"		:	fields.char("StockType"),
		"sharesperlot"		:	fields.char("sharesperlot"),
		'is_imported' 		: 	fields.boolean("Imported to Partner Stock?", select=1),
		"notes"				:	fields.char("Notes"),
		"source"			:	fields.char("Source"),
	}

	def action_import_partner_stock(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner_stock(self, cr, uid, context=None):
		ls_import_partner_stock_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ls_import_partner_stock_limit')
		_logger.warning('running cron ls_import_partner, limit=%s' % ls_import_partner_stock_limit)

		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(ls_import_partner_stock_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner stock to import"
		return True

	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0
		upd = 0
		date = False

		partner = self.pool.get('res.partner')
		stock = self.pool.get('reliance.partner_stock')
		
		for import_stock in self.browse(cr, uid, ids, context=context):
			
			if not import_stock.client_id:
				ex = ex + 1
				self.write(cr, uid, import_stock.id ,  {'notes':'empty line'}, context=context)
				cr.commit()
				continue

			########## cari partner dulu ####################
			pid = partner.search(cr, uid, [( 'ls_client_id','=', import_stock.client_id)], context=context)
			if pid:
				###### cari existing Cash record ############
				cid = stock.search(cr, uid, [('partner_id','=', pid[0]),('stock_id','=',import_stock.stock_id)], context=context)
				date = False 
				if import_stock.date:
					try: 
						date = datetime.strptime(import_stock.date, "%Y-%m-%d")
					except ValueError:
						self.write(cr, uid, import_stock.id, {'notes':'date format error, use yyyy-mm-dd'}, context=context)
						ex = ex+1
						cr.commit()
						continue

				data = {
					"date"				: date,
					"partner_id"		: pid[0],
					"stock_id"			: import_stock.stock_id,
					"stock_name"		: import_stock.stock_name,
					"avg_price"			: import_stock.avg_price,
					"close_price"		: import_stock.close_price, 
					"balance"			: import_stock.balance,
					"lpp"				: import_stock.lpp,
					"stock_avg_value"	: import_stock.stock_avg_value,
					"market_value"		: import_stock.market_value,
					"stock_type"		: import_stock.stock_type,
					"sharesperlot"		: import_stock.sharesperlot,
				}

			
				if not cid:
					stock.create(cr,uid,data,context=context)
					i = i + 1
				else:
					upd = upd + 1
					stock.write(cr,uid, cid, data, context=context)
					_logger.warning('updating partner stock_id=%s partner ls_client_id=%s' % (import_stock.stock_id, import_stock.client_id))
					_logger.warning(data)

			else:
				ex = ex + 1
				msg = 'NO PARTNER'
				self.write(cr, uid, import_stock.id, {'notes':msg}, context=context)
				cr.commit()
				continue

			cr.execute("update reliance_import_ls_stock set is_imported='t' where id=%s" % import_stock.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner_stock, skipped=%s, updated=%s ' % (i,ex, upd) )			


