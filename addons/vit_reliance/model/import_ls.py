from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


####################################################################
# mapping field import LS ke tabel res.partner
####################################################################

PARTNER_MAPPING = {
	"client_id"				:	"cif",
	"client_sid"			:	"sid",
	"client_name"			:	"name",
	"place_birth"			:	"perorangan_tempat_tanggal_lahir",
	"date_birth"			:	"perorangan_tempat_tanggal_lahir",
	"cr_address"			:	"perorangan_alamat_tempat_tinggal_saat_ini",
	"address"				:	"street",
	"id_card_type"			:	"id_card_type",
	"id_card"				:	"perorangan_nomor_ktp",
	"id_card_expire_date"	:	"perorangan_masa_berlaku_ktp",
	"npwp"					:	"perorangan_npwp",
	"nationality"			:	"perorangan_kewarganegaraan",
	"marital_status"		:	"perorangan_status_perkawinan",
	"phone"					:	"phone",
	"cellular"				:	"mobile",
	"fax"					:	"fax",
	# "couplenames"			:	"", masuk ke keluarga
	"email"					:	"email",
	"education"				:	"perorangan_pendidikan_terakhir",
	"religion"				:	"perorangan_agama",
	"mother_name"			:	"perorangan_nama_gadis_ibu_kandung",
	"mothers_maiden_name"	:	"perorangan_nama_gadis_ibu_kandung",
	"title"					:	"pekerjaan_nama",
	"organization"			:	"perorangan_nama_organisasi",
	# "original_location"		:	"",
	"occupation"			:	"pekerjaan_nama",
	# "occupation_desc"		:	"",
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
	"gross_income_per_year"	:	"pekerjaan_penghasilan_per_tahun",
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
		"address"				:		fields.char("Address"),
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
		"client_sid"			:		fields.char("ClientSID"),
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
		'is_imported' 			: 		fields.boolean("Imported to Partner?", select=1)
	}

	def action_import_partner(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner(self, cr, uid, context=None):
		_logger.warning('running cron import_ls')
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=100, context=context)
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

		for import_ls in self.browse(cr, uid, ids, context=context):
			data = {}
			for k in PARTNER_MAPPING.keys():
				partner_fname = PARTNER_MAPPING[k]
				import_ls_fname = "import_ls.%s" % k 
				data.update( {partner_fname : eval(import_ls_fname)})
			
			# check exiting partner 
			pid = partner.search(cr, uid, [('cif','=',import_ls.client_id)],context=context)
			if not pid:
				pid = partner.create(cr, uid, data, context=context)	
				i = i + 1
			else:
				_logger.warning('Partner exist with CIF %s' % import_ls.client_id)
				ex = ex + 1

			cr.execute("update reliance_import_ls set is_imported='t' where id=%s" % import_ls.id)

			#commit per record
			cr.commit()
		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )			


####################################################################
# partner's cash
####################################################################

class import_ls_cash(osv.osv):
	_name 		= "reliance.import_ls_cash"
	_columns 	= {
		"client_id"		:		fields.char("ClientID", select=1),
		"date"			:		fields.char("Date", select=1),
		"cash_on_hand"	:		fields.char("CashOnHand"),
		"net_ac"		:		fields.char("NetAC"),
	}

	def action_import_partner_cash(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner_cash(self, cr, uid, context=None):
		active_ids = self.search(cr, uid, [('is_imported','=', False)], context=context)
		if active_ids:
			self.actual_process(cr, uid, active_ids, context=context)
		else:
			print "no partner cash to import"
		return True

	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		cr.commit()
		raise osv.except_osv( 'OK!' , 'Done creating %s partner_cash ' % (i) )			





####################################################################
# partner's stock
####################################################################
class import_ls_stock(osv.osv):
	_name 		= "reliance.import_ls_stock"
	_columns 	= {	
		"date"				:	fields.char("Date", select=1),
		"client_id"			:	fields.char("ClientID", select=1),
		"stock_id"			:	fields.char("StockID", select=1),
		"avg_price"			:	fields.char("AvgPrice"),
		"close_price"		:	fields.char("ClosePrice"),
		"balance"			:	fields.char("Balance"),
		"lpp"				:	fields.char("LPP"),
		"stock_avg_value"	:	fields.char("StockAvgValue"),
		"market_value"		:	fields.char("MarketValue"),
	}

	def action_import_partner_stock(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner_stock(self, cr, uid, context=None):
		active_ids = self.search(cr, uid, [('is_imported','=', False)], context=context)
		if active_ids:
			self.actual_process(cr, uid, active_ids, context=context)
		else:
			print "no partner stock to import"
		return True

	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		cr.commit()
		raise osv.except_osv( 'OK!' , 'Done creating %s partner_stock ' % (i) )			
