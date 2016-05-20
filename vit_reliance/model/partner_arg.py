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
		"arg_cust_code"			: fields.char("ARG Customer Code", select=1),
		"arg_nomor_polis"		: fields.char("ARG Nomor Polis", select=1),
		"arg_parent_id"			: fields.many2one('res.partner', 'ARG Customer'),

		'partner_polis_ids'		: fields.one2many('reliance.arg_partner_polis','partner_id','ARG Polis', ondelete="cascade"),
		'partner_polis_risk_ids': fields.one2many('reliance.arg_partner_polis_risk','partner_id','ARG Polis Risk', ondelete="cascade"),

	}

	################################################################
	# mengambil data  nasabah ARG berdasarkan  Reliance ID
	################################################################
	def get_arg_customer(self, cr, uid, reliance_id, context=None):
		partner = self.search_read(cr, uid, [('reliance_id','=',reliance_id)], context=context)
		if not partner:
			raise osv.except_osv(_('error'), 'no partner with reliance_id=%s' % reliance_id) 

		return partner 

	################################################################
	# mengambil data  nasabah ARG berdasarkan  Cust Code ARG
	################################################################
	def get_arg_customer_by_cust_code(self, cr, uid, cust_code, context=None):
		partner = self.search_read(cr, uid, [('arg_cust_code','=',cust_code)], context=context)
		if not partner:
			raise osv.except_osv(_('error'), 'no partner with cust_code=%s' % cust_code) 

		return partner 

	################################################################
	# mengambil data semua polis yang dimiliki oleh nasabah
	################################################################
	def get_arg_customer_all_polis(self, cr, uid, reliance_id, context=None):
		polises = False
		pid = self.search(cr, uid, [('reliance_id','=',reliance_id)], context=context)

		if pid:
			polis = self.pool.get('reliance.arg_partner_polis')
			polises = polis.search_read(cr,uid,[('partner_id','=',pid[0])],context=context)
		else:
			raise osv.except_osv(_('errp'), 'no partner with nomor_polis=%s' % nomor_polis ) 

		return polises 

	################################################################
	# mencari data nasabah pemegang polis
	################################################################
	def get_arg_customer_by_polis_number(self, cr, uid, policy_no, context=None):
		polis = self.pool.get('reliance.arg_partner_polis')
		pol = polis.search_read(cr, uid, [('arg_nomor_polis','=',policy_no)], context=context)
		if not pol:
			raise osv.except_osv(_('error'),_("no polis with arg_nomor_polis=%s") % policy_no ) 

		partner = self.search_read(cr, uid, [('id','=',pol[0]['partner_id'][0])], context=context)
		return partner

	################################################################
	# mencari data polis
	################################################################
	def get_arg_polis(self, cr, uid, policy_no, context=None):
		polis = self.pool.get('reliance.arg_partner_polis')
		pol = polis.search_read(cr, uid, [('arg_nomor_polis','=',policy_no)], context=context)
		if not pol:
			raise osv.except_osv(_('error'),_("no polis with arg_nomor_polis=%s") % policy_no ) 

		return pol 


class partner_polis(osv.osv):
	_name = "reliance.arg_partner_polis"
	_rec_name = "arg_nomor_polis"
	_columns = {
		'partner_id'			: fields.many2one('res.partner', 'partner'),
		"arg_nomor_polis"		: fields.char("Nomor Polis"),
		"arg_class"				: fields.char("Class"),
		"arg_subclass"			: fields.char("Sub Class"),	
		"arg_eff_date"			: fields.date("Eff Date"),
		"arg_exp_date"			: fields.date("Exp Date"),

		"arg_company_code"		: fields.char("Company Code"),
		"arg_company_name"		: fields.char("Company Name"),
		"arg_company_type"		: fields.char("Company Type"),
		
		"arg_marketing_code"	: fields.char("Marketing Code"),
		"arg_marketing_name"	: fields.char("Marketing Name"),
		
		"arg_qq"				: fields.char("QQ"),
		"arg_cp"				: fields.char("Cust CP"),

	}

class partner_polis_risk(osv.osv):
	_name = "reliance.arg_partner_polis_risk"
	_columns = {
		'partner_id'				: 	fields.many2one('res.partner', 'Partner', required=True),
		"policy_id"					:	fields.many2one('reliance.arg_partner_polis', 'Polis', required=True),
		"asset_description"			:	fields.char("Asset Description"),
		"item_no"					:	fields.char("Item No"),
		"tahun"						:	fields.integer("Tahun"),
		"total_premi"				:	fields.float("Total Premi"),
		"total_nilai_pertanggungan"	:	fields.float("Total Nilai Pertanggungan"),
	}


