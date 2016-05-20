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

		"refi_domisili_kecamatan" 	: fields.char("REFI Domisili Kec."),
		"refi_domisili_kota"		: fields.char("REFI Domisili Kota"),
		"refi_domisili_propinsi"	: fields.char("REFI Domisili Prop."),
		"refi_kode_pos"				: fields.char("REFI Domisili Kode POS"),
		"refi_tipe_id"				: fields.char("REFI Tipe ID"),

		"refi_parent_id"			: fields.many2one('res.partner', "REFI Perusahaan", select=1),
		"refi_tanggal_bayar"		: fields.char("REFI Tanggal Bayar"),
		"refi_frek_bayar"			: fields.char("REFI Frek Bayar"),
		"refi_tanggal_masuk_kerja"	: fields.char("REFI Tgl. Masuk Kerja"),

		#statement
		"refi_bulan_tahun_survey"				:	fields.char("REFI Bln/Thn Survey"),
		"refi_time_deps_saving_account"			:	fields.float("REFI Time Deps Saving Acc."),
		"refi_vehicle"							:	fields.float("REFI Vehicle"),
		"refi_jml_kendaraan"					:	fields.float("REFI Jml Kendaraan"),
		"refi_properties"						:	fields.float("REFI Properties"),
		"refi_jml_rumah"						:	fields.float("REFI Jml Rumah"),
		"refi_others_aktiva_lainnya"			:	fields.float("REFI Others Aktiva Lainnya"),
		"refi_mortagage_loan_inst"				:	fields.float("REFI Mort. Loan Inst"),
		"refi_mortgage_loan_inst_balance"		:	fields.float("REFI Mort. Loan Inst. Bal."),
		"refi_renting"							:	fields.float("REFI Renting"),
		"refi_car_credit"						:	fields.float("REFI Car Credit"),
		"refi_car_credit_balance"				:	fields.float("REFI Car Credit Balance"),
		"refi_credit_card"						:	fields.float("REFI Credit Card"),
		"refi_credit_card_balance"				:	fields.float("REFI Credit Card Balance"),
		"refi_credit_line"						:	fields.float("REFI Credit Line"),
		"refi_credit_line_balance"				:	fields.float("REFI Credit Line Balance"),
		"refi_monthly_expenditure"				:	fields.float("REFI Monthly Expenditure"),
		"refi_monthly_expenditure_balance"		:	fields.float("REFI Monthly Expenditure Bal."),
		"refi_mortgage_loan_int"				:	fields.float("REFI Mort. Loan Int"),
		"refi_mortgage_loan_int_balance_equity"	:	fields.float("REFI Mort. Loan Int Bal. Equity"),
		"refi_other"							:	fields.float("REFI Other"),
		"refi_other_balance_equity_net_income"	:	fields.float("REFI Other Bal. Equity Net Income"),
		"refi_spouse_income"					:	fields.float("REFI Spouse Income"),
		"refi_other_income"						:	fields.float("REFI Other Income	"),		

		"refi_kontrak_ids"						: 	fields.one2many('reliance.refi_kontrak','partner_id','REFI Kontrak', ondelete="cascade"),
	}


	######################################################################
	# mengambil data kontrak nasabah REFI berdasarkan nomor Reliance ID
	######################################################################
	def get_refi_kontrak(self,cr, uid, reliance_id, context=None):
		kontraks = False
		pid = self.search(cr, uid, [('reliance_id','=',reliance_id)], context=context)

		if pid:
			refi_kontrak = self.pool.get('reliance.refi_kontrak')
			kontraks = refi_kontrak.search_read(cr,uid,[('partner_id','=',pid[0])],context=context)
		else:
			raise osv.except_osv(_('error'),  'no partner with reliance_id=%s' % reliance_id)

		return kontraks 

	######################################################################
	# mengambil data kontrak nasabah REFI berdasarkan nomor Debitur
	######################################################################
	def get_refi_kontrak_by_no_debitur(self,cr, uid, no_debitur, context=None):
		kontraks = False
		pid = self.search(cr, uid, [('refi_no_debitur','=',no_debitur)], context=context)

		if pid:
			refi_kontrak = self.pool.get('reliance.refi_kontrak')
			kontraks = refi_kontrak.search_read(cr,uid,[('partner_id','=',pid[0])],context=context)
		else:
			raise osv.except_osv(_('error'),  'no partner with refi_no_debitur=%s' % no_debitur)

		return kontraks 

	######################################################################
	# mengambil data nasabah REFI berdasarkan nomor Kontrak
	######################################################################
	def get_refi_customer_by_no_kontrak(self,cr, uid, contract_number, context=None):
		refi_kontrak = self.pool.get('reliance.refi_kontrak')
		kid = refi_kontrak.search(cr, uid, [('contract_number','=',contract_number)], context=context)
		if not kid:
			raise osv.except_osv(_('error'),_("Not found kontrak with contract_number=%s")%contract_number ) 

		kontrak = refi_kontrak.browse(cr, uid, kid[0], context=context)

		partner = self.search_read(cr, uid, [('id','=',kontrak.partner_id.id)], context=context)
		if not partner:
			raise osv.except_osv(_('error'),_("Partner Not Found for contract_number=%s")%contract_number ) 

		return partner


class refi_kontrak(osv.osv):
	_name 		= "reliance.refi_kontrak"
	_rec_name	= "contract_number"

	_columns = {
		"partner_id"		: 	fields.many2one('res.partner', 'Partner', select=1),
		"contract_number"	:	fields.char("Contract Number", select=1),	
		"customer_no"		:	fields.char("Customer No", select=1),	
		"customer_name"		:	fields.char("Customer Name", select=1),	
		"product"			:	fields.char("Product", select=1),	
		"asset_name"		:	fields.char("Asset Name", select=1),	
		"outstanding"		:	fields.float("Outstanding"),	
		"next_installment"	:	fields.date("Next Installment"),	
		"pass_due"			:	fields.float("Pass Due"),	
		"maturity_date"		:	fields.date("Maturity Date"),		
	}

